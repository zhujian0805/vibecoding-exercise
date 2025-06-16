import logging
from flask import session

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Manager for caching user-specific data, providing decorators and invalidation methods.
    """
    def __init__(self, cache):
        self.cache = cache

    def generate_cache_key(self, prefix: str, user_id: int) -> str:
        return f"{prefix}:{user_id}"

    def cache_user_data(self, prefix, timeout=3600):
        from functools import wraps
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                user = session.get('user')
                if not user or not user.get('id'):
                    return func(*args, **kwargs)
                key = self.generate_cache_key(prefix, user['id'])
                try:
                    cached = self.cache.get(key)
                    if cached is not None:
                        logger.debug(f"Cache hit for {key}")
                        return cached
                except Exception as e:
                    logger.warning(f"Cache get failed for {key}: {e}")
                result = func(*args, **kwargs)
                try:
                    self.cache.set(key, result, timeout=timeout)
                    logger.debug(f"Cache set for {key} with timeout {timeout}")
                except Exception as e:
                    logger.warning(f"Cache set failed for {key}: {e}")
                return result
            return wrapper
        return decorator

    def invalidate_user_cache(self, user_id, prefix=None):
        try:
            if prefix:
                key = self.generate_cache_key(prefix, user_id)
                self.cache.delete(key)
                logger.debug(f"Cache invalidated for {key}")
            else:
                for p in ['repos', 'repos_raw', 'profile', 'followers', 'following']:
                    key = self.generate_cache_key(p, user_id)
                    self.cache.delete(key)
                logger.debug(f"All cache invalidated for user {user_id}")
        except Exception as e:
            logger.warning(f"Cache invalidation error: {e}")
