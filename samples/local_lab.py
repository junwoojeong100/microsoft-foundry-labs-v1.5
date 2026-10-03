"""Foundry Local device exercise. Plan-only unless --local; never calls Azure."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

from lab_profile import LANGUAGE

ROOT = Path(__file__).resolve().parents[1]
MAX_TOKENS = 256


def messages(style: str) -> list[dict[str, str]]:
    if style not in {"sentence", "checklist"}:
        raise ValueError("Choose sentence or checklist.")
    if LANGUAGE == "en":
        form = "Use one sentence." if style == "sentence" else "Use exactly three short checklist items."
        question = "Explain the difference between a Contoso purchase request draft and an actual order."
        instruction = "Use only this synthetic fact: a draft is not approval, an order, or payment. " + form
    else:
        form = "한 문장으로 답하세요." if style == "sentence" else "짧은 체크리스트 세 항목으로 답하세요."
        question = "Contoso 구매 요청 초안과 실제 주문의 차이를 설명해 주세요."
        instruction = "합성 사실: 초안은 승인, 주문, 결제 완료가 아닙니다. 이 사실만 사용하세요. " + form
    return [{"role": "system", "content": instruction}, {"role": "user", "content": question}]


def exercise(manager, command: str, alias: str, style: str, allow_download: bool) -> dict:
    if command not in {"inspect", "download", "chat"}:
        raise ValueError("Choose inspect, download, or chat.")
    model = manager.catalog.get_model(alias)
    report = {
        "execution": "on_device_not_azure", "requested_alias": alias, "model_id": model.id,
        "cached": model.is_cached, "loaded": model.is_loaded, "language": LANGUAGE,
    }
    if command == "inspect":
        return report
    if command == "download":
        if not allow_download:
            raise ValueError("Model/component downloads require --allow-download.")
        started = time.perf_counter()
        manager.download_and_register_eps(progress_callback=lambda name, percent: print(f"{name}: {percent:.0f}%"))
        model.download(lambda percent: print(f"Model download: {percent:.0f}%"))
        if not model.is_cached:
            raise RuntimeError("Download returned without a cached model.")
        return {**report, "cached": True, "download_seconds": round(time.perf_counter() - started, 6)}
    if not model.is_cached:
        raise RuntimeError("Model is not cached. Review and approve the separate download step first.")
    if model.is_loaded:
        raise RuntimeError("The model is already loaded; do not borrow or unload another session.")
    started = time.perf_counter()
    try:
        model.load()
        report["load_seconds"] = round(time.perf_counter() - started, 6)
        client = model.get_chat_client()
        client.settings.max_tokens = MAX_TOKENS
        started = time.perf_counter()
        result = client.complete_chat(messages(style))
        report["inference_seconds"] = round(time.perf_counter() - started, 6)
        if not result.choices or result.choices[0].finish_reason != "stop":
            raise RuntimeError("Local generation did not finish normally; do not record a truncated answer as complete.")
        answer = result.choices[0].message.content
        if not isinstance(answer, str) or not answer.strip():
            raise RuntimeError("Local generation returned no answer.")
        report.update(answer=answer, style=style, max_output_tokens=MAX_TOKENS)
    finally:
        if model.is_loaded:
            model.unload()
        if model.is_loaded:
            raise RuntimeError("The same local model did not unload; inspect this process before continuing.")
    return {**report, "loaded": False, "unloaded": True}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["inspect", "download", "chat"], nargs="?", default="inspect")
    parser.add_argument("--model", default="qwen2.5-0.5b")
    parser.add_argument("--style", choices=["sentence", "checklist"], default="sentence")
    parser.add_argument("--local", action="store_true", help="Allow actual SDK/catalog/device work, not Azure.")
    parser.add_argument("--allow-download", action="store_true", help="Allow model and execution-provider downloads.")
    args = parser.parse_args(argv)
    if args.allow_download and args.command != "download":
        raise ValueError("--allow-download applies only to the separate download command.")
    if not args.local:
        print(json.dumps({
            "status": "plan_only", "command": args.command, "model": args.model,
            "style": args.style, "sdk_initialized": False, "azure_calls": 0,
            "download_requires": "--local --allow-download", "max_output_tokens": MAX_TOKENS,
        }, indent=2))
        return 0
    if args.command == "download" and not args.allow_download:
        raise ValueError("Review download/license/storage requirements and pass --allow-download explicitly.")
    from foundry_local_sdk import Configuration, FoundryLocalManager

    cache = ROOT / ".build" / "local-model-cache" / LANGUAGE
    cache.mkdir(parents=True, exist_ok=True)
    FoundryLocalManager.initialize(Configuration(app_name="contoso-local-lab", model_cache_dir=str(cache)))
    result = exercise(FoundryLocalManager.instance, args.command, args.model, args.style, args.allow_download)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
