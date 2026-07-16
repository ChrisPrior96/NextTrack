"""SQLAlchemy tables for catalogue stuff only (no user listening data)."""

from sqlalchemy import JSON, String
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
