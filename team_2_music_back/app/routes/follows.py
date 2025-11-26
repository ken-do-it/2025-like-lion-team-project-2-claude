# -*- coding: utf-8 -*-
"""
Follow System API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.follow import Follow
from app.models.user import UserProfile
from app.schemas.follow import (
    FollowResponse,
    FollowStatusResponse,
    FollowersListResponse,
    FollowingListResponse,
    UserFollowInfo,
)


router = APIRouter(prefix="/api/v1/users", tags=["Follow System"])


@router.post("/{user_id}/follow", response_model=FollowResponse, status_code=201)
async def follow_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Follow a user

    TODO: Add JWT authentication to get current user
    TODO: Add rate limiting to prevent spam
    """
    # TODO: Get current user from JWT token
    # For now, use first user in database
    current_user = db.query(UserProfile).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")

    # Get target user
    target_user = db.query(UserProfile).filter(
        UserProfile.id == user_id,
        UserProfile.is_active == True
    ).first()

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Cannot follow yourself
    if current_user.id == target_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    # Check if already following
    existing_follow = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == target_user.id,
        Follow.is_active == True
    ).first()

    if existing_follow:
        raise HTTPException(status_code=400, detail="Already following this user")

    # Create follow relationship
    new_follow = Follow(
        follower_id=current_user.id,
        following_id=target_user.id
    )

    db.add(new_follow)

    # Update follower/following counts
    current_user.following_count = str(int(current_user.following_count) + 1)
    target_user.follower_count = str(int(target_user.follower_count) + 1)

    db.commit()
    db.refresh(new_follow)

    return new_follow


@router.delete("/{user_id}/follow")
async def unfollow_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Unfollow a user

    TODO: Add JWT authentication to get current user
    """
    # TODO: Get current user from JWT token
    current_user = db.query(UserProfile).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")

    # Get target user
    target_user = db.query(UserProfile).filter(
        UserProfile.id == user_id,
        UserProfile.is_active == True
    ).first()

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Find follow relationship
    follow = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == target_user.id,
        Follow.is_active == True
    ).first()

    if not follow:
        raise HTTPException(status_code=404, detail="Not following this user")

    # Soft delete the follow relationship
    follow.is_active = False

    # Update follower/following counts
    current_user.following_count = str(max(0, int(current_user.following_count) - 1))
    target_user.follower_count = str(max(0, int(target_user.follower_count) - 1))

    db.commit()

    return {"message": "Successfully unfollowed user", "user_id": user_id}


@router.get("/{user_id}/followers", response_model=FollowersListResponse)
async def get_followers(
    user_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    Get list of users who follow the specified user
    """
    # Get target user
    target_user = db.query(UserProfile).filter(
        UserProfile.id == user_id,
        UserProfile.is_active == True
    ).first()

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Query followers
    followers_query = db.query(UserProfile).join(
        Follow,
        Follow.follower_id == UserProfile.id
    ).filter(
        Follow.following_id == user_id,
        Follow.is_active == True,
        UserProfile.is_active == True
    )

    # Get total count
    total = followers_query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    followers = followers_query.order_by(Follow.created_at.desc()).offset(offset).limit(page_size).all()

    # Check if there are more pages
    has_more = (offset + page_size) < total

    return FollowersListResponse(
        items=followers,
        total=total,
        page=page,
        page_size=page_size,
        has_more=has_more
    )


@router.get("/{user_id}/following", response_model=FollowingListResponse)
async def get_following(
    user_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    Get list of users that the specified user follows
    """
    # Get target user
    target_user = db.query(UserProfile).filter(
        UserProfile.id == user_id,
        UserProfile.is_active == True
    ).first()

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Query following
    following_query = db.query(UserProfile).join(
        Follow,
        Follow.following_id == UserProfile.id
    ).filter(
        Follow.follower_id == user_id,
        Follow.is_active == True,
        UserProfile.is_active == True
    )

    # Get total count
    total = following_query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    following = following_query.order_by(Follow.created_at.desc()).offset(offset).limit(page_size).all()

    # Check if there are more pages
    has_more = (offset + page_size) < total

    return FollowingListResponse(
        items=following,
        total=total,
        page=page,
        page_size=page_size,
        has_more=has_more
    )


@router.get("/{user_id}/follow/status", response_model=FollowStatusResponse)
async def get_follow_status(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Check if current user follows the specified user

    TODO: Add JWT authentication to get current user
    """
    # TODO: Get current user from JWT token
    current_user = db.query(UserProfile).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")

    # Cannot check follow status for yourself
    if current_user.id == user_id:
        return FollowStatusResponse(is_following=False, follow_id=None)

    # Check if following
    follow = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == user_id,
        Follow.is_active == True
    ).first()

    if follow:
        return FollowStatusResponse(is_following=True, follow_id=follow.id)
    else:
        return FollowStatusResponse(is_following=False, follow_id=None)
