#!/usr/bin/env python3
"""Render a self-hosted, animated 53-week contribution calendar as SVG."""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "contributions.json"
OUTPUT = ROOT / "contrib-heatmap.svg"

WIDTH = 840
PAD = 22
TITLEBAR = 30
TOP_LABEL = 22
CELL = 10
GAP = 3
STEP = CELL + GAP
WEEKS = 53
GRID_HEIGHT = 7 * STEP - GAP
GRID_WIDTH = WEEKS * STEP - GAP
LABEL_WIDTH = 30
LABEL_GAP = 8
CONTENT_WIDTH = LABEL_WIDTH + LABEL_GAP + GRID_WIDTH
CONTENT_LEFT = (WIDTH - CONTENT_WIDTH) // 2
GRID_LEFT = CONTENT_LEFT + LABEL_WIDTH + LABEL_GAP
GRID_TOP = TITLEBAR + TOP_LABEL
HEIGHT = GRID_TOP + GRID_HEIGHT + 108

BACKGROUND = "#0b0d10"
FRAME = "#40382d"
MUTED = "#928b7d"
INK = "#d4c7ad"
ACCENT = "#b58b54"
PALETTE = ["#1a1b1d", "#3b3022", "#5f482d", "#80603b", "#a67b45", "#d0ac6b"]


def level_for(count: int) -> int:
    if count <= 0:
        return 0
    if count <= 3:
        return 1
    if count <= 9:
        return 2
    if count <= 19:
        return 3
    if count <= 39:
        return 4
    return 5


def build_grid(days: list[dict[str, Any]]) -> list[list[dict[str, Any] | None]]:
    grid: list[list[dict[str, Any] | None]] = [[None for _ in range(7)] for _ in range(WEEKS)]
    if not days:
        return grid

    last_date = date.fromisoformat(str(days[-1]["date"]))
    current_sunday = last_date - timedelta(days=(last_date.weekday() + 1) % 7)
    start_sunday = current_sunday - timedelta(weeks=WEEKS - 1)

    for item in days:
        current = date.fromisoformat(str(item["date"]))
        week = (current - start_sunday).days // 7
        weekday = (current.weekday() + 1) % 7
        if 0 <= week < WEEKS:
            grid[week][weekday] = item
    return grid


def svg_escape(value: object) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def render(payload: dict[str, Any]) -> str:
    days = payload.get("days") or []
    grid = build_grid(days)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        "<style>@keyframes reveal{0%{opacity:0;transform:translateY(-5px)}100%{opacity:1;transform:translateY(0)}} .cell{opacity:0;animation:reveal .28s ease-out both}@media(prefers-reduced-motion:reduce){.cell{opacity:1;animation:none}}</style>",
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="12" fill="{BACKGROUND}"/>',
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="12" fill="none" stroke="{FRAME}"/>',
        f'<line x1="0" y1="{TITLEBAR}" x2="{WIDTH}" y2="{TITLEBAR}" stroke="{FRAME}"/>',
        '<circle cx="20" cy="15" r="4.5" fill="#8b5149"/><circle cx="36" cy="15" r="4.5" fill="#9e814b"/><circle cx="52" cy="15" r="4.5" fill="#6e8764"/>',
        f'<text x="{WIDTH / 2}" y="19" fill="{MUTED}" font-size="12" text-anchor="middle">jelome@citadel: ~/contributions --graph</text>',
    ]

    month_labels: list[tuple[int, str]] = []
    seen_months: set[str] = set()
    for column_index, column in enumerate(grid):
        for item in column:
            if item is None:
                continue
            current = date.fromisoformat(str(item["date"]))
            month = current.strftime("%b")
            key = current.strftime("%Y-%m")
            if current.day <= 7 and key not in seen_months:
                month_labels.append((column_index, month))
                seen_months.add(key)

    for column_index, month in month_labels:
        x = GRID_LEFT + column_index * STEP
        parts.append(f'<text x="{x}" y="{TITLEBAR + 15}" fill="{MUTED}" font-size="10">{month}</text>')

    for row_index, weekday in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        y = GRID_TOP + row_index * STEP + CELL * 0.8
        parts.append(f'<text x="{CONTENT_LEFT + LABEL_WIDTH - 4}" y="{y}" fill="{MUTED}" font-size="9" text-anchor="end">{weekday}</text>')

    for column_index, column in enumerate(grid):
        x = GRID_LEFT + column_index * STEP
        for row_index, item in enumerate(column):
            y = GRID_TOP + row_index * STEP
            count = int(item["count"]) if item is not None else 0
            color = PALETTE[level_for(count)]
            title = "No recorded contributions" if item is None else (
                f'{item["date"]}: {count} contribution' + ("" if count == 1 else "s")
            )
            delay = column_index * 0.016 + row_index * 0.032
            parts.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}" '
                f'style="animation-delay:{delay:.3f}s"><title>{svg_escape(title)}</title></rect>'
            )

    legend_y = GRID_TOP + GRID_HEIGHT + 13
    legend_width = 6 * (CELL + 3)
    legend_x = WIDTH - PAD - legend_width - 57
    parts.append(f'<text x="{legend_x}" y="{legend_y + 9}" fill="{MUTED}" font-size="10" text-anchor="end">Less</text>')
    x = legend_x + 8
    for color in PALETTE:
        parts.append(f'<rect x="{x}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>')
        x += CELL + 3
    parts.append(f'<text x="{x + 2}" y="{legend_y + 9}" fill="{MUTED}" font-size="10">More</text>')

    separator_y = legend_y + 26
    parts.append(f'<line x1="0" y1="{separator_y}" x2="{WIDTH}" y2="{separator_y}" stroke="{FRAME}" stroke-opacity="0.7"/>')

    if not days:
        parts.append(f'<text x="{PAD}" y="{separator_y + 28}" fill="{ACCENT}" font-size="13">Contribution history populates on the first workflow run.</text>')
    else:
        total = int(payload.get("total_contributions", 0))
        active = int(payload.get("active_days", 0))
        current = int((payload.get("current_streak") or {}).get("length", 0))
        longest = int((payload.get("longest_streak") or {}).get("length", 0))
        best = payload.get("best_day") or {}
        range_info = payload.get("range") or {}
        parts.append(
            f'<text x="{PAD}" y="{separator_y + 25}" fill="{ACCENT}" font-size="14">'
            f'<tspan font-weight="700">{total:,}</tspan><tspan fill="{MUTED}"> contributions in the last year</tspan></text>'
        )
        parts.append(
            f'<text x="{WIDTH - PAD}" y="{separator_y + 25}" fill="{MUTED}" font-size="11" text-anchor="end">'
            f'{svg_escape(range_info.get("start", ""))} → {svg_escape(range_info.get("end", ""))}</text>'
        )
        parts.append(
            f'<text x="{PAD}" y="{separator_y + 47}" fill="{MUTED}" font-size="12">'
            f'Active days <tspan fill="{INK}">{active}</tspan> · Current streak <tspan fill="{ACCENT}">{current}d</tspan>'
            f' · Longest <tspan fill="{ACCENT}">{longest}d</tspan></text>'
        )
        parts.append(
            f'<text x="{WIDTH - PAD}" y="{separator_y + 47}" fill="{MUTED}" font-size="11" text-anchor="end">'
            f'Best day: {int(best.get("count", 0))} · {svg_escape(best.get("date", ""))}</text>'
        )

    parts.append("</svg>")
    return "".join(parts)


def main() -> None:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    OUTPUT.write_text(render(payload), encoding="utf-8")
    print(f"Rendered {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
