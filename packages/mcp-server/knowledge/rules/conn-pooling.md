---
title: Use Connection Pooling or Multiplexing
impact: HIGH
impactDescription: Reduces connection overhead by 10x or more
tags: connections, pooling, multiplexing, performance
---

## Use Connection Pooling or Multiplexing

Reuse connections via a pool or multiplexing instead of creating new connections per request.

**Correct:** Use a connection pool (redis-py, Jedis, go-redis).

```python
import redis

# Good: Connection pool - reuses existing connections
pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    max_connections=50,
    decode_responses=True
)
r = redis.Redis(connection_pool=pool)

# All operations reuse pooled connections
r.set("key", "value")
r.get("key")
```

**Correct:** Use multiplexing (Lettuce, NRedisStack).

```java
// Lettuce uses multiplexing by default - single connection handles all traffic
RedisClient client = RedisClient.create("redis://localhost:6379");
StatefulRedisConnection<String, String> connection = client.connect();

// All commands share the single connection efficiently
connection.sync().set("key", "value");
```

**Incorrect:** Creating new connections per request.

```python
# Bad: New connection every time - massive overhead
def get_user(user_id):
    r = redis.Redis(host='localhost', port=6379)  # Don't do this!
    return r.get(f"user:{user_id}")
    # Connection never explicitly closed, potential leak
```

**Pooling vs Multiplexing:**

| Feature | Pooling | Multiplexing |
|---------|---------|--------------|
| Connections | Multiple | Single |
| Libraries | redis-py, Jedis, go-redis | Lettuce, NRedisStack |
| Blocking commands | ✅ Supported | ❌ Would stall all callers |
| Memory per connection | ~10KB | Shared |
| Best for | General use | High-throughput, non-blocking |

**Connection pool sizing:**

```python
# Rule of thumb: connections = (requests_per_second / 1000) + buffer
# For 5000 req/s: 5 + 5 buffer = 10 connections minimum

pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    max_connections=20,  # Don't over-provision
    socket_timeout=5.0,  # Always set timeouts
    socket_connect_timeout=2.0
)
```

**Flask/FastAPI example:**

```python
from flask import Flask
import redis

app = Flask(__name__)

# Create pool once at startup
redis_pool = redis.ConnectionPool(host='localhost', port=6379, max_connections=20)

def get_redis():
    return redis.Redis(connection_pool=redis_pool)

@app.route('/user/<user_id>')
def get_user(user_id):
    r = get_redis()  # Gets connection from pool
    return r.hgetall(f"user:{user_id}")
```

Reference: [Redis Connection Pooling](https://redis.io/docs/latest/develop/clients/pools-and-muxing/)
