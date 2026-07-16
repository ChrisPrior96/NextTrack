"""Load tracks.json into SQLite. Safe to run more than once."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Track
from app.db.session import SessionLocal, init_db
from app.services.catalogue import load_tracks_from_json


def seed_tracks(session: Session) -> int:
    """
    Insert any tracks from JSON that are not already in the DB.

    Leaves existing rows alone so re-running is fine.
    Returns how many we added.
    """
    seed_tracks_list = load_tracks_from_json()
    existing_ids = set(session.scalars(select(Track.id)).all())
    inserted = 0

    for record in seed_tracks_list:
        if record.id in existing_ids:
            continue
        session.add(
            Track(
                id=record.id,
                title=record.title,
                artist=record.artist,
                genre=record.genre,
                moods=list(record.moods),
                activities=list(record.activities),
            )
        )
        inserted += 1

    if inserted:
        session.commit()
    return inserted


def seed_database() -> int:
    """Make tables (if needed) then seed tracks."""
    init_db()
    with SessionLocal() as session:
        return seed_tracks(session)
