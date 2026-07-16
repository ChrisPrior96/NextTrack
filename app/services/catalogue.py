"""Read tracks out of SQLite. Listening history does not go in here."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Track
from app.db.session import SessionLocal, init_db

SEED_PATH = Path(__file__).resolve().parent.parent / "data" / "tracks.json"


@dataclass(frozen=True, slots=True)
class TrackRecord:
    id: str
    title: str
    artist: str
    genre: str
    moods: tuple[str, ...]
    activities: tuple[str, ...]


class TrackNotFoundError(KeyError):
    """Track id not in the catalogue."""

    def __init__(self, track_id: str) -> None:
        self.track_id = track_id
        super().__init__(track_id)


def _parse_track(raw: dict) -> TrackRecord:
    return TrackRecord(
        id=str(raw["id"]),
        title=str(raw["title"]),
        artist=str(raw["artist"]),
        genre=str(raw["genre"]),
        moods=tuple(str(item) for item in raw["moods"]),
        activities=tuple(str(item) for item in raw["activities"]),
    )


def load_tracks_from_json(path: Path | None = None) -> list[TrackRecord]:
    """Read tracks.json into TrackRecord objects."""
    seed_path = path or SEED_PATH
    with seed_path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        raise ValueError("Catalogue seed must be a JSON array of tracks")
    return [_parse_track(item) for item in payload]


def _to_record(track: Track) -> TrackRecord:
    return TrackRecord(
        id=track.id,
        title=track.title,
        artist=track.artist,
        genre=track.genre,
        moods=tuple(track.moods or ()),
        activities=tuple(track.activities or ()),
    )


class CatalogueRepository:
    """SQLite reads for tracks. Do not put listening history in here."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_all(self) -> list[TrackRecord]:
        rows = self._session.scalars(select(Track).order_by(Track.id)).all()
        return [_to_record(row) for row in rows]

    def get_by_id(self, track_id: str) -> TrackRecord:
        row = self._session.get(Track, track_id)
        if row is None:
            raise TrackNotFoundError(track_id)
        return _to_record(row)


def get_catalogue(session: Session) -> CatalogueRepository:
    """Wrap a session in CatalogueRepository."""
    return CatalogueRepository(session)


def get_all() -> list[TrackRecord]:
    """All tracks in the DB."""
    init_db()
    with SessionLocal() as session:
        return CatalogueRepository(session).get_all()


def get_by_id(track_id: str) -> TrackRecord:
    """One track by id, or TrackNotFoundError."""
    init_db()
    with SessionLocal() as session:
        return CatalogueRepository(session).get_by_id(track_id)
