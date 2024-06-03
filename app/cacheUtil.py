import functools
import logging
import multiprocessing
import time

from utils import get_app_custom_config

logger = logging.getLogger(__name__)
if get_app_custom_config("debug"):
    logger.setLevel(logging.DEBUG)


class CentralCache:
    # A central cache accessible to all the process leveraging multiprocessing.Manager().dict() for shared caching it
    # Also has an option to set TTL.
    cache = None
    ttl = 3600

    @staticmethod
    def initialise(ttl=3600):
        if CentralCache.cache is None:
            manager = multiprocessing.Manager()
            CentralCache.cache = manager.dict()
            CentralCache.ttl = ttl
            logger.info("Central cache initialised")

    @staticmethod
    def set(key, value):
        # key = pickle.dumps(key)
        timestamp = time.time()
        CentralCache.cache.setdefault(key, (value, timestamp))

    @staticmethod
    def get(key):
        # key = pickle.dumps(key)
        item = CentralCache.cache.get(key)
        if item is not None:
            value, timestamp = item
            if time.time() - timestamp < CentralCache.ttl:
                return value
            else:
                CentralCache.cache.pop(key)
        return None

    @staticmethod
    def exists(key):
        # key = pickle.dumps(key)
        return CentralCache.cache.get(key) is not None

    @staticmethod
    def drop(key):
        # key = pickle.dumps(key)
        if CentralCache.exists(key):
            CentralCache.cache.pop(key)


def cached_with_force_update(maxsize=3000, ttl=3600):
    """
    Decorator to cache the output of a function, with the option to force an update.
    This is required because in some case we may want to update cache before it expires

    Parameters:
        maxsize (int): Maximum size of the cache.
        ttl (int): Time to live for the cache entries in seconds.
    """

    def decorator(func):
        cache_name = func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            force_update = kwargs.pop("force_update", False)
            cache_key = func.__name__ + str(args)

            if force_update or not CentralCache.exists(cache_key):
                if not force_update:
                    logger.debug(
                        f"Unforced cache update for function: {func.__name__}{args}"
                    )
                CentralCache.drop(cache_key)  # Clear cache entry if forcing update
                value = None
                try:
                    value = func(*args, **kwargs)
                    CentralCache.set(cache_key, value)
                except Exception as e:
                    logger.error(
                        f"Error in {func.__name__} with args {args} and {kwargs}: {str(e)}"
                    )
                # logger.debug(f"Calculated values for {func.__name__} with args {args}")
                # logger.debug(value)
                return value

            # logger.debug(f"Cached values for {func.__name__} with args {args}")
            # logger.debug(CentralCache.get(cache_key))
            return CentralCache.get(cache_key)

        return wrapper

    return decorator
