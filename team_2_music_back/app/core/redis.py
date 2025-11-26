# -*- coding: utf-8 -*-
"""
Redis connection and cache management
"""
import redis
from redis import Redis, ConnectionPool
from typing import Optional, Any
import json
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Redis client wrapper with caching utilities
    """

    def __init__(self):
        """
        Initialize Redis connection pool
        """
        self.pool: Optional[ConnectionPool] = None
        self.client: Optional[Redis] = None

    def connect(self) -> None:
        """
        Create Redis connection pool and client
        """
        try:
            self.pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                max_connections=10
            )
            self.client = Redis(connection_pool=self.pool)

            # Test connection
            self.client.ping()
            logger.info("Redis connection established")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            # In development, we can continue without Redis
            if not settings.is_production:
                logger.warning("Continuing without Redis cache (development mode)")
                self.client = None
            else:
                raise

    def disconnect(self) -> None:
        """
        Close Redis connection
        """
        try:
            if self.client:
                self.client.close()
            if self.pool:
                self.pool.disconnect()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")

    def check_connection(self) -> bool:
        """
        Check if Redis connection is working

        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            if self.client:
                self.client.ping()
                logger.info("Redis connection check: OK")
                return True
            return False
        except Exception as e:
            logger.error(f"Redis connection check failed: {e}")
            return False

    # Cache operations

    def get(self, key: str) -> Optional[str]:
        """
        Get value from Redis

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        if not self.client:
            return None

        try:
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None

    def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """
        Set value in Redis with optional TTL

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (optional)

        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            return False

        try:
            if ttl:
                return self.client.setex(key, ttl, value)
            else:
                return self.client.set(key, value)
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete key from Redis

        Args:
            key: Cache key to delete

        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            return False

        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return False

    def get_json(self, key: str) -> Optional[Any]:
        """
        Get JSON value from Redis

        Args:
            key: Cache key

        Returns:
            Deserialized JSON value or None
        """
        value = self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error for key {key}: {e}")
        return None

    def set_json(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set JSON value in Redis

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (optional)

        Returns:
            True if successful, False otherwise
        """
        try:
            json_value = json.dumps(value)
            return self.set(key, json_value, ttl)
        except (TypeError, ValueError) as e:
            logger.error(f"JSON encode error for key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """
        Check if key exists in Redis

        Args:
            key: Cache key

        Returns:
            True if key exists, False otherwise
        """
        if not self.client:
            return False

        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS error for key {key}: {e}")
            return False


# Global Redis client instance
redis_client = RedisClient()


def get_redis() -> RedisClient:
    """
    Get Redis client instance

    Returns:
        RedisClient instance
    """
    return redis_client
