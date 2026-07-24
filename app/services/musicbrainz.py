"""Talk to MusicBrainz (User-Agent + ~1 req/sec). Optional enrichment only."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import Settings, get_settings


class MusicBrainzError(RuntimeError):
    """MusicBrainz call failed / weird response."""


@dataclass(frozen=True, slots=True)
class MusicBrainzRecording:
    """One search hit from MusicBrainz, cleaned up a bit."""

    mbid: str
    title: str
    artist: str
    tags: tuple[str, ...]


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
