"""Pick which tracks are even allowed to be recommended (scoring happens later)."""

from __future__ import annotations

from collections.abc import Sequence

from app.services.catalogue import TrackRecord


def _exclude_recent(
    catalogue: Sequence[TrackRecord],
    recent_tracks: Sequence[str],
) -> list[TrackRecord]:
    recent_ids = set(recent_tracks)
    return [track for track in catalogue if track.id not in recent_ids]


def _artists_in_history(
    catalogue: Sequence[TrackRecord],
    recent_tracks: Sequence[str],
) -> set[str]:
    by_id = {track.id: track for track in catalogue}
    artists: set[str] = set()
    for track_id in recent_tracks:
        track = by_id.get(track_id)
        if track is not None:
            artists.add(track.artist)
    return artists


def _exclude_repeated_artists(
    candidates: Sequence[TrackRecord],
    blocked_artists: set[str],
) -> list[TrackRecord]:
    return [track for track in candidates if track.artist not in blocked_artists]


def generate_candidates(
    catalogue: Sequence[TrackRecord],
    *,
    recent_tracks: Sequence[str] = (),
    avoid_repeated_artists: bool = False,
) -> list[TrackRecord]:
    """
    Return catalogue tracks that are eligible after history exclusions.

    Preference filtering and fallbacks are added in later steps.
    """
    eligible = _exclude_recent(catalogue, recent_tracks)
    if avoid_repeated_artists:
        blocked = _artists_in_history(catalogue, recent_tracks)
        eligible = _exclude_repeated_artists(eligible, blocked)
    return eligible
