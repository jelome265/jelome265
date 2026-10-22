#!/usr/bin/env python3
"""Fetch the public GitHub contribution calendar without a token or GraphQL."""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
USER = os.environ.get("GH_PROFILE_USER", "jelome265")
URL = f"https://github.com/users/{USER}/contributions"
OUTPUT = ROOT / "data" / "contributions.json"
HEADERS = {"User-Agent": "jelome265-profile-art/1.0"}


def parse_count(label: str, level: int, date: str) -> int:
    if re.search(r"no contributions", label, re.IGNORECASE):
        return 0

    match = re.search(r"(\d[\d,]*)\s+contributions?", label, re.IGNORECASE)
    if match:
        return int(match.group(1).replace(",", ""))

    # Empty calendar cells may omit their tooltip. A non-zero cell without a
    # count is treated as a markup change, not silently reported as zero.
    if level == 0:
        return 0
    raise ValueError(f"Could not parse contribution count for {date}: {label!r}")


def fetch_days() -> list[dict[str, int | str]]:
    response = requests.get(URL, headers=HEADERS, timeout=(5, 30))
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    cells = soup.select("td.ContributionCalendar-day[data-date]")
    if not cells:
        cells = soup.select("td[data-date]")
    if not cells:
        raise RuntimeError(
            "GitHub returned no contribution-calendar cells; the public HTML "
            "markup may have changed."
        )

    days: list[dict[str, int | str]] = []
    for cell in cells:
        date = cell.get("data-date")
        if not date:
            continue

        label = (cell.get("aria-label") or "").strip()
        cell_id = cell.get("id")
        if cell_id:
            tooltip = soup.find("tool-tip", attrs={"for": cell_id})
            if tooltip:
                label = tooltip.get_text(" ", strip=True)

        level = int(cell.get("data-level") or 0)
        days.append({"date": date, "count": parse_count(label, level, date), "level": level})

    days.sort(key=lambda item: str(item["date"]))
    unique_days = {str(item["date"]): item for item in days}
    days = list(unique_days.values())
    if not days:
        raise RuntimeError("The contribution calendar contained no dated cells.")
    return days


def streak(days: list[dict[str, int | str]], allow_today_incomplete: bool) -> dict[str, int | str | None]:
    index = len(days) - 1
    today = datetime.now(timezone.utc).date().isoformat()
    if (
        allow_today_incomplete
        and index >= 0
        and days[index]["date"] == today
        and int(days[index]["count"]) == 0
    ):
        index -= 1

    end_index = index
    length = 0
    while index >= 0 and int(days[index]["count"]) > 0:
        length += 1
        index -= 1
    start_index = index + 1
    if length == 0:
        return {"length": 0, "start": None, "end": None}
    return {
        "length": length,
        "start": str(days[start_index]["date"]),
        "end": str(days[end_index]["date"]),
    }


def longest_streak(days: list[dict[str, int | str]]) -> dict[str, int | str | None]:
    best_length = run_length = 0
    best_start: str | None = None
    best_end: str | None = None
    run_start: str | None = None

    for day in days:
        if int(day["count"]) > 0:
            if run_length == 0:
                run_start = str(day["date"])
            run_length += 1
            if run_length > best_length:
                best_length = run_length
                best_start = run_start
                best_end = str(day["date"])
        else:
            run_length = 0
            run_start = None

    return {"length": best_length, "start": best_start, "end": best_end}


def build_payload(days: list[dict[str, int | str]]) -> dict[str, object]:
    total = sum(int(day["count"]) for day in days)
    active_days = sum(int(day["count"]) > 0 for day in days)
    best = max(days, key=lambda day: int(day["count"]))
    monthly: dict[str, int] = {}
    for day in days:
        month = str(day["date"])[:7]
        monthly[month] = monthly.get(month, 0) + int(day["count"])

    return {
        "username": USER,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "range": {"start": days[0]["date"], "end": days[-1]["date"]},
        "total_contributions": total,
        "active_days": active_days,
        "avg_per_active_day": round(total / active_days, 1) if active_days else 0,
        "current_streak": streak(days, allow_today_incomplete=True),
        "longest_streak": longest_streak(days),
        "best_day": {"date": best["date"], "count": int(best["count"])},
        "monthly": [{"month": key, "total": value} for key, value in sorted(monthly.items())],
        "days": days,
    }


def main() -> None:
    days = fetch_days()
    payload = build_payload(days)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        f"Fetched {len(days)} days for @{USER}: "
        f"{payload['total_contributions']} contributions."
    )


if __name__ == "__main__":
    main()
