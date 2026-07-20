"""Small helpers: turn domain errors into the HTTP codes we locked in."""

from fastapi import HTTPException, status

from app.services.candidates import NoCandidatesError
from app.services.recommendation import UnknownTrackIdsError


def http_error_for_domain(exc: Exception) -> HTTPException:
    """Map recommendation domain errors to HTTP responses."""
    if isinstance(exc, UnknownTrackIdsError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    if isinstance(exc, NoCandidatesError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    raise exc
