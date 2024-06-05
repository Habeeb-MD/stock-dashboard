import functools
import logging
import multiprocessing
import time

from utils import get_app_custom_config, CacheExpiredException

logger = logging.getLogger(__name__)
level = logging.INFO
if get_app_custom_config("debug"):
    level = logging.DEBUG
if get_app_custom_config("cache_util_verbose_log"):
    level = 5
logger.setLevel(level)


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
        CentralCache.cache[key] = (value, timestamp)

    @staticmethod
    def get(key):
        # key = pickle.dumps(key)
        if CentralCache.exists(key):
            value, timestamp = CentralCache.cache.get(key)
            # logger.verbose(f"timestamp: {time.time() - timestamp}")
            if time.time() - timestamp < CentralCache.ttl:
                return value
            else:
                CentralCache.cache.pop(key)
                raise CacheExpiredException("Cache expired")
        raise KeyError("Key Not found")

    @staticmethod
    def exists(key):
        # key = pickle.dumps(key)
        return key in CentralCache.cache

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

        def evaluate(cache_key, funct, *args, **kwargs):
            try:
                value = funct(*args, **kwargs)
                CentralCache.set(cache_key, value)
                return value
            except Exception as e:
                logger.error(
                    f"Error in {funct.__name__} with args {args} and {kwargs}: {str(e)}"
                )
            return None

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

                logger.verbose(
                    f"Calculating values for {func.__name__} with args {args}"
                )
                value = evaluate(cache_key, func, *args, **kwargs)

                # logger.verbose(value)
                return value

            else:
                try:
                    logger.verbose(
                        f"Using Cached values for {func.__name__} with args {args}"
                    )
                    value = CentralCache.get(cache_key)
                    # logger.verbose(f"{cache_key} :- {value}")
                    return value
                except (CacheExpiredException, KeyError) as exception:
                    logger.debug(exception)
                    value = func(*args, **kwargs)
                    return value
                except Exception as e:
                    logger.error(e)

        return wrapper

    return decorator
