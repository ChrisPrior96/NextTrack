# Evaluation results

Offline comparison of NextTrack scored recommendations against a **random eligible** baseline.

## Method

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
| study_focused_lofi_history | track_002 | track_031 | 9.00 | 9.00 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| party_excited_electronic_history | track_010 | track_010 | 9.00 | 9.00 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| preferences_only_no_history | track_004 | track_006 | 8.00 | 8.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| history_only_no_prefs | track_025 | track_009 | 1.00 | 0.08 | 0.92 | 0.00 | 0.00 | 1.00 | 0.08 |
| avoid_repeated_artists_on | track_005 | track_021 | 5.00 | 5.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| conflicting_prefs_fallback | track_017 | track_027 | -0.50 | -1.46 | 0.96 | 0.33 | 0.33 | 1.00 | 0.04 |
| long_history_near_exhaustion | track_030 | track_030 | 6.00 | 6.00 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| genre_continuity_from_last_track | track_028 | track_023 | 1.00 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 | 0.16 |
| workout_energetic_rock | track_025 | track_025 | 9.00 | 9.00 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 |

\* `random_id` is the first draw only; `random_score_avg` uses all draws.

## Summary

| Metric | Value |
|--------|------:|
| Scenarios | 9 |
| Mean score gap (scored − random) | **0.320** |
| Mean preference hit-rate (scored) | 0.704 |
| Mean preference hit-rate (random) | 0.704 |
| Artist repeat-rate (scored) | 0.778 |
| Artist repeat-rate (random) | 0.476 |
| Share of scenarios where scored beat random on score | **0.333** |

## Interpretation

- When preferences produce a **tight exact-match pool**, scored and random eligible picks often share the same high score (gap ≈ 0). That is expected: Phase 3 already filtered well.
- Where the eligible set is **broader** (history-only, conflicting prefs, genre continuity), scoring beats random on total score (positive gaps of ~0.9–1.0).
- Preference hit-rates match when the candidate pool is homogeneous on those preferences.
- Scored picks repeat recent artists more often because soft artist continuity is an intentional positive signal (offset by the soft repeat penalty). With `avoid_repeated_artists=true`, both sides stay at 0.00 repeats.

Re-run anytime with:

```bash
python scripts/run_evaluation.py --seed 42
```
