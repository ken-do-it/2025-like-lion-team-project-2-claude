# -*- coding: utf-8 -*-
"""
Playlist Models
"""
from sqlalchemy import Column, String, Text, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Playlist(BaseModel):
    """
    User-created playlists
    """
    __tablename__ = "playlists"

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    cover_image_url = Column(String(500), nullable=True)

    # Owner
    owner_user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, index=True)

    # Visibility
    is_public = Column(Boolean, default=True, nullable=False)

    # Stats
    track_count = Column(Integer, default=0, nullable=False)

    # Relationships
    owner = relationship("UserProfile", back_populates="playlists")
    playlist_tracks = relationship("PlaylistTrack", back_populates="playlist", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Playlist(id={self.id}, title={self.title})>"


class PlaylistTrack(BaseModel):
    """
    Junction table for Playlist and Track (many-to-many)
    """
    __tablename__ = "playlist_tracks"

    playlist_id = Column(Integer, ForeignKey("playlists.id"), nullable=False, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False, index=True)
    position = Column(Integer, nullable=False)  # Order in playlist

    # Relationships
    playlist = relationship("Playlist", back_populates="playlist_tracks")
    track = relationship("Track", back_populates="playlist_tracks")

    def __repr__(self):
        return f"<PlaylistTrack(playlist_id={self.playlist_id}, track_id={self.track_id}, position={self.position})>"
