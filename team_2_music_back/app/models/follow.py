# -*- coding: utf-8 -*-
"""
Follow System Model
"""
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Follow(BaseModel):
    """
    User follow relationships
    follower_id: User who is following
    following_id: User being followed
    """
    __tablename__ = "follows"
    __table_args__ = (
        UniqueConstraint('follower_id', 'following_id', name='unique_follower_following'),
    )

    follower_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, index=True)
    following_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, index=True)

    # Relationships
    follower_user = relationship("UserProfile", foreign_keys=[follower_id], back_populates="following")
    following_user = relationship("UserProfile", foreign_keys=[following_id], back_populates="followers")

    def __repr__(self):
        return f"<Follow(follower_id={self.follower_id}, following_id={self.following_id})>"
