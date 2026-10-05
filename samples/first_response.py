"""A single-request Responses API lesson. Plan-only unless --live is set."""

from __future__ import annotations

import argparse
import sys

from lab_profile import LANGUAGE
from workshop import ensure_response, read_config

DEFAULT_QUERIES = {
    "en": "How should you respond when no company policy has been provided?",
    "ko": "회사 내부 규정이 제공되지 않았을 때 어떻게 답해야 하나요?",
}
MAX_QUERY_CHARACTERS = 2_000
MAX_OUTPUT_TOKENS = 512


def call_model(query: str) -> tuple[str, str]:
    from azure.ai.projects import AIProjectClient
    from azure.core.exceptions import AzureError
    from azure.identity import AzureCliCredential
    from openai import OpenAIError

    endpoint, deployment = read_config()
    try:
        with (
            AzureCliCredential(process_timeout=30) as credential,
            AIProjectClient(endpoint=endpoint, credential=credential, retry_total=0) as project,
            project.get_openai_client(max_retries=0, timeout=60.0) as client,
        ):
            response = client.responses.create(
                model=deployment,
                input=query,
                max_output_tokens=MAX_OUTPUT_TOKENS,
                store=False,
            )
        return ensure_response(response), response.id
    except (AzureError, OpenAIError) as exc:
        status = getattr(exc, "status_code", None)
        raise RuntimeError(
            f"Model call failed ({type(exc).__name__}, status={status}). "
            "Check the configured project, deployment, sign-in, and quota before retrying."
        ) from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--query",
        default=DEFAULT_QUERIES[LANGUAGE],
        help=f"Question to send (maximum {MAX_QUERY_CHARACTERS} characters).",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Send one bounded request to the configured Foundry project; charges may apply.",
    )
    args = parser.parse_args(argv)
    if not args.query.strip():
        parser.error("--query must not be empty.")
    if len(args.query) > MAX_QUERY_CHARACTERS:
        parser.error(f"--query must be at most {MAX_QUERY_CHARACTERS} characters.")
    if not args.live:
        print("PLAN ONLY: no Azure request was made.")
        print(f"input={args.query}")
        return 0
    text, response_id = call_model(args.query)
    print(text)
    print(f"response_id={response_id}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError, OSError, ImportError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
