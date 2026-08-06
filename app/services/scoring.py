"""Score each candidate and sort them. Weights live in scoring_weights."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
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
    # Resolved history in request order (oldest → newest). Used for recency decay.
    recent_history: tuple[TrackRecord, ...] = ()
    recent_genres: frozenset[str] = field(default_factory=frozenset)
    recent_artists: frozenset[str] = field(default_factory=frozenset)
    last_track_genre: str | None = None
    # Optional MusicBrainz tags keyed by catalogue track id.
    external_tags_by_id: Mapping[str, tuple[str, ...]] = field(default_factory=dict)


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
    external_tags_by_id: Mapping[str, tuple[str, ...]] | None = None,
) -> ScoringContext:
    """Look up genres/artists for the recent_tracks ids."""
    by_id = {track.id: track for track in catalogue}
    history: list[TrackRecord] = []
    recent_genres: set[str] = set()
    recent_artists: set[str] = set()

    for track_id in recent_tracks:
        track = by_id.get(track_id)
        if track is None:
            continue
        history.append(track)
        recent_genres.add(track.genre)
        recent_artists.add(track.artist)

    last_track_genre = history[-1].genre if history else None

    return ScoringContext(
        recent_tracks=tuple(recent_tracks),
        mood=mood,
        activity=activity,
        genre=genre,
        avoid_repeated_artists=avoid_repeated_artists,
        recent_history=tuple(history),
        recent_genres=frozenset(recent_genres),
        recent_artists=frozenset(recent_artists),
        last_track_genre=last_track_genre,
        external_tags_by_id=dict(external_tags_by_id or {}),
    )


def _recency_scale(steps_from_newest: int, decay: float) -> float:
    """1.0 for the newest history item, then decay for each step older."""
    if steps_from_newest < 0:
        return 0.0
    factor = min(max(decay, 0.0), 1.0)
    return factor**steps_from_newest


def _best_history_recency(
    history: Sequence[TrackRecord],
    *,
    decay: float,
    matches: Callable[[TrackRecord], bool],
) -> float:
    """
    Strongest recency scale for any matching history track.

    Newest match wins (scale closer to 1.0). Returns 0.0 when nothing matches.
    """
    if not history:
        return 0.0
    best = 0.0
    last_index = len(history) - 1
    for index, past in enumerate(history):
        if not matches(past):
            continue
        scale = _recency_scale(last_index - index, decay)
        if scale > best:
            best = scale
    return best


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


def _external_tag_boost(
    track: TrackRecord,
    context: ScoringContext,
    weights: ScoringWeights,
) -> float:
    """Small boost if cached external tags overlap mood/activity words."""
    tags = context.external_tags_by_id.get(track.id, ())
    if not tags:
        return 0.0
    normalised = {tag.strip().lower() for tag in tags if tag and tag.strip()}
    hit = False
    if context.mood is not None and context.mood.lower() in normalised:
        hit = True
    if context.activity is not None and context.activity.lower() in normalised:
        hit = True
    return weights.external_tag_match if hit else 0.0


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
        "external_tag_match": 0.0,
    }

    if context.genre is not None and track.genre == context.genre:
        components["preferred_genre_match"] = weights.preferred_genre_match

    if context.mood is not None and context.mood in track.moods:
        components["mood_match"] = weights.mood_match

    if context.activity is not None and context.activity in track.activities:
        components["activity_match"] = weights.activity_match

    genre_scale = _best_history_recency(
        context.recent_history,
        decay=weights.recency_decay,
        matches=lambda past: past.genre == track.genre,
    )
    if genre_scale > 0.0:
        components["shared_genre_with_recent"] = (
            weights.shared_genre_with_recent * genre_scale
        )

    artist_scale = _best_history_recency(
        context.recent_history,
        decay=weights.recency_decay,
        matches=lambda past: past.artist == track.artist,
    )
    if artist_scale > 0.0 and not context.avoid_repeated_artists:
        components["shared_artist_with_recent"] = (
            weights.shared_artist_with_recent * artist_scale
        )
        components["soft_artist_repeat_penalty"] = (
            weights.soft_artist_repeat_penalty * artist_scale
        )

    if (
        context.last_track_genre is not None
        and track.genre == context.last_track_genre
    ):
        components["continuity_last_genre"] = weights.continuity_last_genre

    if _has_preference_conflict(track, context):
        components["preference_conflict"] = weights.preference_conflict

    components["external_tag_match"] = _external_tag_boost(track, context, weights)

    total = sum(components.values())
    return ScoreBreakdown(total=total, components=components)


@dataclass(frozen=True, slots=True)
class RankedCandidate:
    """Track + its score."""

    track: TrackRecord
    breakdown: ScoreBreakdown


def rank_candidates(
    candidates: Sequence[TrackRecord],
    context: ScoringContext,
    weights: ScoringWeights = DEFAULT_WEIGHTS,
) -> list[RankedCandidate]:
    """
    Score everyone then sort.

    Ties: higher score wins, then lower track.id so results stay stable.
    """
    ranked = [
        RankedCandidate(track=track, breakdown=score_track(track, context, weights))
        for track in candidates
    ]
    ranked.sort(key=lambda item: (-item.breakdown.total, item.track.id))
    return ranked
