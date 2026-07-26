"""Check we never write listening context into the DB."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import inspect, select, text

from app.core.config import get_settings
from app.db.models import Track
from app.db.session import SessionLocal, engine


def _sqlite_path() -> Path:
    url = get_settings().database_url
    assert url.startswith("sqlite:///"), url
    return Path(url.removeprefix("sqlite:///"))


def _catalogue_snapshot() -> dict:
    """Snapshot DB tables/rows so we can compare before vs after."""
    with SessionLocal() as session:
        table_names = sorted(inspect(session.get_bind()).get_table_names())
        columns = {
            column["name"]
            for column in inspect(session.get_bind()).get_columns("tracks")
        }
        rows = [
            (
                track.id,
                track.title,
                track.artist,
                track.genre,
                tuple(track.moods or []),
                tuple(track.activities or []),
            )
            for track in session.scalars(select(Track).order_by(Track.id)).all()
        ]
    return {
        "tables": table_names,
        "columns": columns,
        "rows": rows,
    }


def test_recommend_does_not_change_persisted_catalogue(client: TestClient) -> None:
    before = _catalogue_snapshot()

    response = client.post(
        "/recommend",
        json={
            "recent_tracks": ["track_001", "track_008"],
            "mood": "focused",
            "activity": "study",
            "genre": "lo-fi",
            "avoid_repeated_artists": True,
        },
    )
    assert response.status_code == 200

    after = _catalogue_snapshot()
    assert after["rows"] == before["rows"]
    assert after["columns"] == before["columns"]
    assert set(after["tables"]).issubset({"tracks", "musicbrainz_cache"})
    assert "tracks" in after["tables"]
    assert after["columns"] == {
        "id",
        "title",
        "artist",
        "genre",
        "moods",
        "activities",
    }
    assert "recent_tracks" not in after["columns"]
    assert "mood" not in after["columns"]
    assert "preferences" not in after["tables"]
    assert "requests" not in after["tables"]
    assert "sessions" not in after["tables"]


def test_unknown_recent_track_is_not_written_to_database(client: TestClient) -> None:
    sentinel = "privacy_probe_track_do_not_store"
    before = _catalogue_snapshot()

    response = client.post(
        "/recommend",
        json={"recent_tracks": [sentinel], "mood": "focused"},
    )
    assert response.status_code == 400

    after = _catalogue_snapshot()
    assert after == before
    assert all(sentinel != row[0] for row in after["rows"])

    db_path = _sqlite_path()
    raw = db_path.read_bytes()
    assert sentinel.encode("utf-8") not in raw


def test_preference_only_request_leaves_database_unchanged(client: TestClient) -> None:
    before = _catalogue_snapshot()

    response = client.post(
        "/recommend",
        json={
            "mood": "excited",
            "activity": "party",
            "genre": "dance",
            "avoid_repeated_artists": False,
        },
    )
    assert response.status_code == 200

    after = _catalogue_snapshot()
    assert after["rows"] == before["rows"]

    # Still only catalogue tables (+ MB cache). No request/pref tables should appear.
    with engine.connect() as connection:
        names = {
            row[0]
            for row in connection.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
        }
    assert "tracks" in names
    assert names.issubset({"tracks", "musicbrainz_cache"})
    assert "requests" not in names
    assert "preferences" not in names


def test_sqlite_file_contains_only_metadata_tables(client: TestClient) -> None:
    client.post("/recommend", json={"mood": "calm", "activity": "relax"})

    db_path = _sqlite_path()
    assert db_path.exists()
    with sqlite3.connect(db_path) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(tracks)")
        }

    assert "tracks" in tables
    assert tables.issubset({"tracks", "musicbrainz_cache"})
    assert columns == {"id", "title", "artist", "genre", "moods", "activities"}
