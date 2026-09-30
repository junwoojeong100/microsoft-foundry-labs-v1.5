"""Contoso Search and GA-minimal Foundry IQ. Every Azure operation requires --live."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from typing import Any
from uuid import uuid4

from cloud import Rest, azure_url, project_client
from evidence import Budget, Evidence
from workshop import DATA, RESULTS, config_values, save_json

SEARCH_API = "2024-07-01"
IQ_API = "2026-04-01"
STATE = RESULTS / "search.json"


def policy_chunks() -> list[dict[str, str]]:
    chunks = []
    for path in sorted((DATA / "policies").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        document_id = re.search(r"^문서 ID: (CONTOSO-[A-Z]+-\d{4}-\d{2})$", text, re.M)
        if document_id is None:
            raise ValueError(f"Missing canonical Contoso document ID: {path.name}")
        title = text.splitlines()[0].removeprefix("# ")
        for section, body in re.findall(r"^## (\d+)\. ([\s\S]*?)(?=^## |\Z)", text, re.M):
            content = title + "\n" + f"## {section}. " + body.strip()
            chunks.append({
                "id": document_id[1] + "-s" + section, "document_id": document_id[1],
                "title": title, "section": section, "filename": path.name, "content": content,
                "content_sha256": hashlib.sha256(content.encode()).hexdigest(),
            })
    if len(chunks) != 13 or len({item["id"] for item in chunks}) != len(chunks):
        raise ValueError("Expected 13 unique policy sections from the three Contoso source documents.")
    return chunks


def index_schema(name: str) -> dict[str, Any]:
    fields = [{"name": "id", "type": "Edm.String", "key": True, "filterable": True}]
    fields += [
        {"name": field, "type": "Edm.String", "searchable": field in {"title", "content"},
         **({"analyzer": "ko.microsoft"} if field in {"title", "content"} else {"filterable": True})}
        for field in ("document_id", "title", "section", "filename", "content", "content_sha256")
    ]
    fields.append({
        "name": "content_vector", "type": "Collection(Edm.Single)", "searchable": True,
        "dimensions": 1536, "vectorSearchProfile": "contoso-vector", "retrievable": False,
    })
    return {
        "name": name, "fields": fields,
        "vectorSearch": {
            "algorithms": [{"name": "contoso-hnsw", "kind": "hnsw"}],
            "profiles": [{"name": "contoso-vector", "algorithm": "contoso-hnsw"}],
        },
        "semantic": {"configurations": [{
            "name": "contoso-semantic", "prioritizedFields": {
                "titleField": {"fieldName": "title"}, "prioritizedContentFields": [{"fieldName": "content"}],
            },
        }]},
    }


def validate_hits(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    expected = {chunk["id"]: chunk for chunk in policy_chunks()}
    for hit in hits:
        canonical = expected.get(hit.get("id"))
        if canonical is None:
            raise ValueError("Retrieved an unknown document section; do not invent a citation.")
        for field in ("document_id", "title", "section", "filename", "content", "content_sha256"):
            if hit.get(field) != canonical[field]:
                raise ValueError(f"Retrieved source differs from the checked-in corpus: {hit['id']}/{field}")
    return hits


def configuration() -> dict[str, str]:
    values = config_values()
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    return {
        "endpoint": azure_url(values["FOUNDRY_SEARCH_ENDPOINT"] or state.get("endpoint", ""), ".search.windows.net"),
        "index": values["FOUNDRY_SEARCH_INDEX"] or state.get("index", ""),
        "knowledge_base": values["FOUNDRY_KNOWLEDGE_BASE"] or state.get("knowledge_base", ""),
        "embedding": values["FOUNDRY_EMBEDDING_DEPLOYMENT_NAME"] or state.get("embedding", ""),
        "embedding_endpoint": values["FOUNDRY_EMBEDDING_ENDPOINT"] or state.get("embedding_endpoint", ""),
    }


class Search:
    def __init__(self, cred: Any, client: Any, evidence: Evidence, budget: Budget, settings: dict[str, str] | None = None):
        self.settings = settings or configuration()
        self.rest = Rest(self.settings["endpoint"], cred, "https://search.azure.com/.default", evidence, budget)
        self.client, self.evidence, self.budget = client, evidence, budget
        self.cred = cred

    def embeddings(self, texts: list[str]) -> list[list[float]]:
        if not self.settings["embedding"]:
            raise ValueError("FOUNDRY_EMBEDDING_DEPLOYMENT_NAME is required for hybrid search.")
        endpoint = azure_url(self.settings["embedding_endpoint"], ".openai.azure.com")
        if sum(len(text) for text in texts) > 40_000:
            raise ValueError("Embedding batch exceeds the synthetic corpus size limit.")
        rest = Rest(endpoint, self.cred, "https://cognitiveservices.azure.com/.default", self.evidence, self.budget)
        result = rest.request("POST", "/openai/v1/embeddings", {
            "model": self.settings["embedding"], "input": texts, "dimensions": 1536, "encoding_format": "float",
        })
        self.budget.record_tokens(result["usage"]["total_tokens"])
        self.evidence.append("embeddings", {"model": result["model"], "count": len(result["data"]), "tokens": result["usage"]["total_tokens"]})
        if len(result["data"]) != len(texts) or any(len(item["embedding"]) != 1536 for item in result["data"]):
            raise RuntimeError("Embedding count/dimensions mismatch.")
        ordered = sorted(result["data"], key=lambda item: item["index"])
        if [item["index"] for item in ordered] != list(range(len(texts))):
            raise RuntimeError("Embedding response indices are incomplete or duplicated.")
        return [item["embedding"] for item in ordered]

    def retrieve(self, query: str, mode: str = "hybrid") -> list[dict[str, Any]]:
        if not query.strip() or len(query) > 4000 or mode not in {"keyword", "hybrid", "iq"}:
            raise ValueError("Use a nonempty query <=4000 characters and keyword, hybrid, or iq.")
        if mode == "iq":
            kb = self.settings["knowledge_base"]
            if not kb:
                raise ValueError("Initialize the knowledge base first.")
            payload = {
                "intents": [{"type": "semantic", "search": query}],
                "includeActivity": True,
                "knowledgeSourceParams": [{
                    "kind": "searchIndex", "knowledgeSourceName": kb + "-source",
                    "includeReferences": True, "includeReferenceSourceData": True,
                }],
            }
            raw = self.rest.request("POST", f"/knowledgebases/{kb}/retrieve?api-version={IQ_API}", payload)
            if any(item.get("error") for item in raw.get("activity", [])):
                raise RuntimeError("IQ returned a source error; partial retrieval is not a pass.")
            hits = [item["sourceData"] for item in raw.get("references", []) if isinstance(item.get("sourceData"), dict)]
            if len(hits) != len(raw.get("references", [])):
                raise RuntimeError("IQ omitted reference source data; do not fill it from the answer key.")
        else:
            payload = {
                "search": query, "top": 5,
                "select": "id,document_id,title,section,filename,content,content_sha256",
            }
            if mode == "hybrid":
                payload.update({
                    "vectorQueries": [{"kind": "vector", "vector": self.embeddings([query])[0], "fields": "content_vector", "k": 20}],
                    "queryType": "semantic", "semanticConfiguration": "contoso-semantic",
                })
            raw = self.rest.request("POST", f"/indexes/{self.settings['index']}/docs/search?api-version={SEARCH_API}", payload)
            hits = raw["value"]
        if not hits:
            raise RuntimeError("No retrieval evidence returned; no grounded answer can be claimed.")
        return validate_hits(hits)

    def policy_scope(self) -> list[dict[str, Any]]:
        required = {item["id"] for item in policy_chunks()}
        result = self.rest.request("POST", f"/indexes/{self.settings['index']}/docs/search?api-version={SEARCH_API}", {
            "search": "*", "top": len(required),
            "filter": "search.in(id, '" + ",".join(sorted(required)) + "', ',')",
            "select": "id,document_id,title,section,filename,content,content_sha256",
        })
        hits = validate_hits(result["value"])
        if {item["id"] for item in hits} != required:
            raise RuntimeError("The small synthetic policy corpus is incomplete; compound policy answers cannot be grounded.")
        self.evidence.append("policy_scope_guard", hits)
        return hits

    def initialize(self, resume: bool = False) -> None:
        if STATE.exists() and not resume:
            raise ValueError("search.json already exists. Reuse its index; do not overwrite another run.")
        if resume:
            state = json.loads(STATE.read_text(encoding="utf-8"))
            if state["endpoint"] != self.settings["endpoint"] or not re.fullmatch(r"contoso-policy-[0-9a-f]{8}", state["index"]):
                raise ValueError("Cannot resume an index outside the recorded Contoso run.")
            name = state["index"]
            actual = self.rest.request("GET", f"/indexes/{name}?api-version={SEARCH_API}")
            if {f["name"] for f in actual["fields"]} != {f["name"] for f in index_schema(name)["fields"]}:
                raise ValueError("Existing index schema differs; resume refused.")
            self.settings.update(index=name, knowledge_base=state["knowledge_base"])
            state["embedding_endpoint"] = self.settings["embedding_endpoint"]
        else:
            name = "contoso-policy-" + uuid4().hex[:8]
            self.settings.update(index=name, knowledge_base=name + "-kb")
            state = {**self.settings, "run_id": self.evidence.run_id, "created": [], "api_versions": [SEARCH_API, IQ_API]}
            save_json(STATE, state)
            self.rest.request("PUT", f"/indexes/{name}?api-version={SEARCH_API}", index_schema(name), create_only=True)
            state["created"].append("index")
            save_json(STATE, state)
        chunks = policy_chunks()
        vectors = self.embeddings([item["content"] for item in chunks])
        upload = self.rest.request(
            "POST", f"/indexes/{name}/docs/index?api-version={SEARCH_API}",
            {"value": [{"@search.action": "upload", **chunk, "content_vector": vector} for chunk, vector in zip(chunks, vectors, strict=True)]},
        )
        if len(upload["value"]) != len(chunks) or not all(item["status"] for item in upload["value"]):
            raise RuntimeError("Partial indexing failure; inspect original indexing responses.")
        kb = self.settings["knowledge_base"]
        source_payload = {
            "name": kb + "-source", "kind": "searchIndex",
            "searchIndexParameters": {
                "searchIndexName": name, "semanticConfigurationName": "contoso-semantic",
                "sourceDataFields": [{"name": key} for key in chunks[0]],
                "searchFields": [{"name": "content"}, {"name": "title"}],
            },
        }
        if "knowledge_source" not in state["created"]:
            self.rest.request("PUT", f"/knowledgesources/{kb}-source?api-version={IQ_API}", source_payload, create_only=True)
            state["created"].append("knowledge_source")
            save_json(STATE, state)
        if "knowledge_base" not in state["created"]:
            self.rest.request("PUT", f"/knowledgebases/{kb}?api-version={IQ_API}", {
                "name": kb, "knowledgeSources": [{"name": kb + "-source"}],
            }, create_only=True)
            state["created"].append("knowledge_base")
        save_json(STATE, state)
        self.evidence.append("initialized", state)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["corpus", "initialize", "query"])
    parser.add_argument("--mode", choices=["keyword", "hybrid", "iq"], default="hybrid")
    parser.add_argument("--query", default="노트북 2대 총액 290만 원의 구매 승인과 비용 처리 규정")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--resume", action="store_true", help="Resume only the owned, schema-matching partial index.")
    args = parser.parse_args()
    if args.command == "corpus":
        print(json.dumps([{"id": c["id"], "file": c["filename"], "sha256": c["content_sha256"]} for c in policy_chunks()], ensure_ascii=False, indent=2))
        return
    if not args.live:
        print(f"PLAN ONLY: Search {args.command}/{args.mode}; no Azure requests.")
        return
    evidence, budget = Evidence("search"), Budget(max_requests=15, max_seconds=300)
    try:
        with project_client(evidence) as (project, cred, _, _), project.get_openai_client(max_retries=0, timeout=60) as client:
            search = Search(cred, client, evidence, budget)
            if args.command == "initialize":
                search.initialize(args.resume)
            else:
                hits = search.retrieve(args.query, args.mode)
                evidence.append("verified_sources", hits)
                print(json.dumps(hits, ensure_ascii=False, indent=2))
    except (ValueError, RuntimeError, OSError) as exc:
        evidence.failure(exc)
        raise
    finally:
        print(f"Evidence: {evidence.path}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
