"""One-off helper: shove the extra real tracks into tracks.json."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "app" / "data" / "tracks.json"

EXTRAS = [
    {
        "id": "track_033",
        "title": "Feather",
        "artist": "Nujabes",
        "genre": "lo-fi",
        "moods": ["calm", "focused"],
        "activities": ["study", "relax"],
    },
    {
        "id": "track_034",
        "title": "Aruarian Dance",
        "artist": "Nujabes",
        "genre": "lo-fi",
        "moods": ["calm", "happy"],
        "activities": ["study", "commute"],
    },
    {
        "id": "track_035",
        "title": "affection",
        "artist": "Jinsang",
        "genre": "lo-fi",
        "moods": ["calm", "focused"],
        "activities": ["study", "work"],
    },
    {
        "id": "track_036",
        "title": "An Ending (Ascent)",
        "artist": "Brian Eno",
        "genre": "ambient",
        "moods": ["calm", "sad"],
        "activities": ["relax", "work"],
    },
    {
        "id": "track_037",
        "title": "Music for Airports 1/1",
        "artist": "Brian Eno",
        "genre": "ambient",
        "moods": ["calm", "focused"],
        "activities": ["relax", "study"],
    },
    {
        "id": "track_038",
        "title": "Xtal",
        "artist": "Aphex Twin",
        "genre": "ambient",
        "moods": ["calm", "focused"],
        "activities": ["work", "relax"],
    },
    {
        "id": "track_039",
        "title": "Digital Love",
        "artist": "Daft Punk",
        "genre": "electronic",
        "moods": ["happy", "excited"],
        "activities": ["commute", "party"],
    },
    {
        "id": "track_040",
        "title": "One More Time",
        "artist": "Daft Punk",
        "genre": "electronic",
        "moods": ["excited", "energetic"],
        "activities": ["party", "workout"],
    },
    {
        "id": "track_041",
        "title": "Strobe",
        "artist": "deadmau5",
        "genre": "electronic",
        "moods": ["focused", "energetic"],
        "activities": ["work", "commute"],
    },
    {
        "id": "track_042",
        "title": "Latch",
        "artist": "Disclosure",
        "genre": "dance",
        "moods": ["happy", "excited"],
        "activities": ["party", "commute"],
    },
    {
        "id": "track_043",
        "title": "Marea (we've lost dancing)",
        "artist": "Fred again..",
        "genre": "dance",
        "moods": ["sad", "energetic"],
        "activities": ["party", "workout"],
    },
    {
        "id": "track_044",
        "title": "Feel So Close",
        "artist": "Calvin Harris",
        "genre": "dance",
        "moods": ["excited", "happy"],
        "activities": ["party", "workout"],
    },
    {
        "id": "track_045",
        "title": "Do I Wanna Know?",
        "artist": "Arctic Monkeys",
        "genre": "indie",
        "moods": ["bored", "energetic"],
        "activities": ["commute", "relax"],
    },
    {
        "id": "track_046",
        "title": "About You",
        "artist": "The 1975",
        "genre": "indie",
        "moods": ["sad", "calm"],
        "activities": ["relax", "commute"],
    },
    {
        "id": "track_047",
        "title": "Electric Feel",
        "artist": "MGMT",
        "genre": "indie",
        "moods": ["happy", "excited"],
        "activities": ["party", "commute"],
    },
    {
        "id": "track_048",
        "title": "Holocene",
        "artist": "Bon Iver",
        "genre": "folk",
        "moods": ["sad", "calm"],
        "activities": ["relax", "study"],
    },
    {
        "id": "track_049",
        "title": "White Winter Hymnal",
        "artist": "Fleet Foxes",
        "genre": "folk",
        "moods": ["calm", "happy"],
        "activities": ["relax", "commute"],
    },
    {
        "id": "track_050",
        "title": "The Night We Met",
        "artist": "Lord Huron",
        "genre": "folk",
        "moods": ["sad", "calm"],
        "activities": ["relax", "commute"],
    },
    {
        "id": "track_051",
        "title": "Everlong",
        "artist": "Foo Fighters",
        "genre": "rock",
        "moods": ["energetic", "excited"],
        "activities": ["workout", "party"],
    },
    {
        "id": "track_052",
        "title": "Seven Nation Army",
        "artist": "The White Stripes",
        "genre": "rock",
        "moods": ["energetic", "bored"],
        "activities": ["workout", "commute"],
    },
    {
        "id": "track_053",
        "title": "Mr. Brightside",
        "artist": "The Killers",
        "genre": "rock",
        "moods": ["excited", "energetic"],
        "activities": ["party", "commute"],
    },
    {
        "id": "track_054",
        "title": "Don't Stop Me Now",
        "artist": "Queen",
        "genre": "rock",
        "moods": ["happy", "excited"],
        "activities": ["party", "workout"],
    },
    {
        "id": "track_055",
        "title": "So What",
        "artist": "Miles Davis",
        "genre": "jazz",
        "moods": ["calm", "focused"],
        "activities": ["work", "relax"],
    },
    {
        "id": "track_056",
        "title": "Blue in Green",
        "artist": "Miles Davis",
        "genre": "jazz",
        "moods": ["sad", "calm"],
        "activities": ["relax", "study"],
    },
    {
        "id": "track_057",
        "title": "Take Five",
        "artist": "The Dave Brubeck Quartet",
        "genre": "jazz",
        "moods": ["focused", "happy"],
        "activities": ["work", "study"],
    },
    {
        "id": "track_058",
        "title": "My Favorite Things",
        "artist": "John Coltrane",
        "genre": "jazz",
        "moods": ["happy", "focused"],
        "activities": ["work", "relax"],
    },
    {
        "id": "track_059",
        "title": "Teardrop",
        "artist": "Massive Attack",
        "genre": "electronic",
        "moods": ["calm", "sad"],
        "activities": ["relax", "commute"],
    },
    {
        "id": "track_060",
        "title": "Midnight City",
        "artist": "M83",
        "genre": "electronic",
        "moods": ["excited", "energetic"],
        "activities": ["commute", "party"],
    },
]


def main() -> None:
    tracks = json.loads(PATH.read_text(encoding="utf-8"))
    existing = {track["id"] for track in tracks}
    added = 0
    for track in EXTRAS:
        if track["id"] in existing:
            continue
        tracks.append(track)
        added += 1
    PATH.write_text(json.dumps(tracks, indent=2) + "\n", encoding="utf-8")
    print(f"Catalogue now has {len(tracks)} tracks ({added} added).")


if __name__ == "__main__":
    main()
