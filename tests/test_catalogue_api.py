"""Smoke tests for GET /catalogue."""

from fastapi.testclient import TestClient


def test_catalogue_lists_seeded_tracks(client: TestClient) -> None:
    response = client.get("/catalogue")
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == len(payload["tracks"])
    assert payload["count"] >= 60
    ids = {track["id"] for track in payload["tracks"]}
    assert "track_001" in ids
    assert "track_033" in ids
    assert "track_060" in ids
    feather = next(track for track in payload["tracks"] if track["id"] == "track_033")
    assert feather["title"] == "Feather"
    assert feather["artist"] == "Nujabes"
