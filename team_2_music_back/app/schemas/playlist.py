# -*- coding: utf-8 -*-
"""
Playlist Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# Playlist base schema
class PlaylistBase(BaseModel):
    """Base playlist fields"""
    title: str = Field(..., min_length=1, max_length=255, description="Playlist title")
    description: Optional[str] = Field(None, max_length=1000, description="Playlist description")
    is_public: Optional[bool] = Field(True, description="Public or private playlist")


# Playlist create schema
class PlaylistCreate(PlaylistBase):
    """Create playlist"""
    pass


# Playlist update schema
class PlaylistUpdate(BaseModel):
    """Update playlist (partial)"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    is_public: Optional[bool] = None


# Minimal track info for playlist tracks
class PlaylistTrackInfo(BaseModel):
    """Minimal track info"""
    id: int
    title: str
    artist_name: Optional[str]
    album_art_url: Optional[str]
    duration: Optional[int]
    play_count: int

    class Config:
        from_attributes = True


# Playlist response
class PlaylistResponse(PlaylistBase):
    """Playlist response"""
    id: int
    owner_user_id: int
    track_count: int
    is_public: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Playlist with tracks
class PlaylistWithTracks(PlaylistResponse):
    """Playlist response with tracks"""
    tracks: List[PlaylistTrackInfo] = []


# Playlists list response
class PlaylistsListResponse(BaseModel):
    """Paginated playlists list"""
    items: List[PlaylistResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


# Add track to playlist response
class AddTrackResponse(BaseModel):
    """Response when adding track to playlist"""
    message: str
    playlist_id: int
    track_id: int
    position: int
