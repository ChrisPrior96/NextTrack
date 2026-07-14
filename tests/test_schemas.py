import pytest
from pydantic import ValidationError

from app.core.enums import Activity, Genre, Mood
from app.models.schemas import RecommendRequest


def test_request_accepts_recent_tracks_only() -> None:
    payload = RecommendRequest(recent_tracks=["track_001"])
    assert payload.recent_tracks == ["track_001"]
    assert payload.avoid_repeated_artists is False


def test_request_accepts_preferences_without_history() -> None:
    payload = RecommendRequest(mood=Mood.focused, activity=Activity.study, genre=Genre.lo_fi)
    assert payload.recent_tracks == []
    assert payload.mood is Mood.focused
    assert payload.activity is Activity.study
    assert payload.genre is Genre.lo_fi


def test_request_accepts_full_example_contract() -> None:
    payload = RecommendRequest.model_validate(
        {
            "recent_tracks": ["track_001"],
            "mood": "focused",
            "activity": "study",
            "genre": "lo-fi",
            "avoid_repeated_artists": False,
        }
    )
    assert payload.mood is Mood.focused
    assert payload.genre is Genre.lo_fi


def test_request_rejects_empty_context() -> None:
    with pytest.raises(ValidationError) as exc_info:
        RecommendRequest()
    assert "recent track" in str(exc_info.value).lower() or "preference" in str(
        exc_info.value
    ).lower()


def test_request_rejects_invalid_mood() -> None:
    with pytest.raises(ValidationError):
        RecommendRequest.model_validate(
            {"recent_tracks": ["track_001"], "mood": "not-a-mood"}
        )


def test_request_rejects_invalid_activity() -> None:
    with pytest.raises(ValidationError):
        RecommendRequest.model_validate(
            {"recent_tracks": ["track_001"], "activity": "sleeping"}
        )


def test_request_rejects_invalid_genre() -> None:
    with pytest.raises(ValidationError):
        RecommendRequest.model_validate(
            {"recent_tracks": ["track_001"], "genre": "polka"}
        )
