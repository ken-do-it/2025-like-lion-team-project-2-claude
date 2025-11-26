# -*- coding: utf-8 -*-
"""
Interaction API Routes (Like, Comment)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.interaction import Like, Comment
from app.models.track import Track
from app.models.user import UserProfile
from app.schemas.interaction import (
    LikeResponse,
    LikesListResponse,
    LikeUserInfo,
    CommentCreate,
    CommentUpdate,
    CommentResponse,
    CommentsListResponse,
    CommentUserInfo,
)


router = APIRouter(prefix="/api/v1/tracks", tags=["Interactions"])


# ============= LIKE ENDPOINTS =============

@router.post("/{track_id}/like", response_model=LikeResponse, status_code=201)
async def like_track(
    track_id: int,
    db: Session = Depends(get_db),
):
    """
    Like a track

    TODO: Add JWT authentication to get current user
    """
    # TODO: Get current user from JWT token
    current_user = db.query(UserProfile).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")

    # Check if track exists
    track = db.query(Track).filter(
        Track.id == track_id,
        Track.is_active == True
    ).first()

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    # Check if already liked
    existing_like = db.query(Like).filter(
        Like.user_id == current_user.id,
        Like.track_id == track_id,
        Like.is_active == True
    ).first()

    if existing_like:
        raise HTTPException(status_code=400, detail="Already liked this track")

    # Create like
    new_like = Like(
        user_id=current_user.id,
        track_id=track_id
    )

    db.add(new_like)

    # Update track like_count
    track.like_count = track.like_count + 1

    db.commit()
    db.refresh(new_like)

    return new_like


@router.delete("/{track_id}/like")
async def unlike_track(
    track_id: int,
    db: Session = Depends(get_db),
):
    """
    Unlike a track

    TODO: Add JWT authentication to get current user
    """
    # TODO: Get current user from JWT token
    current_user = db.query(UserProfile).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")

    # Check if track exists
    track = db.query(Track).filter(
        Track.id == track_id,
        Track.is_active == True
    ).first()

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    # Find like
    like = db.query(Like).filter(
        Like.user_id == current_user.id,
        Like.track_id == track_id,
        Like.is_active == True
    ).first()

    if not like:
        raise HTTPException(status_code=404, detail="Not liked this track")

    # Soft delete
    like.is_active = False

    # Update track like_count
    track.like_count = max(0, track.like_count - 1)

    db.commit()

    return {"message": "Successfully unliked track", "track_id": track_id}


@router.get("/{track_id}/likes", response_model=LikesListResponse)
async def get_track_likes(
    track_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    Get list of users who liked this track
    """
    # Check if track exists
    track = db.query(Track).filter(
        Track.id == track_id,
        Track.is_active == True
    ).first()

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    # Query users who liked this track
    likes_query = db.query(UserProfile).join(
        Like,
        Like.user_id == UserProfile.id
    ).filter(
        Like.track_id == track_id,
        Like.is_active == True,
        UserProfile.is_active == True
    )

    # Get total count
    total = likes_query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    users = likes_query.order_by(Like.created_at.desc()).offset(offset).limit(page_size).all()

    # Check if there are more pages
    has_more = (offset + page_size) < total

    return LikesListResponse(
        items=users,
        total=total,
        page=page,
        page_size=page_size,
        has_more=has_more
    )


# ============= COMMENT ENDPOINTS =============

@router.post("/{track_id}/comments", response_model=CommentResponse, status_code=201)
async def create_comment(
    track_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
):
    """
    Add a comment to a track

    TODO: Add JWT authentication to get current user
    """
    # TODO: Get current user from JWT token
    current_user = db.query(UserProfile).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")

    # Check if track exists
    track = db.query(Track).filter(
        Track.id == track_id,
        Track.is_active == True
    ).first()

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    # Create comment
    new_comment = Comment(
        user_id=current_user.id,
        track_id=track_id,
        text=comment_data.text
    )

    db.add(new_comment)

    # Update track comment_count
    track.comment_count = track.comment_count + 1

    db.commit()
    db.refresh(new_comment)

    # Load user relationship
    comment_response = CommentResponse(
        id=new_comment.id,
        track_id=new_comment.track_id,
        user_id=new_comment.user_id,
        text=new_comment.text,
        created_at=new_comment.created_at,
        updated_at=new_comment.updated_at,
        is_active=new_comment.is_active,
        user=CommentUserInfo(
            id=current_user.id,
            user_id=current_user.user_id,
            username=current_user.username,
            display_name=current_user.display_name,
            avatar_url=current_user.avatar_url
        )
    )

    return comment_response


@router.get("/{track_id}/comments", response_model=CommentsListResponse)
async def get_track_comments(
    track_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    Get comments on a track
    """
    # Check if track exists
    track = db.query(Track).filter(
        Track.id == track_id,
        Track.is_active == True
    ).first()

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    # Query comments
    comments_query = db.query(Comment).filter(
        Comment.track_id == track_id,
        Comment.is_active == True
    )

    # Get total count
    total = comments_query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    comments = comments_query.order_by(Comment.created_at.desc()).offset(offset).limit(page_size).all()

    # Build response with user info
    comment_responses = []
    for comment in comments:
        user = db.query(UserProfile).filter(UserProfile.id == comment.user_id).first()
        comment_responses.append(
            CommentResponse(
                id=comment.id,
                track_id=comment.track_id,
                user_id=comment.user_id,
                text=comment.text,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
                is_active=comment.is_active,
                user=CommentUserInfo(
                    id=user.id,
                    user_id=user.user_id,
                    username=user.username,
                    display_name=user.display_name,
                    avatar_url=user.avatar_url
                ) if user else None
            )
        )

    # Check if there are more pages
    has_more = (offset + page_size) < total

    return CommentsListResponse(
        items=comment_responses,
        total=total,
        page=page,
        page_size=page_size,
        has_more=has_more
    )


@router.patch("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    update_data: CommentUpdate,
    db: Session = Depends(get_db),
):
    """
    Update a comment

    TODO: Add JWT authentication to get current user
    TODO: Verify user owns this comment
    """
    # Find comment
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.is_active == True
    ).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # TODO: Verify ownership
    # if comment.user_id != current_user.id:
    #     raise HTTPException(status_code=403, detail="Not authorized to update this comment")

    # Update content
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(comment, field, value)

    db.commit()
    db.refresh(comment)

    # Load user relationship
    user = db.query(UserProfile).filter(UserProfile.id == comment.user_id).first()

    return CommentResponse(
        id=comment.id,
        track_id=comment.track_id,
        user_id=comment.user_id,
        text=comment.text,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        is_active=comment.is_active,
        user=CommentUserInfo(
            id=user.id,
            user_id=user.user_id,
            username=user.username,
            display_name=user.display_name,
            avatar_url=user.avatar_url
        ) if user else None
    )


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete a comment

    TODO: Add JWT authentication to get current user
    TODO: Verify user owns this comment
    """
    # Find comment
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.is_active == True
    ).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # TODO: Verify ownership
    # if comment.user_id != current_user.id:
    #     raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    # Soft delete
    comment.is_active = False

    # Update track comment_count
    track = db.query(Track).filter(Track.id == comment.track_id).first()
    if track:
        track.comment_count = max(0, track.comment_count - 1)

    db.commit()

    return {"message": "Comment deleted successfully", "comment_id": comment_id}
