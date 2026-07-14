"""Request/response shapes for the API (Pydantic)."""

from pydantic import BaseModel, Field, model_validator

from app.core.enums import Activity, Genre, Mood


class RecommendRequest(BaseModel):
    recent_tracks: list[str] = Field(default_factory=list)
    mood: Mood | None = None
    activity: Activity | None = None
    genre: Genre | None = None
    avoid_repeated_artists: bool = False

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
    id: str
    title: str
    artist: str
    genre: str
    moods: list[str]
    activities: list[str]


class RecommendResponse(BaseModel):
    recommended_track: TrackSummary
    score: float
    reason: str
