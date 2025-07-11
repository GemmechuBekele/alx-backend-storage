#!/usr/bin/env python3
"""
Web caching module with Redis and request tracking
"""

import redis
import requests
from functools import wraps

# Initialize Redis client (default localhost:6379)
redis_client = redis.Redis()


def count_requests(method):
    """
    Decorator to count how many times a URL is accessed,
    using key "count:{url}" in Redis.
    """

    @wraps(method)
    def wrapper(url: str) -> str:
        count_key = f"count:{url}"
        redis_client.incr(count_key)
        return method(url)

    return wrapper


def cache_page(expiration: int = 10):
    """
    Decorator to cache the HTML content of a URL in Redis with an expiration.
    Cache key: "cached:{url}"
    """

    def decorator(method):
        @wraps(method)
        def wrapper(url: str) -> str:
            cache_key = f"cached:{url}"
            cached = redis_client.get(cache_key)
            if cached:
                return cached.decode('utf-8')

            page = method(url)
            redis_client.setex(cache_key, expiration, page)
            return page

        return wrapper

    return decorator


@count_requests
@cache_page(expiration=10)
def get_page(url: str) -> str:
    """
    Fetch the HTML content of the URL using requests and return it.

    Args:
        url: URL string

    Returns:
        HTML content as string
    """
    response = requests.get(url)
    response.raise_for_status()
    return response.text
