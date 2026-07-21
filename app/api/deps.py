"""Small helpers: turn domain errors into the HTTP codes we locked in."""

from fastapi import HTTPException, status

from app.services.candidates import NoCandidatesError
from app.services.recommendation import UnknownTrackIdsError

UNKNOWN_TRACK_DETAIL = "Unknown track id(s): {ids}"
NO_CANDIDATES_DETAIL = "No eligible candidate tracks found"


def http_error_for_domain(exc: Exception) -> HTTPException:
    """Unknown ids → 400, no candidates → 404."""
    if isinstance(exc, UnknownTrackIdsError):
        ids = ", ".join(exc.track_ids)
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=UNKNOWN_TRACK_DETAIL.format(ids=ids),
        )
    if isinstance(exc, NoCandidatesError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=NO_CANDIDATES_DETAIL,
        )
    raise exc
