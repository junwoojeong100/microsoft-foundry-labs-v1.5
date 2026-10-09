"""Synthetic Memory lifecycle. Deleting an item never deletes its Azure store or RG."""

from __future__ import annotations

import argparse
from datetime import timedelta
import json
import time
from uuid import uuid4

from cloud import project_client
from evidence import Budget, Evidence
from lab_cli import run as run_cli
from workshop import LANGUAGE, RESULTS, config_values, save_json

STATE = RESULTS / "memory.json"
PREFERENCE = (
    "Synthetic Contoso workshop user A prefers purchasing-policy answers in table format."
    if LANGUAGE == "en" else "Contoso 실습용 사용자 A는 구매 규정 답변을 표 형식으로 받는 것을 선호한다."
)


def memory_ids(result) -> set[str]:
    return {item.memory_item.memory_id for item in result.memories}


def run(command: str, confirm: str | None, evidence: Evidence) -> None:
    from azure.ai.projects.models import MemorySearchOptions, MemoryStoreDefaultDefinition, MemoryStoreDefaultOptions

    budget = Budget(max_requests=30, max_seconds=180)
    with project_client(evidence) as (project, _, endpoint, model):
        store = project.beta.memory_stores
        if command == "create":
            if STATE.exists():
                raise ValueError("Memory ownership receipt exists; no store is overwritten.")
            embedding = config_values()["FOUNDRY_EMBEDDING_DEPLOYMENT_NAME"]
            if not embedding:
                raise ValueError("Set FOUNDRY_EMBEDDING_DEPLOYMENT_NAME.")
            name = "contoso-memory-" + uuid4().hex[:8]
            state = {
                "name": name, "endpoint": endpoint, "run_id": evidence.run_id,
                "scope_a": evidence.run_id + "-user-a", "scope_b": evidence.run_id + "-user-b",
                "chat_model": model, "embedding_model": embedding, "ttl_seconds": 3600,
            }
            save_json(STATE, state)
            budget.before_request()
            created = store.create(
                name=name, definition=MemoryStoreDefaultDefinition(
                    chat_model=model, embedding_model=embedding,
                    options=MemoryStoreDefaultOptions(
                        user_profile_enabled=True, chat_summary_enabled=False, procedural_memory_enabled=False,
                        default_ttl_seconds=timedelta(hours=1),
                    ),
                ), metadata={"workshop_run": evidence.run_id}, description="Synthetic Contoso display preference only",
            )
            evidence.append("store_created", created)
            return
        state = json.loads(STATE.read_text(encoding="utf-8"))
        if state["endpoint"] != endpoint:
            raise ValueError("Memory receipt belongs to another project.")
        budget.before_request()
        actual = store.get(state["name"])
        if actual.metadata.get("workshop_run") != state["run_id"]:
            raise ValueError("Memory store ownership mismatch.")
        if not state.get("memory_id") and "/" in state["scope_a"]:
            evidence.append("empty_scope_contract_repair", {"old_a": state["scope_a"], "old_b": state["scope_b"]})
            state["previous_empty_scopes"] = [state["scope_a"], state["scope_b"]]
            state["scope_a"], state["scope_b"] = state["scope_a"].replace("/", "-"), state["scope_b"].replace("/", "-")
            save_json(STATE, state)
        if command == "remember":
            if state.get("memory_id"):
                raise ValueError("An item is already recorded. Do not create a duplicate.")
            budget.before_request()
            item = store.create_memory(
                name=state["name"], scope=state["scope_a"], content=PREFERENCE, kind="user_profile",
            )
            evidence.append("memory_created", item)
            state["memory_id"] = item.memory_id
            save_json(STATE, state)
        if not state.get("memory_id"):
            raise ValueError("Run remember before verify or forget.")
        if command == "forget":
            if confirm != state["memory_id"]:
                raise ValueError("Repeat the exact owned memory ID with --confirm. The store is retained.")
            budget.before_request()
            current = store.get_memory(state["name"], state["memory_id"])
            if current.scope != state["scope_a"]:
                raise ValueError("Memory scope mismatch; deletion refused.")
            budget.before_request()
            evidence.append("memory_deleted", store.delete_memory(state["name"], state["memory_id"]))
            state["deleted"] = True
            save_json(STATE, state)
        expected_present = not state.get("deleted", False)
        for attempt in range(6):
            results = {}
            for scope in ("scope_a", "scope_b"):
                budget.before_request()
                result = store.search_memories(
                    name=state["name"], scope=state[scope],
                    items=[{"role": "user", "type": "message", "content": (
                        "What answer format does this workshop user prefer?"
                        if LANGUAGE == "en" else "이 실습의 답변 형식 선호는?"
                    )}],
                    options=MemorySearchOptions(max_memories=5),
                )
                evidence.append("memory_search", {"scope_label": scope, "result": result})
                results[scope] = memory_ids(result)
            if results["scope_b"]:
                raise RuntimeError("Isolation failed: user B received a memory.")
            present = state["memory_id"] in results["scope_a"]
            if present == expected_present:
                evidence.append("verified", {
                    "stored_item_retrievable": expected_present,
                    "other_scope_empty": True, "deleted_item_absent": not expected_present,
                    "store_retained": True,
                })
                print("Memory item/search/isolation state verified; see actual item IDs in private evidence.")
                return
            if attempt < 5:
                time.sleep(3)
        raise RuntimeError("Memory read-after-write/delete did not converge within the bounded wait.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["create", "remember", "verify", "forget"])
    parser.add_argument("--confirm")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if not args.live:
        print(f"PLAN ONLY: Memory {args.command}. No memory, model, or Azure operations.")
        return
    evidence = Evidence("memory")
    try:
        run(args.command, args.confirm, evidence)
    except (ValueError, RuntimeError, OSError) as exc:
        evidence.failure(exc)
        raise
    finally:
        print(f"Evidence: {evidence.path}")


if __name__ == "__main__":
    run_cli(main)
