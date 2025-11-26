# -*- coding: utf-8 -*-
"""
Interaction (Like, Comment) Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# Like schemas
class LikeResponse(BaseModel):
    """Like response"""
    id: int
    user_id: int
    track_id: int
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class LikeUserInfo(BaseModel):
    """User info for likes list"""
    id: int
    user_id: str
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]

    class Config:
        from_attributes = True


class LikesListResponse(BaseModel):
    """Paginated likes list"""
    items: List[LikeUserInfo]
    total: int
    page: int
    page_size: int
    has_more: bool


# Comment schemas
class CommentBase(BaseModel):
    """Base comment fields"""
    text: str = Field(..., min_length=1, max_length=1000, description="Comment text")


class CommentCreate(CommentBase):
    """Create comment"""
    pass


class CommentUpdate(BaseModel):
    """Update comment (partial)"""
    text: Optional[str] = Field(None, min_length=1, max_length=1000)


class CommentUserInfo(BaseModel):
    """User info for comment author"""
    id: int
    user_id: str
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]

    class Config:
        from_attributes = True


class CommentResponse(CommentBase):
    """Comment response with user info"""
    id: int
    track_id: int
    user_id: int
    user: Optional[CommentUserInfo] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class CommentsListResponse(BaseModel):
    """Paginated comments list"""
    items: List[CommentResponse]
    total: int
    page: int
    page_size: int
    has_more: bool
