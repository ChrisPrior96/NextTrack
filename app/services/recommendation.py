"""Glue: load catalogue, get candidates, score them, return the top one."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from app.core.scoring_weights import DEFAULT_WEIGHTS, ScoringWeights
from app.services.candidates import NoCandidatesError, generate_candidates
from app.services.catalogue import TrackRecord
from app.services.explanation import build_reason
from app.services.scoring import (
    ScoreBreakdown,
    build_scoring_context,
    rank_candidates,
)


class UnknownTrackIdsError(ValueError):
    """Someone sent a track id we do not have."""

    def __init__(self, track_ids: Sequence[str]) -> None:
        self.track_ids = tuple(track_ids)
        ids = ", ".join(self.track_ids)
        super().__init__(f"Unknown track id(s): {ids}")


@dataclass(frozen=True, slots=True)
class RecommendationResult:
    track: TrackRecord
    score: float
    reason: str
    breakdown: ScoreBreakdown


def _validate_recent_track_ids(
    catalogue: Sequence[TrackRecord],
    recent_tracks: Sequence[str],
) -> None:
    known = {track.id for track in catalogue}
    missing = [track_id for track_id in recent_tracks if track_id not in known]
    if missing:
        raise UnknownTrackIdsError(missing)


def recommend_track(
    catalogue: Sequence[TrackRecord],
    *,
    recent_tracks: Sequence[str] = (),
    mood: str | None = None,
    activity: str | None = None,
    genre: str | None = None,
    avoid_repeated_artists: bool = False,
    weights: ScoringWeights = DEFAULT_WEIGHTS,
) -> RecommendationResult:
    """
    Select the top-scoring eligible track for the request context.

    Listening history and preferences stay request-scoped and are never persisted.
    """
    _validate_recent_track_ids(catalogue, recent_tracks)

    candidates = generate_candidates(
        catalogue,
        recent_tracks=recent_tracks,
        avoid_repeated_artists=avoid_repeated_artists,
        mood=mood,
        activity=activity,
        genre=genre,
    )
    if not candidates:
        raise NoCandidatesError()

    context = build_scoring_context(
        catalogue,
        recent_tracks=recent_tracks,
        mood=mood,
        activity=activity,
        genre=genre,
        avoid_repeated_artists=avoid_repeated_artists,
    )
    ranked = rank_candidates(candidates, context, weights)
    top = ranked[0]
    reason = build_reason(
        top.breakdown,
        top.track,
        mood=mood,
        activity=activity,
        genre=genre,
    )
    return RecommendationResult(
        track=top.track,
        score=top.breakdown.total,
        reason=reason,
        breakdown=top.breakdown,
    )


def recommend_from_catalogue(
    *,
    recent_tracks: Sequence[str] = (),
    mood: str | None = None,
    activity: str | None = None,
    genre: str | None = None,
    avoid_repeated_artists: bool = False,
    weights: ScoringWeights = DEFAULT_WEIGHTS,
) -> RecommendationResult:
    """Load catalogue from DB then recommend."""
    from app.db.seed import seed_database
    from app.services.catalogue import get_all

    seed_database()
    catalogue = get_all()
    if not catalogue:
        raise NoCandidatesError("Catalogue is empty")
    return recommend_track(
        catalogue,
        recent_tracks=recent_tracks,
        mood=mood,
        activity=activity,
        genre=genre,
        avoid_repeated_artists=avoid_repeated_artists,
        weights=weights,
    )
