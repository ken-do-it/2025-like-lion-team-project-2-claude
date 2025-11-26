# -*- coding: utf-8 -*-
"""
Database Models
Import all models here for Alembic to detect them
"""
from app.models.base import BaseModel
from app.models.user import UserProfile
from app.models.track import Track, TrackStatus
from app.models.interaction import Like, Comment
from app.models.follow import Follow
from app.models.playlist import Playlist, PlaylistTrack
from app.models.tag import Tag, TrackTag
from app.models.history import PlayHistory
from app.models.notification import Notification

__all__ = [
    "BaseModel",
    "UserProfile",
    "Track",
    "TrackStatus",
    "Like",
    "Comment",
    "Follow",
    "Playlist",
    "PlaylistTrack",
    "Tag",
    "TrackTag",
    "PlayHistory",
    "Notification",
]
