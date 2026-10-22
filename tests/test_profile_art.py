"""Focused regression tests for the profile README asset generators."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import fetch_contributions
from scripts import make_ascii_svg
from scripts import make_info_card
from scripts import render_heatmap_svg


class ContributionParsingTests(unittest.TestCase):
    def test_parses_plural_count(self) -> None:
        self.assertEqual(
            fetch_contributions.parse_count(
                "12 contributions on Thursday, October 22, 2026", 3, "2026-10-22"
            ),
            12,
        )

    def test_parses_singular_count(self) -> None:
        self.assertEqual(
            fetch_contributions.parse_count(
                "1 contribution on Thursday, October 22, 2026", 1, "2026-10-22"
            ),
            1,
        )

    def test_parses_no_contributions(self) -> None:
        self.assertEqual(
            fetch_contributions.parse_count(
                "No contributions on Thursday, October 22, 2026", 0, "2026-10-22"
            ),
            0,
        )

    def test_empty_zero_level_cell_is_zero(self) -> None:
        self.assertEqual(fetch_contributions.parse_count("", 0, "2026-10-22"), 0)

    def test_nonempty_cell_with_unrecognized_tooltip_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            fetch_contributions.parse_count("Activity recorded", 2, "2026-10-22")

    def test_current_streak_does_not_break_on_incomplete_today(self) -> None:
        today = datetime.now(timezone.utc).date()
        days = [
            {"date": (today - timedelta(days=2)).isoformat(), "count": 1, "level": 1},
            {"date": (today - timedelta(days=1)).isoformat(), "count": 3, "level": 2},
            {"date": today.isoformat(), "count": 0, "level": 0},
        ]
        result = fetch_contributions.streak(days, allow_today_incomplete=True)
        self.assertEqual(result["length"], 2)
        self.assertEqual(result["start"], (today - timedelta(days=2)).isoformat())
        self.assertEqual(result["end"], (today - timedelta(days=1)).isoformat())

    def test_longest_streak_finds_longest_consecutive_run(self) -> None:
        start = date(2026, 10, 1)
        counts = [0, 1, 2, 0, 4]
        days = [
            {
                "date": (start + timedelta(days=index)).isoformat(),
                "count": count,
                "level": 1 if count else 0,
            }
            for index, count in enumerate(counts)
        ]
        result = fetch_contributions.longest_streak(days)
        self.assertEqual(result["length"], 2)
        self.assertEqual(result["start"], "2026-10-02")
        self.assertEqual(result["end"], "2026-10-03")


class SvgGenerationTests(unittest.TestCase):
    def test_heatmap_is_valid_svg_and_maps_latest_dates(self) -> None:
        days = [
            {"date": "2026-10-22", "count": 2, "level": 1},
            {"date": "2026-10-23", "count": 0, "level": 0},
        ]
        payload = {
            "days": days,
            "total_contributions": 2,
            "active_days": 1,
            "current_streak": {"length": 0},
            "longest_streak": {"length": 1},
            "best_day": {"date": "2026-10-22", "count": 2},
            "range": {"start": "2026-10-22", "end": "2026-10-23"},
        }
        root = ET.fromstring(render_heatmap_svg.render(payload))
        self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
        titles = [node.text for node in root.iter("{http://www.w3.org/2000/svg}title")]
        self.assertTrue(any("2026-10-22: 2 contributions" in (title or "") for title in titles))

        grid = render_heatmap_svg.build_grid(days)
        last_date = date(2026, 10, 23)
        sunday = last_date - timedelta(days=(last_date.weekday() + 1) % 7)
        start_sunday = sunday - timedelta(weeks=52)
        week = (last_date - start_sunday).days // 7
        weekday = (last_date.weekday() + 1) % 7
        self.assertEqual(grid[week][weekday]["date"], "2026-10-23")

    def test_ascii_generator_produces_animated_well_formed_svg(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as tmp:
            temp_dir = Path(tmp)
            source = temp_dir / "avatar.png"
            output = temp_dir / "portrait.svg"
            gradient = Image.linear_gradient("L").resize((160, 160))
            gradient.convert("RGB").save(source)

            with patch.object(make_ascii_svg, "SOURCE", source), patch.object(
                make_ascii_svg, "OUTPUT", output
            ):
                make_ascii_svg.main()

            svg = output.read_text(encoding="utf-8")
            root = ET.fromstring(svg)
            self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
            self.assertIn("<animate", svg)
            self.assertIn("<clipPath", svg)
            self.assertIn("jelome265@github", svg)
            self.assertNotIn("citadel", svg.lower())

    def test_info_card_generator_produces_well_formed_svg(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as tmp:
            output = Path(tmp) / "info-card.svg"
            with patch.object(make_info_card, "OUTPUT", output):
                make_info_card.main()

            root = ET.parse(output).getroot()
            text_content = "".join(node.text or "" for node in root.iter("{http://www.w3.org/2000/svg}text"))
            self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
            self.assertIn("Jelome Ngamuti", text_content)
            self.assertIn("Rust", text_content)
            self.assertIn("neofetch", text_content)
            self.assertNotIn("citadel", text_content.lower())

    def test_readme_matches_the_guide_layout(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn('src="./contrib-heatmap.svg" width="860"', readme)
        self.assertIn('src="./portrait.svg" width="370"', readme)
        self.assertIn('src="./info-card.svg" width="490"', readme)
        self.assertNotIn("citadel", readme.lower())

    def test_heatmap_uses_the_guide_green_palette(self) -> None:
        self.assertIn("#0e4429", render_heatmap_svg.PALETTE)
        self.assertIn("#39d353", render_heatmap_svg.PALETTE)

    def test_committed_profile_svgs_are_well_formed_xml(self) -> None:
        for name in ("portrait.svg", "info-card.svg", "contrib-heatmap.svg"):
            with self.subTest(name=name):
                root = ET.parse(ROOT / name).getroot()
                self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")


if __name__ == "__main__":
    unittest.main()
