"""SQLAlchemy tables for catalogue stuff only (no user listening data)."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Track(Base):
    """Track row. Listening history never lands in this table."""

    __tablename__ = "tracks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    artist: Mapped[str] = mapped_column(String(255), nullable=False)
    genre: Mapped[str] = mapped_column(String(64), nullable=False)
    moods: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    activities: Mapped[list] = mapped_column(JSON, nullable=False, default=list)


class MusicBrainzCache(Base):
    """
    Cache of MusicBrainz lookups for our tracks.

    External metadata only — not listening history.
    """

    __tablename__ = "musicbrainz_cache"

    local_track_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("tracks.id"),
        primary_key=True,
    )
    mbid: Mapped[str | None] = mapped_column(String(64), nullable=True)
    normalised_title: Mapped[str] = mapped_column(String(255), nullable=False)
    normalised_artist: Mapped[str] = mapped_column(String(255), nullable=False)
    tags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    source_status: Mapped[str] = mapped_column(String(32), nullable=False, default="ok")
    raw_snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
