"""Score each candidate and sort them. Weights live in scoring_weights."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

from app.core.scoring_weights import DEFAULT_WEIGHTS, ScoringWeights
from app.services.catalogue import TrackRecord


@dataclass(frozen=True, slots=True)
class ScoringContext:
    """Bits of the request we need while scoring (history + prefs)."""

    recent_tracks: tuple[str, ...] = ()
    mood: str | None = None
    activity: str | None = None
    genre: str | None = None
    avoid_repeated_artists: bool = False
    recent_genres: frozenset[str] = field(default_factory=frozenset)
    recent_artists: frozenset[str] = field(default_factory=frozenset)
    last_track_genre: str | None = None


@dataclass(frozen=True, slots=True)
class ScoreBreakdown:
    """Final score + the named bits that made it up."""

    total: float
    components: Mapping[str, float]

    def contributing_components(self) -> dict[str, float]:
        """Drop zero components so the reason string stays short."""
        return {name: value for name, value in self.components.items() if value != 0.0}


def build_scoring_context(
    catalogue: Sequence[TrackRecord],
    *,
    recent_tracks: Sequence[str] = (),
    mood: str | None = None,
    activity: str | None = None,
    genre: str | None = None,
    avoid_repeated_artists: bool = False,
) -> ScoringContext:
    """Look up genres/artists for the recent_tracks ids."""
    by_id = {track.id: track for track in catalogue}
    recent_genres: set[str] = set()
    recent_artists: set[str] = set()
    last_track_genre: str | None = None

    for track_id in recent_tracks:
        track = by_id.get(track_id)
        if track is None:
            continue
        recent_genres.add(track.genre)
        recent_artists.add(track.artist)

    for track_id in reversed(recent_tracks):
        track = by_id.get(track_id)
        if track is not None:
            last_track_genre = track.genre
            break

    return ScoringContext(
        recent_tracks=tuple(recent_tracks),
        mood=mood,
        activity=activity,
        genre=genre,
        avoid_repeated_artists=avoid_repeated_artists,
        recent_genres=frozenset(recent_genres),
        recent_artists=frozenset(recent_artists),
        last_track_genre=last_track_genre,
    )


def _has_preference_conflict(track: TrackRecord, context: ScoringContext) -> bool:
    """True if they asked for something this track does not have."""
    checks: list[bool] = []
    if context.mood is not None:
        checks.append(context.mood in track.moods)
    if context.activity is not None:
        checks.append(context.activity in track.activities)
    if context.genre is not None:
        checks.append(track.genre == context.genre)
    if not checks:
        return False
    return not all(checks)


def score_track(
    track: TrackRecord,
    context: ScoringContext,
    weights: ScoringWeights = DEFAULT_WEIGHTS,
) -> ScoreBreakdown:
    """Score one track — each signal is a named component."""
    components: dict[str, float] = {
        "preferred_genre_match": 0.0,
        "mood_match": 0.0,
        "activity_match": 0.0,
        "shared_genre_with_recent": 0.0,
        "shared_artist_with_recent": 0.0,
        "continuity_last_genre": 0.0,
        "soft_artist_repeat_penalty": 0.0,
        "preference_conflict": 0.0,
    }

    if context.genre is not None and track.genre == context.genre:
        components["preferred_genre_match"] = weights.preferred_genre_match

    if context.mood is not None and context.mood in track.moods:
        components["mood_match"] = weights.mood_match

    if context.activity is not None and context.activity in track.activities:
        components["activity_match"] = weights.activity_match

    if track.genre in context.recent_genres:
        components["shared_genre_with_recent"] = weights.shared_genre_with_recent

    artist_in_history = track.artist in context.recent_artists
    if artist_in_history and not context.avoid_repeated_artists:
        components["shared_artist_with_recent"] = weights.shared_artist_with_recent
        components["soft_artist_repeat_penalty"] = weights.soft_artist_repeat_penalty

    if (
        context.last_track_genre is not None
        and track.genre == context.last_track_genre
    ):
        components["continuity_last_genre"] = weights.continuity_last_genre

    if _has_preference_conflict(track, context):
        components["preference_conflict"] = weights.preference_conflict

    total = sum(components.values())
    return ScoreBreakdown(total=total, components=components)
