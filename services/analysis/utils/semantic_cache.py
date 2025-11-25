"""
Semantic Cache Manager for Analysis Service
Provides deterministic caching of LLM classification results
"""

import hashlib
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import redis

logger = logging.getLogger(__name__)

class SemanticCache:
    """
    Semantic caching system for LLM classification results

    Ensures consistency by caching the first (majority-voted) result
    and returning it for subsequent identical utterances.

    Cache Key Format: semantic:{version}:{classifier_type}:{content_hash}
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.cache_version = "v1"
        self.ttl = 2592000  # 30 days in seconds

    def generate_key(self, utterance_text: str, classifier_type: str, context: Optional[Dict] = None) -> str:
        """
        Generate a cache key from utterance text and classifier type

        Args:
            utterance_text: The text to classify
            classifier_type: Type of classifier ('stage', 'context', 'level')
            context: Optional context data that affects classification

        Returns:
            Cache key in format: semantic:v1:{hash}
        """
        # Include context in hash if provided (e.g., lesson stage for context classification)
        content = f"{classifier_type}:{utterance_text}"
        if context:
            context_str = json.dumps(context, sort_keys=True)
            content += f":{context_str}"

        # Generate SHA256 hash
        hash_key = hashlib.sha256(content.encode('utf-8')).hexdigest()

        return f"semantic:{self.cache_version}:{classifier_type}:{hash_key}"

    def get(self, utterance_text: str, classifier_type: str, context: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached classification result

        Args:
            utterance_text: The text to classify
            classifier_type: Type of classifier
            context: Optional context data

        Returns:
            Cached result dictionary or None if cache miss
        """
        try:
            key = self.generate_key(utterance_text, classifier_type, context)
            cached_data = self.redis.get(key)

            if cached_data:
                result = json.loads(cached_data)
                logger.info(f"✓ Semantic cache HIT ({classifier_type}): {key[:60]}...")

                # Add cache hit metadata
                result['_cache_metadata'] = {
                    'cache_hit': True,
                    'cache_key': key,
                    'retrieved_at': datetime.now().isoformat()
                }

                return result

            logger.info(f"✗ Semantic cache MISS ({classifier_type}): {key[:60]}...")
            return None

        except Exception as e:
            logger.error(f"Semantic cache retrieval error: {str(e)}")
            return None

    def set(
        self,
        utterance_text: str,
        classifier_type: str,
        result: Dict[str, Any],
        context: Optional[Dict] = None,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Store classification result in cache

        Args:
            utterance_text: The text that was classified
            classifier_type: Type of classifier
            result: Classification result to cache
            context: Optional context data
            ttl: Optional TTL in seconds (default: 30 days)

        Returns:
            True if successful, False otherwise
        """
        try:
            key = self.generate_key(utterance_text, classifier_type, context)

            # Add cache metadata to result
            cache_data = {
                **result,
                '_cache_metadata': {
                    'cached_at': datetime.now().isoformat(),
                    'cache_version': self.cache_version,
                    'classifier_type': classifier_type,
                    'ttl_seconds': ttl or self.ttl
                }
            }

            # Store in Redis with TTL
            self.redis.setex(
                key,
                ttl or self.ttl,
                json.dumps(cache_data, ensure_ascii=False)
            )

            logger.info(f"✓ Cached result ({classifier_type}): {key[:60]}...")
            return True

        except Exception as e:
            logger.error(f"Semantic cache storage error: {str(e)}")
            return False

    def invalidate(self, utterance_text: str, classifier_type: str, context: Optional[Dict] = None) -> bool:
        """
        Delete a specific cache entry

        Args:
            utterance_text: The text to classify
            classifier_type: Type of classifier
            context: Optional context data

        Returns:
            True if deleted, False otherwise
        """
        try:
            key = self.generate_key(utterance_text, classifier_type, context)
            deleted = self.redis.delete(key)

            if deleted:
                logger.info(f"✓ Invalidated cache ({classifier_type}): {key[:60]}...")
                return True
            else:
                logger.warning(f"✗ Cache key not found ({classifier_type}): {key[:60]}...")
                return False

        except Exception as e:
            logger.error(f"Semantic cache invalidation error: {str(e)}")
            return False

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Delete all cache keys matching a pattern

        Args:
            pattern: Redis key pattern (e.g., 'semantic:v1:stage:*')

        Returns:
            Number of keys deleted
        """
        try:
            keys = self.redis.keys(pattern)
            if keys:
                deleted = self.redis.delete(*keys)
                logger.info(f"✓ Invalidated {deleted} cache entries matching: {pattern}")
                return deleted
            else:
                logger.info(f"✗ No cache entries found matching: {pattern}")
                return 0

        except Exception as e:
            logger.error(f"Semantic cache pattern invalidation error: {str(e)}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dictionary with cache stats
        """
        try:
            all_keys = self.redis.keys(f"semantic:{self.cache_version}:*")

            # Count by classifier type
            type_counts = {
                'stage': 0,
                'context': 0,
                'level': 0,
                'other': 0
            }

            for key in all_keys:
                if ':stage:' in key:
                    type_counts['stage'] += 1
                elif ':context:' in key:
                    type_counts['context'] += 1
                elif ':level:' in key:
                    type_counts['level'] += 1
                else:
                    type_counts['other'] += 1

            stats = {
                'total_cached_entries': len(all_keys),
                'by_classifier_type': type_counts,
                'cache_version': self.cache_version,
                'default_ttl_days': self.ttl // 86400,
                'redis_memory_used_mb': self.redis.info('memory')['used_memory'] / (1024 * 1024)
            }

            return stats

        except Exception as e:
            logger.error(f"Semantic cache stats error: {str(e)}")
            return {'error': str(e)}

    def clear_all(self) -> int:
        """
        Clear all semantic cache entries (use with caution!)

        Returns:
            Number of keys deleted
        """
        return self.invalidate_pattern(f"semantic:{self.cache_version}:*")
