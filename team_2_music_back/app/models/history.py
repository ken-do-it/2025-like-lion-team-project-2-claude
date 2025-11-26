# -*- coding: utf-8 -*-
"""
Play History Model
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import BaseModel


class PlayHistory(BaseModel):
    """
    Track play history for analytics and recommendations
    """
    __tablename__ = "play_history"

    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False, index=True)
    played_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Optional: Track listening duration
    listen_duration = Column(Integer, nullable=True)  # seconds listened
    completed = Column(Integer, default=0, nullable=False)  # 1 if listened to end, 0 otherwise

    # Relationships
    user = relationship("UserProfile", back_populates="play_history")
    track = relationship("Track", back_populates="play_history")

    def __repr__(self):
        return f"<PlayHistory(user_id={self.user_id}, track_id={self.track_id}, played_at={self.played_at})>"
