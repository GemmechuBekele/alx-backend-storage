#!/usr/bin/env python3
"""
Web cache and tracker implementation with Redis
"""

import requests
import redis
from functools import wraps
from typing import Callable

# Create Redis connection
redis_client = redis.Redis()


def cache_and_track(expiration: int = 10) -> Callable:
    """
    Decorator to cache webpage content with expiration and track access counts

    Args:
        expiration: Cache expiration time in seconds (default: 10)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(url: str) -> str:
            # Track URL access count
            count_key = f"count:{url}"
            redis_client.incr(count_key)

            # Check if content is cached
            cache_key = f"cache:{url}"
            cached_content = redis_client.get(cache_key)

            if cached_content:
                return cached_content.decode('utf-8')

            # If not cached, fetch the content
            content = func(url)

            # Cache the content with expiration
            redis_client.setex(cache_key, expiration, content)

            return content
        return wrapper
    return decorator


@cache_and_track(expiration=10)
def get_page(url: str) -> str:
    """
    Get the HTML content of a URL

    Args:
        url: URL to fetch

    Returns:
        HTML content as string
    """
    response = requests.get(url)
    return response.text


if __name__ == "__main__":
    # Test with a slow URL
    slow_url = "http://slowwly.robertomurray.co.uk/delay/1000/url/http://www.google.com"

    # First call - will be slow and cached
    print(get_page(slow_url)[:100] + "...")  # Print first 100 chars

    # Subsequent calls within 10 seconds will be fast (from cache)
    print(get_page(slow_url)[:100] + "...")

    # Check access count
    print(f"Access count for {slow_url}: {redis_client.get(f'count:{slow_url}').decode('utf-8')}")