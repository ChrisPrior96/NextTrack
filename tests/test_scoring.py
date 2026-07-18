"""Scoring unit tests."""

from __future__ import annotations

from app.services.catalogue import TrackRecord
from app.services.scoring import (
    ScoringContext,
    build_scoring_context,
    score_track,
)


def _track(
    track_id: str,
    *,
    artist: str,
    genre: str,
    moods: tuple[str, ...] = (),
    activities: tuple[str, ...] = (),
) -> TrackRecord:
    return TrackRecord(
        id=track_id,
        title=track_id,
        artist=artist,
        genre=genre,
        moods=moods,
        activities=activities,
    )


def test_score_applies_preference_and_history_signals() -> None:
    catalogue = [
        _track("t1", artist="Alpha", genre="lo-fi", moods=("focused",), activities=("study",)),
        _track("t2", artist="Beta", genre="lo-fi", moods=("focused",), activities=("study",)),
    ]
    context = build_scoring_context(
        catalogue,
        recent_tracks=["t1"],
        mood="focused",
        activity="study",
        genre="lo-fi",
        avoid_repeated_artists=False,
    )
    breakdown = score_track(catalogue[1], context)

    assert breakdown.components["preferred_genre_match"] == 3.0
    assert breakdown.components["mood_match"] == 2.5
    assert breakdown.components["activity_match"] == 2.5
    assert breakdown.components["shared_genre_with_recent"] == 1.5
    assert breakdown.components["continuity_last_genre"] == 1.0
    assert breakdown.components["shared_artist_with_recent"] == 0.0
    assert breakdown.components["soft_artist_repeat_penalty"] == 0.0
    assert breakdown.components["preference_conflict"] == 0.0
    assert breakdown.total == 10.5


def test_soft_artist_repeat_bonus_and_penalty() -> None:
    catalogue = [
        _track("t1", artist="Alpha", genre="lo-fi"),
        _track("t2", artist="Alpha", genre="indie", moods=("happy",)),
    ]
    context = build_scoring_context(
        catalogue,
        recent_tracks=["t1"],
        avoid_repeated_artists=False,
    )
    breakdown = score_track(catalogue[1], context)

    assert breakdown.components["shared_artist_with_recent"] == 0.5
    assert breakdown.components["soft_artist_repeat_penalty"] == -2.0
    assert breakdown.total == -1.5


def test_preference_conflict_penalty_when_partial_fit() -> None:
    track = _track(
        "t9",
        artist="Gamma",
        genre="jazz",
        moods=("focused",),
        activities=("work",),
    )
    context = ScoringContext(
        mood="focused",
        activity="study",
        genre="lo-fi",
    )
    breakdown = score_track(track, context)

    assert breakdown.components["mood_match"] == 2.5
    assert breakdown.components["activity_match"] == 0.0
    assert breakdown.components["preferred_genre_match"] == 0.0
    assert breakdown.components["preference_conflict"] == -4.0
    assert breakdown.total == -1.5


def test_unknown_recent_ids_are_ignored_in_context() -> None:
    catalogue = [_track("t1", artist="Alpha", genre="rock")]
    context = build_scoring_context(catalogue, recent_tracks=["missing", "t1"])
    assert context.recent_genres == frozenset({"rock"})
    assert context.recent_artists == frozenset({"Alpha"})
    assert context.last_track_genre == "rock"
