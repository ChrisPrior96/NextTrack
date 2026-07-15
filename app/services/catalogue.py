"""Load and look up catalogue tracks from the local seed file."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

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


@lru_cache
def _track_index() -> dict[str, TrackRecord]:
    return {track.id: track for track in load_tracks_from_json()}


def get_all() -> list[TrackRecord]:
    """Return every track from the seed catalogue."""
    return list(_track_index().values())


def get_by_id(track_id: str) -> TrackRecord:
    """Return a single track or raise TrackNotFoundError."""
    try:
        return _track_index()[track_id]
    except KeyError as exc:
        raise TrackNotFoundError(track_id) from exc
