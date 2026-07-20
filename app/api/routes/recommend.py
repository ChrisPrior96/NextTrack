from fastapi import APIRouter, status

from app.api.deps import http_error_for_domain
from app.models.schemas import RecommendRequest, RecommendResponse, TrackSummary
from app.services.candidates import NoCandidatesError
from app.services.recommendation import (
    UnknownTrackIdsError,
    recommend_from_catalogue,
)

router = APIRouter(tags=["recommend"])


def _to_summary(track) -> TrackSummary:
    return TrackSummary(
        id=track.id,
        title=track.title,
        artist=track.artist,
        genre=track.genre,
        moods=list(track.moods),
        activities=list(track.activities),
    )


@router.post(
    "/recommend",
    response_model=RecommendResponse,
    summary="Recommend the next track",
    description=(
        "Validate listening session context and preferences, then return the "
        "top-scoring eligible catalogue track with a numeric score and reason."
    ),
    responses={
        400: {
            "description": "One or more recent_tracks ids are not in the catalogue."
        },
        404: {
            "description": "No eligible candidate tracks remain after exclusions."
        },
        422: {
            "description": (
                "Request failed validation (invalid enum, malformed body, or "
                "empty context with neither recent tracks nor preferences)."
            )
        },
    },
)
def recommend(body: RecommendRequest) -> RecommendResponse:
    """POST /recommend — pick the next track."""
    try:
        result = recommend_from_catalogue(
            recent_tracks=body.recent_tracks,
            mood=body.mood.value if body.mood is not None else None,
            activity=body.activity.value if body.activity is not None else None,
            genre=body.genre.value if body.genre is not None else None,
            avoid_repeated_artists=body.avoid_repeated_artists,
        )
    except (UnknownTrackIdsError, NoCandidatesError) as exc:
        raise http_error_for_domain(exc) from exc

    return RecommendResponse(
        recommended_track=_to_summary(result.track),
        score=result.score,
        reason=result.reason,
    )
