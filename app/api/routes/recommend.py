from fastapi import APIRouter, HTTPException

from app.models.schemas import RecommendRequest, RecommendResponse

router = APIRouter(tags=["recommend"])


@router.post(
    "/recommend",
    response_model=RecommendResponse,
    responses={
        501: {
            "description": "Recommendation logic is not implemented yet",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Recommendation logic is not implemented yet"
                    }
                }
            },
        }
    },
)
def recommend(_body: RecommendRequest) -> RecommendResponse:
    raise HTTPException(
        status_code=501,
        detail="Recommendation logic is not implemented yet",
    )
