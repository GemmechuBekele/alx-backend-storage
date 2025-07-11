#!/usr/bin/env python3
"""
Main file to test Cache class
"""

import redis
Cache = __import__('exercise').Cache

cache = Cache()

# Test basic storing and raw retrieval
data = b"hello"
key = cache.store(data)
print(f"Stored key: {key}")

local_redis = redis.Redis()
print(f"Raw Redis value: {local_redis.get(key)}")

# Test get() with type recovery
TEST_CASES = {
    b"foo": None,
    123: int,
    "bar": lambda d: d.decode("utf-8")
}

for value, fn in TEST_CASES.items():
    key = cache.store(value)
    assert cache.get(key, fn=fn) == value, f"Failed for value: {value}"

print("All test cases passed!")
