#!/usr/bin/env python3
"""Download the profile owner's public GitHub avatar for ASCII conversion.

The raster image is generated locally/inside Actions and is intentionally not
committed. Only the derived SVG is published with the profile README.
"""
from __future__ import annotations

import os
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
USER = os.environ.get("GH_PROFILE_USER", "jelome265")
OUTPUT = ROOT / "data" / "profile-avatar.png"
HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "jelome265-profile-art",
}


def main() -> None:
    profile_response = requests.get(
        f"https://api.github.com/users/{USER}",
        headers=HEADERS,
        timeout=(5, 20),
    )
    profile_response.raise_for_status()
    profile = profile_response.json()
    avatar_url = profile.get("avatar_url")
    if not isinstance(avatar_url, str) or not avatar_url.startswith("https://"):
        raise RuntimeError(f"GitHub did not return a valid avatar URL for {USER!r}")

    avatar_response = requests.get(
        avatar_url,
        headers={"User-Agent": HEADERS["User-Agent"]},
        timeout=(5, 30),
    )
    avatar_response.raise_for_status()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(BytesIO(avatar_response.content)) as image:
        if image.width < 64 or image.height < 64:
            raise ValueError(f"Avatar resolution is unexpectedly small: {image.size}")
        image.convert("RGB").save(OUTPUT, format="PNG", optimize=True)

    print(f"Downloaded public avatar for @{USER} to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
