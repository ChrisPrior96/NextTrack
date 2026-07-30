"""Catalogue load / seed / lookup tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import Session, sessionmaker

from app.db.models import Track
from app.db.seed import seed_tracks
from app.db.session import Base
from app.services.catalogue import (
    CatalogueRepository,
    TrackNotFoundError,
    load_tracks_from_json,
)


SEED_PATH = Path(__file__).resolve().parents[1] / "app" / "data" / "tracks.json"
EXPECTED_TRACK_COUNT = 60


@pytest.fixture
def db_session(tmp_path: Path) -> Session:
    engine = create_engine(
        f"sqlite:///{tmp_path / 'catalogue-test.db'}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_load_tracks_from_json_returns_typed_records() -> None:
    tracks = load_tracks_from_json(SEED_PATH)
    assert len(tracks) == EXPECTED_TRACK_COUNT
    first = tracks[0]
    assert first.id == "track_001"
    assert first.title
    assert first.artist
    assert first.genre
    assert first.moods
    assert first.activities


def test_seed_inserts_all_tracks_once(db_session: Session) -> None:
    first = seed_tracks(db_session)
    second = seed_tracks(db_session)
    count = len(db_session.scalars(select(Track)).all())

    assert first == EXPECTED_TRACK_COUNT
    assert second == 0
    assert count == EXPECTED_TRACK_COUNT


def test_catalogue_get_by_id_returns_track(db_session: Session) -> None:
    seed_tracks(db_session)
    repo = CatalogueRepository(db_session)

    track = repo.get_by_id("track_014")

    assert track.id == "track_014"
    assert track.title == "Midnight Crowd"
    assert track.artist == "Club Aster"
    assert track.genre == "dance"
    assert "happy" in track.moods
    assert "party" in track.activities


def test_catalogue_get_by_id_missing_raises(db_session: Session) -> None:
    seed_tracks(db_session)
    repo = CatalogueRepository(db_session)

    with pytest.raises(TrackNotFoundError) as exc_info:
        repo.get_by_id("track_missing")

    assert exc_info.value.track_id == "track_missing"


def test_catalogue_get_all_returns_seeded_tracks(db_session: Session) -> None:
    seed_tracks(db_session)
    repo = CatalogueRepository(db_session)

    tracks = repo.get_all()

    assert len(tracks) == EXPECTED_TRACK_COUNT
    assert tracks[0].id == "track_001"


def test_sqlite_schema_only_has_track_metadata(db_session: Session) -> None:
    seed_tracks(db_session)
    table_names = set(inspect(db_session.get_bind()).get_table_names())
    columns = {column["name"] for column in inspect(db_session.get_bind()).get_columns("tracks")}

    assert "tracks" in table_names
    assert table_names.issubset({"tracks", "musicbrainz_cache"})
    assert columns == {"id", "title", "artist", "genre", "moods", "activities"}
    assert "recent_tracks" not in columns
    assert "request" not in table_names
