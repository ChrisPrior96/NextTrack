"""Turn the score breakdown into a short plain-English reason string."""

from __future__ import annotations

from app.services.catalogue import TrackRecord
from app.services.scoring import ScoreBreakdown

_COMPONENT_LABELS = {
    "preferred_genre_match": "matches your preferred genre ({genre})",
    "mood_match": "fits the {mood} mood",
    "activity_match": "suits {activity}",
    "shared_genre_with_recent": "continues genres from your recent listening",
    "shared_artist_with_recent": "soft continuity with an artist you recently heard",
    "continuity_last_genre": "keeps continuity with your last track's genre",
    "soft_artist_repeat_penalty": "soft penalty for repeating a recent artist",
    "preference_conflict": "only partially matches your stated preferences",
    "external_tag_match": "picks up a matching tag from cached MusicBrainz metadata",
}


def build_reason(
    breakdown: ScoreBreakdown,
    track: TrackRecord,
    *,
    mood: str | None = None,
    activity: str | None = None,
    genre: str | None = None,
) -> str:
    """
    Build the reason string from whichever score bits actually fired.

    Positives first, then any penalties.
    """
    contributing = breakdown.contributing_components()
    if not contributing:
        return (
            f"Recommended '{track.title}' by {track.artist} "
            "as an eligible catalogue match."
        )

    positives: list[str] = []
    negatives: list[str] = []
    values = {
        "genre": genre or track.genre,
        "mood": mood or "requested",
        "activity": activity or "requested",
    }

    for name, value in contributing.items():
        template = _COMPONENT_LABELS.get(name)
        if template is None:
            continue
        phrase = template.format(**values)
        if value > 0:
            positives.append(phrase)
        else:
            negatives.append(phrase)

    parts = [f"Recommended '{track.title}' by {track.artist}"]
    if positives:
        parts.append("because it " + "; ".join(positives))
    if negatives:
        connector = "although" if positives else "with"
        parts.append(f"{connector} " + "; ".join(negatives))

    return " ".join(parts) + "."
