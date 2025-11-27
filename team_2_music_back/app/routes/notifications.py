# -*- coding: utf-8 -*-
"""
Notification API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.models.user import UserProfile
from app.models.notification import Notification
from app.schemas.notification import (
    NotificationCreate, NotificationResponse, NotificationWithActor,
    NotificationListResponse, MarkAsReadRequest, NotificationStats
)

router = APIRouter(prefix="/api/v1", tags=["notifications"])


# ============================================================================
# NOTIFICATION CRUD ENDPOINTS
# ============================================================================

@router.get("/notifications/me", response_model=NotificationListResponse)
async def get_my_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False, description="Show only unread notifications"),
    type_filter: Optional[str] = Query(None, description="Filter by notification type"),
    db: Session = Depends(get_db)
):
    """
    Get current user's notifications with pagination and filtering

    TODO: Add authentication to get current user
    """
    # TODO: Get current user from JWT token
    current_user = db.query(UserProfile).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")

    # Build query
    query = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_active == True
    )

    # Apply filters
    if unread_only:
        query = query.filter(Notification.is_read == False)

    if type_filter:
        query = query.filter(Notification.type == type_filter)

    # Get total and unread counts
    total = query.count()
    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_active == True,
        Notification.is_read == False
    ).count()

    # Get paginated results ordered by created_at desc
    notifications = query.order_by(desc(Notification.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    # Join with actor user info
    items = []
    for notif in notifications:
        actor_info = None
        if notif.actor_user_id:
            actor_info = db.query(UserProfile).filter(UserProfile.id == notif.actor_user_id).first()

        items.append(NotificationWithActor(
            id=notif.id,
            user_id=notif.user_id,
            type=notif.type,
            actor_user_id=notif.actor_user_id,
            target_type=notif.target_type,
            target_id=notif.target_id,
            message=notif.message,
            is_read=notif.is_read,
            read_at=notif.read_at,
            is_active=notif.is_active,
            created_at=notif.created_at,
            updated_at=notif.updated_at,
            actor_username=actor_info.username if actor_info else None,
            actor_display_name=actor_info.display_name if actor_info else None,
            actor_profile_image=actor_info.avatar_url if actor_info else None
        ))

    return NotificationListResponse(
        items=items,
        total=total,
        unread_count=unread_count,
        page=page,
        page_size=page_size,
        has_more=(page * page_size) < total
    )


@router.get("/notifications/{notification_id}", response_model=NotificationWithActor)
async def get_notification(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """
    Get specific notification by ID

    TODO: Add authentication and verify ownership
    """
    # TODO: Get current user from JWT token
    current_user = db.query(UserProfile).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")

    # Get notification
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.is_active == True
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    # TODO: Verify ownership
    # if notification.user_id != current_user.id:
    #     raise HTTPException(status_code=403, detail="Not authorized to view this notification")

    # Get actor info
    actor_info = None
    if notification.actor_user_id:
        actor_info = db.query(UserProfile).filter(UserProfile.id == notification.actor_user_id).first()

    return NotificationWithActor(
        id=notification.id,
        user_id=notification.user_id,
        type=notification.type,
        actor_user_id=notification.actor_user_id,
        target_type=notification.target_type,
        target_id=notification.target_id,
        message=notification.message,
        is_read=notification.is_read,
        read_at=notification.read_at,
        is_active=notification.is_active,
        created_at=notification.created_at,
        updated_at=notification.updated_at,
        actor_username=actor_info.username if actor_info else None,
        actor_display_name=actor_info.display_name if actor_info else None,
        actor_profile_image=actor_info.avatar_url if actor_info else None
    )


@router.post("/notifications/", response_model=NotificationResponse, status_code=201)
async def create_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a notification (mostly for testing - usually created automatically)

    TODO: Add authentication - only admins or system can create notifications manually
    """
    # Verify target user exists
    target_user = db.query(UserProfile).filter(UserProfile.id == notification_data.user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found")

    # Verify actor user exists (if provided)
    if notification_data.actor_user_id:
        actor_user = db.query(UserProfile).filter(UserProfile.id == notification_data.actor_user_id).first()
        if not actor_user:
            raise HTTPException(status_code=404, detail="Actor user not found")

    # Create notification
    new_notification = Notification(
        user_id=notification_data.user_id,
        type=notification_data.type,
        actor_user_id=notification_data.actor_user_id,
        target_type=notification_data.target_type,
        target_id=notification_data.target_id,
        message=notification_data.message,
        is_read=False
    )

    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)

    return new_notification


@router.patch("/notifications/mark-read")
async def mark_notifications_as_read(
    mark_data: MarkAsReadRequest,
    db: Session = Depends(get_db)
):
    """
    Mark notification(s) as read

    If notification_ids is None or empty, marks all unread notifications as read
    Otherwise, marks only the specified notifications as read

    TODO: Add authentication to get current user
    """
    # TODO: Get current user from JWT token
    current_user = db.query(UserProfile).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")

    # Build query
    query = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_active == True,
        Notification.is_read == False
    )

    # Filter by specific IDs if provided
    if mark_data.notification_ids and len(mark_data.notification_ids) > 0:
        query = query.filter(Notification.id.in_(mark_data.notification_ids))

    # Update notifications
    notifications = query.all()
    if not notifications:
        return {"message": "No unread notifications found", "marked_count": 0}

    now = datetime.utcnow()
    for notif in notifications:
        notif.is_read = True
        notif.read_at = now

    db.commit()

    return {
        "message": f"Marked {len(notifications)} notification(s) as read",
        "marked_count": len(notifications)
    }


@router.delete("/notifications/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """
    Soft delete a notification

    TODO: Add authentication and verify ownership
    """
    # TODO: Get current user from JWT token
    current_user = db.query(UserProfile).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")

    # Get notification
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.is_active == True
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    # TODO: Verify ownership
    # if notification.user_id != current_user.id:
    #     raise HTTPException(status_code=403, detail="Not authorized to delete this notification")

    # Soft delete
    notification.is_active = False

    db.commit()

    return {"message": "Notification deleted successfully", "notification_id": notification_id}


# ============================================================================
# NOTIFICATION STATISTICS
# ============================================================================

@router.get("/notifications/stats/me", response_model=NotificationStats)
async def get_notification_stats(
    db: Session = Depends(get_db)
):
    """
    Get current user's notification statistics

    TODO: Add authentication to get current user
    """
    # TODO: Get current user from JWT token
    current_user = db.query(UserProfile).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")

    # Get total notifications
    total = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_active == True
    ).count()

    # Get unread count
    unread = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_active == True,
        Notification.is_read == False
    ).count()

    # Get read count
    read = total - unread

    # Get notification types breakdown
    type_counts = db.query(
        Notification.type,
        func.count(Notification.id).label("count")
    ).filter(
        Notification.user_id == current_user.id,
        Notification.is_active == True
    ).group_by(Notification.type).all()

    notification_types = {type_name: count for type_name, count in type_counts}

    return NotificationStats(
        total_notifications=total,
        unread_count=unread,
        read_count=read,
        notification_types=notification_types
    )
