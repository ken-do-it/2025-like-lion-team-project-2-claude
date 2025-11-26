# -*- coding: utf-8 -*-
"""
Pydantic Schemas (Request/Response models)
"""
from app.schemas.common import (
    ErrorResponse,
    SuccessResponse,
    PaginationParams,
    HealthCheckResponse
)
from app.schemas.user import (
    UserProfileBase,
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileResponse,
    UserProfileMinimal
)
from app.schemas.track import (
    TrackStatus,
    TrackBase,
    TrackCreate,
    TrackUpdate,
    TrackResponse,
    TrackMinimal,
    TrackListResponse
)

__all__ = [
    # Common
    "ErrorResponse",
    "SuccessResponse",
    "PaginationParams",
    "HealthCheckResponse",
    # User
    "UserProfileBase",
    "UserProfileCreate",
    "UserProfileUpdate",
    "UserProfileResponse",
    "UserProfileMinimal",
    # Track
    "TrackStatus",
    "TrackBase",
    "TrackCreate",
    "TrackUpdate",
    "TrackResponse",
    "TrackMinimal",
    "TrackListResponse",
]
