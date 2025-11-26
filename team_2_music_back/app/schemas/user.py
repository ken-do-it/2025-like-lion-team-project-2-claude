# -*- coding: utf-8 -*-
"""
User Profile Pydantic Schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# Base schema with common fields
class UserProfileBase(BaseModel):
    """Base user profile fields"""
    username: str = Field(..., min_length=3, max_length=100, description="Unique username")
    email: EmailStr = Field(..., description="User email address")
    display_name: Optional[str] = Field(None, max_length=100, description="Display name")
    bio: Optional[str] = Field(None, max_length=500, description="User bio")
    avatar_url: Optional[str] = Field(None, max_length=500, description="Avatar image URL")


# Schema for creating a new user profile
class UserProfileCreate(UserProfileBase):
    """Create user profile (from Auth Server data)"""
    user_id: str = Field(..., description="External user ID from Auth Server")


# Schema for updating user profile
class UserProfileUpdate(BaseModel):
    """Update user profile (partial update allowed)"""
    display_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=500)


# Schema for response
class UserProfileResponse(UserProfileBase):
    """User profile response"""
    id: int
    user_id: str
    follower_count: str
    following_count: str
    track_count: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy models


# Minimal user info for nested responses
class UserProfileMinimal(BaseModel):
    """Minimal user info (for nested objects)"""
    id: int
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]

    class Config:
        from_attributes = True
