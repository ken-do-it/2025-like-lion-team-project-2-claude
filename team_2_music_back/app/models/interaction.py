# -*- coding: utf-8 -*-
"""
User Interaction Models (Like, Comment)
"""
from sqlalchemy import Column, Integer, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Like(BaseModel):
    """
    Track likes
    """
    __tablename__ = "likes"
    __table_args__ = (
        UniqueConstraint('track_id', 'user_id', name='unique_track_user_like'),
    )

    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, index=True)

    # Relationships
    track = relationship("Track", back_populates="likes")
    user = relationship("UserProfile", back_populates="likes")

    def __repr__(self):
        return f"<Like(track_id={self.track_id}, user_id={self.user_id})>"


class Comment(BaseModel):
    """
    Track comments
    """
    __tablename__ = "comments"

    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, index=True)
    text = Column(Text, nullable=False)

    # Optional: parent comment for nested replies
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True, index=True)

    # Relationships
    track = relationship("Track", back_populates="comments")
    user = relationship("UserProfile", back_populates="comments")

    # Self-referential for nested comments
    replies = relationship("Comment", backref="parent", remote_side="Comment.id")

    def __repr__(self):
        return f"<Comment(id={self.id}, track_id={self.track_id}, user_id={self.user_id})>"
