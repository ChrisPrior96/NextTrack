"""Candidate generation / fallback tests."""

from __future__ import annotations

import pytest

from app.services.candidates import NoCandidatesError, generate_candidates
from app.services.catalogue import TrackRecord


def _track(
    track_id: str,
    *,
    artist: str,
    genre: str,
    moods: tuple[str, ...],
    activities: tuple[str, ...],
) -> TrackRecord:
    return TrackRecord(
        id=track_id,
        title=track_id,
        artist=artist,
        genre=genre,
        moods=moods,
        activities=activities,
    )


@pytest.fixture
def catalogue() -> list[TrackRecord]:
    return [
        _track(
            "t1",
            artist="Alpha",
            genre="lo-fi",
            moods=("focused", "calm"),
            activities=("study", "work"),
        ),
        _track(
            "t2",
            artist="Alpha",
            genre="lo-fi",
            moods=("calm",),
            activities=("relax",),
        ),
        _track(
            "t3",
            artist="Beta",
            genre="rock",
            moods=("energetic", "excited"),
            activities=("workout", "party"),
        ),
        _track(
            "t4",
            artist="Gamma",
            genre="jazz",
            moods=("focused",),
            activities=("work",),
        ),
        _track(
            "t5",
            artist="Gamma",
            genre="indie",
            moods=("happy", "focused"),
            activities=("study", "commute"),
        ),
    ]


def _ids(tracks: list[TrackRecord]) -> set[str]:
    return {track.id for track in tracks}


def test_excludes_recently_played_tracks(catalogue: list[TrackRecord]) -> None:
    result = generate_candidates(catalogue, recent_tracks=["t1", "t3"])
    assert _ids(result) == {"t2", "t4", "t5"}


def test_does_not_exclude_artists_by_default(catalogue: list[TrackRecord]) -> None:
    result = generate_candidates(catalogue, recent_tracks=["t1"])
    assert "t2" in _ids(result)


def test_optionally_excludes_artists_from_history(catalogue: list[TrackRecord]) -> None:
    result = generate_candidates(
        catalogue,
        recent_tracks=["t1"],
        avoid_repeated_artists=True,
    )
    assert _ids(result) == {"t3", "t4", "t5"}


def test_unknown_recent_ids_are_ignored_for_artist_exclusion(
    catalogue: list[TrackRecord],
) -> None:
    result = generate_candidates(
        catalogue,
        recent_tracks=["missing"],
        avoid_repeated_artists=True,
    )
    assert _ids(result) == {"t1", "t2", "t3", "t4", "t5"}


def test_exact_match_requires_all_provided_preferences(
    catalogue: list[TrackRecord],
) -> None:
    result = generate_candidates(
        catalogue,
        recent_tracks=[],
        mood="focused",
        activity="study",
        genre="lo-fi",
    )
    assert _ids(result) == {"t1"}


def test_exact_match_with_single_preference(catalogue: list[TrackRecord]) -> None:
    result = generate_candidates(catalogue, genre="rock")
    assert _ids(result) == {"t3"}


def test_partial_match_fallback_when_exact_empty(catalogue: list[TrackRecord]) -> None:
    # No track is focused + party + lo-fi, but t1/t5 share focused; t1 also lo-fi.
    result = generate_candidates(
        catalogue,
        mood="focused",
        activity="party",
        genre="lo-fi",
    )
    assert _ids(result) == {"t1"}


def test_partial_match_keeps_best_overlap_group(catalogue: list[TrackRecord]) -> None:
    # focused+study matches t1 (mood+activity) and t5 (mood+activity); both score 2.
    result = generate_candidates(
        catalogue,
        mood="focused",
        activity="study",
        genre="dance",
    )
    assert _ids(result) == {"t1", "t5"}


def test_general_catalogue_fallback_when_no_preference_overlap(
    catalogue: list[TrackRecord],
) -> None:
    result = generate_candidates(
        catalogue,
        recent_tracks=["t1"],
        mood="bored",
        genre="classical",
    )
    assert _ids(result) == {"t2", "t3", "t4", "t5"}


def test_no_preferences_returns_eligible_after_exclusions(
    catalogue: list[TrackRecord],
) -> None:
    result = generate_candidates(
        catalogue,
        recent_tracks=["t3"],
        avoid_repeated_artists=True,
    )
    assert _ids(result) == {"t1", "t2", "t4", "t5"}


def test_empty_eligible_set_raises_domain_error(catalogue: list[TrackRecord]) -> None:
    with pytest.raises(NoCandidatesError):
        generate_candidates(
            catalogue,
            recent_tracks=["t1", "t2", "t3", "t4", "t5"],
        )


def test_artist_exclusion_can_empty_set_and_raise(
    catalogue: list[TrackRecord],
) -> None:
    tiny = [
        _track(
            "a1",
            artist="Solo",
            genre="folk",
            moods=("calm",),
            activities=("relax",),
        ),
        _track(
            "a2",
            artist="Solo",
            genre="folk",
            moods=("happy",),
            activities=("commute",),
        ),
    ]
    with pytest.raises(NoCandidatesError):
        generate_candidates(
            tiny,
            recent_tracks=["a1"],
            avoid_repeated_artists=True,
            mood="calm",
        )


def test_does_not_select_a_single_best_track(catalogue: list[TrackRecord]) -> None:
    result = generate_candidates(catalogue, mood="focused")
    assert len(result) > 1
    assert _ids(result) == {"t1", "t4", "t5"}
