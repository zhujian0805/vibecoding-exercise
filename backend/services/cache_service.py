"""
Enhanced cache manager with Singleton pattern and better organization
"""
import logging
from functools import wraps
from typing import Optional, Any
from flask import session

logger = logging.getLogger(__name__)


class CacheManagerSingleton:
    """Singleton cache manager with enhanced functionality"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, cache=None):
        if cls._instance is None:
            cls._instance = super(CacheManagerSingleton, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, cache=None):
        if not self._initialized:
            self.cache = cache
            self._initialized = True
    
    def generate_cache_key(self, prefix: str, user_id: int) -> str:
        """Generate cache key for user-specific data"""
        return f"{prefix}:{user_id}"
    
    def cache_user_data(self, prefix: str, timeout: int = 3600):
        """Decorator for caching user-specific data"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                user = session.get('user')
                if not user or not user.get('id'):
                    return func(*args, **kwargs)
                
                key = self.generate_cache_key(prefix, user['id'])
                
                # Try to get from cache
                try:
                    cached = self.cache.get(key)
                    if cached is not None:
                        logger.debug(f"Cache hit for {key}")
                        return cached
                except Exception as e:
                    logger.warning(f"Cache get failed for {key}: {e}")
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                
                try:
                    self.cache.set(key, result, timeout=timeout)
                    logger.debug(f"Cache set for {key} with timeout {timeout}")
                except Exception as e:
                    logger.warning(f"Cache set failed for {key}: {e}")
                
                return result
            return wrapper
        return decorator
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            return self.cache.get(key)
        except Exception as e:
            logger.warning(f"Cache get failed for {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, timeout: int = 3600) -> bool:
        """Set value in cache"""
        try:
            self.cache.set(key, value, timeout=timeout)
            logger.debug(f"Cache set for {key} with timeout {timeout}")
            return True
        except Exception as e:
            logger.warning(f"Cache set failed for {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            self.cache.delete(key)
            logger.debug(f"Cache deleted for {key}")
            return True
        except Exception as e:
            logger.warning(f"Cache delete failed for {key}: {e}")
            return False
    
    def invalidate_user_cache(self, user_id: int, prefix: Optional[str] = None) -> bool:
        """Invalidate user-specific cache"""
        try:
            if prefix:
                key = self.generate_cache_key(prefix, user_id)
                return self.delete(key)
            else:
                # Clear all user-specific caches
                prefixes = ['repos', 'profile', 'followers', 'following', 'rate_limit']
                success = True
                for p in prefixes:
                    key = self.generate_cache_key(p, user_id)
                    if not self.delete(key):
                        success = False
                logger.debug(f"All cache invalidated for user {user_id}")
                return success
        except Exception as e:
            logger.warning(f"Cache invalidation error: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Clear all cache"""
        try:
            self.cache.clear()
            logger.debug("All cache cleared")
            return True
        except Exception as e:
            logger.warning(f"Cache clear all failed: {e}")
            return False
    
    def get_cache_info(self) -> dict:
        """Get cache configuration information"""
        try:
            cache_type = self.cache.config.get('CACHE_TYPE', 'unknown')
            return {
                'cache_type': cache_type,
                'redis_configured': cache_type == 'redis'
            }
        except Exception as e:
            logger.warning(f"Failed to get cache info: {e}")
            return {'cache_type': 'unknown', 'redis_configured': False}


# For backward compatibility, provide the original class name
class CacheManager(CacheManagerSingleton):
    """Backward compatible alias for CacheManagerSingleton"""
    pass
