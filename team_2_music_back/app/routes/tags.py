# -*- coding: utf-8 -*-
"""
Tag and Search API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.user import UserProfile
from app.models.track import Track
from app.models.tag import Tag, TrackTag
from app.schemas.tag import (
    TagCreate, TagUpdate, TagResponse, TagsListResponse,
    AddTagToTrackRequest, TrackTagInfo
)
from app.schemas.track import TrackResponse, TrackListResponse

router = APIRouter(prefix="/api/v1", tags=["tags"])


# ============================================================================
# TAG CRUD ENDPOINTS
# ============================================================================

@router.get("/tags/", response_model=TagsListResponse)
async def list_tags(
    category: Optional[str] = Query(None, description="Filter by category"),
    min_usage: Optional[int] = Query(None, ge=0, description="Minimum usage count"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get list of all tags with optional filtering
    """
    query = db.query(Tag).filter(Tag.is_active == True)

    # Apply filters
    if category:
        query = query.filter(Tag.category == category)
    if min_usage is not None:
        query = query.filter(Tag.usage_count >= min_usage)

    # Get total count
    total = query.count()

    # Apply pagination and ordering
    tags = query.order_by(Tag.usage_count.desc(), Tag.name).offset((page - 1) * page_size).limit(page_size).all()

    return TagsListResponse(
        items=tags,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(page * page_size) < total
    )


@router.get("/tags/{tag_id}", response_model=TagResponse)
async def get_tag(tag_id: int, db: Session = Depends(get_db)):
    """
    Get tag details by ID
    """
    tag = db.query(Tag).filter(Tag.id == tag_id, Tag.is_active == True).first()

    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    return tag


