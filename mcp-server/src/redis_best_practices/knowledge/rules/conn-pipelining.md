---
title: Use Pipelining for Bulk Operations
impact: HIGH
impactDescription: Reduces round trips, 5-10x faster for batch operations
tags: pipelining, batch, performance, round-trips
---

## Use Pipelining for Bulk Operations

Batch multiple commands into a single round trip to reduce network latency.

**Correct:** Use pipeline for multiple commands.

```python
import redis

r = redis.Redis(host='localhost', port=6379)

# Good: Single round trip for multiple commands
pipe = r.pipeline()
for user_id in user_ids:
    pipe.get(f"user:{user_id}")
results = pipe.execute()  # One round trip for all commands

# Process results
for user_id, data in zip(user_ids, results):
    print(f"User {user_id}: {data}")
```

**Incorrect:** Sequential commands in a loop.

```python
# Bad: N round trips for N users
results = []
for user_id in user_ids:
    results.append(r.get(f"user:{user_id}"))  # Each call = 1 round trip
```

**Performance comparison:**

| Approach | 100 keys | 1000 keys | 10000 keys |
|----------|----------|-----------|------------|
| Sequential | ~100ms | ~1000ms | ~10000ms |
| Pipeline | ~2ms | ~20ms | ~200ms |

**Pipeline with transactions (MULTI/EXEC):**

```python
# Atomic pipeline - all or nothing
pipe = r.pipeline(transaction=True)
pipe.incr("counter")
pipe.expire("counter", 3600)
pipe.lpush("log", "counter incremented")
pipe.execute()  # Executes atomically
```

**Pipeline without transactions (faster):**

```python
# Non-atomic pipeline - maximum throughput
pipe = r.pipeline(transaction=False)
for key in keys:
    pipe.get(key)
results = pipe.execute()
```

**Chunked pipeline for very large batches:**

```python
def chunked_pipeline(redis_client, keys, chunk_size=1000):
    """Pipeline large operations in chunks to avoid memory issues."""
    all_results = []
    for i in range(0, len(keys), chunk_size):
        chunk = keys[i:i + chunk_size]
        pipe = redis_client.pipeline(transaction=False)
        for key in chunk:
            pipe.get(key)
        all_results.extend(pipe.execute())
    return all_results
```

**Pipeline with error handling:**

```python
pipe = r.pipeline()
pipe.set("key1", "value1")
pipe.incr("key2")  # Might fail if key2 is not a number
pipe.set("key3", "value3")

try:
    results = pipe.execute(raise_on_error=False)
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Command {i} failed: {result}")
        else:
            print(f"Command {i} succeeded: {result}")
except redis.RedisError as e:
    print(f"Pipeline failed: {e}")
```

Reference: [Redis Pipelining](https://redis.io/docs/latest/develop/use/pipelining/)
