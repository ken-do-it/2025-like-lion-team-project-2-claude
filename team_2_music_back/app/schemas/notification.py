# -*- coding: utf-8 -*-
"""
Notification Schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# Notification types enum (for reference)
# LIKE = "like"
# COMMENT = "comment"
# FOLLOW = "follow"
# TRACK_UPLOAD = "track_upload"  # When someone you follow uploads a track
# PLAYLIST_ADD = "playlist_add"  # When someone adds your track to a playlist


# Notification create request
class NotificationCreate(BaseModel):
    """Create notification"""
    user_id: int = Field(..., gt=0, description="User who receives the notification")
    type: str = Field(..., min_length=1, max_length=50, description="Notification type (like, comment, follow, etc.)")
    actor_user_id: Optional[int] = Field(None, gt=0, description="User who triggered the notification")
    target_type: Optional[str] = Field(None, max_length=50, description="Target type (track, comment, playlist)")
    target_id: Optional[int] = Field(None, gt=0, description="Target ID")
    message: str = Field(..., min_length=1, description="Notification message")


# Notification response
class NotificationResponse(BaseModel):
    """Notification response"""
    id: int
    user_id: int
    type: str
    actor_user_id: Optional[int] = None
    target_type: Optional[str] = None
    target_id: Optional[int] = None
    message: str
    is_read: bool
    read_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Notification with actor info
class NotificationWithActor(NotificationResponse):
    """Notification with actor user information"""
    actor_username: Optional[str] = None
    actor_display_name: Optional[str] = None
    actor_profile_image: Optional[str] = None


# Notification list response
class NotificationListResponse(BaseModel):
    """List of notifications with pagination"""
    items: List[NotificationWithActor]
    total: int
    unread_count: int
    page: int
    page_size: int
    has_more: bool


# Mark as read request
class MarkAsReadRequest(BaseModel):
    """Mark notification(s) as read"""
    notification_ids: Optional[List[int]] = Field(None, description="Specific notification IDs to mark as read (if None, marks all as read)")


# Notification stats
class NotificationStats(BaseModel):
    """Notification statistics"""
    total_notifications: int
    unread_count: int
    read_count: int
    notification_types: dict  # {"like": 5, "comment": 3, "follow": 2}
