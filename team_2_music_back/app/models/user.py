# -*- coding: utf-8 -*-
"""
User Profile Model
"""
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class UserProfile(BaseModel):
    """
    User profile information
    Note: Authentication is handled by external Auth Server
    This only stores profile data
    """
    __tablename__ = "user_profiles"

    # External user ID from Auth Server (JWT sub claim)
    user_id = Column(String(255), unique=True, nullable=False, index=True)

    # Profile Information
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)

    # Social Stats (denormalized for performance)
    follower_count = Column(String(50), default="0", nullable=False)
    following_count = Column(String(50), default="0", nullable=False)
    track_count = Column(String(50), default="0", nullable=False)

    # Relationships
    tracks = relationship("Track", back_populates="owner", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    playlists = relationship("Playlist", back_populates="owner", cascade="all, delete-orphan")
    play_history = relationship("PlayHistory", back_populates="user", cascade="all, delete-orphan")
    # notifications = relationship("Notification", foreign_keys="Notification.user_id", back_populates="user", cascade="all, delete-orphan")  # TODO: Fix ambiguous foreign keys

    # Followers (users who follow this user)
    followers = relationship(
        "Follow",
        foreign_keys="Follow.following_id",
        back_populates="following_user",
        cascade="all, delete-orphan"
    )

    # Following (users this user follows)
    following = relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        back_populates="follower_user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<UserProfile(id={self.id}, username={self.username})>"
