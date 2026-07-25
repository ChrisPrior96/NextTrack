"""Talk to MusicBrainz (User-Agent + ~1 req/sec). Optional enrichment only."""

from __future__ import annotations

import json
import re
import threading
import time
from dataclasses import dataclass
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.models import MusicBrainzCache
from app.services.catalogue import TrackRecord


class MusicBrainzError(RuntimeError):
    """MusicBrainz call failed / weird response."""


_WHITESPACE_RE = re.compile(r"\s+")


def normalise_text(value: str) -> str:
    """Lowercase + squash spaces so matching is less fussy."""
    return _WHITESPACE_RE.sub(" ", value.strip()).lower()


@dataclass(frozen=True, slots=True)
class MusicBrainzRecording:
    """One search hit from MusicBrainz, cleaned up a bit."""

    mbid: str
    title: str
    artist: str
    tags: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CachedEnrichment:
    """What we stash in musicbrainz_cache for a local track."""

    local_track_id: str
    mbid: str | None
    normalised_title: str
    normalised_artist: str
    tags: tuple[str, ...]
    source_status: str


class MusicBrainzClient:
    """
    Small MusicBrainz client.

    They want a proper User-Agent and roughly one request a second.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        transport: httpx.BaseTransport | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._lock = threading.Lock()
        self._last_request_at = 0.0
        self._owns_client = client is None
        self._client = client or httpx.Client(
            base_url=self._settings.musicbrainz_base_url.rstrip("/"),
            headers={
                "User-Agent": self._settings.musicbrainz_user_agent,
                "Accept": "application/json",
            },
            timeout=self._settings.musicbrainz_timeout_seconds,
            transport=transport,
        )

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "MusicBrainzClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _throttle(self) -> None:
        """Sleep if we are calling MB too fast."""
        with self._lock:
            minimum = max(0.0, self._settings.musicbrainz_min_interval_seconds)
            now = time.monotonic()
            wait_for = minimum - (now - self._last_request_at)
            if wait_for > 0:
                time.sleep(wait_for)
            self._last_request_at = time.monotonic()

    def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        self._throttle()
        try:
            response = self._client.get(path, params=params)
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise MusicBrainzError(f"MusicBrainz request failed: {exc}") from exc
        if not isinstance(payload, dict):
            raise MusicBrainzError("MusicBrainz returned a non-object JSON payload")
        return payload

    def search_recording(self, *, artist: str, title: str, limit: int = 5) -> list[MusicBrainzRecording]:
        """Search MB by artist + title."""
        query = f'recording:"{title}" AND artist:"{artist}"'
        payload = self._get(
            "/recording",
            {
                "query": query,
                "fmt": "json",
                "limit": limit,
            },
        )
        recordings = payload.get("recordings") or []
        results: list[MusicBrainzRecording] = []
        for item in recordings:
            if not isinstance(item, dict):
                continue
            mbid = str(item.get("id") or "").strip()
            rec_title = str(item.get("title") or "").strip()
            if not mbid or not rec_title:
                continue
            credit = item.get("artist-credit") or []
            artist_name = ""
            if credit and isinstance(credit[0], dict):
                artist_name = str(
                    credit[0].get("name")
                    or (credit[0].get("artist") or {}).get("name")
                    or ""
                ).strip()
            tags = tuple(
                sorted(
                    {
                        str(tag.get("name")).strip().lower()
                        for tag in (item.get("tags") or [])
                        if isinstance(tag, dict) and tag.get("name")
                    }
                )
            )
            results.append(
                MusicBrainzRecording(
                    mbid=mbid,
                    title=rec_title,
                    artist=artist_name or artist,
                    tags=tags,
                )
            )
        return results

    def lookup_best_recording(self, *, artist: str, title: str) -> MusicBrainzRecording | None:
        """Best hit, or None if MB found nothing."""
        hits = self.search_recording(artist=artist, title=title, limit=1)
        return hits[0] if hits else None


def get_cached_enrichment(session: Session, local_track_id: str) -> CachedEnrichment | None:
    row = session.get(MusicBrainzCache, local_track_id)
    if row is None:
        return None
    return CachedEnrichment(
        local_track_id=row.local_track_id,
        mbid=row.mbid,
        normalised_title=row.normalised_title,
        normalised_artist=row.normalised_artist,
        tags=tuple(row.tags or ()),
        source_status=row.source_status,
    )


def upsert_enrichment_cache(
    session: Session,
    *,
    track: TrackRecord,
    recording: MusicBrainzRecording | None,
    source_status: str = "ok",
) -> CachedEnrichment:
    """Write / update the cache row for this track."""
    normalised_title = normalise_text(track.title)
    normalised_artist = normalise_text(track.artist)
    tags = list(recording.tags) if recording is not None else []
    mbid = recording.mbid if recording is not None else None
    raw_snippet = None
    if recording is not None:
        raw_snippet = json.dumps(
            {
                "mbid": recording.mbid,
                "title": recording.title,
                "artist": recording.artist,
                "tags": list(recording.tags),
            },
            ensure_ascii=True,
        )

    existing = session.get(MusicBrainzCache, track.id)
    if existing is None:
        existing = MusicBrainzCache(local_track_id=track.id)
        session.add(existing)

    existing.mbid = mbid
    existing.normalised_title = normalised_title
    existing.normalised_artist = normalised_artist
    existing.tags = tags
    existing.source_status = source_status
    existing.raw_snippet = raw_snippet
    session.commit()
    session.refresh(existing)

    return CachedEnrichment(
        local_track_id=existing.local_track_id,
        mbid=existing.mbid,
        normalised_title=existing.normalised_title,
        normalised_artist=existing.normalised_artist,
        tags=tuple(existing.tags or ()),
        source_status=existing.source_status,
    )


def fetch_and_cache_enrichment(
    session: Session,
    track: TrackRecord,
    client: MusicBrainzClient | None = None,
) -> CachedEnrichment:
    """
    Ask MB about this track and save the result.

    Raises MusicBrainzError on network/API fail — caller can ignore it.
    """
    owns_client = client is None
    mb_client = client or MusicBrainzClient()
    try:
        recording = mb_client.lookup_best_recording(artist=track.artist, title=track.title)
        status = "ok" if recording is not None else "not_found"
        return upsert_enrichment_cache(
            session,
            track=track,
            recording=recording,
            source_status=status,
        )
    finally:
        if owns_client:
            mb_client.close()
