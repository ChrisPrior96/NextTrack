# Evaluation results

Offline comparison of NextTrack scored recommendations against a **random eligible** baseline.

## Method

- Catalogue: 60 curated tracks (32 synthetic fixtures + 28 real recordings)
- Scenarios: `tests/evaluation/scenarios.json` (9 cases)
- Runner: `python scripts/run_evaluation.py --seed 42`
- For each scenario:
  1. Build the eligible candidate set (Phase 3 rules)
  2. Take the scored top pick (Phase 4)
  3. Draw **25** random eligible tracks (seeded RNG) and average their scores / preference hits / artist-repeat flags
- Metrics:
  - **score gap** = scored total − mean random total
  - **preference hit-rate** = fraction of provided mood/activity/genre preferences matched
  - **artist repeat-rate** = share of picks whose artist already appears in resolved recent history

## Results (seed = 42, random draws = 25)

| scenario | scored_id | random_id* | scored_score | random_score_avg | score_gap | pref_hit_scored | pref_hit_random | artist_repeat_scored | artist_repeat_random |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| study_focused_lofi_history | track_033 | track_002 | 10.50 | 9.54 | 0.96 | 1.00 | 1.00 | 0.00 | 0.64 |
| party_excited_electronic_history | track_039 | track_040 | 10.50 | 10.02 | 0.48 | 1.00 | 1.00 | 0.00 | 0.32 |
| preferences_only_no_history | track_004 | track_004 | 8.00 | 8.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| history_only_no_prefs | track_051 | track_005 | 2.50 | 0.30 | 2.20 | 0.00 | 0.00 | 0.00 | 0.00 |
| avoid_repeated_artists_on | track_033 | track_035 | 7.50 | 5.60 | 1.90 | 1.00 | 1.00 | 0.00 | 0.00 |
| conflicting_prefs_fallback | track_047 | track_017 | 1.00 | -1.42 | 2.42 | 0.33 | 0.33 | 0.00 | 0.08 |
| long_history_near_exhaustion | track_059 | track_059 | 6.50 | 6.50 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| genre_continuity_from_last_track | track_055 | track_014 | 2.50 | 0.16 | 2.34 | 0.00 | 0.00 | 0.00 | 0.08 |
| workout_energetic_rock | track_051 | track_052 | 10.50 | 9.78 | 0.72 | 1.00 | 1.00 | 0.00 | 0.48 |

\* `random_id` is the first draw only; `random_score_avg` uses all draws.

## Summary

| Metric | Value |
|--------|------:|
| Scenarios | 9 |
| Mean score gap (scored − random) | **1.224** |
| Mean preference hit-rate (scored) | 0.704 |
| Mean preference hit-rate (random) | 0.704 |
| Artist repeat-rate (scored) | 0.000 |
| Artist repeat-rate (random) | 0.178 |
| Share of scenarios where scored beat random on score | **0.778** |

## Interpretation

- Expanding the catalogue with curated real recordings widens many eligible pools, so scoring has more room to beat random (mean gap **1.224**, scored ahead in **7/9** scenarios).
- When the remaining pool is tiny (near-exhaustion) or preference filtering already collapses to a single high-scoring cluster, gap can still be ≈ 0.
- Preference hit-rates stay matched when Phase 3 already filtered to preference-homogeneous candidates.
- Scored artist-repeat rate is low here because several winning real tracks introduce artists not present in the short history; random draws still hit repeats more often in denser genre pools.

Re-run anytime with:

```bash
python scripts/run_evaluation.py --seed 42
```
