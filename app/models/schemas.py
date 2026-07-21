"""Request/response shapes for the API (Pydantic)."""

from pydantic import BaseModel, Field, field_validator, model_validator

from app.core.enums import Activity, Genre, Mood


class ErrorResponse(BaseModel):
    """Error payload: just a detail string."""

    detail: str = Field(
        description="Human-readable explanation of why the request failed.",
        examples=["Unknown track id(s): track_missing"],
    )


class RecommendRequest(BaseModel):
    """What the client sends in for a recommendation."""

    recent_tracks: list[str] = Field(
        default_factory=list,
        description=(
            "Catalogue track IDs from the current listening session. "
            "May be empty only when at least one preference field is set. "
            "Unknown ids yield HTTP 400 after validation succeeds."
        ),
        examples=[["track_001"]],
    )
    mood: Mood | None = Field(
        default=None,
        description="Optional mood preference from the locked mood vocabulary.",
        examples=["focused"],
    )
    activity: Activity | None = Field(
        default=None,
        description="Optional activity context from the locked activity vocabulary.",
        examples=["study"],
    )
    genre: Genre | None = Field(
        default=None,
        description="Optional genre preference from the locked genre vocabulary.",
        examples=["lo-fi"],
    )
    avoid_repeated_artists: bool = Field(
        default=False,
        description=(
            "When true, exclude tracks whose artist already appears in recent_tracks."
        ),
    )

    @field_validator("recent_tracks")
    @classmethod
    def recent_tracks_must_be_non_empty_ids(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        for track_id in value:
            if not isinstance(track_id, str) or not track_id.strip():
                raise ValueError("recent_tracks entries must be non-empty track ids")
            cleaned.append(track_id.strip())
        return cleaned

    @model_validator(mode="after")
    def require_history_or_preferences(self) -> "RecommendRequest":
        has_history = bool(self.recent_tracks)
        has_preferences = any(
            value is not None for value in (self.mood, self.activity, self.genre)
        )
        if not has_history and not has_preferences:
            raise ValueError(
                "Provide at least one recent track or a mood, activity, or genre preference"
            )
        return self


class TrackSummary(BaseModel):
    """Track fields we send back."""

    id: str = Field(description="Stable catalogue identifier.", examples=["track_014"])
    title: str = Field(description="Track title.")
    artist: str = Field(description="Primary artist name.")
    genre: str = Field(description="Primary genre label for the track.")
    moods: list[str] = Field(
        description="Mood tags associated with the track.",
        examples=[["focused", "calm"]],
    )
    activities: list[str] = Field(
        description="Activity tags associated with the track.",
        examples=[["study", "work"]],
    )


class RecommendResponse(BaseModel):
    """Happy-path recommend response."""

    recommended_track: TrackSummary = Field(
        description="The top recommended catalogue track."
    )
    score: float = Field(
        description="Relative ranking score for the recommendation.",
        examples=[9.0],
    )
    reason: str = Field(
        description="Short human-readable explanation of why the track was chosen.",
        examples=["Matches focused study listening with lo-fi preference."],
    )
