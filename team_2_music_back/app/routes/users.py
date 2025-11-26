# -*- coding: utf-8 -*-
"""
User Profile API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.user import UserProfile
from app.schemas.user import (
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileResponse
)

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    db: Session = Depends(get_db)
):
    """
    Get current user's profile
    TODO: Add JWT authentication to get user_id from token
    For now, returns first user for testing
    """
    # TODO: Get user_id from JWT token
    # user_id = current_user.user_id

    # For testing: get first user
    user = db.query(UserProfile).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )

    return user


@router.patch("/me", response_model=UserProfileResponse)
async def update_current_user_profile(
    update_data: UserProfileUpdate,
    db: Session = Depends(get_db)
):
    """
    Update current user's profile
    TODO: Add JWT authentication
    """
    # TODO: Get user_id from JWT token

    # For testing: get first user
    user = db.query(UserProfile).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )

    # Update only provided fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user_profile_by_id(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get user profile by ID (public endpoint)
    """
    user = db.query(UserProfile).filter(
        UserProfile.id == user_id,
        UserProfile.is_active == True
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    return user


@router.post("/", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_user_profile(
    user_data: UserProfileCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new user profile
    Usually called after user registers via Auth Server
    """
    # Check if user already exists
    existing_user = db.query(UserProfile).filter(
        (UserProfile.user_id == user_data.user_id) |
        (UserProfile.username == user_data.username) |
        (UserProfile.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this user_id, username, or email already exists"
        )

    # Create new user
    new_user = UserProfile(**user_data.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
