# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),

## [Unreleased]

### Added

- Repository bootstrap: ignore rules, dependency lists, and pytest configuration
- FastAPI application scaffold with `GET /health`
- Locked recommend API contract with enums and validation
- Local JSON catalogue seeded into SQLite (track metadata only)
- Candidate generation with history/artist exclusions and preference fallbacks
- Scoring, ranking, explanations, and working `POST /recommend`
- Hardened error matrix, privacy tests, and project README
- Offline evaluation scenarios and scored-vs-random baseline results ([docs/evaluation/RESULTS.md](docs/evaluation/RESULTS.md))
- Optional MusicBrainz enrichment client with SQLite cache and fail-open offline behaviour
- Minimal browser demo UI for recommend requests (`frontend/`)
- Expanded curated catalogue (~60 tracks) with real recordings, `GET /catalogue`, and a MusicBrainz enrichment sample ([docs/enrichment_sample.json](docs/enrichment_sample.json))
- Recency decay on history genre/artist scoring signals (newer listening counts more)
- Optional soft score boost from cached MusicBrainz tags when enrichment is enabled

### Changed

- `POST /recommend` now returns a scored track instead of HTTP 501
- Offline evaluation results refreshed against the expanded catalogue
- Enrichment cache `fetched_at` default uses SQL `CURRENT_TIMESTAMP`
- Shared genre/artist history scores now fade for older items in `recent_tracks`
