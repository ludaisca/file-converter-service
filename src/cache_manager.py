"""Cache manager for file conversion results using Redis.

Implements intelligent caching of conversion results to reduce
processing time and CPU usage for repeated conversions.
"""
import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, Any
import logging

try:
    import redis
    from redis.exceptions import RedisError, ConnectionError as RedisConnectionError
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from src.config import settings

logger = logging.getLogger('file_converter.cache')


class ConversionCache:
    """Manages caching of file conversion results.
    
    Uses Redis as backend storage with file hash as key to detect
    identical files and serve cached results.
    """
    
    def __init__(self, redis_url: Optional[str] = None, enabled: bool = True):
        """Initialize cache manager.
        
        Args:
            redis_url: Redis connection URL (defaults to settings.REDIS_URL)
            enabled: Whether caching is enabled (defaults to settings.ENABLE_CACHE)
        """
        self.enabled = enabled and REDIS_AVAILABLE and settings.ENABLE_CACHE
        self.redis_client = None
        self.ttl_seconds = settings.CACHE_TTL_HOURS * 3600
        
        if not REDIS_AVAILABLE:
            logger.warning("Redis library not installed. Cache disabled.")
            self.enabled = False
            return
        
        if not self.enabled:
            logger.info("Cache disabled via configuration")
            return
        
        try:
            redis_url = redis_url or settings.REDIS_URL
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            logger.info(f"Cache enabled. Connected to Redis at {redis_url}")
        except (RedisConnectionError, RedisError) as e:
            logger.error(f"Failed to connect to Redis: {e}")
            logger.warning("Cache disabled due to Redis connection failure")
            self.enabled = False
            self.redis_client = None
    
    def _hash_file(self, file_path: Path, chunk_size: int = 8192) -> str:
        """Generate SHA256 hash of file content.
        
        Only reads first 1MB to optimize performance for large files.
        
        Args:
            file_path: Path to file
            chunk_size: Size of chunks to read
            
        Returns:
            Hexadecimal hash string
        """
        sha256_hash = hashlib.sha256()
        max_bytes = 1024 * 1024  # 1MB
        bytes_read = 0
        
        try:
            with open(file_path, "rb") as f:
                while bytes_read < max_bytes:
                    chunk = f.read(min(chunk_size, max_bytes - bytes_read))
                    if not chunk:
                        break
                    sha256_hash.update(chunk)
                    bytes_read += len(chunk)
            
            # Also include file size for uniqueness
            file_size = file_path.stat().st_size
            sha256_hash.update(str(file_size).encode())
            
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Error hashing file {file_path}: {e}")
            # Return a unique hash based on filename and timestamp as fallback
            return hashlib.sha256(
                f"{file_path.name}_{file_path.stat().st_mtime}".encode()
            ).hexdigest()
    
    def _get_cache_key(self, file_hash: str, target_format: str) -> str:
        """Generate cache key from file hash and target format.
        
        Args:
            file_hash: SHA256 hash of file
            target_format: Target conversion format (e.g., 'pdf', '.pdf')
            
        Returns:
            Redis cache key
        """
        # Normalize format (remove leading dot)
        format_normalized = target_format.lstrip('.')
        return f"conversion:v1:{file_hash}:{format_normalized}"
    
    def get(self, file_path: Path, target_format: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached conversion result.
        
        Args:
            file_path: Path to source file
            target_format: Target format for conversion
            
        Returns:
            Cached result dict or None if not found
        """
        if not self.enabled:
            return None
        
        try:
            file_hash = self._hash_file(file_path)
            cache_key = self._get_cache_key(file_hash, target_format)
            
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                result = json.loads(cached_data)
                logger.info(f"Cache HIT: {cache_key[:32]}... (format: {target_format})")
                
                # Verify cached file still exists
                cached_file = Path(result.get('output_path', ''))
                if cached_file.exists():
                    return result
                else:
                    # Cached file was deleted, remove from cache
                    logger.warning(f"Cached file not found: {cached_file}. Removing from cache.")
                    self.delete(file_path, target_format)
                    return None
            
            logger.debug(f"Cache MISS: {cache_key[:32]}...")
            return None
            
        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"Cache retrieval error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected cache error: {e}", exc_info=True)
            return None
    
    def set(self, file_path: Path, target_format: str, result_data: Dict[str, Any]) -> bool:
        """Store conversion result in cache.
        
        Args:
            file_path: Path to source file
            target_format: Target format
            result_data: Result dictionary to cache
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            file_hash = self._hash_file(file_path)
            cache_key = self._get_cache_key(file_hash, target_format)
            
            # Store with TTL
            serialized = json.dumps(result_data)
            self.redis_client.setex(
                cache_key,
                self.ttl_seconds,
                serialized
            )
            
            logger.info(f"Cached result: {cache_key[:32]}... (TTL: {settings.CACHE_TTL_HOURS}h)")
            return True
            
        except (RedisError, json.JSONEncodeError) as e:
            logger.error(f"Cache storage error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected cache error: {e}", exc_info=True)
            return False
    
    def delete(self, file_path: Path, target_format: str) -> bool:
        """Delete cached conversion result.
        
        Args:
            file_path: Path to source file
            target_format: Target format
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            file_hash = self._hash_file(file_path)
            cache_key = self._get_cache_key(file_hash, target_format)
            
            deleted = self.redis_client.delete(cache_key)
            if deleted:
                logger.info(f"Deleted cache entry: {cache_key[:32]}...")
            return bool(deleted)
            
        except RedisError as e:
            logger.error(f"Cache deletion error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected cache error: {e}", exc_info=True)
            return False
    
    def clear_all(self) -> int:
        """Clear all conversion cache entries.
        
        Returns:
            Number of keys deleted
        """
        if not self.enabled:
            return 0
        
        try:
            keys = self.redis_client.keys("conversion:v1:*")
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"Cleared {deleted} cache entries")
                return deleted
            return 0
            
        except RedisError as e:
            logger.error(f"Cache clear error: {e}")
            return 0
        except Exception as e:
            logger.error(f"Unexpected cache error: {e}", exc_info=True)
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        if not self.enabled:
            return {
                'enabled': False,
                'status': 'disabled'
            }
        
        try:
            info = self.redis_client.info('stats')
            keys = len(self.redis_client.keys("conversion:v1:*"))
            
            return {
                'enabled': True,
                'status': 'connected',
                'total_keys': keys,
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'hit_rate': self._calculate_hit_rate(info),
                'ttl_hours': settings.CACHE_TTL_HOURS
            }
            
        except RedisError as e:
            logger.error(f"Error getting cache stats: {e}")
            return {
                'enabled': True,
                'status': 'error',
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error getting stats: {e}", exc_info=True)
            return {
                'enabled': True,
                'status': 'error',
                'error': str(e)
            }
    
    def _calculate_hit_rate(self, info: Dict[str, Any]) -> float:
        """Calculate cache hit rate percentage."""
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        
        if total == 0:
            return 0.0
        
        return round((hits / total) * 100, 2)
    
    def health_check(self) -> Dict[str, Any]:
        """Check Redis connection health.
        
        Returns:
            Health status dictionary
        """
        if not self.enabled:
            return {
                'healthy': False,
                'status': 'disabled',
                'message': 'Cache is disabled'
            }
        
        try:
            self.redis_client.ping()
            return {
                'healthy': True,
                'status': 'connected',
                'message': 'Redis connection healthy'
            }
        except (RedisConnectionError, RedisError) as e:
            return {
                'healthy': False,
                'status': 'error',
                'message': f'Redis connection failed: {str(e)}'
            }
        except Exception as e:
            return {
                'healthy': False,
                'status': 'error',
                'message': f'Unexpected error: {str(e)}'
            }


# Global cache instance
_cache_instance = None

def get_cache() -> ConversionCache:
    """Get or create global cache instance.
    
    Returns:
        ConversionCache instance
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = ConversionCache()
    return _cache_instance
