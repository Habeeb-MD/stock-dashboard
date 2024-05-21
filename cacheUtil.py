import functools
import logging

from cachetools import TTLCache

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def cached_with_force_update(maxsize=3000, ttl=3600):
    """
    Decorator to cache the output of a function, with the option to force an update.
    This is required because in some case we may want to update cache before it expires

    Parameters:
        maxsize (int): Maximum size of the cache.
        ttl (int): Time to live for the cache entries in seconds.
    """

    def decorator(func):
        local_cache = TTLCache(maxsize, ttl)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            force_update = kwargs.pop("force_update", False)
            cache_key = args

            if force_update or cache_key not in local_cache:
                if not force_update:
                    logger.info(f"Updating cache for function: {func.__name__}{args}")
                local_cache.pop(cache_key, None)  # Clear cache entry if forcing update
                value = None
                try:
                    value = func(*args, **kwargs)
                    local_cache[cache_key] = value
                except Exception as e:
                    logger.error(
                        f"Error in {func.__name__} with {args} and {kwargs}: {str(e)}"
                    )
                return value

            return local_cache.get(cache_key)

        return wrapper

    return decorator
