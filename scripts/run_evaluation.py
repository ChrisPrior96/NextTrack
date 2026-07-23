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
DEFAULT_RANDOM_DRAWS = 25


@dataclass(frozen=True, slots=True)
class ScenarioResult:
    scenario_id: str
    scored_track_id: str
    random_track_id: str
    scored_score: float
    random_score: float
    score_gap: float
    preference_hit_rate_scored: float
    preference_hit_rate_random: float
    artist_repeat_rate_scored: float
    artist_repeat_rate_random: float


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


def preference_hit_rate(
    track: TrackRecord,
    mood: str | None,
    activity: str | None,
    genre: str | None,
) -> float:
    """How many of the given prefs this track hits."""
    checks: list[bool] = []
    if mood is not None:
        checks.append(mood in track.moods)
    if activity is not None:
        checks.append(activity in track.activities)
    if genre is not None:
        checks.append(track.genre == genre)
    if not checks:
        return 0.0
    return sum(1 for hit in checks if hit) / len(checks)


def artist_repeated(
    track: TrackRecord,
    catalogue: list[TrackRecord],
    recent_tracks: list[str],
) -> bool:
    by_id = {item.id: item for item in catalogue}
    recent_artists = {
        by_id[track_id].artist for track_id in recent_tracks if track_id in by_id
    }
    return track.artist in recent_artists


def evaluate_scenario(
    scenario: dict,
    catalogue: list[TrackRecord],
    rng: random.Random,
    *,
    random_draws: int = DEFAULT_RANDOM_DRAWS,
) -> ScenarioResult:
    fields = _request_fields(scenario)
    scored = recommend_track(catalogue, **fields)

    candidates = generate_candidates(catalogue, **fields)
    if not candidates:
        raise RuntimeError(f"Scenario {scenario['id']} produced no candidates")

    context = build_scoring_context(catalogue, **fields)
    candidate_list = list(candidates)

    random_scores: list[float] = []
    random_pref_hits: list[float] = []
    random_repeats: list[float] = []
    first_random_id = ""

    for index in range(random_draws):
        pick = rng.choice(candidate_list)
        if index == 0:
            first_random_id = pick.id
        random_scores.append(score_track(pick, context).total)
        random_pref_hits.append(
            preference_hit_rate(pick, fields["mood"], fields["activity"], fields["genre"])
        )
        random_repeats.append(
            1.0 if artist_repeated(pick, catalogue, fields["recent_tracks"]) else 0.0
        )

    mean_random_score = sum(random_scores) / len(random_scores)
    return ScenarioResult(
        scenario_id=scenario["id"],
        scored_track_id=scored.track.id,
        random_track_id=first_random_id,
        scored_score=scored.score,
        random_score=mean_random_score,
        score_gap=scored.score - mean_random_score,
        preference_hit_rate_scored=preference_hit_rate(
            scored.track, fields["mood"], fields["activity"], fields["genre"]
        ),
        preference_hit_rate_random=sum(random_pref_hits) / len(random_pref_hits),
        artist_repeat_rate_scored=(
            1.0
            if artist_repeated(scored.track, catalogue, fields["recent_tracks"])
            else 0.0
        ),
        artist_repeat_rate_random=sum(random_repeats) / len(random_repeats),
    )


def run_evaluation(
    *,
    seed: int = DEFAULT_SEED,
    scenarios_path: Path | None = None,
    random_draws: int = DEFAULT_RANDOM_DRAWS,
) -> list[ScenarioResult]:
    catalogue = load_tracks_from_json()
    scenarios = load_scenarios(scenarios_path)
    rng = random.Random(seed)
    return [
        evaluate_scenario(scenario, catalogue, rng, random_draws=random_draws)
        for scenario in scenarios
    ]


def summarise(results: list[ScenarioResult]) -> dict[str, float]:
    n = len(results)
    return {
        "scenarios": float(n),
        "mean_score_gap": sum(item.score_gap for item in results) / n,
        "mean_pref_hit_scored": sum(item.preference_hit_rate_scored for item in results) / n,
        "mean_pref_hit_random": sum(item.preference_hit_rate_random for item in results) / n,
        "artist_repeat_rate_scored": sum(item.artist_repeat_rate_scored for item in results) / n,
        "artist_repeat_rate_random": sum(item.artist_repeat_rate_random for item in results) / n,
        "scored_wins_on_score": sum(1 for item in results if item.score_gap > 0) / n,
    }


def format_results_table(results: list[ScenarioResult]) -> str:
    headers = [
        "scenario",
        "scored_id",
        "random_id*",
        "scored_score",
        "random_score_avg",
        "score_gap",
        "pref_hit_scored",
        "pref_hit_random",
        "artist_repeat_scored",
        "artist_repeat_random",
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
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
                    f"{item.preference_hit_rate_scored:.2f}",
                    f"{item.preference_hit_rate_random:.2f}",
                    f"{item.artist_repeat_rate_scored:.2f}",
                    f"{item.artist_repeat_rate_random:.2f}",
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--scenarios", type=Path, default=SCENARIOS_PATH)
    parser.add_argument(
        "--random-draws",
        type=int,
        default=DEFAULT_RANDOM_DRAWS,
        help="Random eligible draws per scenario for baseline averages",
    )
    args = parser.parse_args()

    results = run_evaluation(
        seed=args.seed,
        scenarios_path=args.scenarios,
        random_draws=args.random_draws,
    )
    summary = summarise(results)

    print(f"Evaluation seed: {args.seed} (random draws per scenario: {args.random_draws})")
    print(format_results_table(results))
    print()
    print("* random_id is the first draw only; random_score_avg uses all draws.")
    print()
    print("Summary")
    print(f"- scenarios: {int(summary['scenarios'])}")
    print(f"- mean score gap (scored - random): {summary['mean_score_gap']:.3f}")
    print(f"- mean preference hit-rate scored: {summary['mean_pref_hit_scored']:.3f}")
    print(f"- mean preference hit-rate random: {summary['mean_pref_hit_random']:.3f}")
    print(f"- artist repeat-rate scored: {summary['artist_repeat_rate_scored']:.3f}")
    print(f"- artist repeat-rate random: {summary['artist_repeat_rate_random']:.3f}")
    print(
        f"- share of scenarios where scored beat random on score: "
        f"{summary['scored_wins_on_score']:.3f}"
    )


if __name__ == "__main__":
    main()
