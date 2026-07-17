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


def generate_candidates(
    catalogue: Sequence[TrackRecord],
    *,
    recent_tracks: Sequence[str] = (),
) -> list[TrackRecord]:
    """
    Return catalogue tracks that are eligible after history exclusions.

    Preference filtering and fallbacks are added in later steps.
    """
    return _exclude_recent(catalogue, recent_tracks)
