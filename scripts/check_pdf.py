"""Check PDF text, module coverage, page bounds and portable links."""

import json
from pathlib import Path
import re
import unicodedata

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "Foundry-Hands-on-2026-09-29.pdf"


def normalized(text):
    return re.sub(r"\s+", "", unicodedata.normalize("NFC", text))


def main():
    chapters = json.loads((ROOT / "content/chapters.json").read_text(encoding="utf-8"))
    with pymupdf.open(PDF) as document:
        texts = [page.get_text() for page in document]
        combined = normalized("\n".join(texts))
        missing = [chapter["title"] for chapter in chapters if normalized(chapter["title"]) not in combined]
        if missing:
            raise ValueError(f"PDF is missing module headings: {missing}")
        tracks = {"core": "기본 코스", "advanced": "심화 코스", "reference": "참고 자료"}
        for chapter in chapters:
            label = chapter["number"] if chapter["track"] == "reference" else "L" + chapter["number"]
            marker = normalized(f"{label} / {tracks[chapter['track']]}")
            if marker not in combined:
                raise ValueError(f"PDF contains a TOC entry but no actual module body: {chapter['id']}")
        out_of_bounds = []
        local_links = []
        internal_links = 0
        destinations = set()
        sparse_pages = []
        for number, page in enumerate(document, 1):
            if len(normalized(texts[number - 1])) < 70:
                sparse_pages.append(number)
            for block in page.get_text("blocks"):
                x0, y0, x1, y1, text = block[:5]
                if text.strip() and (x0 < -1 or y0 < -1 or x1 > page.rect.width + 1 or y1 > page.rect.height + 1):
                    out_of_bounds.append({"page": number, "text": text[:70], "bounds": [x0, y0, x1, y1]})
            for link in page.get_links():
                if link["kind"] in {pymupdf.LINK_GOTO, pymupdf.LINK_NAMED} and 0 <= link.get("page", -1) < len(document):
                    internal_links += 1
                    if link.get("nameddest"):
                        destinations.add(link["nameddest"])
                uri = link.get("uri", "")
                if "127.0.0.1" in uri or uri.startswith("file:"):
                    local_links.append({"page": number, "uri": uri})
        if out_of_bounds or local_links or sparse_pages:
            raise ValueError(json.dumps({
                "out_of_bounds": out_of_bounds, "nonportable_links": local_links, "nearly_blank_pages": sparse_pages,
            }, ensure_ascii=False))
        if internal_links < 30 or not {chapter["id"] + "-title" for chapter in chapters} <= destinations:
            raise ValueError("The PDF must preserve a usable internal table of contents.")
        if "직접만들며이해하기" not in combined:
            raise ValueError("Korean text was not extracted correctly.")
        report = {
            "status": "passed", "pages": len(document), "chapter_headings": len(chapters),
            "internal_links": internal_links, "bookmarks": len(document.get_toc()),
            "module_destinations": len({chapter["id"] + "-title" for chapter in chapters} & destinations),
            "out_of_bounds_text_blocks": 0, "nearly_blank_pages": [],
            "nonportable_local_links": 0, "korean_text_extractable": "직접만들며이해하기" in combined,
        }
        document[0].get_pixmap(matrix=pymupdf.Matrix(1.3, 1.3)).save(ROOT / "validation/pdf-cover.png")
        document[1].get_pixmap(matrix=pymupdf.Matrix(1.3, 1.3)).save(ROOT / "validation/pdf-lab.png")
        target = ROOT / "validation/pdf.json"
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
