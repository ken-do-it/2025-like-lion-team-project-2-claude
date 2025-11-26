# -*- coding: utf-8 -*-
"""
Common Pydantic Schemas (Errors, Pagination, etc.)
"""
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class ErrorResponse(BaseModel):
    """Standard error response"""
    error_code: str
    message: str
    status_code: int
    timestamp: str = datetime.utcnow().isoformat()
    details: Optional[Any] = None


class SuccessResponse(BaseModel):
    """Standard success response"""
    message: str
    data: Optional[Any] = None


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = 1
    page_size: int = 20
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[str] = "desc"  # asc or desc


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    service: str
    version: str
    environment: str
    database: str
    redis: str
