"""Check PDF text, module coverage, page bounds and portable links."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import unicodedata

import pymupdf

from build_guide import load_content

ROOT = Path(__file__).resolve().parents[1]
RELEASE = json.loads((ROOT / "content/release.json").read_text(encoding="utf-8"))


def normalized(text):
    return re.sub(r"\s+", "", unicodedata.normalize("NFC", text))


def image_digest(pixmap):
    if pixmap.alpha:
        pixmap = pymupdf.Pixmap(pixmap, 0)
    if pixmap.colorspace is None:
        raise ValueError("Cannot verify a screenshot without a color space.")
    if pixmap.colorspace.n != 3:
        pixmap = pymupdf.Pixmap(pymupdf.csRGB, pixmap)
    return hashlib.sha256(pixmap.samples).hexdigest()


def check_pdf(language, report_dir):
    edition = RELEASE["languages"][language]
    pdf = ROOT / edition["pdf"]
    chapters, _, _ = load_content(language)
    captures = json.loads((ROOT / "content/portal-screenshots.json").read_text(encoding="utf-8"))["captures"]
    expected_images = {image_digest(pymupdf.Pixmap(ROOT / item["path"])): item["path"] for item in captures}
    with pymupdf.open(pdf) as document:
        texts = [page.get_text() for page in document]
        combined = normalized("\n".join(texts))
        if "Contoso" not in combined or "한빛" in combined or "Hanbit" in combined:
            raise ValueError("Current PDF must use the Contoso scenario, not historical branding.")
        missing = [chapter["title"] for chapter in chapters if normalized(chapter["title"]) not in combined]
        if missing:
            raise ValueError(f"PDF is missing module headings: {missing}")
        tracks = json.loads((ROOT / "content/reader-labels.json").read_text(encoding="utf-8"))[language]["tracks"]
        if len(texts) < 2 or normalized(f"L00 / {tracks['core']}") not in normalized(texts[1]):
            raise ValueError("The cover and table of contents must fit on one page; L00 must begin on page 2.")
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
        seen_images = set()
        checked_xrefs = set()
        for number, page in enumerate(document, 1):
            for image in page.get_images(full=True):
                if image[0] not in checked_xrefs:
                    seen_images.add(image_digest(pymupdf.Pixmap(document, image[0])))
                    checked_xrefs.add(image[0])
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
        missing_images = [path for fingerprint, path in expected_images.items() if fingerprint not in seen_images]
        if missing_images:
            raise ValueError(f"PDF is missing original portal screenshot pixels: {missing_images}")
        if internal_links < 30 or not {chapter["id"] + "-title" for chapter in chapters} <= destinations:
            raise ValueError("The PDF must preserve a usable internal table of contents.")
        phrase = "직접만들며이해하기" if language == "ko" else "learnbybuilding"
        if phrase not in combined.lower():
            raise ValueError(f"{language}: PDF text was not extracted correctly.")
        report = {
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "language": language, "pdf": edition["pdf"],
            "pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
            "status": "passed", "pages": len(document), "chapter_headings": len(chapters),
            "cover_pages": 1, "first_module_page": 2,
            "internal_links": internal_links, "bookmarks": len(document.get_toc()),
            "module_destinations": len({chapter["id"] + "-title" for chapter in chapters} & destinations),
            "out_of_bounds_text_blocks": 0, "nearly_blank_pages": [],
            "nonportable_local_links": 0, "localized_text_extractable": True,
            "portal_screenshots_with_matching_pixels": len(expected_images),
        }
        report_dir.mkdir(parents=True, exist_ok=True)
        document[0].get_pixmap(matrix=pymupdf.Matrix(1.3, 1.3)).save(report_dir / "pdf-cover.png")
        document[1].get_pixmap(matrix=pymupdf.Matrix(1.3, 1.3)).save(report_dir / "pdf-lab.png")
        target = report_dir / "pdf.json"
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-dir", type=Path, default=Path(RELEASE["documentation_validation"]))
    args = parser.parse_args()
    report_dir = (ROOT / args.report_dir).resolve()
    if not report_dir.is_relative_to(ROOT / "validation") or report_dir == ROOT / "validation":
        raise ValueError("Reports must be inside validation/.")
    report = {
        "scope": "Local bilingual PDF checks only; no Azure execution.",
        "languages": {
            language: check_pdf(language, report_dir if language == RELEASE["default_language"] else report_dir / language)
            for language in RELEASE["languages"]
        },
    }
    (report_dir / "pdf.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
