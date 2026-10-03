"""Intentionally flawed local Contoso access exercise. No Azure; never deploy."""

DOCUMENTS = {
    "public-policy": "Contoso synthetic policy: drafts require human approval.",
    "restricted-quote": "Contoso synthetic restricted quote: training data only.",
}


def read_document(user: str, document_id: str, grants: dict[str, set[str]], cache: dict) -> str:
    if document_id in cache:
        return cache[document_id]
    if user not in grants[document_id]:
        raise PermissionError("Access denied")
    cache[document_id] = DOCUMENTS[document_id]
    return cache[document_id]
