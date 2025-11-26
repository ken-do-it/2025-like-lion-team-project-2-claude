# -*- coding: utf-8 -*-
"""
Tag and TrackTag Models
"""
from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Tag(BaseModel):
    """
    Tags for categorizing tracks (genre, mood, etc.)
    """
    __tablename__ = "tags"

    name = Column(String(50), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=True)  # e.g., 'genre', 'mood', 'instrument'
    usage_count = Column(Integer, default=0, nullable=False)  # How many tracks use this tag

    # Relationships
    track_tags = relationship("TrackTag", back_populates="tag", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name})>"


class TrackTag(BaseModel):
    """
    Junction table for Track and Tag (many-to-many)
    """
    __tablename__ = "track_tags"
    __table_args__ = (
        UniqueConstraint('track_id', 'tag_id', name='unique_track_tag'),
    )

    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False, index=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False, index=True)

    # Relationships
    track = relationship("Track", back_populates="tags")
    tag = relationship("Tag", back_populates="track_tags")

    def __repr__(self):
        return f"<TrackTag(track_id={self.track_id}, tag_id={self.tag_id})>"
