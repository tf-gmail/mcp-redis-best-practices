---
title: Set TTL on Cache Keys
impact: HIGH
impactDescription: Prevents unbounded memory growth and stale data
tags: ttl, expiration, cache, memory, stale-data
---

## Set TTL on Cache Keys

Always set expiration (TTL) on cache keys to prevent memory bloat and stale data.

**Correct:** Set TTL when creating cache keys.

```python
import redis

r = redis.Redis(host='localhost', port=6379)

# Set with expiration in one command
r.setex("cache:user:1001", 3600, user_data)  # Expires in 1 hour

# Or use SET with EX parameter
r.set("cache:user:1001", user_data, ex=3600)

# For millisecond precision
r.psetex("cache:user:1001", 60000, user_data)  # Expires in 60 seconds
```

**Incorrect:** Cache keys without expiration.

```python
# Bad: No TTL - data lives forever, memory grows unbounded
r.set("cache:user:1001", user_data)

# Eventually you'll have millions of stale cache entries
```

**TTL strategies:**

| Strategy | TTL | Use Case |
|----------|-----|----------|
| Short TTL | 60-300s | Frequently changing data, API responses |
| Medium TTL | 1-24 hours | User sessions, computed results |
| Long TTL | Days-weeks | Rarely changing reference data |
| Sliding TTL | Reset on access | Active sessions, rate limiters |

**Sliding expiration (reset TTL on access):**

```python
def get_with_sliding_ttl(key, ttl=3600):
    """Get value and reset TTL on each access."""
    pipe = r.pipeline()
    pipe.get(key)
    pipe.expire(key, ttl)  # Reset TTL
    results = pipe.execute()
    return results[0]
```

**Cache-aside pattern with TTL:**

```python
def get_user(user_id):
    """Cache-aside pattern with proper TTL."""
    cache_key = f"cache:user:{user_id}"
    
    # Try cache first
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Cache miss - fetch from database
    user = db.query_user(user_id)
    
    # Cache with TTL
    r.setex(cache_key, 3600, json.dumps(user))
    
    return user
```

**Field-level expiration (Redis 7.4+):**

```python
# Expire individual hash fields
r.hset("session:abc", mapping={
    "user_id": "1001",
    "ip": "192.168.1.1",
    "csrf_token": "xyz123"
})

# Expire IP field in 1 hour (for privacy)
r.hexpire("session:abc", 3600, "ip")

# Expire CSRF token in 15 minutes
r.hexpire("session:abc", 900, "csrf_token")
```

**Prevent cache stampede:**

```python
import random

def get_cached_with_jitter(key, compute_fn, base_ttl=3600):
    """Cache with jittered TTL to prevent stampede."""
    cached = r.get(key)
    if cached:
        return json.loads(cached)
    
    # Add jitter: ±10% variation
    jitter = random.uniform(0.9, 1.1)
    ttl = int(base_ttl * jitter)
    
    value = compute_fn()
    r.setex(key, ttl, json.dumps(value))
    return value
```

**Early expiration / probabilistic refresh:**

```python
import random
import time

def get_with_early_refresh(key, compute_fn, ttl=3600, beta=1.0):
    """Probabilistically refresh before expiration."""
    pipe = r.pipeline()
    pipe.get(key)
    pipe.ttl(key)
    value, remaining_ttl = pipe.execute()
    
    if value is None:
        # Cache miss
        value = compute_fn()
        r.setex(key, ttl, json.dumps(value))
        return json.loads(value) if isinstance(value, str) else value
    
    # Probabilistic early refresh
    # Higher probability of refresh as TTL approaches 0
    if remaining_ttl > 0:
        random_threshold = remaining_ttl - (beta * ttl * random.random())
        if random_threshold < 0:
            # Refresh in background
            value = compute_fn()
            r.setex(key, ttl, json.dumps(value))
    
    return json.loads(value)
```

Reference: [Redis Key Expiration](https://redis.io/docs/latest/develop/use/keyspace/#key-expiration)
