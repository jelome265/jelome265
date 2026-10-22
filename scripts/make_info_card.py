#!/usr/bin/env python3
"""Render the static profile facts card with a one-shot terminal-style reveal."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "info-card.svg"

WIDTH = HEIGHT = 840
BACKGROUND = "#0b0d10"
FRAME = "#34312b"
MUTED = "#928b7d"
INK = "#d4c7ad"
ACCENT = "#b58b54"

ROWS = [
    ("IDENTITY", "Jelome Ngamuti"),
    ("STUDY", "Computer Science · Year 2"),
    ("FOCUS", "Rust · backend systems · architecture"),
    ("BUILDING", "Sitolo · Rustacean"),
    ("ENGINEERING", "Security · reliability · maintainability"),
    ("BASE", "Malawi"),
]


def main() -> None:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        "<style>@keyframes reveal{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}} .row{opacity:0;animation:reveal .45s ease-out both}@media(prefers-reduced-motion:reduce){.row{opacity:1;animation:none}}</style>",
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="12" fill="{BACKGROUND}"/>',
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="12" fill="none" stroke="{FRAME}"/>',
        f'<line x1="0" y1="34" x2="{WIDTH}" y2="34" stroke="{FRAME}"/>',
        f'<circle cx="20" cy="17" r="5" fill="#8b5149"/><circle cx="36" cy="17" r="5" fill="#9e814b"/><circle cx="52" cy="17" r="5" fill="#6e8764"/>',
        f'<text x="{WIDTH / 2}" y="22" fill="{MUTED}" font-size="12" text-anchor="middle">jelome@citadel:~$ ./about.sh</text>',
        f'<text x="32" y="91" fill="{ACCENT}" font-size="18">PROFILE / ENGINEERING RECORD</text>',
        f'<text x="32" y="125" fill="{INK}" font-size="28">Build systems worth trusting.</text>',
        f'<line x1="32" y1="151" x2="{WIDTH - 32}" y2="151" stroke="{FRAME}"/>',
    ]

    row_top = 176
    row_height = 91
    for index, (label, value) in enumerate(ROWS):
        y = row_top + index * row_height
        delay = index * 0.12
        parts.append(f'<g class="row" style="animation-delay:{delay:.2f}s">')
        parts.append(f'<text x="34" y="{y + 22}" fill="{ACCENT}" font-size="16">{label}</text>')
        parts.append(f'<text x="34" y="{y + 55}" fill="{INK}" font-size="23">{value}</text>')
        parts.append(f'<line x1="32" y1="{y + 72}" x2="{WIDTH - 32}" y2="{y + 72}" stroke="{FRAME}" stroke-opacity="0.7"/>')
        parts.append("</g>")

    parts.extend(
        [
            f'<text x="32" y="{HEIGHT - 40}" fill="{MUTED}" font-size="14">principle: correctness first; complexity only when earned</text>',
            "</svg>",
        ]
    )
    OUTPUT.write_text("".join(parts), encoding="utf-8")
    print(f"Rendered {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
