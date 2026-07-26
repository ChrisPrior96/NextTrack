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
- Transparent scoring, ranking, explanations, and working `POST /recommend`
- Hardened error matrix, privacy tests, and marker-ready README
- Offline evaluation scenarios and scored-vs-random baseline results ([docs/evaluation/RESULTS.md](docs/evaluation/RESULTS.md))
- Optional MusicBrainz enrichment client with SQLite cache and fail-open offline behaviour

### Changed

- `POST /recommend` now returns a scored track instead of HTTP 501
- README is versioned again for run/privacy instructions
