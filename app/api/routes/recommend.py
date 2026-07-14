from fastapi import APIRouter, HTTPException, status

from app.models.schemas import RecommendRequest, RecommendResponse

router = APIRouter(tags=["recommend"])


@router.post(
    "/recommend",
    response_model=RecommendResponse,
    summary="Recommend the next track",
    description=(
        "Validate listening session context and preferences against the locked "
        "API contract. Recommendation scoring is not implemented yet and always "
        "returns HTTP 501 for valid requests."
    ),
    responses={
        422: {
            "description": (
                "Request failed validation (invalid enum, malformed body, or "
                "empty context with neither recent tracks nor preferences)."
            )
        },
        501: {
            "description": "Recommendation logic is not implemented yet",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Recommendation logic is not implemented yet"
                    }
                }
            },
        },
    },
)
def recommend(_body: RecommendRequest) -> RecommendResponse:
    """Accept a validated recommend request; logic arrives in a later phase."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Recommendation logic is not implemented yet",
    )
