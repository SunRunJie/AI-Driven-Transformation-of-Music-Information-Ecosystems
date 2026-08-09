"""Download the documented third-party AOTY and RYM archives.

Run this script explicitly. It never substitutes generated data when a
download fails. Review each dataset's terms and license before redistribution.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import time
import urllib.request
import zipfile
from pathlib import Path

import sys

_SRC = str(Path(__file__).resolve().parent.parent)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from config import EXTERNAL_DIR, USER_AGENT


DATASETS = {
    "aoty_metacritic_30000": {
        "slug": "kauvinlucas/30000-albums-aggregated-review-ratings",
        "sha256": "b32bc999964deee9244c13bc1df55afa2277e7ccc32bda34b5bc913d07cd65eb",
    },
    "aoty_top5000": {
        "slug": "tabibyte/aoty-5000-highest-user-rated-albums",
        "sha256": "d14fd33233701fe48508096104c2d9bac7648523c5783ea5c77da8f514b274f1",
    },
    "rym_top5000": {
        "slug": "tobennao/rym-top-5000",
        "sha256": "e41350ef9202c5b09911404d5d14d78742ae80054a9784acaf87758e08aeaee1",
    },
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _download(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response:
        with destination.open("wb") as output:
            shutil.copyfileobj(response, output)


def download_all() -> None:
    EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)
    for name, spec in DATASETS.items():
        archive_path = EXTERNAL_DIR / f"{name}.zip"
        extract_dir = EXTERNAL_DIR / name
        download_url = f"https://www.kaggle.com/api/v1/datasets/download/{spec['slug']}"
        metadata_url = f"https://www.kaggle.com/api/v1/datasets/view/{spec['slug']}"

        if not archive_path.exists():
            print(f"[GET] {download_url}")
            _download(download_url, archive_path)
            time.sleep(2)

        actual_hash = _sha256(archive_path)
        if actual_hash != spec["sha256"]:
            raise ValueError(f"Checksum mismatch for {archive_path.name}: {actual_hash}")

        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive_path) as archive:
            archive.extractall(extract_dir)

        metadata_path = extract_dir / "kaggle_metadata.json"
        if not metadata_path.exists():
            request = urllib.request.Request(
                metadata_url, headers={"User-Agent": USER_AGENT}
            )
            with urllib.request.urlopen(request, timeout=120) as response:
                metadata = json.load(response)
            metadata_path.write_text(
                json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            time.sleep(2)
        print(f"[OK] {name}: {actual_hash}")


if __name__ == "__main__":
    download_all()
