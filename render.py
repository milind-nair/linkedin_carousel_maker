#!/usr/bin/env python3
"""CLI entry point — render a JSON carousel payload to PDF.

Usage:
    python render.py payload.json [output.pdf]
    python render.py payload.json --instagram
"""

import argparse
from pathlib import Path
from carousel.pipeline import render_carousel

OUTPUTS_DIR = Path(__file__).resolve().parent / "outputs"


def main():
    parser = argparse.ArgumentParser(description="Render a JSON carousel to PDF or Instagram PNGs.")
    parser.add_argument("payload", help="Path to the JSON payload file")
    parser.add_argument("output", nargs="?", default=None, help="Output PDF path (default: outputs/<name>.pdf)")
    parser.add_argument("--instagram", action="store_true", help="Export as 1080x1350 PNGs for Instagram")
    args = parser.parse_args()

    stem = Path(args.payload).stem
    OUTPUTS_DIR.mkdir(exist_ok=True)

    if args.instagram:
        # Render scaled PDF, then split into PNGs
        pdf_path = str(OUTPUTS_DIR / (stem + "-instagram.pdf"))
        render_carousel(args.payload, pdf_path, instagram=True)
        _split_pdf_to_pngs(pdf_path, OUTPUTS_DIR / stem)
    else:
        output_path = args.output or str(OUTPUTS_DIR / (stem + ".pdf"))
        render_carousel(args.payload, output_path)


def _split_pdf_to_pngs(pdf_path: str, out_dir: Path):
    """Convert each PDF page to a PNG using PyMuPDF."""
    import fitz

    out_dir.mkdir(exist_ok=True)
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc, 1):
        pix = page.get_pixmap(dpi=216)
        png_path = out_dir / f"slide-{i:02d}.png"
        pix.save(str(png_path))
    doc.close()

    # Clean up the intermediate PDF
    Path(pdf_path).unlink()
    print(f"Instagram PNGs: {out_dir}/ ({i} slides)")


if __name__ == "__main__":
    main()
