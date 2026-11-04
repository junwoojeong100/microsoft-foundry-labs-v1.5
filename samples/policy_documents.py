"""Read the public synthetic policy corpus without an Azure SDK dependency."""

import hashlib
from pathlib import Path
import re


def policy_chunks(data: Path, language: str) -> list[dict[str, str]]:
    chunks = []
    for path in sorted((data / "policies").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        label = "Document ID" if language == "en" else "문서 ID"
        document_id = re.search(rf"^{label}: (CONTOSO-[A-Z]+-\d{{4}}-\d{{2}})$", text, re.M)
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
