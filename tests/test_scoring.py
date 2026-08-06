"""Scoring unit tests."""

from __future__ import annotations

from app.services.catalogue import TrackRecord
from app.services.explanation import build_reason
from app.services.recommendation import recommend_track
from app.services.scoring import (
    ScoringContext,
    build_scoring_context,
    rank_candidates,
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


def test_rank_candidates_uses_score_then_stable_id_tiebreak() -> None:
    catalogue = [
        _track("t2", artist="B", genre="lo-fi", moods=("focused",), activities=("study",)),
        _track("t1", artist="A", genre="lo-fi", moods=("focused",), activities=("study",)),
    ]
    context = build_scoring_context(
        catalogue,
        mood="focused",
        activity="study",
        genre="lo-fi",
    )
    ranked = rank_candidates(catalogue, context)
    assert [item.track.id for item in ranked] == ["t1", "t2"]
    assert ranked[0].breakdown.total == ranked[1].breakdown.total


def test_rank_candidates_prefers_higher_total_score() -> None:
    catalogue = [
        _track("t1", artist="A", genre="rock", moods=("happy",), activities=("party",)),
        _track("t2", artist="B", genre="lo-fi", moods=("focused",), activities=("study",)),
    ]
    context = build_scoring_context(
        catalogue,
        mood="focused",
        activity="study",
        genre="lo-fi",
    )
    ranked = rank_candidates(catalogue, context)
    assert ranked[0].track.id == "t2"
    assert ranked[0].breakdown.total > ranked[1].breakdown.total


def test_build_reason_mentions_positive_factors() -> None:
    track = _track(
        "t2",
        artist="Beta",
        genre="lo-fi",
        moods=("focused",),
        activities=("study",),
    )
    context = ScoringContext(mood="focused", activity="study", genre="lo-fi")
    breakdown = score_track(track, context)
    reason = build_reason(
        breakdown,
        track,
        mood="focused",
        activity="study",
        genre="lo-fi",
    )
    assert "Beta" in reason
    assert "preferred genre" in reason or "lo-fi" in reason
    assert "focused" in reason
    assert "study" in reason


def test_recommend_track_returns_stable_top_pick() -> None:
    catalogue = [
        _track("t1", artist="Alpha", genre="lo-fi", moods=("focused",), activities=("study",)),
        _track(
            "t2",
            artist="Beta",
            genre="lo-fi",
            moods=("focused",),
            activities=("study",),
        ),
        _track("t3", artist="Gamma", genre="rock", moods=("energetic",), activities=("workout",)),
    ]
    first = recommend_track(
        catalogue,
        recent_tracks=["t3"],
        mood="focused",
        activity="study",
        genre="lo-fi",
    )
    second = recommend_track(
        catalogue,
        recent_tracks=["t3"],
        mood="focused",
        activity="study",
        genre="lo-fi",
    )
    assert first.track.id == "t1"
    assert second.track.id == "t1"
    assert first.track.id != "t3"
    assert "focused" in first.reason or "study" in first.reason or "genre" in first.reason


def test_score_without_preferences_uses_history_signals_only() -> None:
    catalogue = [
        _track("t1", artist="Alpha", genre="lo-fi"),
        _track("t2", artist="Beta", genre="lo-fi"),
    ]
    context = build_scoring_context(catalogue, recent_tracks=["t1"])
    breakdown = score_track(catalogue[1], context)
    assert breakdown.components["shared_genre_with_recent"] == 1.5
    assert breakdown.components["continuity_last_genre"] == 1.0
    assert breakdown.components["preferred_genre_match"] == 0.0
    assert breakdown.total == 2.5


def test_avoid_repeated_artists_skips_soft_artist_signals() -> None:
    catalogue = [
        _track("t1", artist="Alpha", genre="lo-fi"),
        _track("t2", artist="Alpha", genre="indie"),
    ]
    context = build_scoring_context(
        catalogue,
        recent_tracks=["t1"],
        avoid_repeated_artists=True,
    )
    breakdown = score_track(catalogue[1], context)
    assert breakdown.components["shared_artist_with_recent"] == 0.0
    assert breakdown.components["soft_artist_repeat_penalty"] == 0.0


def test_build_reason_mentions_penalties() -> None:
    track = _track("t2", artist="Alpha", genre="indie")
    context = ScoringContext(
        recent_artists=frozenset({"Alpha"}),
        avoid_repeated_artists=False,
        mood="focused",
        genre="lo-fi",
    )
    breakdown = score_track(track, context)
    reason = build_reason(breakdown, track, mood="focused", genre="lo-fi")
    assert "penalty" in reason or "partially matches" in reason


def test_build_reason_when_no_contributing_components() -> None:
    track = _track("t9", artist="Zed", genre="folk")
    context = ScoringContext()
    breakdown = score_track(track, context)
    reason = build_reason(breakdown, track)
    assert "eligible catalogue match" in reason


def test_last_track_genre_uses_last_resolvable_id() -> None:
    catalogue = [
        _track("t1", artist="A", genre="jazz"),
        _track("t2", artist="B", genre="rock"),
    ]
    context = build_scoring_context(
        catalogue,
        recent_tracks=["t1", "missing", "t2"],
    )
    assert context.last_track_genre == "rock"


def test_recency_decay_prefers_newer_genre_match() -> None:
    catalogue = [
        _track("old", artist="A", genre="jazz"),
        _track("new", artist="B", genre="rock"),
        _track("cand_jazz", artist="C", genre="jazz"),
        _track("cand_rock", artist="D", genre="rock"),
    ]
    # History oldest → newest: jazz then rock. Rock match should keep full weight;
    # jazz match is one step older so it gets decayed.
    context = build_scoring_context(
        catalogue,
        recent_tracks=["old", "new"],
    )
    jazz_score = score_track(catalogue[2], context)
    rock_score = score_track(catalogue[3], context)

    assert jazz_score.components["shared_genre_with_recent"] == 1.5 * 0.7
    assert rock_score.components["shared_genre_with_recent"] == 1.5
    assert rock_score.components["continuity_last_genre"] == 1.0
    assert jazz_score.components["continuity_last_genre"] == 0.0
    assert rock_score.total > jazz_score.total


def test_recency_decay_scales_artist_repeat_signals() -> None:
    catalogue = [
        _track("old", artist="Alpha", genre="lo-fi"),
        _track("mid", artist="Beta", genre="indie"),
        _track("cand", artist="Alpha", genre="folk"),
    ]
    context = build_scoring_context(
        catalogue,
        recent_tracks=["old", "mid"],
        avoid_repeated_artists=False,
    )
    breakdown = score_track(catalogue[2], context)
    # Alpha appears one step back from newest → scale 0.7
    assert breakdown.components["shared_artist_with_recent"] == 0.5 * 0.7
    assert breakdown.components["soft_artist_repeat_penalty"] == -2.0 * 0.7


def test_external_tag_match_boosts_when_cache_overlaps_mood() -> None:
    track = _track("t1", artist="X", genre="electronic", moods=("calm",))
    context = ScoringContext(
        mood="calm",
        external_tags_by_id={"t1": ("chillout", "calm", "downtempo")},
    )
    breakdown = score_track(track, context)
    assert breakdown.components["mood_match"] == 2.5
    assert breakdown.components["external_tag_match"] == 1.0
    assert breakdown.total == 3.5


def test_external_tag_match_ignored_when_no_overlap() -> None:
    track = _track("t1", artist="X", genre="rock")
    context = ScoringContext(
        mood="focused",
        external_tags_by_id={"t1": ("punk", "live")},
    )
    breakdown = score_track(track, context)
    assert breakdown.components["external_tag_match"] == 0.0
