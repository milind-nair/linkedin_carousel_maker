#!/usr/bin/env python3
"""CLI entry point — render a JSON carousel payload to PDF.

Usage:
    python render.py payload.json [output.pdf]
"""

import sys
from pathlib import Path
from carousel.pipeline import render_carousel

OUTPUTS_DIR = Path(__file__).resolve().parent / "outputs"


def main():
    if len(sys.argv) < 2:
        print("Usage: python render.py <payload.json> [output.pdf]")
        sys.exit(1)

    payload_path = sys.argv[1]
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    else:
        OUTPUTS_DIR.mkdir(exist_ok=True)
        output_path = str(OUTPUTS_DIR / (Path(payload_path).stem + ".pdf"))
    render_carousel(payload_path, output_path)


if __name__ == "__main__":
    main()
