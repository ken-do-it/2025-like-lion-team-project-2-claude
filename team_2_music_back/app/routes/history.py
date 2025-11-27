# -*- coding: utf-8 -*-
"""
Play History API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.user import UserProfile
from app.models.track import Track
from app.models.history import PlayHistory
from app.schemas.history import (
    PlayHistoryCreate, PlayHistoryResponse, PlayHistoryWithTrack,
    PlayHistoryListResponse, RecentlyPlayedTrack, RecentlyPlayedListResponse,
    UserPlayStats, TrackPlayStats
)

router = APIRouter(prefix="/api/v1", tags=["play-history"])


# ============================================================================
# PLAY HISTORY RECORDING
# ============================================================================

@router.post("/play-history", response_model=PlayHistoryResponse, status_code=201)
async def record_play(
    play_data: PlayHistoryCreate,
    db: Session = Depends(get_db)
):
    """
    Record a play event for a track

    This increments the track's play_count and updates trending_score

    TODO: Add authentication to get current user
    """
    # TODO: Get current user from JWT token
    current_user = db.query(UserProfile).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")

    # Verify track exists
    track = db.query(Track).filter(Track.id == play_data.track_id, Track.is_active == True).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    # Create play history record
    play_record = PlayHistory(
        user_id=current_user.id,
        track_id=play_data.track_id,
        listen_duration=play_data.listen_duration,
        completed=1 if play_data.completed else 0
    )

    db.add(play_record)

    # Increment track play count
    track.play_count = track.play_count + 1

    # Update trending score (simple formula: play_count * 0.5 + like_count * 1.5)
    # This can be made more sophisticated with time decay, etc.
    track.trending_score = (track.play_count * 0.5) + (track.like_count * 1.5)

    db.commit()
    db.refresh(play_record)

    return play_record


# ============================================================================
# PLAY HISTORY RETRIEVAL
# ============================================================================

@router.get("/play-history/me", response_model=PlayHistoryListResponse)
async def get_my_play_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    days: Optional[int] = Query(None, ge=1, description="Filter by days (e.g., 7 for last week)"),
    db: Session = Depends(get_db)
):
    """
    Get current user's play history with track information

    TODO: Add authentication to get current user
    """
    # TODO: Get current user from JWT token
    current_user = db.query(UserProfile).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")

    # Build query
    query = db.query(
        PlayHistory,
        Track.title.label("track_title"),
        Track.artist_name.label("track_artist"),
        Track.album_art_url.label("track_album_art"),
        Track.duration.label("track_duration")
    ).join(Track).filter(
        PlayHistory.user_id == current_user.id,
        PlayHistory.is_active == True,
        Track.is_active == True
    )

    # Filter by days if specified
    if days:
        since = datetime.utcnow() - timedelta(days=days)
        query = query.filter(PlayHistory.played_at >= since)

    # Get total count
    total = query.count()

    # Get paginated results ordered by played_at desc
    results = query.order_by(desc(PlayHistory.played_at)).offset((page - 1) * page_size).limit(page_size).all()

    # Convert to response format
    items = []
    for play_record, track_title, track_artist, track_album_art, track_duration in results:
        items.append(PlayHistoryWithTrack(
            id=play_record.id,
            user_id=play_record.user_id,
            track_id=play_record.track_id,
            played_at=play_record.played_at,
            listen_duration=play_record.listen_duration,
            completed=play_record.completed,
            is_active=play_record.is_active,
            created_at=play_record.created_at,
            updated_at=play_record.updated_at,
            track_title=track_title,
            track_artist=track_artist,
            track_album_art=track_album_art,
            track_duration=track_duration
        ))

    return PlayHistoryListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(page * page_size) < total
    )


@router.get("/play-history/recently-played", response_model=RecentlyPlayedListResponse)
async def get_recently_played(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    days: Optional[int] = Query(30, ge=1, description="Filter by days (default: 30)"),
    db: Session = Depends(get_db)
):
    """
    Get recently played unique tracks (one entry per track with last play time)

    TODO: Add authentication to get current user
    """
    # TODO: Get current user from JWT token
    current_user = db.query(UserProfile).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")

    # Filter by time period
    since = datetime.utcnow() - timedelta(days=days)

    # Subquery to get last played_at and play count per track
    subquery = db.query(
        PlayHistory.track_id,
        func.max(PlayHistory.played_at).label("last_played_at"),
        func.count(PlayHistory.id).label("play_count")
    ).filter(
        PlayHistory.user_id == current_user.id,
        PlayHistory.is_active == True,
        PlayHistory.played_at >= since
    ).group_by(PlayHistory.track_id).subquery()

    # Join with Track to get track details
    query = db.query(
        Track.id.label("track_id"),
        Track.title,
        Track.artist_name,
        Track.album_art_url,
        Track.duration,
        subquery.c.last_played_at,
        subquery.c.play_count
    ).join(subquery, Track.id == subquery.c.track_id).filter(
        Track.is_active == True
    )

    # Get total count
    total = query.count()

    # Get paginated results ordered by last_played_at desc
    results = query.order_by(desc(subquery.c.last_played_at)).offset((page - 1) * page_size).limit(page_size).all()

    # Convert to response format
    items = [
        RecentlyPlayedTrack(
            track_id=row.track_id,
            title=row.title,
            artist_name=row.artist_name,
            album_art_url=row.album_art_url,
            duration=row.duration,
            last_played_at=row.last_played_at,
            play_count=row.play_count
        )
        for row in results
    ]

    return RecentlyPlayedListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(page * page_size) < total
    )


# ============================================================================
# PLAY STATISTICS
# ============================================================================

@router.get("/play-history/stats/me", response_model=UserPlayStats)
async def get_my_play_stats(
    days: Optional[int] = Query(None, ge=1, description="Filter by days (optional)"),
    db: Session = Depends(get_db)
):
    """
    Get current user's play statistics

    TODO: Add authentication to get current user
    """
    # TODO: Get current user from JWT token
    current_user = db.query(UserProfile).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")

    # Build query
    query = db.query(PlayHistory).filter(
        PlayHistory.user_id == current_user.id,
        PlayHistory.is_active == True
    )

    # Filter by days if specified
    if days:
        since = datetime.utcnow() - timedelta(days=days)
        query = query.filter(PlayHistory.played_at >= since)

    # Calculate statistics
    total_plays = query.count()
    unique_tracks = query.with_entities(PlayHistory.track_id).distinct().count()

    # Total listen time (sum of listen_duration where not null)
    total_listen_time = db.query(func.sum(PlayHistory.listen_duration)).filter(
        PlayHistory.user_id == current_user.id,
        PlayHistory.is_active == True,
        PlayHistory.listen_duration.isnot(None)
    ).scalar() or 0

    # Completed plays
    completed_plays = query.filter(PlayHistory.completed == 1).count()

    # Most played track
    most_played = db.query(
        PlayHistory.track_id,
        Track.title,
        func.count(PlayHistory.id).label("play_count")
    ).join(Track).filter(
        PlayHistory.user_id == current_user.id,
        PlayHistory.is_active == True,
        Track.is_active == True
    ).group_by(PlayHistory.track_id, Track.title).order_by(desc(func.count(PlayHistory.id))).first()

    return UserPlayStats(
        user_id=current_user.id,
        total_plays=total_plays,
        unique_tracks_played=unique_tracks,
        total_listen_time=int(total_listen_time),
        completed_plays=completed_plays,
        most_played_track_id=most_played[0] if most_played else None,
        most_played_track_title=most_played[1] if most_played else None,
        most_played_track_count=most_played[2] if most_played else None
    )


@router.get("/tracks/{track_id}/play-stats", response_model=TrackPlayStats)
async def get_track_play_stats(
    track_id: int,
    days: Optional[int] = Query(None, ge=1, description="Filter by days (optional)"),
    db: Session = Depends(get_db)
):
    """
    Get play statistics for a specific track
    """
    # Verify track exists
    track = db.query(Track).filter(Track.id == track_id, Track.is_active == True).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    # Build query
    query = db.query(PlayHistory).filter(
        PlayHistory.track_id == track_id,
        PlayHistory.is_active == True
    )

    # Filter by days if specified
    if days:
        since = datetime.utcnow() - timedelta(days=days)
        query = query.filter(PlayHistory.played_at >= since)

    # Calculate statistics
    total_plays = query.count()
    unique_listeners = query.with_entities(PlayHistory.user_id).distinct().count()

    # Total listen time
    total_listen_time = db.query(func.sum(PlayHistory.listen_duration)).filter(
        PlayHistory.track_id == track_id,
        PlayHistory.is_active == True,
        PlayHistory.listen_duration.isnot(None)
    ).scalar() or 0

    # Completed plays
    completed_plays = query.filter(PlayHistory.completed == 1).count()

    # Average completion rate
    avg_completion_rate = (completed_plays / total_plays * 100) if total_plays > 0 else 0.0

    return TrackPlayStats(
        track_id=track_id,
        total_plays=total_plays,
        unique_listeners=unique_listeners,
        total_listen_time=int(total_listen_time),
        completed_plays=completed_plays,
        avg_completion_rate=round(avg_completion_rate, 2)
    )
