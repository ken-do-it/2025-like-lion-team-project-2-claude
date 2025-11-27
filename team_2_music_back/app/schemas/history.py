# -*- coding: utf-8 -*-
"""
Play History Schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# Play history record request
class PlayHistoryCreate(BaseModel):
    """Record a play event"""
    track_id: int = Field(..., gt=0, description="Track ID to record play for")
    listen_duration: Optional[int] = Field(None, ge=0, description="Duration listened in seconds")
    completed: bool = Field(False, description="Whether the track was listened to completion")


# Play history response
class PlayHistoryResponse(BaseModel):
    """Play history record"""
    id: int
    user_id: int
    track_id: int
    played_at: datetime
    listen_duration: Optional[int] = None
    completed: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Play history with track info
class PlayHistoryWithTrack(PlayHistoryResponse):
    """Play history with basic track information"""
    track_title: Optional[str] = None
    track_artist: Optional[str] = None
    track_album_art: Optional[str] = None
    track_duration: Optional[int] = None


# Play history list response
class PlayHistoryListResponse(BaseModel):
    """List of play history records with pagination"""
    items: List[PlayHistoryWithTrack]
    total: int
    page: int
    page_size: int
    has_more: bool


# Recently played tracks (unique tracks)
class RecentlyPlayedTrack(BaseModel):
    """Recently played track with last play time"""
    track_id: int
    title: str
    artist_name: Optional[str] = None
    album_art_url: Optional[str] = None
    duration: Optional[int] = None
    last_played_at: datetime
    play_count: int  # Total times this user played this track

    class Config:
        from_attributes = True


# Recently played tracks list
class RecentlyPlayedListResponse(BaseModel):
    """List of recently played tracks"""
    items: List[RecentlyPlayedTrack]
    total: int
    page: int
    page_size: int
    has_more: bool


# Play stats for a user
class UserPlayStats(BaseModel):
    """User's play statistics"""
    user_id: int
    total_plays: int
    unique_tracks_played: int
    total_listen_time: int  # Total seconds listened
    completed_plays: int  # Number of completed plays
    most_played_track_id: Optional[int] = None
    most_played_track_title: Optional[str] = None
    most_played_track_count: Optional[int] = None


# Play stats for a track
class TrackPlayStats(BaseModel):
    """Track's play statistics"""
    track_id: int
    total_plays: int
    unique_listeners: int
    total_listen_time: int  # Total seconds listened
    completed_plays: int  # Number of completed plays
    avg_completion_rate: float  # Percentage (0-100)
