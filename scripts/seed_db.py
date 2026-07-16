"""CLI: seed the local DB from tracks.json."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.seed import seed_database


def main() -> None:
    inserted = seed_database()
    print(f"Seed complete. Inserted {inserted} track(s).")


if __name__ == "__main__":
    main()
