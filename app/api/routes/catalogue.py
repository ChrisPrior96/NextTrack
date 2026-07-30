"""GET /catalogue — just list tracks for the demo page."""

from fastapi import APIRouter

from app.models.schemas import CatalogueResponse, TrackSummary
from app.services.catalogue import get_all

router = APIRouter(tags=["catalogue"])


@router.get(
    "/catalogue",
    response_model=CatalogueResponse,
    summary="List catalogue tracks",
    description=(
        "Return every persisted catalogue track. Intended for the local demo UI "
        "and inspection — not a recommendation endpoint."
    ),
)
def list_catalogue() -> CatalogueResponse:
    """List every track for the demo."""
    tracks = [
        TrackSummary(
            id=track.id,
            title=track.title,
            artist=track.artist,
            genre=track.genre,
            moods=list(track.moods),
            activities=list(track.activities),
        )
        for track in get_all()
    ]
    return CatalogueResponse(tracks=tracks, count=len(tracks))
