# -*- coding: utf-8 -*-
"""
Track (Music) Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TrackStatus(str, Enum):
    """Track processing status"""
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


# Base schema
class TrackBase(BaseModel):
    """Base track fields"""
    title: str = Field(..., min_length=1, max_length=255, description="Track title")
    description: Optional[str] = Field(None, description="Track description")
    artist_name: Optional[str] = Field(None, max_length=255, description="Artist name")
    album_art_url: Optional[str] = Field(None, max_length=500, description="Album art URL")


# Schema for creating a track (after upload)
class TrackCreate(TrackBase):
    """Create track"""
    s3_key: str = Field(..., description="S3 storage key")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    content_type: Optional[str] = Field(None, description="MIME type")


# Schema for updating track
class TrackUpdate(BaseModel):
    """Update track (partial update)"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    artist_name: Optional[str] = Field(None, max_length=255)
    album_art_url: Optional[str] = Field(None, max_length=500)
    is_public: Optional[str] = None


# Schema for response
class TrackResponse(TrackBase):
    """Track response"""
    id: int
    owner_user_id: int
    s3_key: str
    status: TrackStatus
    duration: Optional[int] = Field(None, description="Duration in seconds")
    bpm: Optional[int] = Field(None, description="Beats per minute")
    play_count: int
    like_count: int
    comment_count: int
    download_count: int
    trending_score: float
    is_public: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Nested objects
    # owner: Optional["UserProfileMinimal"] = None  # Can add later

    class Config:
        from_attributes = True


# Minimal track info for nested responses
class TrackMinimal(BaseModel):
    """Minimal track info"""
    id: int
    title: str
    artist_name: Optional[str]
    album_art_url: Optional[str]
    duration: Optional[int]
    play_count: int

    class Config:
        from_attributes = True


# Track list response with pagination
class TrackListResponse(BaseModel):
    """Paginated track list"""
    items: List[TrackResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


# Upload flow schemas (3-stage upload)
class UploadInitiateRequest(BaseModel):
    """Request to initiate upload"""
    file_name: str = Field(..., description="Original file name")
    file_size: int = Field(..., gt=0, description="File size in bytes")
    content_type: str = Field(..., description="MIME type (e.g., audio/mpeg)")


class UploadInitiateResponse(BaseModel):
    """Response from upload initiation"""
    upload_id: str = Field(..., description="Unique upload ID")
    presigned_url: str = Field(..., description="S3 presigned upload URL")
    s3_key: str = Field(..., description="S3 object key")
    expires_in: int = Field(..., description="URL expiration time in seconds")


class UploadFinalizeRequest(TrackBase):
    """Request to finalize upload"""
    upload_id: str = Field(..., description="Upload ID from initiate step")
    s3_key: str = Field(..., description="S3 key from initiate step")
    file_size: int = Field(..., description="File size in bytes")
