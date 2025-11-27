# -*- coding: utf-8 -*-
"""
Tag and Search Schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# Tag base schema
class TagBase(BaseModel):
    """Base tag fields"""
    name: str = Field(..., min_length=1, max_length=50, description="Tag name")
    category: Optional[str] = Field(None, max_length=50, description="Tag category (genre, mood, instrument, etc.)")


# Tag create schema
class TagCreate(TagBase):
    """Create tag"""
    pass


# Tag update schema
class TagUpdate(BaseModel):
    """Update tag (partial)"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    category: Optional[str] = Field(None, max_length=50)


# Tag response
class TagResponse(TagBase):
    """Tag response"""
    id: int
    usage_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Tag list response
class TagsListResponse(BaseModel):
    """List of tags with pagination"""
    items: List[TagResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


# Track tag info (minimal)
class TrackTagInfo(BaseModel):
    """Minimal tag info for track responses"""
    id: int
    name: str
    category: Optional[str] = None

    class Config:
        from_attributes = True


# Add tag to track request
class AddTagToTrackRequest(BaseModel):
    """Request to add tag to track"""
    tag_name: str = Field(..., min_length=1, max_length=50, description="Tag name (will create if doesn't exist)")
    category: Optional[str] = Field(None, max_length=50, description="Tag category")


# Search query parameters (used in route, not directly as request body)
class SearchParams(BaseModel):
    """Search and filter parameters"""
    q: Optional[str] = Field(None, description="Search query (title, artist, description)")
    tags: Optional[List[str]] = Field(None, description="Filter by tag names")
    category: Optional[str] = Field(None, description="Filter by tag category")
    mood: Optional[str] = Field(None, description="Filter by mood tag")
    genre: Optional[str] = Field(None, description="Filter by genre tag")
    min_duration: Optional[int] = Field(None, ge=0, description="Minimum duration in seconds")
    max_duration: Optional[int] = Field(None, ge=0, description="Maximum duration in seconds")
    min_bpm: Optional[int] = Field(None, ge=0, description="Minimum BPM")
    max_bpm: Optional[int] = Field(None, ge=0, description="Maximum BPM")
    is_public: Optional[bool] = Field(None, description="Filter by public/private")
    sort_by: Optional[str] = Field("created_at", description="Sort field: created_at, play_count, like_count, trending_score")
    sort_order: Optional[str] = Field("desc", description="Sort order: asc, desc")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


# Trending tracks response (uses existing TrackResponse from track schema)
# Just need to add a trending period parameter
class TrendingParams(BaseModel):
    """Parameters for trending tracks"""
    period: Optional[str] = Field("week", description="Trending period: day, week, month, all_time")
    category: Optional[str] = Field(None, description="Filter by tag category")
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
