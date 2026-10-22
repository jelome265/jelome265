#!/usr/bin/env python3
"""Render the public GitHub avatar as a monochrome, self-typing ASCII SVG."""
from __future__ import annotations

import html
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "profile-avatar.png"
OUTPUT = ROOT / "avi-ascii.svg"

WIDTH = HEIGHT = 840
TITLEBAR = 34
PAD = 20
COLS = 100
ROWS = 50
ART_WIDTH = WIDTH - 2 * PAD
CELL_HEIGHT = 15.0
ART_TOP = 48.0
RAMP = " .`:-=+*#%@"
BACKGROUND = "#0b0d10"
PANEL = "#111317"
FRAME = "#34312b"
MUTED = "#928b7d"
INK = "#d4c7ad"
ACCENT = "#b58b54"
ROW_DURATION = 5.8 / ROWS


def main() -> None:
    if not SOURCE.is_file():
        raise SystemExit("Avatar image missing. Run: python scripts/fetch_avatar.py")

    with Image.open(SOURCE) as source:
        image = ImageOps.fit(
            source.convert("L"),
            (COLS, ROWS),
            method=Image.Resampling.LANCZOS,
        )
    image = ImageOps.autocontrast(image, cutoff=2)
    image = ImageEnhance.Contrast(image).enhance(1.12)
    pixels = image.load()

    lines: list[str] = []
    for y in range(ROWS):
        chars: list[str] = []
        for x in range(COLS):
            luminance = pixels[x, y] / 255.0
            luminance = luminance ** 1.08
            if luminance >= 0.86:
                chars.append(" ")
            else:
                index = round((1.0 - luminance) * (len(RAMP) - 1))
                chars.append(RAMP[max(0, min(len(RAMP) - 1, index))])
        lines.append("".join(chars))

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        "<defs><linearGradient id=\"panel\" x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\"><stop offset=\"0\" stop-color=\"#14161a\"/><stop offset=\"1\" stop-color=\"#090b0e\"/></linearGradient></defs>",
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="12" fill="url(#panel)"/>',
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="12" fill="none" stroke="{FRAME}"/>',
        f'<line x1="0" y1="{TITLEBAR}" x2="{WIDTH}" y2="{TITLEBAR}" stroke="{FRAME}"/>',
    ]
    for index, color in enumerate(("#8b5149", "#9e814b", "#6e8764")):
        parts.append(f'<circle cx="{PAD + index * 16}" cy="{TITLEBAR / 2}" r="5" fill="{color}"/>')
    parts.append(
        f'<text x="{WIDTH / 2}" y="22" fill="{MUTED}" font-size="12" text-anchor="middle">jelome@citadel:~$ ./portrait.sh</text>'
    )

    font_size = 13.4
    for row_index, line in enumerate(lines):
        y = ART_TOP + row_index * CELL_HEIGHT + CELL_HEIGHT * 0.78
        clip_y = ART_TOP + row_index * CELL_HEIGHT
        text = (
            f'<text xml:space="preserve" x="{PAD}" y="{y:.2f}" '
            f'font-size="{font_size}" fill="{INK}" textLength="{ART_WIDTH}" '
            f'lengthAdjust="spacing">{html.escape(line)}</text>'
        )
        delay = row_index * ROW_DURATION
        parts.append(
            f'<clipPath id="row-{row_index}"><rect x="{PAD}" y="{clip_y:.2f}" width="0" height="{CELL_HEIGHT}">'
            f'<animate attributeName="width" from="0" to="{ART_WIDTH}" begin="{delay:.3f}s" '
            f'dur="{ROW_DURATION:.3f}s" fill="freeze"/></rect></clipPath>'
        )
        parts.append(f'<g clip-path="url(#row-{row_index})">{text}</g>')
        parts.append(
            f'<rect x="{PAD}" y="{clip_y + 1:.2f}" width="7" height="{CELL_HEIGHT - 2:.2f}" fill="{ACCENT}" opacity="0">'
            f'<animate attributeName="x" from="{PAD}" to="{PAD + ART_WIDTH}" begin="{delay:.3f}s" '
            f'dur="{ROW_DURATION:.3f}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0.8" begin="{delay:.3f}s"/>'
            f'<set attributeName="opacity" to="0" begin="{delay + ROW_DURATION:.3f}s"/></rect>'
        )

    status_y = HEIGHT - 28
    parts.extend(
        [
            f'<line x1="0" y1="{HEIGHT - 42}" x2="{WIDTH}" y2="{HEIGHT - 42}" stroke="{FRAME}"/>',
            f'<text x="{PAD}" y="{status_y}" fill="{MUTED}" font-size="13">jelome@citadel:~$ whoami <tspan fill="{INK}">Jelome Ngamuti</tspan></text>',
            "</svg>",
        ]
    )
    OUTPUT.write_text("".join(parts), encoding="utf-8")
    print(f"Rendered {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
