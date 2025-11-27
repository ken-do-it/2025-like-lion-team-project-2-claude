# -*- coding: utf-8 -*-
"""
Playlist API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.playlist import Playlist, PlaylistTrack
from app.models.track import Track
from app.models.user import UserProfile
from app.schemas.playlist import (
    PlaylistCreate,
    PlaylistUpdate,
    PlaylistResponse,
    PlaylistWithTracks,
    PlaylistsListResponse,
    PlaylistTrackInfo,
    AddTrackResponse,
)


router = APIRouter(prefix="/api/v1/playlists", tags=["Playlists"])


@router.post("/", response_model=PlaylistResponse, status_code=201)
async def create_playlist(
    playlist_data: PlaylistCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new playlist

    TODO: Add JWT authentication to get current user
    """
    # TODO: Get current user from JWT token
    current_user = db.query(UserProfile).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")

    # Create playlist
    new_playlist = Playlist(
        owner_user_id=current_user.id,
        title=playlist_data.title,
        description=playlist_data.description,
        is_public=playlist_data.is_public if playlist_data.is_public is not None else True,
        track_count=0
    )

    db.add(new_playlist)
    db.commit()
    db.refresh(new_playlist)

    return new_playlist


@router.get("/{playlist_id}", response_model=PlaylistWithTracks)
async def get_playlist(
    playlist_id: int,
    db: Session = Depends(get_db),
):
    """
    Get playlist details with tracks
    """
    playlist = db.query(Playlist).filter(
        Playlist.id == playlist_id,
        Playlist.is_active == True
    ).first()

    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    # TODO: Check if playlist is private and user has access

    # Get tracks in playlist
    playlist_tracks = db.query(Track).join(
        PlaylistTrack,
        PlaylistTrack.track_id == Track.id
    ).filter(
        PlaylistTrack.playlist_id == playlist_id,
        PlaylistTrack.is_active == True,
        Track.is_active == True
    ).order_by(PlaylistTrack.position.asc()).all()

    # Build response
    response_data = PlaylistResponse.model_validate(playlist)
    return PlaylistWithTracks(
        **response_data.model_dump(),
        tracks=[PlaylistTrackInfo.model_validate(track) for track in playlist_tracks]
    )


