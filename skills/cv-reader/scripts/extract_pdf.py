# /// script
# requires-python = ">=3.12,<3.15"
# dependencies = ["pdfplumber", "pypdfium2"]
# ///
"""Collect local PDF evidence for cv-reader; semantic extraction is done by the agent."""

import argparse
import json
from pathlib import Path

import pdfplumber


def extract_pdf(source, render_dir=None):
    source = Path(source)
    result = {"filename": source.name, "page_count": None, "pages": []}
    if render_dir is not None:
        render_dir = Path(render_dir)
        render_dir.mkdir(parents=True, exist_ok=True)
    with pdfplumber.open(source) as document:
        result["page_count"] = len(document.pages)
        for number, page in enumerate(document.pages, start=1):
            record = {
                "page": number,
                "width": page.width,
                "height": page.height,
                "text": "",
                "layout_text": "",
                "words": [],
                "links": [],
                "image_count": len(page.images),
                "review_reasons": [],
            }
            try:
                record["text"] = page.extract_text() or ""
                record["layout_text"] = page.extract_text(layout=True) or ""
                record["words"] = [
                    {key: word[key] for key in ("text", "x0", "top", "x1", "bottom")}
                    for word in page.extract_words()
                ]
            except Exception as error:
                record["review_reasons"].append(f"Text extraction failed: {error}")
            try:
                for link in page.hyperlinks:
                    record["links"].append({
                        "uri": link.get("uri"),
                        "bbox": [link.get(key) for key in ("x0", "top", "x1", "bottom")],
                    })
            except Exception as error:
                record["review_reasons"].append(f"Link extraction failed: {error}")
            if not record["text"].strip():
                record["review_reasons"].append("No text layer extracted; inspect page image or use OCR.")
            if record["image_count"]:
                record["review_reasons"].append("Contains images; check for text missing from the text layer.")
            if render_dir is not None:
                image_path = render_dir / f"page-{number:03d}.png"
                if image_path.exists():
                    raise FileExistsError(f"Refusing to overwrite page image: {image_path}")
                try:
                    page.to_image(resolution=150).save(image_path)
                    record["rendered_image"] = str(image_path.resolve())
                except Exception as error:
                    record["review_reasons"].append(f"Page rendering failed: {error}")
            result["pages"].append(record)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--render-dir", type=Path)
    args = parser.parse_args()
    if args.output.exists() or args.output.resolve() == args.pdf.resolve():
        parser.error("Choose a new output path; existing files are not overwritten.")
    try:
        result = extract_pdf(args.pdf, args.render_dir)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as output:
            json.dump(result, output, ensure_ascii=False, indent=2)
            output.write("\n")
    except Exception as error:
        parser.exit(1, f"PDF extraction failed: {error}\n")
    print(f"Saved evidence for {result['page_count']} page(s) to {args.output}")


if __name__ == "__main__":
    main()
