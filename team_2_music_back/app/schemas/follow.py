# -*- coding: utf-8 -*-
"""
Follow System Pydantic Schemas
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# Follow response
class FollowResponse(BaseModel):
    """Follow relationship response"""
    id: int
    follower_id: int
    following_id: int
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# Follow status check response
class FollowStatusResponse(BaseModel):
    """Check if current user follows target user"""
    is_following: bool
    follow_id: Optional[int] = None


# User minimal info for follower/following lists
class UserFollowInfo(BaseModel):
    """Minimal user info for follow lists"""
    id: int
    user_id: str
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    follower_count: str
    following_count: str
    track_count: str

    class Config:
        from_attributes = True


# Followers list response with pagination
class FollowersListResponse(BaseModel):
    """Paginated followers list"""
    items: List[UserFollowInfo]
    total: int
    page: int
    page_size: int
    has_more: bool


# Following list response with pagination
class FollowingListResponse(BaseModel):
    """Paginated following list"""
    items: List[UserFollowInfo]
    total: int
    page: int
    page_size: int
    has_more: bool
