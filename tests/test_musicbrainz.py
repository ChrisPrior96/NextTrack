"""MusicBrainz tests (mocked — no live network)."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.db.models import MusicBrainzCache, Track
from app.db.session import Base
from app.services.catalogue import TrackRecord
from app.services.musicbrainz import (
    MusicBrainzClient,
    MusicBrainzError,
    enrich_track,
    fetch_and_cache_enrichment,
    get_cached_enrichment,
    normalise_text,
    upsert_enrichment_cache,
)


def _track() -> TrackRecord:
    return TrackRecord(
        id="track_001",
        title="Desk Lamp Glow",
        artist="Nova Circuit",
        genre="lo-fi",
        moods=("focused", "calm"),
        activities=("study", "work"),
    )


@pytest.fixture
def db_session(tmp_path: Path) -> Session:
    engine = create_engine(
        f"sqlite:///{tmp_path / 'mb-test.db'}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = factory()
    track = _track()
    session.add(
        Track(
            id=track.id,
            title=track.title,
            artist=track.artist,
            genre=track.genre,
            moods=list(track.moods),
            activities=list(track.activities),
        )
    )
    session.commit()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _mock_transport(payload: dict, status_code: int = 200) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        assert "User-Agent" in request.headers
        assert request.headers["User-Agent"]
        return httpx.Response(status_code, json=payload)

    return httpx.MockTransport(handler)


def test_normalise_text_collapses_whitespace() -> None:
    assert normalise_text("  Desk   Lamp Glow ") == "desk lamp glow"


def test_search_recording_parses_mocked_response() -> None:
    payload = {
        "recordings": [
            {
                "id": "mbid-123",
                "title": "Desk Lamp Glow",
                "artist-credit": [{"name": "Nova Circuit"}],
                "tags": [{"name": "lo-fi"}, {"name": "study"}],
            }
        ]
    }
    settings = Settings(
        musicbrainz_enabled=True,
        musicbrainz_min_interval_seconds=0.0,
        musicbrainz_user_agent="NextTrackTest/1.0 (test@example.com)",
    )
    with MusicBrainzClient(settings, transport=_mock_transport(payload)) as client:
        hits = client.search_recording(artist="Nova Circuit", title="Desk Lamp Glow")

    assert len(hits) == 1
    assert hits[0].mbid == "mbid-123"
    assert hits[0].artist == "Nova Circuit"
    assert hits[0].tags == ("lo-fi", "study")


def test_client_raises_on_http_error() -> None:
    settings = Settings(musicbrainz_min_interval_seconds=0.0)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="unavailable")

    with MusicBrainzClient(settings, transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(MusicBrainzError):
            client.lookup_best_recording(artist="A", title="B")


def test_upsert_and_get_cached_enrichment(db_session: Session) -> None:
    track = _track()
    from app.services.musicbrainz import MusicBrainzRecording

    recording = MusicBrainzRecording(
        mbid="mbid-123",
        title="Desk Lamp Glow",
        artist="Nova Circuit",
        tags=("lo-fi", "chill"),
    )
    cached = upsert_enrichment_cache(
        db_session,
        track=track,
        recording=recording,
        source_status="ok",
    )
    again = get_cached_enrichment(db_session, track.id)

    assert cached.mbid == "mbid-123"
    assert again is not None
    assert again.tags == ("lo-fi", "chill")
    assert db_session.get(MusicBrainzCache, track.id) is not None


def test_fetch_and_cache_uses_mocked_client(db_session: Session) -> None:
    payload = {
        "recordings": [
            {
                "id": "mbid-999",
                "title": "Desk Lamp Glow",
                "artist-credit": [{"name": "Nova Circuit"}],
                "tags": [{"name": "ambient"}],
            }
        ]
    }
    settings = Settings(musicbrainz_min_interval_seconds=0.0)
    with MusicBrainzClient(settings, transport=_mock_transport(payload)) as client:
        cached = fetch_and_cache_enrichment(db_session, _track(), client=client)

    assert cached.mbid == "mbid-999"
    assert cached.tags == ("ambient",)
    assert cached.source_status == "ok"


def test_enrich_track_disabled_returns_local_only(db_session: Session) -> None:
    settings = Settings(musicbrainz_enabled=False)
    result = enrich_track(db_session, _track(), settings=settings)
    assert result.used_external is False
    assert result.enrichment is None
    assert result.track.id == "track_001"


def test_enrich_track_fails_open_on_network_error(db_session: Session) -> None:
    settings = Settings(
        musicbrainz_enabled=True,
        musicbrainz_min_interval_seconds=0.0,
    )

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("offline", request=request)

    with MusicBrainzClient(settings, transport=httpx.MockTransport(handler)) as client:
        result = enrich_track(
            db_session,
            _track(),
            settings=settings,
            client=client,
        )

    assert result.used_external is False
    assert result.enrichment is None
    assert result.track.title == "Desk Lamp Glow"


def test_enrich_track_reuses_cache_without_network(db_session: Session) -> None:
    settings = Settings(
        musicbrainz_enabled=True,
        musicbrainz_min_interval_seconds=0.0,
    )
    from app.services.musicbrainz import MusicBrainzRecording

    upsert_enrichment_cache(
        db_session,
        track=_track(),
        recording=MusicBrainzRecording(
            mbid="cached-mbid",
            title="Desk Lamp Glow",
            artist="Nova Circuit",
            tags=("cached",),
        ),
    )

    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("network should not be called when cache exists")

    with MusicBrainzClient(settings, transport=httpx.MockTransport(handler)) as client:
        result = enrich_track(
            db_session,
            _track(),
            settings=settings,
            client=client,
        )

    assert result.used_external is True
    assert result.enrichment is not None
    assert result.enrichment.mbid == "cached-mbid"


def test_recommend_still_works_offline_with_enrichment_disabled(
    client,
) -> None:
    response = client.post(
        "/recommend",
        json={"recent_tracks": ["track_001"], "mood": "focused", "genre": "lo-fi"},
    )
    assert response.status_code == 200
    assert response.json()["recommended_track"]["id"] != "track_001"
