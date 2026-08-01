"""The knobs for scoring (genre/mood/activity etc). Change these to tune."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ScoringWeights:
    """Weight values the scorer adds up."""

    preferred_genre_match: float = 3.0
    mood_match: float = 2.5
    activity_match: float = 2.5
    shared_genre_with_recent: float = 1.5
    shared_artist_with_recent: float = 0.5
    continuity_last_genre: float = 1.0
    soft_artist_repeat_penalty: float = -2.0
    preference_conflict: float = -4.0
    # How fast older history fades (1.0 = no fade, 0.7 = each step back keeps 70%).
    recency_decay: float = 0.7


DEFAULT_WEIGHTS = ScoringWeights()