@router.get("/user/{user_id}", response_model=PlaylistsListResponse)
async def get_user_playlists(
    user_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    Get user's playlists
    """
    # Check if user exists
    user = db.query(UserProfile).filter(
        UserProfile.id == user_id,
        UserProfile.is_active == True
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Query playlists
    playlists_query = db.query(Playlist).filter(
        Playlist.owner_user_id == user_id,
        Playlist.is_active == True
    )

    # Get total count
    total = playlists_query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    playlists = playlists_query.order_by(Playlist.updated_at.desc()).offset(offset).limit(page_size).all()

    # Check if there are more pages
    has_more = (offset + page_size) < total

    return PlaylistsListResponse(
        items=playlists,
        total=total,
        page=page,
        page_size=page_size,
        has_more=has_more
    )


@router.patch("/{playlist_id}", response_model=PlaylistResponse)
async def update_playlist(
    playlist_id: int,
    update_data: PlaylistUpdate,
    db: Session = Depends(get_db),
):
    """
    Update playlist

    TODO: Add JWT authentication
    TODO: Verify user owns this playlist
    """
    playlist = db.query(Playlist).filter(
        Playlist.id == playlist_id,
        Playlist.is_active == True
    ).first()

    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    # TODO: Verify ownership
    # if playlist.owner_user_id != current_user.id:
    #     raise HTTPException(status_code=403, detail="Not authorized to update this playlist")

    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(playlist, field, value)

    db.commit()
    db.refresh(playlist)

    return playlist


@router.delete("/{playlist_id}")
async def delete_playlist(
    playlist_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete playlist (soft delete)

    TODO: Add JWT authentication
    TODO: Verify user owns this playlist
    """
    playlist = db.query(Playlist).filter(
        Playlist.id == playlist_id,
        Playlist.is_active == True
    ).first()

    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    # TODO: Verify ownership
    # if playlist.owner_user_id != current_user.id:
    #     raise HTTPException(status_code=403, detail="Not authorized to delete this playlist")

    # Soft delete playlist
    playlist.is_active = False

    # Soft delete all playlist tracks
    playlist_tracks = db.query(PlaylistTrack).filter(
        PlaylistTrack.playlist_id == playlist_id
    ).all()

    for pt in playlist_tracks:
        pt.is_active = False

    db.commit()

    return {"message": "Playlist deleted successfully", "playlist_id": playlist_id}


# ============= PLAYLIST TRACK MANAGEMENT =============

@router.post("/{playlist_id}/tracks/{track_id}", response_model=AddTrackResponse)
async def add_track_to_playlist(
    playlist_id: int,
    track_id: int,
    db: Session = Depends(get_db),
):
    """
    Add a track to playlist

    TODO: Add JWT authentication
    TODO: Verify user owns this playlist
    """
    # Check if playlist exists
    playlist = db.query(Playlist).filter(
        Playlist.id == playlist_id,
        Playlist.is_active == True
    ).first()

    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    # Check if track exists
    track = db.query(Track).filter(
        Track.id == track_id,
        Track.is_active == True
    ).first()

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    # Check if track already in playlist
    existing = db.query(PlaylistTrack).filter(
        PlaylistTrack.playlist_id == playlist_id,
        PlaylistTrack.track_id == track_id,
        PlaylistTrack.is_active == True
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Track already in playlist")

    # Get next position
    max_position = db.query(PlaylistTrack).filter(
        PlaylistTrack.playlist_id == playlist_id,
        PlaylistTrack.is_active == True
    ).count()

    position = max_position

    # Add track to playlist
    playlist_track = PlaylistTrack(
        playlist_id=playlist_id,
        track_id=track_id,
        position=position
    )

    db.add(playlist_track)

    # Update playlist metadata
    playlist.track_count = playlist.track_count + 1

    db.commit()

    return AddTrackResponse(
        message="Track added to playlist successfully",
        playlist_id=playlist_id,
        track_id=track_id,
        position=position
    )


@router.delete("/{playlist_id}/tracks/{track_id}")
async def remove_track_from_playlist(
    playlist_id: int,
    track_id: int,
    db: Session = Depends(get_db),
):
    """
    Remove a track from playlist

    TODO: Add JWT authentication
    TODO: Verify user owns this playlist
    """
    # Check if playlist exists
    playlist = db.query(Playlist).filter(
        Playlist.id == playlist_id,
        Playlist.is_active == True
    ).first()

    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    # Find playlist track
    playlist_track = db.query(PlaylistTrack).filter(
        PlaylistTrack.playlist_id == playlist_id,
        PlaylistTrack.track_id == track_id,
        PlaylistTrack.is_active == True
    ).first()

    if not playlist_track:
        raise HTTPException(status_code=404, detail="Track not in playlist")

    # Soft delete
    playlist_track.is_active = False

    # Update playlist metadata
    playlist.track_count = max(0, playlist.track_count - 1)

    db.commit()

    return {"message": "Track removed from playlist successfully", "playlist_id": playlist_id, "track_id": track_id}


@router.get("/{playlist_id}/tracks", response_model=PlaylistsListResponse)
async def get_playlist_tracks(
    playlist_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    Get tracks in a playlist with pagination
    """
    # Check if playlist exists
    playlist = db.query(Playlist).filter(
        Playlist.id == playlist_id,
        Playlist.is_active == True
    ).first()

    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    # Query tracks
    tracks_query = db.query(Track).join(
        PlaylistTrack,
        PlaylistTrack.track_id == Track.id
    ).filter(
        PlaylistTrack.playlist_id == playlist_id,
        PlaylistTrack.is_active == True,
        Track.is_active == True
    )

    # Get total count
    total = tracks_query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    tracks = tracks_query.order_by(PlaylistTrack.position.asc()).offset(offset).limit(page_size).all()

    # Check if there are more pages
    has_more = (offset + page_size) < total

    return PlaylistsListResponse(
        items=tracks,
        total=total,
        page=page,
        page_size=page_size,
        has_more=has_more
    )
