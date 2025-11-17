"""
Transcript Cache Manager
Centralized caching logic for transcript results

This module provides a unified interface for caching transcription results
across both YouTube videos and uploaded video files, using Redis as a hot cache
with automatic LRU eviction and version control for schema changes.
"""

import hashlib
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import redis

logger = logging.getLogger(__name__)

# Cache configuration
CACHE_VERSION = "v1"  # Increment on schema changes
CACHE_TTL = 604800  # 7 days in seconds (168 hours)


class TranscriptCacheManager:
    """
    Manages transcript caching with Redis hot cache

    Features:
    - Version-controlled cache keys for schema migration
    - Separate key generation for YouTube vs uploaded videos
    - Quick video hashing for uploaded files
    - Automatic TTL management
    - Graceful error handling (never blocks transcription)
    """

    def __init__(self, redis_client: redis.Redis):
        """
        Initialize cache manager

        Args:
            redis_client: Connected Redis client instance
        """
        self.redis = redis_client
        self.version = CACHE_VERSION
        self.default_ttl = CACHE_TTL

    def generate_youtube_key(self, video_id: str, language: str) -> str:
        """
        Generate cache key for YouTube videos

        Args:
            video_id: YouTube video ID (e.g., "dQw4w9WgXcQ")
            language: Language code (e.g., "ko", "en")

        Returns:
            Cache key string (e.g., "transcript:v1:youtube:dQw4w9WgXcQ:ko")
        """
        return f"transcript:{self.version}:youtube:{video_id}:{language}"

    def generate_upload_key(
        self,
        video_hash: str,
        language: str,
        min_speakers: Optional[int] = None,
        max_speakers: Optional[int] = None
    ) -> str:
        """
        Generate cache key for uploaded videos

        Args:
            video_hash: SHA256 hash of video file
            language: Language code (e.g., "ko", "en")
            min_speakers: Minimum number of speakers for diarization
            max_speakers: Maximum number of speakers for diarization

        Returns:
            Cache key string (e.g., "transcript:v1:upload:{hash}:ko:2:5")

        Note:
            Speaker parameters are included in key because they affect
            diarization results. Same video with different speaker configs
            = different transcripts.
        """
        if min_speakers is not None and max_speakers is not None:
            speakers = f"{min_speakers}:{max_speakers}"
        else:
            speakers = "auto"

        return f"transcript:{self.version}:upload:{video_hash}:{language}:{speakers}"

    def calculate_video_hash(self, file_path: str, quick: bool = True) -> str:
        """
        Calculate SHA256 hash of video file

        Args:
            file_path: Path to video file
            quick: If True, only hash first 10MB + last 10MB (faster)
                  If False, hash entire file (slower but more accurate)

        Returns:
            Hexadecimal hash string

        Performance:
            - Quick mode: ~100ms for 2GB file
            - Full mode: ~5-10 seconds for 2GB file

        Note:
            Quick mode provides sufficient uniqueness for cache lookup
            while maintaining good performance for large video files.
        """
        hash_sha256 = hashlib.sha256()

        try:
            if quick:
                with open(file_path, 'rb') as f:
                    # Read first 10MB
                    chunk = f.read(10 * 1024 * 1024)
                    hash_sha256.update(chunk)

                    # Try to read last 10MB
                    try:
                        f.seek(-10 * 1024 * 1024, 2)  # Seek from end
                        chunk = f.read()
                        hash_sha256.update(chunk)
                    except OSError:
                        # File smaller than 20MB, already fully hashed
                        logger.debug("Video file smaller than 20MB, using partial hash")
            else:
                # Full file hash (slow for large files)
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_sha256.update(chunk)

            return hash_sha256.hexdigest()

        except Exception as e:
            logger.error(f"Failed to calculate video hash: {e}")
            # Return timestamp-based fallback (won't match cache, but won't break)
            return hashlib.sha256(str(datetime.now()).encode()).hexdigest()

    def get(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached transcript from Redis

        Args:
            cache_key: Cache key to lookup

        Returns:
            Cached data dictionary if found, None otherwise

        Note:
            Logs cache hits and misses for monitoring.
            Returns None on any error (graceful degradation).
        """
        try:
            cached = self.redis.get(cache_key)
            if cached:
                logger.info(f"Cache HIT: {cache_key}")
                data = json.loads(cached)

                # Validate cache version
                if data.get("cache_version") != self.version:
                    logger.warning(f"Cache version mismatch for {cache_key}, treating as miss")
                    return None

                return data
            else:
                logger.info(f"Cache MISS: {cache_key}")
                return None

        except json.JSONDecodeError as e:
            logger.error(f"Cache data corrupted for {cache_key}: {e}")
            # Delete corrupted cache entry
            self.delete(cache_key)
            return None

        except Exception as e:
            logger.error(f"Cache read error for {cache_key}: {e}")
            return None

    def set(self, cache_key: str, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Store transcript in Redis cache

        Args:
            cache_key: Cache key to store under
            data: Transcript data dictionary
            ttl: Time-to-live in seconds (default: CACHE_TTL = 7 days)

        Returns:
            True if successfully cached, False otherwise

        Note:
            Automatically adds cache metadata (version, timestamp).
            Never raises exceptions (graceful degradation).
        """
        if ttl is None:
            ttl = self.default_ttl

        try:
            # Add cache metadata
            data["cache_version"] = self.version
            data["cached_at"] = datetime.now().isoformat()

            # Store in Redis with TTL
            self.redis.setex(cache_key, ttl, json.dumps(data))
            logger.info(f"Cache SET: {cache_key} (TTL: {ttl}s)")
            return True

        except Exception as e:
            logger.error(f"Cache write error for {cache_key}: {e}")
            return False

    def delete(self, cache_key: str) -> bool:
        """
        Delete cached transcript

        Args:
            cache_key: Cache key to delete

        Returns:
            True if key existed and was deleted, False otherwise
        """
        try:
            deleted = self.redis.delete(cache_key)
            logger.info(f"Cache DELETE: {cache_key} (existed: {bool(deleted)})")
            return bool(deleted)

        except Exception as e:
            logger.error(f"Cache delete error for {cache_key}: {e}")
            return False

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Delete all cache keys matching pattern

        Args:
            pattern: Redis key pattern (e.g., "transcript:v1:youtube:*")

        Returns:
            Number of keys deleted

        Warning:
            This can be slow on large keyspaces. Use sparingly.
        """
        try:
            keys = self.redis.keys(pattern)
            if keys:
                deleted = self.redis.delete(*keys)
                logger.info(f"Cache INVALIDATE: {pattern} ({deleted} keys)")
                return deleted
            return 0

        except Exception as e:
            logger.error(f"Cache invalidate error for pattern {pattern}: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dictionary with cache metrics:
            - total_keys: Number of cached transcripts
            - memory_used: Redis memory usage in bytes
            - hit_rate: Cache hit rate (if available)
        """
        try:
            info = self.redis.info('memory')

            # Count transcript cache keys
            keys = self.redis.keys(f"transcript:{self.version}:*")

            return {
                "total_keys": len(keys),
                "memory_used_bytes": info.get('used_memory', 0),
                "memory_human": info.get('used_memory_human', 'N/A'),
                "cache_version": self.version,
                "default_ttl_seconds": self.default_ttl
            }

        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"error": str(e)}
