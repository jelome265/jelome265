#!/usr/bin/env python3
"""Render the profile's neofetch-style information card as an animated SVG."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "info-card.svg"

WIDTH = HEIGHT = 840
BACKGROUND = "#0d1117"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#e6edf3"
ACCENT = "#7ee787"

ROWS = [
    ("Name", "Jelome Ngamuti"),
    ("Now", "Computer Science student · Year 2"),
    ("Stack", "Rust · Node.js · JavaScript"),
    ("Building", "Sitolo · Rustacean"),
    ("Focus", "Backend engineering · system design"),
    ("Based in", "Malawi"),
]


def main() -> None:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        "<style>@keyframes reveal{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}} .row{opacity:0;animation:reveal .45s ease-out both}@media(prefers-reduced-motion:reduce){.row{opacity:1;animation:none}}</style>",
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="12" fill="{BACKGROUND}"/>',
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="12" fill="none" stroke="{FRAME}"/>',
        f'<line x1="0" y1="34" x2="{WIDTH}" y2="34" stroke="{FRAME}"/>',
        f'<circle cx="20" cy="17" r="5" fill="#ff5f56"/><circle cx="36" cy="17" r="5" fill="#ffbd2e"/><circle cx="52" cy="17" r="5" fill="#27c93f"/>',
        f'<text x="{WIDTH / 2}" y="22" fill="{MUTED}" font-size="12" text-anchor="middle">jelome265@github ~ $ neofetch</text>',
    ]
    row_top = 86
    row_height = 103
    for index, (label, value) in enumerate(ROWS):
        y = row_top + index * row_height
        delay = index * 0.12
        parts.append(f'<g class="row" style="animation-delay:{delay:.2f}s">')
        parts.append(f'<text x="34" y="{y + 22}" fill="{ACCENT}" font-size="18">{label}</text>')
        parts.append(f'<text x="34" y="{y + 58}" fill="{INK}" font-size="23">{value}</text>')
        parts.append(f'<line x1="32" y1="{y + 77}" x2="{WIDTH - 32}" y2="{y + 77}" stroke="{FRAME}" stroke-opacity="0.7"/>')
        parts.append("</g>")
    parts.append("</svg>")
    OUTPUT.write_text("".join(parts), encoding="utf-8")
    print(f"Rendered {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
