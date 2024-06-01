from typing import overload

from redis import Redis


@overload
async def invalidate_cache(redis: Redis, key: str) -> None: ...


@overload
async def invalidate_cache(
    redis: Redis, key: str, as_pattern: bool = False
) -> None: ...


async def invalidate_cache(redis: Redis, key: str, as_pattern: bool = False) -> None:
    """
    Invalidate cache entries based on the provided key.

    Args:
        :redis (Redis): Redis client instance.
        :key (str): The key or pattern to identify cache entries to invalidate.
        :as_pattern (bool, optional): If True, the provided key is treated as a pattern to match multiple keys.
            Defaults to False.

    Returns:
        None

    Description:
        This function invalidates cache entries based on the provided key. If `as_pattern` is False (default),
        it deletes the cache entry corresponding to the provided key. If `as_pattern` is True, it treats the
        provided key as a pattern and deletes all cache entries that match the pattern.
    """
    if as_pattern:
        for k in redis.scan_iter(match=f"{key}*"):
            redis.delete(k)
    else:
        redis.delete(key)
