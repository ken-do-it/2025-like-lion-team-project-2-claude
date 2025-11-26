# -*- coding: utf-8 -*-
"""
Notification Model
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Notification(BaseModel):
    """
    User notifications (likes, comments, follows, etc.)
    """
    __tablename__ = "notifications"

    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, index=True)

    # Notification Type (like, comment, follow, etc.)
    type = Column(String(50), nullable=False, index=True)

    # Actor (who triggered the notification)
    actor_user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=True)

    # Target (what the notification is about)
    target_type = Column(String(50), nullable=True)  # 'track', 'comment', 'playlist'
    target_id = Column(Integer, nullable=True)

    # Message
    message = Column(Text, nullable=False)

    # Read Status
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    # user = relationship("UserProfile", foreign_keys=[user_id], back_populates="notifications")  # TODO: Fix ambiguous foreign keys

    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type}, is_read={self.is_read})>"
