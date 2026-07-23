"""Make sure the eval scenarios still pass."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from app.services.catalogue import TrackRecord, load_tracks_from_json
from app.services.recommendation import recommend_track

ROOT = Path(__file__).resolve().parents[2]
SCENARIOS_PATH = Path(__file__).resolve().parent / "scenarios.json"


def _load_runner():
    script_path = ROOT / "scripts" / "run_evaluation.py"
    spec = importlib.util.spec_from_file_location("run_evaluation", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["run_evaluation"] = module
    spec.loader.exec_module(module)
    return module


runner = _load_runner()


@pytest.fixture(scope="module")
def catalogue() -> list[TrackRecord]:
    return load_tracks_from_json()


@pytest.fixture(scope="module")
def scenarios() -> list[dict]:
    return runner.load_scenarios(SCENARIOS_PATH)


def _artists_in_recent(catalogue: list[TrackRecord], recent_tracks: list[str]) -> set[str]:
    by_id = {track.id: track for track in catalogue}
    return {by_id[track_id].artist for track_id in recent_tracks if track_id in by_id}


@pytest.mark.parametrize("index", range(9))
def test_scenario_expectations(catalogue: list[TrackRecord], scenarios: list[dict], index: int) -> None:
    scenario = scenarios[index]
    request = scenario["request"]
    expectations = scenario["expectations"]
    result = recommend_track(
        catalogue,
        recent_tracks=list(request.get("recent_tracks") or []),
        mood=request.get("mood"),
        activity=request.get("activity"),
        genre=request.get("genre"),
        avoid_repeated_artists=bool(request.get("avoid_repeated_artists", False)),
    )
    track = result.track

    if expectations.get("recommended_not_in_recent", True):
        assert track.id not in set(request.get("recent_tracks") or [])

    if "allowed_ids" in expectations:
        assert track.id in set(expectations["allowed_ids"])

    if expectations.get("avoid_artists_from_recent"):
        blocked = _artists_in_recent(catalogue, list(request.get("recent_tracks") or []))
        assert track.artist not in blocked

    hits = 0
    provided = 0
    if request.get("mood") is not None:
        provided += 1
        if request["mood"] in track.moods:
            hits += 1
    if request.get("activity") is not None:
        provided += 1
        if request["activity"] in track.activities:
            hits += 1
    if request.get("genre") is not None:
        provided += 1
        if track.genre == request["genre"]:
            hits += 1

    assert hits >= int(expectations.get("min_preference_hits", 0))

    if not expectations.get("allow_partial_or_general"):
        if expectations.get("prefer_genre"):
            assert track.genre == expectations["prefer_genre"]
        if expectations.get("prefer_mood"):
            assert expectations["prefer_mood"] in track.moods
        if expectations.get("prefer_activity"):
            assert expectations["prefer_activity"] in track.activities

    if expectations.get("prefer_continuity_genre"):
        # Last track was jazz so continuity should pull toward jazz.
        assert track.genre == expectations["prefer_continuity_genre"]


def test_evaluation_is_deterministic_with_fixed_seed(catalogue: list[TrackRecord]) -> None:
    first = runner.run_evaluation(seed=42, random_draws=10)
    second = runner.run_evaluation(seed=42, random_draws=10)
    assert [item.scored_track_id for item in first] == [item.scored_track_id for item in second]
    assert [item.random_track_id for item in first] == [item.random_track_id for item in second]
    assert [round(item.score_gap, 6) for item in first] == [
        round(item.score_gap, 6) for item in second
    ]


def test_evaluation_summary_reports_core_metrics() -> None:
    results = runner.run_evaluation(seed=42, random_draws=10)
    summary = runner.summarise(results)
    assert summary["scenarios"] == 9
    assert summary["mean_score_gap"] >= 0
    assert 0.0 <= summary["mean_pref_hit_scored"] <= 1.0
    assert 0.0 <= summary["artist_repeat_rate_random"] <= 1.0