@router.post("/tags/", response_model=TagResponse, status_code=201)
async def create_tag(
    tag_data: TagCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new tag

    TODO: Add authentication - only authenticated users can create tags
    """
    # TODO: Get current user from JWT token
    current_user = db.query(UserProfile).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")

    # Check if tag already exists
    existing_tag = db.query(Tag).filter(Tag.name == tag_data.name, Tag.is_active == True).first()
    if existing_tag:
        raise HTTPException(status_code=400, detail="Tag already exists")

    # Create tag
    new_tag = Tag(
        name=tag_data.name,
        category=tag_data.category,
        usage_count=0
    )

    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)

    return new_tag


@router.patch("/tags/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    db: Session = Depends(get_db)
):
    """
    Update tag

    TODO: Add authentication - only admins can update tags
    """
    # TODO: Get current user from JWT token
    current_user = db.query(UserProfile).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")

    # Get tag
    tag = db.query(Tag).filter(Tag.id == tag_id, Tag.is_active == True).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # Update fields
    if tag_data.name is not None:
        # Check if new name already exists
        existing = db.query(Tag).filter(Tag.name == tag_data.name, Tag.id != tag_id, Tag.is_active == True).first()
        if existing:
            raise HTTPException(status_code=400, detail="Tag name already exists")
        tag.name = tag_data.name

    if tag_data.category is not None:
        tag.category = tag_data.category

    db.commit()
    db.refresh(tag)

    return tag


@router.delete("/tags/{tag_id}")
async def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
    """
    Soft delete a tag

    TODO: Add authentication - only admins can delete tags
    """
    # TODO: Get current user from JWT token
    current_user = db.query(UserProfile).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")

    # Get tag
    tag = db.query(Tag).filter(Tag.id == tag_id, Tag.is_active == True).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # Soft delete
    tag.is_active = False

    # Also soft delete all track_tags
    db.query(TrackTag).filter(TrackTag.tag_id == tag_id, TrackTag.is_active == True).update({"is_active": False})

    db.commit()

    return {"message": "Tag deleted successfully", "tag_id": tag_id}


# ============================================================================
# TRACK-TAG MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/tracks/{track_id}/tags", response_model=TrackTagInfo)
async def add_tag_to_track(
    track_id: int,
    tag_request: AddTagToTrackRequest,
    db: Session = Depends(get_db)
):
    """
    Add a tag to a track (creates tag if doesn't exist)

    TODO: Add authentication - only track owner can add tags
    """
    # TODO: Get current user from JWT token
    current_user = db.query(UserProfile).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")

    # Get track
    track = db.query(Track).filter(Track.id == track_id, Track.is_active == True).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    # TODO: Verify ownership
    # if track.owner_user_id != current_user.id:
    #     raise HTTPException(status_code=403, detail="Not authorized to modify this track")

    # Get or create tag
    tag = db.query(Tag).filter(Tag.name == tag_request.tag_name, Tag.is_active == True).first()
    if not tag:
        tag = Tag(
            name=tag_request.tag_name,
            category=tag_request.category,
            usage_count=0
        )
        db.add(tag)
        db.flush()  # Get tag.id

    # Check if already tagged
    existing = db.query(TrackTag).filter(
        TrackTag.track_id == track_id,
        TrackTag.tag_id == tag.id,
        TrackTag.is_active == True
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Track already has this tag")

    # Create track_tag
    track_tag = TrackTag(
        track_id=track_id,
        tag_id=tag.id
    )
    db.add(track_tag)

    # Increment usage count
    tag.usage_count = tag.usage_count + 1

    db.commit()
    db.refresh(tag)

    return tag


@router.delete("/tracks/{track_id}/tags/{tag_id}")
async def remove_tag_from_track(
    track_id: int,
    tag_id: int,
    db: Session = Depends(get_db)
):
    """
    Remove a tag from a track

    TODO: Add authentication - only track owner can remove tags
    """
    # TODO: Get current user from JWT token
    current_user = db.query(UserProfile).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")

    # Get track
    track = db.query(Track).filter(Track.id == track_id, Track.is_active == True).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    # Get track_tag
    track_tag = db.query(TrackTag).filter(
        TrackTag.track_id == track_id,
        TrackTag.tag_id == tag_id,
        TrackTag.is_active == True
    ).first()

    if not track_tag:
        raise HTTPException(status_code=404, detail="Tag not associated with this track")

    # Soft delete
    track_tag.is_active = False

    # Decrement usage count
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        tag.usage_count = max(0, tag.usage_count - 1)

    db.commit()

    return {"message": "Tag removed from track successfully", "track_id": track_id, "tag_id": tag_id}


@router.get("/tracks/{track_id}/tags", response_model=TagsListResponse)
async def get_track_tags(
    track_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all tags for a track
    """
    # Get track
    track = db.query(Track).filter(Track.id == track_id, Track.is_active == True).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    # Get tags
    tags = db.query(Tag).join(TrackTag).filter(
        TrackTag.track_id == track_id,
        TrackTag.is_active == True,
        Tag.is_active == True
    ).all()

    return TagsListResponse(
        items=tags,
        total=len(tags),
        page=1,
        page_size=len(tags),
        has_more=False
    )


# ============================================================================
# SEARCH & DISCOVERY ENDPOINTS
# ============================================================================

@router.get("/search/tracks", response_model=TrackListResponse)
async def search_tracks(
    q: Optional[str] = Query(None, description="Search query (title, artist, description)"),
    tags: Optional[str] = Query(None, description="Comma-separated tag names"),
    category: Optional[str] = Query(None, description="Filter by tag category"),
    min_duration: Optional[int] = Query(None, ge=0),
    max_duration: Optional[int] = Query(None, ge=0),
    min_bpm: Optional[int] = Query(None, ge=0),
    max_bpm: Optional[int] = Query(None, ge=0),
    is_public: Optional[bool] = Query(None),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="asc or desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Advanced search for tracks with multiple filters
    """
    query = db.query(Track).filter(Track.is_active == True)

    # Text search
    if q:
        search_filter = or_(
            Track.title.ilike(f"%{q}%"),
            Track.artist_name.ilike(f"%{q}%"),
            Track.description.ilike(f"%{q}%")
        )
        query = query.filter(search_filter)

    # Tag filtering
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        # Join with TrackTag and Tag tables
        query = query.join(TrackTag).join(Tag).filter(
            Tag.name.in_(tag_list),
            TrackTag.is_active == True,
            Tag.is_active == True
        )

    # Category filtering (via tags)
    if category:
        if not tags:  # Only join if not already joined
            query = query.join(TrackTag).join(Tag)
        query = query.filter(
            Tag.category == category,
            TrackTag.is_active == True,
            Tag.is_active == True
        )

    # Duration filtering
    if min_duration is not None:
        query = query.filter(Track.duration >= min_duration)
    if max_duration is not None:
        query = query.filter(Track.duration <= max_duration)

    # BPM filtering
    if min_bpm is not None:
        query = query.filter(Track.bpm >= min_bpm)
    if max_bpm is not None:
        query = query.filter(Track.bpm <= max_bpm)

    # Public/private filtering
    if is_public is not None:
        query = query.filter(Track.is_public == str(is_public).lower())

    # Get total before pagination
    total = query.count()

    # Sorting
    valid_sort_fields = ["created_at", "play_count", "like_count", "trending_score", "title"]
    if sort_by not in valid_sort_fields:
        sort_by = "created_at"

    sort_column = getattr(Track, sort_by)
    if sort_order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # Pagination
    tracks = query.offset((page - 1) * page_size).limit(page_size).all()

    return TrackListResponse(
        items=tracks,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(page * page_size) < total
    )


@router.get("/discover/trending", response_model=TrackListResponse)
async def get_trending_tracks(
    period: str = Query("week", description="day, week, month, all_time"),
    category: Optional[str] = Query(None, description="Filter by tag category"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get trending tracks based on trending_score and time period
    """
    query = db.query(Track).filter(Track.is_active == True)

    # Filter by time period
    now = datetime.utcnow()
    if period == "day":
        since = now - timedelta(days=1)
    elif period == "week":
        since = now - timedelta(weeks=1)
    elif period == "month":
        since = now - timedelta(days=30)
    else:  # all_time
        since = None

    if since:
        query = query.filter(Track.created_at >= since)

    # Category filtering
    if category:
        query = query.join(TrackTag).join(Tag).filter(
            Tag.category == category,
            TrackTag.is_active == True,
            Tag.is_active == True
        )

    # Get total
    total = query.count()

    # Sort by trending score (combines play_count, like_count, recency)
    tracks = query.order_by(Track.trending_score.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return TrackListResponse(
        items=tracks,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(page * page_size) < total
    )


@router.get("/discover/by-tag/{tag_name}", response_model=TrackListResponse)
async def discover_by_tag(
    tag_name: str,
    sort_by: str = Query("created_at", description="created_at, play_count, like_count"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Discover tracks by a specific tag
    """
    # Get tag
    tag = db.query(Tag).filter(Tag.name == tag_name, Tag.is_active == True).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # Get tracks with this tag
    query = db.query(Track).join(TrackTag).filter(
        TrackTag.tag_id == tag.id,
        TrackTag.is_active == True,
        Track.is_active == True
    )

    # Get total
    total = query.count()

    # Sorting
    valid_sort_fields = ["created_at", "play_count", "like_count", "trending_score"]
    if sort_by not in valid_sort_fields:
        sort_by = "created_at"

    sort_column = getattr(Track, sort_by)
    tracks = query.order_by(sort_column.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return TrackListResponse(
        items=tracks,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(page * page_size) < total
    )
