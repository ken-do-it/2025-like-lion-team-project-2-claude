# -*- coding: utf-8 -*-
"""
Track (Music) Model
"""
from sqlalchemy import Column, String, Text, Integer, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum
from app.models.base import BaseModel


class TrackStatus(str, Enum):
    """Track processing status"""
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class Track(BaseModel):
    """
    Music track uploaded by users
    """
    __tablename__ = "tracks"

    # Basic Information
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    artist_name = Column(String(255), nullable=True)  # Can be different from uploader

    # Owner
    owner_user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, index=True)

    # File Storage (S3)
    s3_key = Column(String(500), nullable=False, unique=True)
    file_size = Column(Integer, nullable=True)  # in bytes
    content_type = Column(String(100), nullable=True)

    # Audio Metadata (extracted after upload)
    duration = Column(Integer, nullable=True)  # in seconds
    bpm = Column(Integer, nullable=True)  # beats per minute
    waveform_json = Column(Text, nullable=True)  # JSON array of waveform data

    # Album Art
    album_art_url = Column(String(500), nullable=True)

    # Processing Status
    status = Column(SQLEnum(TrackStatus), default=TrackStatus.PROCESSING, nullable=False, index=True)

    # Stats (denormalized for performance)
    play_count = Column(Integer, default=0, nullable=False, index=True)
    like_count = Column(Integer, default=0, nullable=False)
    comment_count = Column(Integer, default=0, nullable=False)
    download_count = Column(Integer, default=0, nullable=False)

    # Trending Score (for ranking)
    trending_score = Column(Float, default=0.0, nullable=False, index=True)

    # Visibility
    is_public = Column(String(10), default="true", nullable=False)

    # Relationships
    owner = relationship("UserProfile", back_populates="tracks")
    likes = relationship("Like", back_populates="track", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="track", cascade="all, delete-orphan")
    tags = relationship("TrackTag", back_populates="track", cascade="all, delete-orphan")
    playlist_tracks = relationship("PlaylistTrack", back_populates="track", cascade="all, delete-orphan")
    play_history = relationship("PlayHistory", back_populates="track", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Track(id={self.id}, title={self.title}, status={self.status})>"
