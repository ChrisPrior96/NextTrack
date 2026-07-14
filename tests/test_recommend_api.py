from fastapi.testclient import TestClient


VALID_BODY = {
    "recent_tracks": ["track_001"],
    "mood": "focused",
    "activity": "study",
    "genre": "lo-fi",
    "avoid_repeated_artists": False,
}


def test_recommend_valid_body_returns_not_implemented(client: TestClient) -> None:
    response = client.post("/recommend", json=VALID_BODY)
    assert response.status_code == 501
    assert response.json() == {
        "detail": "Recommendation logic is not implemented yet"
    }


def test_recommend_preferences_only_returns_not_implemented(client: TestClient) -> None:
    response = client.post(
        "/recommend",
        json={"mood": "calm", "activity": "relax"},
    )
    assert response.status_code == 501


def test_recommend_empty_context_returns_422(client: TestClient) -> None:
    response = client.post("/recommend", json={})
    assert response.status_code == 422


def test_recommend_invalid_enum_returns_422(client: TestClient) -> None:
    response = client.post(
        "/recommend",
        json={"recent_tracks": ["track_001"], "mood": "anxious"},
    )
    assert response.status_code == 422


def test_recommend_openapi_includes_models(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    paths = schema["paths"]
    assert "/recommend" in paths
    components = schema["components"]["schemas"]
    assert "RecommendRequest" in components
    assert "RecommendResponse" in components
