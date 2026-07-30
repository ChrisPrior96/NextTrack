"""
Hit MusicBrainz for a few real tracks and dump the results to JSON.

I used this for the limitations write-up. Sleeps ~1s between calls.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import Settings
from app.db.session import SessionLocal, init_db
from app.services.catalogue import get_by_id
from app.services.musicbrainz import MusicBrainzClient, fetch_and_cache_enrichment

# Real tracks from the expanded catalogue (033+).
SAMPLE_IDS = [
    "track_033",  # Nujabes — Feather
    "track_039",  # Daft Punk — Digital Love
    "track_045",  # Arctic Monkeys — Do I Wanna Know?
    "track_051",  # Foo Fighters — Everlong
    "track_055",  # Miles Davis — So What
    "track_059",  # Massive Attack — Teardrop
]

REPORT_PATH = ROOT / "docs" / "enrichment_sample.json"


def main() -> None:
    init_db()
    settings = Settings(
        musicbrainz_enabled=True,
        musicbrainz_min_interval_seconds=1.1,
        musicbrainz_user_agent=(
            "NextTrack/1.0 (final-year-project; contact=local-demo@example.edu)"
        ),
    )
    rows: list[dict] = []

    with SessionLocal() as session, MusicBrainzClient(settings=settings) as client:
        for track_id in SAMPLE_IDS:
            track = get_by_id(track_id)
            try:
                cached = fetch_and_cache_enrichment(session, track, client=client)
                rows.append(
                    {
                        "local_track_id": track.id,
                        "title": track.title,
                        "artist": track.artist,
                        "genre": track.genre,
                        "source_status": cached.source_status,
                        "mbid": cached.mbid,
                        "normalised_title": cached.normalised_title,
                        "normalised_artist": cached.normalised_artist,
                        "tags": list(cached.tags),
                        "error": None,
                    }
                )
                print(
                    f"{track.id}: {cached.source_status}"
                    f" mbid={cached.mbid!r} tags={list(cached.tags)}"
                )
            except Exception as exc:  # noqa: BLE001 — report failures for the write-up
                rows.append(
                    {
                        "local_track_id": track.id,
                        "title": track.title,
                        "artist": track.artist,
                        "genre": track.genre,
                        "source_status": "error",
                        "mbid": None,
                        "normalised_title": None,
                        "normalised_artist": None,
                        "tags": [],
                        "error": str(exc),
                    }
                )
                print(f"{track.id}: error — {exc}")

    ok = sum(1 for row in rows if row["source_status"] == "ok")
    not_found = sum(1 for row in rows if row["source_status"] == "not_found")
    errors = sum(1 for row in rows if row["source_status"] == "error")
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sample_size": len(rows),
        "summary": {"ok": ok, "not_found": not_found, "error": errors},
        "tracks": rows,
        "notes": (
            "Hand-picked real catalogue tracks looked up against MusicBrainz WS/2. "
            "Results are cached in musicbrainz_cache and do not change recommend scoring."
        ),
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT_PATH} ({ok} ok / {not_found} not_found / {errors} error)")


if __name__ == "__main__":
    main()
