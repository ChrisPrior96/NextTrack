from fastapi.testclient import TestClient


VALID_BODY = {
    "recent_tracks": ["track_001"],
    "mood": "focused",
    "activity": "study",
    "genre": "lo-fi",
    "avoid_repeated_artists": False,
}


def test_recommend_valid_body_returns_track(client: TestClient) -> None:
    response = client.post("/recommend", json=VALID_BODY)
    assert response.status_code == 200
    payload = response.json()
    track = payload["recommended_track"]
    assert track["id"] != "track_001"
    assert isinstance(payload["score"], (int, float))
    assert isinstance(payload["reason"], str)
    assert payload["reason"]
    assert track["title"]
    assert track["artist"]
    assert track["genre"]
    assert isinstance(track["moods"], list)
    assert isinstance(track["activities"], list)


def test_recommend_preferences_only_returns_track(client: TestClient) -> None:
    response = client.post(
        "/recommend",
        json={"mood": "calm", "activity": "relax"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "recommended_track" in payload
    assert payload["reason"]


def test_recommend_empty_context_returns_422(client: TestClient) -> None:
    response = client.post("/recommend", json={})
    assert response.status_code == 422


def test_recommend_invalid_enum_returns_422(client: TestClient) -> None:
    response = client.post(
        "/recommend",
        json={"recent_tracks": ["track_001"], "mood": "anxious"},
    )
    assert response.status_code == 422


def test_recommend_unknown_recent_track_returns_400(client: TestClient) -> None:
    response = client.post(
        "/recommend",
        json={"recent_tracks": ["track_does_not_exist"], "mood": "focused"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Unknown track id(s): track_does_not_exist"}


def test_recommend_blank_recent_track_returns_422(client: TestClient) -> None:
    response = client.post(
        "/recommend",
        json={"recent_tracks": ["  "], "mood": "focused"},
    )
    assert response.status_code == 422


def test_recommend_no_candidates_returns_404(client: TestClient) -> None:
    # Wipe the whole catalogue from recent_tracks → should 404.
    all_ids = [f"track_{index:03d}" for index in range(1, 61)]
    response = client.post(
        "/recommend",
        json={"recent_tracks": all_ids},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "No eligible candidate tracks found"}


def test_recommend_openapi_includes_models(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    paths = schema["paths"]
    assert "/recommend" in paths
    components = schema["components"]["schemas"]
    assert "RecommendRequest" in components
    assert "RecommendResponse" in components
