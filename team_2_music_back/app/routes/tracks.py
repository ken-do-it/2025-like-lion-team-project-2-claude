# -*- coding: utf-8 -*-
"""
Track API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import uuid
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.track import Track, TrackStatus
from app.models.user import UserProfile
from app.schemas.track import (
    TrackResponse,
    TrackListResponse,
    TrackUpdate,
    UploadInitiateRequest,
    UploadInitiateResponse,
    UploadFinalizeRequest,
)
from app.schemas.common import PaginationParams


router = APIRouter(prefix="/api/v1/tracks", tags=["Tracks"])


@router.get("/", response_model=TrackListResponse)
async def list_tracks(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status (ready, processing, failed)"),
    is_public: Optional[bool] = Query(None, description="Filter by public/private"),
    db: Session = Depends(get_db),
):
    """
    List all tracks with pagination and filters
    """
    # Build query
    query = db.query(Track).filter(Track.is_active == True)

    # Apply filters
    if status:
        query = query.filter(Track.status == status)
    if is_public is not None:
        query = query.filter(Track.is_public == str(is_public).lower())

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    tracks = query.order_by(Track.created_at.desc()).offset(offset).limit(page_size).all()

    # Check if there are more pages
    has_more = (offset + page_size) < total

    return TrackListResponse(
        items=tracks,
        total=total,
        page=page,
        page_size=page_size,
        has_more=has_more
    )


@router.get("/{track_id}", response_model=TrackResponse)
async def get_track(
    track_id: int,
    db: Session = Depends(get_db),
):
    """
    Get track details by ID
    """
    track = db.query(Track).filter(
        Track.id == track_id,
        Track.is_active == True
    ).first()

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    return track


@router.post("/upload/initiate", response_model=UploadInitiateResponse)
async def initiate_upload(
    request: UploadInitiateRequest,
    db: Session = Depends(get_db),
):
    """
    Step 1: Initiate track upload
    Returns presigned S3 URL for direct upload

    TODO: Implement actual S3 presigned URL generation
    TODO: Add JWT authentication to get current user
    """
    # Generate unique upload ID
    upload_id = str(uuid.uuid4())

    # Generate S3 key
    # Format: tracks/{user_id}/{upload_id}/{filename}
    # For now using placeholder user_id
    user_id = "temp-user"  # TODO: Get from JWT token
    s3_key = f"tracks/{user_id}/{upload_id}/{request.file_name}"

    # TODO: Generate actual S3 presigned URL
    # For now, return a placeholder URL
    presigned_url = f"https://s3.amazonaws.com/placeholder-bucket/{s3_key}?upload_id={upload_id}"

    # Presigned URLs typically expire in 15 minutes (900 seconds)
    expires_in = 900

    return UploadInitiateResponse(
        upload_id=upload_id,
        presigned_url=presigned_url,
        s3_key=s3_key,
        expires_in=expires_in
    )


@router.post("/upload/finalize", response_model=TrackResponse)
async def finalize_upload(
    request: UploadFinalizeRequest,
    db: Session = Depends(get_db),
):
    """
    Step 3: Finalize track upload after successful S3 upload
    Creates Track record in database

    TODO: Add JWT authentication to get current user
    TODO: Trigger async audio processing (duration, BPM, waveform)
    """
    # TODO: Get current user from JWT token
    # For now, use first user in database
    user = db.query(UserProfile).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please create a user first.")

    # TODO: Verify upload_id is valid and not expired
    # TODO: Verify S3 file exists

    # Create track record
    new_track = Track(
        owner_user_id=user.id,
        title=request.title,
        description=request.description,
        artist_name=request.artist_name,
        album_art_url=request.album_art_url,
        s3_key=request.s3_key,
        file_size=request.file_size,
        status=TrackStatus.PROCESSING,  # Will be updated by async processing
        is_public="true",  # Default to public
    )

    db.add(new_track)
    db.commit()
    db.refresh(new_track)

    # TODO: Trigger Celery task for audio processing
    # process_audio_task.delay(new_track.id)

    # Update user track count
    user.track_count = str(int(user.track_count) + 1)
    db.commit()

    return new_track


@router.patch("/{track_id}", response_model=TrackResponse)
async def update_track(
    track_id: int,
    update_data: TrackUpdate,
    db: Session = Depends(get_db),
):
    """
    Update track metadata

    TODO: Add JWT authentication
    TODO: Verify user owns this track
    """
    track = db.query(Track).filter(
        Track.id == track_id,
        Track.is_active == True
    ).first()

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    # TODO: Verify ownership
    # if track.owner_user_id != current_user.id:
    #     raise HTTPException(status_code=403, detail="Not authorized to update this track")

    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(track, field, value)

    db.commit()
    db.refresh(track)

    return track


@router.delete("/{track_id}")
async def delete_track(
    track_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete track (soft delete)

    TODO: Add JWT authentication
    TODO: Verify user owns this track
    """
    track = db.query(Track).filter(
        Track.id == track_id,
        Track.is_active == True
    ).first()

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    # TODO: Verify ownership
    # if track.owner_user_id != current_user.id:
    #     raise HTTPException(status_code=403, detail="Not authorized to delete this track")

    # Soft delete
    track.is_active = False

    # Update user track count
    user = db.query(UserProfile).filter(UserProfile.id == track.owner_user_id).first()
    if user:
        user.track_count = str(max(0, int(user.track_count) - 1))

    db.commit()

    return {"message": "Track deleted successfully", "track_id": track_id}
