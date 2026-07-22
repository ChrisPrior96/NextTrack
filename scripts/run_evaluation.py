"""Compare scored picks against random eligible tracks (offline eval)."""

from __future__ import annotations

import argparse
import json
import random
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.candidates import generate_candidates
from app.services.catalogue import TrackRecord, load_tracks_from_json
from app.services.recommendation import recommend_track
from app.services.scoring import build_scoring_context, score_track

SCENARIOS_PATH = ROOT / "tests" / "evaluation" / "scenarios.json"
DEFAULT_SEED = 42


@dataclass(frozen=True, slots=True)
class ScenarioResult:
    scenario_id: str
    scored_track_id: str
    random_track_id: str
    scored_score: float
    random_score: float
    score_gap: float


def load_scenarios(path: Path | None = None) -> list[dict]:
    scenarios_path = path or SCENARIOS_PATH
    with scenarios_path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list) or not payload:
        raise ValueError("scenarios.json must be a non-empty JSON array")
    return payload


def _request_fields(scenario: dict) -> dict:
    request = scenario["request"]
    return {
        "recent_tracks": list(request.get("recent_tracks") or []),
        "mood": request.get("mood"),
        "activity": request.get("activity"),
        "genre": request.get("genre"),
        "avoid_repeated_artists": bool(request.get("avoid_repeated_artists", False)),
    }


def evaluate_scenario(
    scenario: dict,
    catalogue: list[TrackRecord],
    rng: random.Random,
) -> ScenarioResult:
    fields = _request_fields(scenario)
    scored = recommend_track(catalogue, **fields)

    candidates = generate_candidates(catalogue, **fields)
    if not candidates:
        raise RuntimeError(f"Scenario {scenario['id']} produced no candidates")

    random_track = rng.choice(list(candidates))
    context = build_scoring_context(catalogue, **fields)
    random_breakdown = score_track(random_track, context)

    return ScenarioResult(
        scenario_id=scenario["id"],
        scored_track_id=scored.track.id,
        random_track_id=random_track.id,
        scored_score=scored.score,
        random_score=random_breakdown.total,
        score_gap=scored.score - random_breakdown.total,
    )


def run_evaluation(
    *,
    seed: int = DEFAULT_SEED,
    scenarios_path: Path | None = None,
) -> list[ScenarioResult]:
    catalogue = load_tracks_from_json()
    scenarios = load_scenarios(scenarios_path)
    rng = random.Random(seed)
    return [evaluate_scenario(scenario, catalogue, rng) for scenario in scenarios]


def format_results_table(results: list[ScenarioResult]) -> str:
    headers = [
        "scenario",
        "scored_id",
        "random_id",
        "scored_score",
        "random_score",
        "score_gap",
    ]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for item in results:
        lines.append(
            "| "
            + " | ".join(
                [
                    item.scenario_id,
                    item.scored_track_id,
                    item.random_track_id,
                    f"{item.scored_score:.2f}",
                    f"{item.random_score:.2f}",
                    f"{item.score_gap:.2f}",
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--scenarios", type=Path, default=SCENARIOS_PATH)
    args = parser.parse_args()

    results = run_evaluation(seed=args.seed, scenarios_path=args.scenarios)
    mean_gap = sum(item.score_gap for item in results) / len(results)
    wins = sum(1 for item in results if item.score_gap > 0) / len(results)

    print(f"Evaluation seed: {args.seed}")
    print(format_results_table(results))
    print()
    print("Summary")
    print(f"- scenarios: {len(results)}")
    print(f"- mean score gap (scored - random): {mean_gap:.3f}")
    print(f"- share of scenarios where scored beat random on score: {wins:.3f}")


if __name__ == "__main__":
    main()
