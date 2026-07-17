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


def _preference_values(
    mood: str | None,
    activity: str | None,
    genre: str | None,
) -> dict[str, str]:
    values: dict[str, str] = {}
    if mood is not None:
        values["mood"] = mood
    if activity is not None:
        values["activity"] = activity
    if genre is not None:
        values["genre"] = genre
    return values


def _matches_all_preferences(track: TrackRecord, preferences: dict[str, str]) -> bool:
    if "mood" in preferences and preferences["mood"] not in track.moods:
        return False
    if "activity" in preferences and preferences["activity"] not in track.activities:
        return False
    if "genre" in preferences and track.genre != preferences["genre"]:
        return False
    return True


def _filter_exact(
    candidates: Sequence[TrackRecord],
    preferences: dict[str, str],
) -> list[TrackRecord]:
    if not preferences:
        return list(candidates)
    return [track for track in candidates if _matches_all_preferences(track, preferences)]


def generate_candidates(
    catalogue: Sequence[TrackRecord],
    *,
    recent_tracks: Sequence[str] = (),
    avoid_repeated_artists: bool = False,
    mood: str | None = None,
    activity: str | None = None,
    genre: str | None = None,
) -> list[TrackRecord]:
    """
    Return eligible tracks after history exclusions and exact preference matching.

    Partial and general catalogue fallbacks are added next.
    """
    eligible = _exclude_recent(catalogue, recent_tracks)
    if avoid_repeated_artists:
        blocked = _artists_in_history(catalogue, recent_tracks)
        eligible = _exclude_repeated_artists(eligible, blocked)

    preferences = _preference_values(mood, activity, genre)
    return _filter_exact(eligible, preferences)
