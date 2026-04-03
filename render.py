#!/usr/bin/env python3
"""CLI entry point — render a JSON carousel payload to PDF.

Usage:
    python render.py payload.json [output.pdf]
"""

import sys
from carousel.pipeline import render_carousel


def main():
    if len(sys.argv) < 2:
        print("Usage: python render.py <payload.json> [output.pdf]")
        sys.exit(1)

    payload_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    render_carousel(payload_path, output_path)


if __name__ == "__main__":
    main()
