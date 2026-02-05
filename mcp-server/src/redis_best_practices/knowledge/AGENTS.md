# Redis Development Best Practices

**Version 0.1.0**  
MCP Redis Best Practices  
February 2026

> **Note:**  
> This document is optimized for AI agents and LLMs to follow when
> generating or refactoring Redis applications. Humans may also find
> it useful, but guidance here is optimized for automation and consistency.

---

## Abstract

Best practices for Redis including data structures, memory management,
connection handling, Redis Query Engine (RQE), vector search with RedisVL,
semantic caching with LangCache, security, and performance optimization.

---

## Table of Contents

1. [Data Structures & Keys](#1-data-structures--keys) — **HIGH**
   - [Choose the Right Data Structure](#choose-the-right-data-structure)
   - [Use Consistent Key Naming Conventions](#use-consistent-key-naming-conventions)
2. [Memory & Expiration](#2-memory--expiration) — **HIGH**
   - [Configure Memory Limits and Eviction Policies](#configure-memory-limits-and-eviction-policies)
   - [Set TTL on Cache Keys](#set-ttl-on-cache-keys)
3. [Connection & Performance](#3-connection--performance) — **HIGH**
   - [Avoid Slow Commands in Production](#avoid-slow-commands-in-production)
   - [Configure Connection Timeouts](#configure-connection-timeouts)
   - [Use Connection Pooling or Multiplexing](#use-connection-pooling-or-multiplexing)
   - [Use Pipelining for Bulk Operations](#use-pipelining-for-bulk-operations)
4. [JSON Documents](#4-json-documents) — **MEDIUM**
   - [Choose JSON vs Hash Appropriately](#choose-json-vs-hash-appropriately)
   - [Use JSON Paths for Partial Updates](#use-json-paths-for-partial-updates)
5. [Redis Query Engine](#5-redis-query-engine) — **HIGH**
   - [Choose the Correct Field Type](#choose-the-correct-field-type)
   - [Index Only Fields You Query](#index-only-fields-you-query)
6. [Vector Search & RedisVL](#6-vector-search--redisvl) — **HIGH**
   - [Choose HNSW vs FLAT Based on Requirements](#choose-hnsw-vs-flat-based-on-requirements)
   - [Implement RAG Pattern Correctly](#implement-rag-pattern-correctly)
7. [Semantic Caching](#7-semantic-caching) — **MEDIUM**
   - [Configure Semantic Cache Properly](#configure-semantic-cache-properly)
8. [Streams & Pub/Sub](#8-streams--pubsub) — **MEDIUM**
   - [Choose Streams vs Pub/Sub Appropriately](#choose-streams-vs-pub/sub-appropriately)
9. [Clustering & Replication](#9-clustering--replication) — **MEDIUM**
   - [Use Hash Tags for Multi-Key Operations](#use-hash-tags-for-multi-key-operations)
   - [Use Read Replicas for Read-Heavy Workloads](#use-read-replicas-for-read-heavy-workloads)
10. [Security](#10-security) — **HIGH**
   - [Always Use Authentication in Production](#always-use-authentication-in-production)
   - [Secure Network Access](#secure-network-access)
   - [Use ACLs for Fine-Grained Access Control](#use-acls-for-fine-grained-access-control)
11. [Observability](#11-observability) — **MEDIUM**
   - [Monitor Key Redis Metrics](#monitor-key-redis-metrics)
   - [Use Observability Commands for Debugging](#use-observability-commands-for-debugging)

---

## 1. Data Structures & Keys

**Impact:** HIGH

*Choosing the right Redis data type and key naming conventions. Foundation for efficient Redis usage.*

### Choose the Right Data Structure

**Impact: HIGH** (Optimal memory usage and operation performance)

## Choose the Right Data Structure

Selecting the appropriate Redis data type for your use case is fundamental to performance and memory efficiency.

| Use Case | Recommended Type | Why |
|----------|------------------|-----|
| Simple values, counters | String | Fast, atomic operations |
| Object with fields | Hash | Memory efficient, partial updates, field-level expiration |
| Queue, recent items | List | O(1) push/pop at ends |
| Unique items, membership | Set | O(1) add/remove/check |
| Rankings, ranges | Sorted Set | Score-based ordering |
| Nested/hierarchical data | JSON | Path queries, nested structures, geospatial indexing with RQE |
| Event logs, messaging | Stream | Persistent, consumer groups |
| Similarity search | Vector Set | Native vector storage with built-in HNSW indexing |

**Incorrect:** Using strings for everything.

```python
# Storing object as JSON string loses atomic field updates
redis.set("user:1001", json.dumps({"name": "Alice", "email": "alice@example.com"}))

# To update email, must fetch, parse, modify, and rewrite entire object
user = json.loads(redis.get("user:1001"))
user["email"] = "new@example.com"
redis.set("user:1001", json.dumps(user))
```

**Correct:** Use Hash for objects with fields.

```python
# Hash allows atomic field updates
redis.hset("user:1001", mapping={"name": "Alice", "email": "alice@example.com"})

# Update single field without touching others
redis.hset("user:1001", "email", "new@example.com")
```

**Common patterns:**

| Pattern | Data Structure | Example Key |
|---------|----------------|-------------|
| Session store | Hash | `session:{session_id}` |
| Rate limiter | Sorted Set | `ratelimit:{user_id}` |
| Leaderboard | Sorted Set | `leaderboard:{game_id}` |
| Recent activity | List (capped) | `recent:{user_id}` |
| Unique visitors | Set or HyperLogLog | `visitors:{date}` |
| Feature flags | Hash | `features:{app_id}` |
| Message queue | Stream | `queue:{topic}` |
| Shopping cart | Hash | `cart:{user_id}` |

Reference: [Choosing the Right Data Type](https://redis.io/docs/latest/develop/data-types/compare-data-types/)

---

### Use Consistent Key Naming Conventions

**Impact: MEDIUM** (Improved maintainability and debugging)

## Use Consistent Key Naming Conventions

Well-structured key names improve code maintainability, debugging, and enable efficient key scanning.

**Correct:** Use colons as separators with a consistent hierarchy.

```python
# Pattern: service:entity:id:attribute
user:1001:profile
user:1001:settings
order:2024:items
cache:api:users:list
session:abc123
```

**Incorrect:** Inconsistent naming, spaces, or very long keys.

```python
# These cause confusion and waste memory
User_1001_Profile              # Inconsistent casing and separator
my key with spaces             # Spaces cause issues
com.mycompany.myapp.production.users.profile.data.1001  # Too long
userProfile1001                # No structure, hard to scan
```

**Key naming tips:**

- Keep keys short but readable—they consume memory
- Consider key prefixes for multi-tenant applications: `tenant:{id}:user:{user_id}`
- Extract short identifiers from URLs or long strings rather than using the whole thing
- For large binary values, consider using a hash digest as the key instead of the value itself
- Use consistent separators (colons are conventional in Redis)

**Recommended patterns:**

```python
# Entity-based
user:{user_id}                    # Primary entity
user:{user_id}:profile            # Sub-resource
user:{user_id}:settings           # Another sub-resource

# Cache keys
cache:{source}:{identifier}       # cache:api:user:1001
cache:{source}:{hash}             # cache:graphql:abc123

# Time-based
metrics:{date}:{metric}           # metrics:2024-01-15:signups
events:{year}:{month}             # events:2024:01

# Multi-tenant
{tenant}:user:{user_id}           # acme:user:1001
```

**SCAN-friendly naming:**

```python
# Good: Enables efficient SCAN patterns
user:*:profile                    # Find all user profiles
cache:api:*                       # Find all API cache entries

# Bad: No common prefix to scan
profile_user_1001
api_cache_users
```

Reference: [Redis Keys](https://redis.io/docs/latest/develop/use/keyspace/)

---

## 2. Memory & Expiration

**Impact:** HIGH

*Memory limits, eviction policies, TTL strategies, and memory optimization techniques.*

### Configure Memory Limits and Eviction Policies

**Impact: HIGH** (Prevents out-of-memory crashes and unpredictable behavior)

## Configure Memory Limits and Eviction Policies

Always configure `maxmemory` and an eviction policy to prevent Redis from consuming all available memory.

**Correct:** Set explicit memory limits.

```
# In redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
```

```python
# Or via CONFIG SET
r.config_set("maxmemory", "2gb")
r.config_set("maxmemory-policy", "allkeys-lru")
```

**Incorrect:** Running Redis without memory limits.

```python
# No maxmemory set - Redis will use all available RAM
# Can cause OOM killer to terminate Redis or other processes
```

**Eviction policies explained:**

| Policy | Behavior | Best For |
|--------|----------|----------|
| `noeviction` | Return errors when full | Critical data that can't be lost |
| `allkeys-lru` | Evict any key, LRU first | General caching |
| `volatile-lru` | Evict keys with TTL, LRU first | Cache + persistent data mix |
| `allkeys-lfu` | Evict any key, LFU first | Frequency-based caching (Redis 4.0+) |
| `volatile-lfu` | Evict TTL keys, LFU first | Mixed workloads |
| `allkeys-random` | Evict random keys | When LRU overhead matters |
| `volatile-random` | Evict random TTL keys | Simple TTL-based cache |
| `volatile-ttl` | Evict keys closest to expiring | Time-sensitive data |

**Memory optimization tips:**

```python
# 1. Use Hashes for small objects (memory efficient)
# Instead of:
r.set("user:1001:name", "Alice")
r.set("user:1001:email", "alice@example.com")

# Use:
r.hset("user:1001", mapping={"name": "Alice", "email": "alice@example.com"})

# 2. Use short key names in high-volume scenarios
r.set("u:1001:n", "Alice")  # Saves bytes per key

# 3. Use integers when possible (smaller encoding)
r.set("count", 42)  # Uses int encoding, not string
```

**Monitor memory usage:**

```python
# Get memory info
info = r.info("memory")
print(f"Used memory: {info['used_memory_human']}")
print(f"Peak memory: {info['used_memory_peak_human']}")
print(f"Fragmentation ratio: {info['mem_fragmentation_ratio']}")

# Memory usage of specific key
memory_bytes = r.memory_usage("mykey")
print(f"Key uses {memory_bytes} bytes")

# Find big keys (use with caution - can be slow)
# redis-cli --bigkeys
```

**Memory alerts:**

```python
def check_memory_health(redis_client, threshold_percent=80):
    """Check if Redis memory usage is healthy."""
    info = redis_client.info("memory")
    
    maxmemory = info.get("maxmemory", 0)
    used_memory = info["used_memory"]
    
    if maxmemory == 0:
        return {"status": "warning", "message": "No maxmemory limit set!"}
    
    usage_percent = (used_memory / maxmemory) * 100
    
    if usage_percent > threshold_percent:
        return {
            "status": "critical",
            "message": f"Memory at {usage_percent:.1f}%",
            "used": used_memory,
            "max": maxmemory
        }
    
    return {"status": "healthy", "usage_percent": usage_percent}
```

Reference: [Redis Memory Optimization](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/memory-optimization/)

---

### Set TTL on Cache Keys

**Impact: HIGH** (Prevents unbounded memory growth and stale data)

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

---

## 3. Connection & Performance

**Impact:** HIGH

*Connection pooling, pipelining, timeouts, and avoiding blocking commands.*

### Avoid Slow Commands in Production

**Impact: HIGH** (Prevents blocking that can take down entire Redis instance)

## Avoid Slow Commands in Production

Some Redis commands block the entire server. Avoid them in production code paths.

**Commands to avoid:**

| Command | Problem | Alternative |
|---------|---------|-------------|
| `KEYS *` | Scans entire keyspace, blocks server | Use `SCAN` |
| `SMEMBERS` on large sets | Returns all members at once | Use `SSCAN` |
| `HGETALL` on large hashes | Returns all fields at once | Use `HSCAN` or `HMGET` specific fields |
| `LRANGE 0 -1` on large lists | Returns entire list | Paginate with `LRANGE start end` |
| `FLUSHALL` / `FLUSHDB` | Blocks until complete | Use `FLUSHALL ASYNC` |
| `DEBUG SLEEP` | Blocks server | Never use in production |

**Incorrect:** Using KEYS in production.

```python
# DISASTER: This blocks Redis for seconds/minutes on large datasets
keys = r.keys("user:*")  # Never do this!
for key in keys:
    process_user(r.get(key))
```

**Correct:** Use SCAN for iteration.

```python
# Good: Non-blocking iteration with SCAN
cursor = 0
while True:
    cursor, keys = r.scan(cursor=cursor, match="user:*", count=100)
    for key in keys:
        process_user(r.get(key))
    if cursor == 0:
        break
```

**Incorrect:** Getting all members of a large set.

```python
# Bad: Blocks if set has millions of members
all_members = r.smembers("large:set")
```

**Correct:** Use SSCAN for large sets.

```python
# Good: Iterate without blocking
cursor = 0
while True:
    cursor, members = r.sscan("large:set", cursor=cursor, count=100)
    for member in members:
        process_member(member)
    if cursor == 0:
        break
```

**Correct:** Use HSCAN for large hashes.

```python
# Good: Iterate hash fields without blocking
cursor = 0
while True:
    cursor, data = r.hscan("large:hash", cursor=cursor, count=100)
    for field, value in data.items():
        process_field(field, value)
    if cursor == 0:
        break
```

**Monitor for slow commands:**

```python
# Check SLOWLOG for problematic commands
slow_logs = r.slowlog_get(10)  # Get last 10 slow commands
for log in slow_logs:
    print(f"Command: {log['command']}, Duration: {log['duration']}µs")
```

**Configure slow log threshold:**

```
# In redis.conf or via CONFIG SET
slowlog-log-slower-than 10000  # Log commands slower than 10ms
slowlog-max-len 128            # Keep last 128 slow commands
```

**Use OBJECT commands carefully:**

```python
# These can be slow on large keys
r.object("encoding", key)  # OK for small keys
r.object("freq", key)      # OK
r.debug_object(key)        # Avoid - very slow
```

Reference: [Redis Latency Problems](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency/)

---

### Configure Connection Timeouts

**Impact: HIGH** (Prevents hanging connections and cascading failures)

## Configure Connection Timeouts

Always set socket and connection timeouts to prevent hanging connections from cascading into application failures.

**Correct:** Configure all relevant timeouts.

```python
import redis

# Good: Explicit timeouts for all connection aspects
pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    
    # Connection establishment timeout
    socket_connect_timeout=2.0,  # Fail fast if can't connect in 2s
    
    # Operation timeout (read/write)
    socket_timeout=5.0,  # Fail if operation takes > 5s
    
    # Keep-alive settings
    socket_keepalive=True,
    socket_keepalive_options={
        # TCP_KEEPIDLE: Start keepalive after 60s idle
        1: 60,
        # TCP_KEEPINTVL: Send keepalive every 15s
        2: 15,
        # TCP_KEEPCNT: Close after 3 failed probes
        3: 3,
    },
    
    # Connection pool settings
    max_connections=20,
    
    # Retry configuration
    retry_on_timeout=True,
    retry_on_error=[redis.ConnectionError, redis.TimeoutError],
)

r = redis.Redis(connection_pool=pool)
```

**Incorrect:** No timeout configuration.

```python
# Bad: No timeouts - can hang forever
r = redis.Redis(host='localhost', port=6379)

# If Redis is unresponsive, this blocks indefinitely
result = r.get("key")  # Could hang forever!
```

**Timeout recommendations by use case:**

| Use Case | Connect Timeout | Operation Timeout |
|----------|-----------------|-------------------|
| Web request handler | 1-2s | 2-5s |
| Background job | 5s | 30s |
| Real-time features | 0.5-1s | 1-2s |
| Batch processing | 5s | 60s |
| Health check | 1s | 1s |

**Handle timeout errors gracefully:**

```python
import redis
from redis.exceptions import TimeoutError, ConnectionError

r = redis.Redis(
    host='localhost',
    socket_timeout=2.0,
    socket_connect_timeout=1.0
)

def get_with_fallback(key, default=None):
    """Get value with graceful degradation on timeout."""
    try:
        return r.get(key)
    except TimeoutError:
        logger.warning(f"Redis timeout getting {key}")
        return default
    except ConnectionError:
        logger.error(f"Redis connection error getting {key}")
        return default
```

**Circuit breaker pattern:**

```python
import time
from functools import wraps

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.last_failure_time = None
        self.state = "CLOSED"
    
    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF-OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "HALF-OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except (TimeoutError, ConnectionError) as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            raise

# Usage
circuit_breaker = CircuitBreaker()
result = circuit_breaker.call(r.get, "key")
```

Reference: [Redis Connection Handling](https://redis.io/docs/latest/develop/clients/)

---

### Use Connection Pooling or Multiplexing

**Impact: HIGH** (Reduces connection overhead by 10x or more)

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

---

### Use Pipelining for Bulk Operations

**Impact: HIGH** (Reduces round trips, 5-10x faster for batch operations)

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

---

## 4. JSON Documents

**Impact:** MEDIUM

*Using Redis JSON for nested structures, partial updates, and integration with RQE.*

### Choose JSON vs Hash Appropriately

**Impact: MEDIUM** (Optimal storage for document data)

## Choose JSON vs Hash Appropriately

Use JSON for nested/hierarchical data and Hash for flat objects.

**When to use JSON:**

- Nested objects and arrays
- Need for JSON path queries
- Complex document structures
- Integration with Redis Query Engine geospatial features

**When to use Hash:**

- Flat key-value objects
- Need field-level expiration (Redis 7.4+)
- Memory efficiency for small objects
- Simple field updates

**Correct:** Use JSON for nested structures.

```python
import redis

r = redis.Redis(host='localhost', port=6379)

# Store nested document with JSON
r.json().set("user:1001", "$", {
    "name": "Alice",
    "email": "alice@example.com",
    "address": {
        "street": "123 Main St",
        "city": "Boston",
        "zip": "02101"
    },
    "tags": ["premium", "verified"],
    "preferences": {
        "theme": "dark",
        "notifications": True,
        "language": "en"
    }
})

# Update nested field directly
r.json().set("user:1001", "$.address.city", "Cambridge")

# Query nested data
city = r.json().get("user:1001", "$.address.city")

# Array operations
r.json().arrappend("user:1001", "$.tags", "loyalty")
```

**Correct:** Use Hash for flat objects or when you need field-level expiration.

```python
# Hash is simpler and more memory-efficient for flat data
r.hset("session:abc", mapping={
    "user_id": "1001",
    "created_at": "2024-01-01T10:00:00Z",
    "ip": "192.168.1.1",
    "user_agent": "Mozilla/5.0..."
})

# Field-level expiration (Redis 7.4+)
r.hexpire("session:abc", 3600, "ip")  # Expire IP field in 1 hour
```

**Incorrect:** Storing JSON as a string.

```python
# Bad: Loses queryability and atomic updates
import json

user = {"name": "Alice", "address": {"city": "Boston"}}
r.set("user:1001", json.dumps(user))

# To update city, must fetch, parse, modify, serialize, store
data = json.loads(r.get("user:1001"))
data["address"]["city"] = "Cambridge"
r.set("user:1001", json.dumps(data))
```

**Comparison table:**

| Feature | Hash | JSON |
|---------|------|------|
| Nested structures | ❌ | ✅ |
| Arrays | ❌ | ✅ |
| Field-level expiration | ✅ (7.4+) | ❌ |
| Memory (small objects) | Better | Good |
| Memory (large objects) | Good | Better |
| Path queries | ❌ | ✅ |
| Index with RQE | ✅ | ✅ |
| Atomic field updates | ✅ | ✅ |

Reference: [Redis JSON vs Hash](https://redis.io/docs/latest/develop/data-types/compare-data-types/#documents)

---

### Use JSON Paths for Partial Updates

**Impact: MEDIUM** (Reduces bandwidth and enables atomic nested updates)

## Use JSON Paths for Partial Updates

Use JSON path syntax to update specific fields without fetching the entire document.

**Correct:** Use JSON paths for targeted updates.

```python
import redis

r = redis.Redis(host='localhost', port=6379)

# Store JSON document
r.json().set("user:1001", "$", {
    "name": "Alice",
    "email": "alice@example.com",
    "stats": {
        "logins": 0,
        "posts": 0
    },
    "preferences": {"theme": "dark", "notifications": True},
    "tags": ["user"]
})

# Update nested field without fetching entire document
r.json().set("user:1001", "$.preferences.theme", "light")

# Get specific field
theme = r.json().get("user:1001", "$.preferences.theme")

# Increment numeric field atomically
r.json().numincrby("user:1001", "$.stats.logins", 1)

# Append to array
r.json().arrappend("user:1001", "$.tags", "premium")

# Insert at specific array position
r.json().arrinsert("user:1001", "$.tags", 0, "verified")

# Pop from array
removed = r.json().arrpop("user:1001", "$.tags", -1)

# Toggle boolean
current = r.json().get("user:1001", "$.preferences.notifications")
r.json().set("user:1001", "$.preferences.notifications", not current[0])
```

**Incorrect:** Fetching entire document to update one field.

```python
# Bad: Fetches entire document, modifies locally, writes back
import json

data = r.get("user:1001")
user = json.loads(data)
user["preferences"]["theme"] = "light"
r.set("user:1001", json.dumps(user))

# Problems:
# - Race conditions with concurrent updates
# - Unnecessary bandwidth
# - Not atomic
```

**JSON path expressions:**

| Path | Description | Example |
|------|-------------|---------|
| `$` | Root | `$.name` → "Alice" |
| `.field` | Object field | `$.preferences.theme` |
| `[index]` | Array element | `$.tags[0]` |
| `[*]` | All array elements | `$.tags[*]` |
| `..field` | Recursive descent | `$..name` |
| `[start:end]` | Array slice | `$.tags[0:2]` |

**Conditional updates:**

```python
# Update only if path exists
r.json().set("user:1001", "$.preferences.theme", "light", xx=True)

# Create only if path doesn't exist
r.json().set("user:1001", "$.preferences.new_setting", "value", nx=True)
```

**Multiple path operations:**

```python
# Get multiple paths in one call
result = r.json().get("user:1001", "$.name", "$.email", "$.preferences.theme")

# Result: {'$.name': ['Alice'], '$.email': ['alice@example.com'], '$.preferences.theme': ['light']}
```

**Merge/patch updates:**

```python
# Merge new fields into existing object
r.json().merge("user:1001", "$.preferences", {
    "theme": "dark",
    "font_size": 14,
    "language": "en"
})
```

Reference: [Redis JSON Path](https://redis.io/docs/latest/develop/data-types/json/path/)

---

## 5. Redis Query Engine

**Impact:** HIGH

*FT.CREATE, FT.SEARCH, FT.AGGREGATE, index design, field types, and query optimization.*

### Choose the Correct Field Type

**Impact: HIGH** (Correct field types enable efficient querying and indexing)

## Choose the Correct Field Type

Select the right field type in FT.CREATE for optimal query performance.

**Field types and their use cases:**

| Type | Use Case | Operations | Example |
|------|----------|------------|---------|
| `TEXT` | Full-text search | Tokenized search, stemming | Product descriptions |
| `TAG` | Exact match, categories | Exact match, IN clauses | Status, categories |
| `NUMERIC` | Numbers, ranges | Range queries, sorting | Price, age, count |
| `GEO` | Coordinates | Radius search | Store locations |
| `VECTOR` | Embeddings | KNN, similarity | Semantic search |

**Correct:** Match field type to query patterns.

```python
import redis

r = redis.Redis(host='localhost', port=6379)

# Create index with appropriate field types
r.execute_command(
    'FT.CREATE', 'idx:products',
    'ON', 'JSON',
    'PREFIX', '1', 'product:',
    'SCHEMA',
    # TEXT for full-text search
    '$.name', 'AS', 'name', 'TEXT', 'WEIGHT', '2.0',
    '$.description', 'AS', 'description', 'TEXT',
    
    # TAG for exact match / filtering
    '$.category', 'AS', 'category', 'TAG',
    '$.brand', 'AS', 'brand', 'TAG',
    '$.status', 'AS', 'status', 'TAG',
    
    # NUMERIC for ranges and sorting
    '$.price', 'AS', 'price', 'NUMERIC', 'SORTABLE',
    '$.rating', 'AS', 'rating', 'NUMERIC', 'SORTABLE',
    '$.stock', 'AS', 'stock', 'NUMERIC',
    
    # GEO for location queries
    '$.location', 'AS', 'location', 'GEO'
)
```

**Incorrect:** Using TEXT for categorical data.

```python
# Bad: TEXT tokenizes values, breaks exact match
r.execute_command(
    'FT.CREATE', 'idx:products', 'ON', 'JSON',
    'SCHEMA',
    '$.status', 'AS', 'status', 'TEXT'  # Wrong! "in stock" becomes two tokens
)

# This won't work as expected:
# FT.SEARCH idx:products "@status:in stock"  # Searches for "in" AND "stock"
```

**TAG vs TEXT comparison:**

```python
# Store product
r.json().set("product:1", "$", {
    "name": "Wireless Bluetooth Headphones",  # TEXT: searchable words
    "category": "electronics>audio>headphones",  # TAG: exact hierarchy
    "tags": ["wireless", "bluetooth", "premium"],  # TAG array
    "status": "in stock"  # TAG: exact match
})

# TEXT search: finds "bluetooth" in name
r.execute_command('FT.SEARCH', 'idx:products', '@name:bluetooth')

# TAG exact match: finds exact category
r.execute_command('FT.SEARCH', 'idx:products', '@category:{electronics>audio>headphones}')

# TAG with multiple values
r.execute_command('FT.SEARCH', 'idx:products', '@tags:{wireless|premium}')
```

**SORTABLE for sorting fields:**

```python
# Add SORTABLE for fields you'll ORDER BY
r.execute_command(
    'FT.CREATE', 'idx:products', 'ON', 'JSON',
    'SCHEMA',
    '$.price', 'AS', 'price', 'NUMERIC', 'SORTABLE',  # Will sort by price
    '$.created_at', 'AS', 'created_at', 'NUMERIC', 'SORTABLE'  # Will sort by date
)

# Now sorting works efficiently
r.execute_command('FT.SEARCH', 'idx:products', '*', 'SORTBY', 'price', 'ASC')
```

**INDEX vs NOINDEX:**

```python
# Only index fields you'll actually query
r.execute_command(
    'FT.CREATE', 'idx:users', 'ON', 'JSON',
    'SCHEMA',
    '$.email', 'AS', 'email', 'TAG',  # Indexed: will search
    '$.name', 'AS', 'name', 'TEXT',  # Indexed: will search
    '$.internal_notes', 'AS', 'notes', 'TEXT', 'NOINDEX'  # Not indexed: just stored
)
```

Reference: [Redis Query Engine Field Types](https://redis.io/docs/latest/develop/interact/search-and-query/basic-constructs/field-and-type-options/)

---

### Index Only Fields You Query

**Impact: HIGH** (Reduces memory usage and indexing overhead)

## Index Only Fields You Query

Only create indexes on fields you actually query. Extra indexes waste memory and slow writes.

**Correct:** Index only queried fields.

```python
import redis

r = redis.Redis(host='localhost', port=6379)

# Only index fields that will be searched or filtered
r.execute_command(
    'FT.CREATE', 'idx:orders',
    'ON', 'JSON',
    'PREFIX', '1', 'order:',
    'SCHEMA',
    # Fields we'll query:
    '$.status', 'AS', 'status', 'TAG',           # Filter by status
    '$.customer_id', 'AS', 'customer_id', 'TAG', # Filter by customer
    '$.total', 'AS', 'total', 'NUMERIC', 'SORTABLE',  # Sort by total
    '$.created_at', 'AS', 'created_at', 'NUMERIC', 'SORTABLE'  # Sort by date
    # NOT indexed: order_items, shipping_address, internal_notes
    # These are stored but not searched
)
```

**Incorrect:** Indexing everything.

```python
# Bad: Indexes fields that are never queried
r.execute_command(
    'FT.CREATE', 'idx:orders', 'ON', 'JSON',
    'SCHEMA',
    '$.status', 'AS', 'status', 'TAG',
    '$.customer_id', 'AS', 'customer_id', 'TAG',
    '$.total', 'AS', 'total', 'NUMERIC',
    '$.shipping_address.street', 'AS', 'street', 'TEXT',  # Never searched!
    '$.shipping_address.city', 'AS', 'city', 'TEXT',      # Never searched!
    '$.shipping_address.zip', 'AS', 'zip', 'TAG',         # Never searched!
    '$.internal_notes', 'AS', 'notes', 'TEXT',            # Never searched!
    '$.items[*].sku', 'AS', 'sku', 'TAG',                 # Never searched!
    '$.items[*].name', 'AS', 'item_name', 'TEXT'          # Never searched!
)
# Result: 4x memory usage, slower writes, no benefit
```

**Check index memory usage:**

```python
# See how much memory the index uses
info = r.execute_command('FT.INFO', 'idx:orders')
# Look for: "index_data_size_mb"

# Compare before and after adding fields
# Rule of thumb: TEXT fields use more memory than TAG
```

**Partial indexing with FILTER:**

```python
# Only index active orders (not archived)
r.execute_command(
    'FT.CREATE', 'idx:active_orders',
    'ON', 'JSON',
    'PREFIX', '1', 'order:',
    'FILTER', '@status!="archived"',  # Only index non-archived
    'SCHEMA',
    '$.status', 'AS', 'status', 'TAG',
    '$.customer_id', 'AS', 'customer_id', 'TAG'
)
```

**NOINDEX for stored-only fields:**

```python
# Store field for retrieval but don't index it
r.execute_command(
    'FT.CREATE', 'idx:products',
    'ON', 'JSON',
    'SCHEMA',
    '$.name', 'AS', 'name', 'TEXT',
    '$.price', 'AS', 'price', 'NUMERIC', 'SORTABLE',
    '$.long_description', 'AS', 'description', 'TEXT', 'NOINDEX'  # Stored, not indexed
)
```

**Index optimization tips:**

| Scenario | Recommendation |
|----------|----------------|
| High write volume | Fewer indexed fields |
| Read-heavy | Index what you query |
| Large TEXT fields | Consider NOINDEX or TAG |
| Array fields | Index only if queried |
| Nested objects | Index leaf fields only |

**Monitor index performance:**

```python
# Check indexing lag
info = r.execute_command('FT.INFO', 'idx:orders')
# Look for:
# - "indexing" (should be "complete")
# - "percent_indexed" (should be 100%)
# - "number_of_uses" (query count)

# Profile slow queries
r.execute_command('FT.PROFILE', 'idx:products', 'SEARCH', 'QUERY', '@name:headphones')
```

Reference: [Redis Index Creation](https://redis.io/docs/latest/develop/interact/search-and-query/indexing/)

---

## 6. Vector Search & RedisVL

**Impact:** HIGH

*Vector indexes, HNSW vs FLAT, hybrid search, and RAG patterns with RedisVL.*

### Choose HNSW vs FLAT Based on Requirements

**Impact: HIGH** (Right algorithm choice affects latency, accuracy, and memory)

## Choose HNSW vs FLAT Based on Requirements

Select the right vector index algorithm based on your dataset size, accuracy needs, and latency requirements.

**HNSW vs FLAT comparison:**

| Feature | HNSW | FLAT |
|---------|------|------|
| Algorithm | Approximate KNN | Exact KNN |
| Accuracy | ~95-99% | 100% |
| Latency | O(log n) | O(n) |
| Memory | Higher | Lower |
| Build time | Longer | Instant |
| Best for | >10K vectors | <10K vectors |
| Updates | Slower | Instant |

**Correct:** Use HNSW for large datasets.

```python
import redis
import numpy as np

r = redis.Redis(host='localhost', port=6379)

# HNSW for large-scale similarity search (>10K vectors)
r.execute_command(
    'FT.CREATE', 'idx:embeddings',
    'ON', 'HASH',
    'PREFIX', '1', 'doc:',
    'SCHEMA',
    'embedding', 'VECTOR', 'HNSW', '10',
        'TYPE', 'FLOAT32',
        'DIM', '384',           # Embedding dimension
        'DISTANCE_METRIC', 'COSINE',
        'M', '16',              # Connections per layer (16-64)
        'EF_CONSTRUCTION', '200', # Build-time quality (100-500)
    'content', 'TEXT'
)

# Query with HNSW
embedding = get_embedding("search query")
results = r.execute_command(
    'FT.SEARCH', 'idx:embeddings',
    f'*=>[KNN 10 @embedding $vec AS score]',
    'PARAMS', '2', 'vec', embedding.tobytes(),
    'SORTBY', 'score',
    'RETURN', '2', 'content', 'score',
    'DIALECT', '2'
)
```

**Correct:** Use FLAT for small datasets or 100% accuracy.

```python
# FLAT for small datasets (<10K) or when exact results needed
r.execute_command(
    'FT.CREATE', 'idx:products_flat',
    'ON', 'HASH',
    'PREFIX', '1', 'product:',
    'SCHEMA',
    'embedding', 'VECTOR', 'FLAT', '6',
        'TYPE', 'FLOAT32',
        'DIM', '384',
        'DISTANCE_METRIC', 'COSINE'
)
```

**HNSW parameter tuning:**

```python
# High accuracy, slower build
r.execute_command(
    'FT.CREATE', 'idx:high_accuracy',
    'ON', 'HASH', 'SCHEMA',
    'embedding', 'VECTOR', 'HNSW', '10',
        'TYPE', 'FLOAT32',
        'DIM', '384',
        'DISTANCE_METRIC', 'COSINE',
        'M', '32',              # Higher M = more accurate, more memory
        'EF_CONSTRUCTION', '400' # Higher = better index, slower build
)

# At query time, increase EF_RUNTIME for better accuracy
results = r.execute_command(
    'FT.SEARCH', 'idx:high_accuracy',
    f'*=>[KNN 10 @embedding $vec EF_RUNTIME 250 AS score]',
    'PARAMS', '2', 'vec', embedding.tobytes(),
    'DIALECT', '2'
)
```

**Distance metrics:**

| Metric | Use Case | Range |
|--------|----------|-------|
| `COSINE` | Text embeddings, semantic search | 0-2 (lower=similar) |
| `L2` (Euclidean) | Image embeddings, general | 0-∞ (lower=similar) |
| `IP` (Inner Product) | When vectors are normalized | Higher=similar |

**Memory estimation:**

```python
# HNSW memory per vector (approximate):
# base_size = dim * 4 bytes (FLOAT32)
# hnsw_overhead = M * 2 * 4 bytes per layer
# Example: 384-dim, M=16, 1M vectors
# Memory ≈ 1M * (384 * 4 + 16 * 2 * 4 * avg_layers) ≈ 2-3 GB

# FLAT memory per vector:
# Memory = dim * 4 bytes per vector
# Example: 384-dim, 1M vectors
# Memory ≈ 1M * 384 * 4 = 1.5 GB
```

**When to choose:**

| Scenario | Algorithm |
|----------|-----------|
| <10K vectors | FLAT |
| 10K-10M vectors | HNSW |
| Need 100% accuracy | FLAT |
| Need low latency at scale | HNSW |
| Frequent vector updates | FLAT (or accept HNSW rebuild) |
| Memory constrained | FLAT |

Reference: [Redis Vector Similarity](https://redis.io/docs/latest/develop/interact/search-and-query/advanced-concepts/vectors/)

---

### Implement RAG Pattern Correctly

**Impact: HIGH** (Effective retrieval-augmented generation for LLM applications)

## Implement RAG Pattern Correctly

Use Redis as a vector database for retrieval-augmented generation (RAG) to ground LLM responses in your data.

**Correct:** Complete RAG implementation with RedisVL.

```python
from redisvl.index import SearchIndex
from redisvl.query import VectorQuery
from redisvl.utils.vectorize import OpenAITextVectorizer
import redis
import openai

# 1. Define schema
schema = {
    "index": {
        "name": "docs",
        "prefix": "doc:",
    },
    "fields": [
        {"name": "content", "type": "text"},
        {"name": "source", "type": "tag"},
        {"name": "embedding", "type": "vector",
         "attrs": {
             "dims": 1536,
             "distance_metric": "cosine",
             "algorithm": "hnsw",
             "datatype": "float32"
         }}
    ]
}

# 2. Create index
index = SearchIndex.from_dict(schema)
index.connect("redis://localhost:6379")
index.create(overwrite=True)

# 3. Vectorizer (using OpenAI embeddings)
vectorizer = OpenAITextVectorizer(
    model="text-embedding-3-small",
    api_config={"api_key": os.environ["OPENAI_API_KEY"]}
)

# 4. Index documents
def index_documents(documents):
    for doc in documents:
        embedding = vectorizer.embed(doc["content"])
        index.load([{
            "content": doc["content"],
            "source": doc["source"],
            "embedding": embedding
        }])

# 5. RAG query function
def rag_query(question: str, k: int = 5) -> str:
    # Generate query embedding
    query_embedding = vectorizer.embed(question)
    
    # Search for relevant documents
    query = VectorQuery(
        vector=query_embedding,
        vector_field_name="embedding",
        return_fields=["content", "source"],
        num_results=k
    )
    
    results = index.query(query)
    
    # Build context from retrieved documents
    context = "\n\n".join([
        f"Source: {r['source']}\n{r['content']}"
        for r in results
    ])
    
    # Generate response with LLM
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"Answer based on this context:\n\n{context}"},
            {"role": "user", "content": question}
        ]
    )
    
    return response.choices[0].message.content
```

**Incorrect:** RAG without proper chunking or retrieval.

```python
# Bad: Embedding entire documents (too long, loses precision)
embedding = get_embedding(entire_document)  # 10,000+ tokens

# Bad: No relevance filtering
results = index.query(query)  # Returns irrelevant results

# Bad: No source tracking
context = " ".join([r["content"] for r in results])  # Can't verify sources
```

**Chunking strategies:**

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Good chunking for RAG
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,       # ~100-500 tokens per chunk
    chunk_overlap=50,     # Overlap to maintain context
    separators=["\n\n", "\n", ". ", " ", ""]
)

chunks = splitter.split_text(document)

# Index with metadata
for i, chunk in enumerate(chunks):
    embedding = vectorizer.embed(chunk)
    index.load([{
        "content": chunk,
        "source": doc_id,
        "chunk_index": i,
        "embedding": embedding
    }])
```

**Hybrid search (vector + keyword):**

```python
from redisvl.query import FilterQuery

# Combine vector similarity with keyword filters
query = VectorQuery(
    vector=query_embedding,
    vector_field_name="embedding",
    return_fields=["content", "source"],
    num_results=10,
    filter_expression="@source:{technical_docs}"  # Pre-filter by source
)

# Or post-filter with score threshold
results = [r for r in index.query(query) if r["vector_distance"] < 0.3]
```

**RAG best practices:**

| Practice | Why |
|----------|-----|
| Chunk size 100-500 tokens | Balances context and precision |
| Overlap chunks 10-20% | Maintains context across chunks |
| Store metadata | Enable filtering and attribution |
| Use hybrid search | Combine semantic + keyword |
| Set similarity threshold | Filter irrelevant results |
| Include source in prompt | LLM can cite sources |

Reference: [RedisVL Documentation](https://redis.io/docs/latest/integrate/redisvl/)

---

## 7. Semantic Caching

**Impact:** MEDIUM

*LangCache for LLM response caching, distance thresholds, and cache strategies.*

### Configure Semantic Cache Properly

**Impact: MEDIUM** (Reduces LLM costs and latency through intelligent caching)

## Configure Semantic Cache Properly

Use semantic caching to reduce LLM API costs by returning cached responses for semantically similar queries.

**Correct:** Configure LangCache with appropriate thresholds.

```python
from langcache import LangCache
import openai

# Initialize semantic cache
cache = LangCache(
    redis_url="redis://localhost:6379",
    
    # Distance threshold: lower = stricter matching
    # 0.1 = very similar, 0.3 = somewhat similar
    distance_threshold=0.15,
    
    # TTL for cached responses
    ttl=86400,  # 24 hours
    
    # Embedding model
    embedding_model="text-embedding-3-small"
)

# Wrap your LLM calls
@cache.cache
def ask_llm(question: str) -> str:
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": question}]
    )
    return response.choices[0].message.content

# First call: hits LLM API
answer1 = ask_llm("What is the capital of France?")

# Similar query: returns cached response (no API call!)
answer2 = ask_llm("What's the capital city of France?")

# Different query: hits LLM API
answer3 = ask_llm("What is the population of France?")
```

**Incorrect:** Semantic cache with wrong threshold.

```python
# Bad: Threshold too high - returns irrelevant cached responses
cache = LangCache(
    distance_threshold=0.8  # Too permissive!
)

# "What is Python?" might return cached answer for "What is Java?"

# Bad: Threshold too low - rarely hits cache
cache = LangCache(
    distance_threshold=0.01  # Too strict!
)

# Only exact matches will hit cache, defeating the purpose
```

**Threshold guidelines:**

| Threshold | Behavior | Use Case |
|-----------|----------|----------|
| 0.05-0.10 | Very strict | Factual Q&A, exact matches |
| 0.10-0.20 | Balanced | General conversation |
| 0.20-0.30 | Permissive | Creative tasks, summaries |
| >0.30 | Too loose | Risk of wrong cached answers |

**Manual semantic cache with Redis:**

```python
import redis
import numpy as np
from openai import OpenAI

r = redis.Redis(host='localhost', port=6379)
client = OpenAI()

def get_embedding(text: str) -> np.ndarray:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(response.data[0].embedding, dtype=np.float32)

def semantic_cache_get(query: str, threshold: float = 0.15):
    """Check semantic cache for similar query."""
    query_embedding = get_embedding(query)
    
    # Search for similar cached queries
    results = r.execute_command(
        'FT.SEARCH', 'idx:llm_cache',
        f'*=>[KNN 1 @embedding $vec AS distance]',
        'PARAMS', '2', 'vec', query_embedding.tobytes(),
        'RETURN', '2', 'response', 'distance',
        'DIALECT', '2'
    )
    
    if results[0] > 0:
        distance = float(results[2][3])
        if distance <= threshold:
            return results[2][1]  # Return cached response
    
    return None

def semantic_cache_set(query: str, response: str, ttl: int = 86400):
    """Store query-response pair in semantic cache."""
    query_embedding = get_embedding(query)
    key = f"cache:{hash(query)}"
    
    r.hset(key, mapping={
        "query": query,
        "response": response,
        "embedding": query_embedding.tobytes()
    })
    r.expire(key, ttl)
```

**Cache with context awareness:**

```python
# Include relevant context in cache key
def ask_with_context(question: str, context: str) -> str:
    # Combine question + context for cache lookup
    cache_input = f"Context: {context[:500]}\nQuestion: {question}"
    
    cached = semantic_cache_get(cache_input)
    if cached:
        return cached
    
    response = call_llm(question, context)
    semantic_cache_set(cache_input, response)
    return response
```

**Monitor cache effectiveness:**

```python
# Track hit rate
hits = r.incr("cache:stats:hits")
misses = r.incr("cache:stats:misses")
hit_rate = hits / (hits + misses)

# Track cost savings
# Average cost per API call * number of cache hits
```

Reference: [Redis Semantic Cache](https://redis.io/docs/latest/integrate/redisvl/user-guide/semantic-caching/)

---

## 8. Streams & Pub/Sub

**Impact:** MEDIUM

*Choosing between Streams and Pub/Sub for messaging patterns.*

### Choose Streams vs Pub/Sub Appropriately

**Impact: MEDIUM** (Right messaging pattern for durability and delivery requirements)

## Choose Streams vs Pub/Sub Appropriately

Use Streams for durable messaging with delivery guarantees. Use Pub/Sub for ephemeral real-time notifications.

**When to use Streams:**

- Message persistence required
- Consumer groups needed
- At-least-once delivery guarantees
- Message replay capability
- Slow/offline consumers

**When to use Pub/Sub:**

- Real-time notifications
- Fire-and-forget messages
- No persistence needed
- Broadcast to all subscribers
- Simple fan-out pattern

**Comparison:**

| Feature | Streams | Pub/Sub |
|---------|---------|---------|
| Persistence | ✅ Yes | ❌ No |
| Message replay | ✅ Yes | ❌ No |
| Consumer groups | ✅ Yes | ❌ No |
| Delivery guarantee | At-least-once | At-most-once |
| Offline consumers | ✅ Messages wait | ❌ Messages lost |
| Memory usage | Higher | Lower |
| Use case | Event sourcing, queues | Notifications, cache invalidation |

**Correct:** Use Streams for durable message processing.

```python
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Producer: Add message to stream
message_id = r.xadd("events:orders", {
    "type": "order_created",
    "order_id": "12345",
    "user_id": "1001",
    "amount": "99.99"
})

# Create consumer group (run once)
try:
    r.xgroup_create("events:orders", "order-processors", id="0", mkstream=True)
except redis.ResponseError as e:
    if "BUSYGROUP" not in str(e):
        raise

# Consumer: Read from group with acknowledgment
def process_messages():
    while True:
        # Read messages (block up to 5 seconds)
        messages = r.xreadgroup(
            groupname="order-processors",
            consumername="worker-1",
            streams={"events:orders": ">"},
            count=10,
            block=5000
        )
        
        for stream, message_list in messages:
            for message_id, data in message_list:
                try:
                    # Process message
                    process_order(data)
                    # Acknowledge successful processing
                    r.xack("events:orders", "order-processors", message_id)
                except Exception as e:
                    print(f"Failed to process {message_id}: {e}")
                    # Message will be redelivered to another consumer
```

**Correct:** Use Pub/Sub for real-time notifications.

```python
import redis
import threading

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Subscriber (runs in separate thread)
def subscriber():
    pubsub = r.pubsub()
    pubsub.subscribe("notifications:user:1001")
    
    for message in pubsub.listen():
        if message["type"] == "message":
            print(f"Received: {message['data']}")

# Start subscriber in background
thread = threading.Thread(target=subscriber, daemon=True)
thread.start()

# Publisher: Send notification
r.publish("notifications:user:1001", "You have a new message!")
```

**Stream with trimming (bounded memory):**

```python
# Keep only last 10000 messages
r.xadd("events:logs", {"level": "info", "msg": "test"}, maxlen=10000)

# Approximate trimming (faster, ~10000 messages)
r.xadd("events:logs", fields, maxlen=10000, approximate=True)

# Trim by time (keep last 24 hours)
min_id = f"{int(time.time() - 86400) * 1000}-0"
r.xtrim("events:logs", minid=min_id)
```

**Claim pending messages (handle failed consumers):**

```python
# Find stuck messages (pending > 60 seconds)
pending = r.xpending_range(
    "events:orders",
    "order-processors",
    min="-",
    max="+",
    count=10
)

# Claim messages from failed consumer
for entry in pending:
    if entry["time_since_delivered"] > 60000:  # > 60 seconds
        r.xclaim(
            "events:orders",
            "order-processors",
            "worker-2",  # New consumer
            min_idle_time=60000,
            message_ids=[entry["message_id"]]
        )
```

Reference: [Redis Streams](https://redis.io/docs/latest/develop/data-types/streams/)

---

## 9. Clustering & Replication

**Impact:** MEDIUM

*Hash tags for key colocation, read replicas, and cluster-aware patterns.*

### Use Hash Tags for Multi-Key Operations

**Impact: MEDIUM** (Enables multi-key operations in Redis Cluster)

## Use Hash Tags for Multi-Key Operations

In Redis Cluster, keys are distributed across slots based on their hash. Use hash tags to ensure related keys are on the same slot.

**Correct:** Use hash tags for keys used in multi-key operations.

```python
import redis

r = redis.Redis(host='localhost', port=6379)

# These keys go to the same slot because {user:1001} is the hash tag
r.set("{user:1001}:profile", '{"name": "Alice"}')
r.set("{user:1001}:settings", '{"theme": "dark"}')
r.set("{user:1001}:cart", '[]')

# Now you can use transactions and pipelines
pipe = r.pipeline()
pipe.get("{user:1001}:profile")
pipe.get("{user:1001}:settings")
pipe.execute()  # Works in cluster!

# Multi-key commands also work
r.mget("{user:1001}:profile", "{user:1001}:settings")

# Atomic operations across keys
r.lmove("{user:1001}:pending", "{user:1001}:processed", "LEFT", "RIGHT")
```

**Incorrect:** Keys without hash tags that need multi-key operations.

```python
# Bad: These may be on different slots
r.set("user:1001:profile", "...")
r.set("user:1001:settings", "...")

# This will fail in cluster mode!
pipe = r.pipeline()
pipe.get("user:1001:profile")
pipe.get("user:1001:settings")
pipe.execute()  # CROSSSLOT error!

# This also fails
r.mget("user:1001:profile", "user:1001:settings")  # CROSSSLOT error!
```

**Hash tag rules:**

- Only the part between `{` and `}` is hashed for slot assignment
- If multiple `{}` exist, only the first one counts
- Empty `{}` means the whole key is hashed (no effect)

**Examples:**

| Key | Hash Tag | Slot Based On |
|-----|----------|---------------|
| `{user:1001}:profile` | `user:1001` | `user:1001` |
| `{user:1001}:settings` | `user:1001` | `user:1001` |
| `user:{1001}:profile` | `1001` | `1001` |
| `user:1001:profile` | (none) | `user:1001:profile` |
| `{order}:123:items` | `order` | `order` |

**When to use hash tags:**

✅ Use hash tags:
- User data that needs atomic updates
- Shopping carts with item operations
- Transactions across related keys
- Lua scripts accessing multiple keys

❌ Avoid hash tags:
- Independent keys that don't need multi-key ops
- When you want even distribution
- High-volume keys (can create hot spots)

**Prevent hot slots:**

```python
# Bad: All users hash to same slot!
r.set("{users}:1001", "...")
r.set("{users}:1002", "...")
r.set("{users}:1003", "...")

# Good: Each user gets their own slot group
r.set("{user:1001}:profile", "...")  # Slot X
r.set("{user:1002}:profile", "...")  # Slot Y
r.set("{user:1003}:profile", "...")  # Slot Z
```

**Check key slot in cluster:**

```python
# Verify keys are on same slot
slot1 = r.cluster_keyslot("{user:1001}:profile")
slot2 = r.cluster_keyslot("{user:1001}:settings")
print(f"Same slot: {slot1 == slot2}")  # True
```

Reference: [Redis Cluster Hash Tags](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/#hash-tags)

---

### Use Read Replicas for Read-Heavy Workloads

**Impact: MEDIUM** (Scales read throughput and reduces primary load)

## Use Read Replicas for Read-Heavy Workloads

Distribute read operations across replicas to scale read throughput and reduce load on the primary.

**Correct:** Configure client to use read replicas.

```python
import redis
from redis.sentinel import Sentinel

# Option 1: Redis Sentinel with read replicas
sentinel = Sentinel([
    ('sentinel1.example.com', 26379),
    ('sentinel2.example.com', 26379),
    ('sentinel3.example.com', 26379)
], socket_timeout=0.5)

# Get master for writes
master = sentinel.master_for('mymaster', socket_timeout=0.5)
master.set("key", "value")

# Get slave/replica for reads
slave = sentinel.slave_for('mymaster', socket_timeout=0.5)
value = slave.get("key")
```

```python
# Option 2: Redis Cluster with READONLY
from redis.cluster import RedisCluster

rc = RedisCluster(
    host='cluster-node1.example.com',
    port=6379,
    read_from_replicas=True  # Enable reading from replicas
)

# Reads automatically distributed to replicas
value = rc.get("key")
```

**Correct:** Explicit replica reads for specific operations.

```python
# For operations that can tolerate slight staleness
def get_from_replica(key):
    """Read from replica, accepting potentially stale data."""
    replica = sentinel.slave_for('mymaster', socket_timeout=0.5)
    return replica.get(key)

# For operations requiring consistency
def get_from_primary(key):
    """Read from primary for guaranteed consistency."""
    primary = sentinel.master_for('mymaster', socket_timeout=0.5)
    return primary.get(key)

# Read-after-write pattern
def update_and_read(key, value):
    """Write to primary, read from primary for consistency."""
    primary = sentinel.master_for('mymaster', socket_timeout=0.5)
    primary.set(key, value)
    return primary.get(key)  # Read from primary, not replica
```

**Incorrect:** Always reading from primary under heavy load.

```python
# Bad: All reads go to primary - doesn't scale
r = redis.Redis(host='primary.example.com', port=6379)

for user_id in user_ids:
    r.get(f"user:{user_id}")  # Primary handles all reads
```

**Replication lag awareness:**

```python
def get_with_lag_check(key, max_lag_seconds=1):
    """Read from replica only if lag is acceptable."""
    # Check replication lag
    replica = sentinel.slave_for('mymaster')
    info = replica.info('replication')
    
    # master_last_io_seconds_ago indicates lag
    lag = info.get('master_last_io_seconds_ago', 0)
    
    if lag > max_lag_seconds:
        # Lag too high, read from primary
        primary = sentinel.master_for('mymaster')
        return primary.get(key)
    
    return replica.get(key)
```

**Load balancing strategies:**

| Strategy | Use Case | Trade-off |
|----------|----------|-----------|
| Round-robin replicas | Even distribution | May hit lagging replica |
| Nearest replica | Low latency | Uneven load |
| Random replica | Simple, decent distribution | Unpredictable |
| Weighted replicas | Control traffic ratio | More complex |

**Cloud managed Redis:**

```python
# AWS ElastiCache - Reader endpoint
writer = redis.Redis(host='my-cluster.abc123.ng.0001.use1.cache.amazonaws.com')
reader = redis.Redis(host='my-cluster-ro.abc123.ng.0001.use1.cache.amazonaws.com')

# Azure Cache for Redis - Read replicas via connection string
# Google Cloud Memorystore - Read replicas enabled in config
```

Reference: [Redis Replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/)

---

## 10. Security

**Impact:** HIGH

*Authentication, ACLs, TLS, and network security.*

### Always Use Authentication in Production

**Impact: HIGH** (Prevents unauthorized access to data)

## Always Use Authentication in Production

Never run Redis without authentication in production. Use strong passwords and ACLs.

**Correct:** Configure authentication.

```
# In redis.conf
requirepass your-very-strong-password-here-min-32-chars

# Or use ACL (Redis 6.0+) for fine-grained control
user default off
user app on >strong-password ~app:* +@all -@dangerous
user readonly on >readonly-password ~* +@read -@write -@admin
```

```python
import redis

# Connect with password
r = redis.Redis(
    host='localhost',
    port=6379,
    password='your-very-strong-password-here',
    decode_responses=True
)

# Or with username (ACL, Redis 6.0+)
r = redis.Redis(
    host='localhost',
    port=6379,
    username='app',
    password='app-password',
    decode_responses=True
)
```

**Incorrect:** No authentication.

```python
# DANGEROUS: Open to anyone who can reach the port
r = redis.Redis(host='localhost', port=6379)
```

**ACL best practices (Redis 6.0+):**

```
# Create specific users with minimal permissions

# Application user - access only app:* keys
user app on >app-secret-password ~app:* +@all -@dangerous -@admin

# Cache user - read/write cache:* keys only
user cache on >cache-password ~cache:* +get +set +del +expire +ttl -@admin

# Analytics user - read-only access
user analytics on >analytics-password ~* +@read -@write -@admin

# Monitoring user - only INFO and monitoring commands
user monitor on >monitor-password ~* +info +slowlog +client +memory -@write
```

**Generate strong passwords:**

```python
import secrets
import string

def generate_redis_password(length=32):
    """Generate a strong password for Redis."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

password = generate_redis_password()
print(f"Generated password: {password}")
```

**Environment-based configuration:**

```python
import os
import redis

# Never hardcode passwords!
r = redis.Redis(
    host=os.environ.get('REDIS_HOST', 'localhost'),
    port=int(os.environ.get('REDIS_PORT', 6379)),
    password=os.environ.get('REDIS_PASSWORD'),
    username=os.environ.get('REDIS_USERNAME'),
    decode_responses=True
)
```

**Verify ACL configuration:**

```python
# Check current user permissions
r.acl_whoami()

# List all users (admin only)
users = r.acl_list()

# Test if user can run a command
can_run = r.acl_dryrun("username", "SET", "key", "value")
```

Reference: [Redis Security](https://redis.io/docs/latest/operate/oss_and_stack/management/security/)

---

### Secure Network Access

**Impact: HIGH** (Prevents network-level attacks and unauthorized access)

## Secure Network Access

Bind Redis to specific interfaces, use TLS, and configure firewalls properly.

**Correct:** Bind to specific interfaces and enable TLS.

```
# In redis.conf

# Only listen on localhost and internal network
bind 127.0.0.1 10.0.0.1

# Enable protected mode (blocks external connections without auth)
protected-mode yes

# Enable TLS (Redis 6.0+)
tls-port 6380
port 0  # Disable non-TLS port

tls-cert-file /path/to/redis.crt
tls-key-file /path/to/redis.key
tls-ca-cert-file /path/to/ca.crt

# Require client certificates (mutual TLS)
tls-auth-clients yes
```

```python
import redis

# Connect with TLS
r = redis.Redis(
    host='redis.example.com',
    port=6380,
    password='your-password',
    ssl=True,
    ssl_certfile='/path/to/client.crt',
    ssl_keyfile='/path/to/client.key',
    ssl_ca_certs='/path/to/ca.crt',
    ssl_cert_reqs='required'  # Verify server certificate
)
```

**Incorrect:** Binding to all interfaces without protection.

```
# DANGEROUS: Open to the world
bind 0.0.0.0
protected-mode no
```

**Network security checklist:**

| Setting | Production Value | Why |
|---------|------------------|-----|
| `bind` | Specific IPs only | Limit network exposure |
| `protected-mode` | `yes` | Block unauthenticated external access |
| `port` | `0` (with TLS) | Disable unencrypted connections |
| `tls-port` | `6380` | Enable encrypted connections |
| `tls-auth-clients` | `yes` | Require client certificates |

**Firewall rules (example with iptables):**

```bash
# Allow Redis only from application servers
iptables -A INPUT -p tcp --dport 6379 -s 10.0.1.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 6379 -j DROP

# Or with UFW
ufw allow from 10.0.1.0/24 to any port 6379
ufw deny 6379
```

**Cloud-specific security:**

```python
# AWS ElastiCache - use security groups and VPC
# Azure Cache for Redis - use private endpoints
# Google Cloud Memorystore - use VPC networks

# Example: AWS ElastiCache connection
r = redis.Redis(
    host='my-cluster.abc123.use1.cache.amazonaws.com',
    port=6379,
    ssl=True,  # Always use TLS with ElastiCache
    password=os.environ['REDIS_AUTH_TOKEN'],
    decode_responses=True
)
```

**Redis Sentinel with TLS:**

```python
from redis.sentinel import Sentinel

sentinel = Sentinel(
    [('sentinel1.example.com', 26379),
     ('sentinel2.example.com', 26379),
     ('sentinel3.example.com', 26379)],
    socket_timeout=0.5,
    sentinel_kwargs={
        'ssl': True,
        'ssl_ca_certs': '/path/to/ca.crt'
    }
)

master = sentinel.master_for(
    'mymaster',
    socket_timeout=0.5,
    password='redis-password',
    ssl=True,
    ssl_ca_certs='/path/to/ca.crt'
)
```

**Disable dangerous commands:**

```
# In redis.conf - rename or disable dangerous commands
rename-command FLUSHALL ""
rename-command FLUSHDB ""
rename-command DEBUG ""
rename-command CONFIG "CONFIG_b840fc02"  # Rename to obscure name
rename-command SHUTDOWN "SHUTDOWN_a1b2c3d4"
```

Reference: [Redis TLS Support](https://redis.io/docs/latest/operate/oss_and_stack/management/security/encryption/)

---

### Use ACLs for Fine-Grained Access Control

**Impact: HIGH** (Principle of least privilege - limit damage from compromised credentials)

## Use ACLs for Fine-Grained Access Control

Use Redis ACLs (Access Control Lists) to grant minimal permissions to each user/application.

**Correct:** Create specific users with limited permissions.

```
# Application user - can only access app:* keys
ACL SETUSER app on >strong-password ~app:* +@all -@dangerous -@admin -DEBUG -SHUTDOWN

# Cache service - read/write cache:* keys, no admin commands
ACL SETUSER cache-service on >cache-password ~cache:* +GET +SET +DEL +EXPIRE +TTL +MGET +MSET -@admin

# Read-only analytics user
ACL SETUSER analytics on >analytics-password ~* +@read -@write -@admin

# Pub/Sub only user
ACL SETUSER pubsub-client on >pubsub-password &channel:* +SUBSCRIBE +PUBLISH +PSUBSCRIBE -@all
```

**Incorrect:** Using default user for everything.

```
# Bad: Single password with full access
requirepass shared-password

# Every application has root access!
```

**ACL command patterns:**

```python
import redis

# As admin, create users
admin = redis.Redis(host='localhost', password='admin-password')

# Create application user
admin.acl_setuser(
    'app',
    enabled=True,
    passwords=['+app-secret-password'],
    keys=['app:*'],
    commands=['+@all', '-@dangerous', '-@admin']
)

# Create read-only user
admin.acl_setuser(
    'readonly',
    enabled=True,
    passwords=['+readonly-password'],
    keys=['*'],
    commands=['+@read', '-@write']
)

# Verify user permissions
admin.acl_getuser('app')
```

**Permission categories:**

| Category | Commands | Use Case |
|----------|----------|----------|
| `@read` | GET, MGET, HGET, etc. | Read-only access |
| `@write` | SET, DEL, LPUSH, etc. | Write access |
| `@admin` | CONFIG, ACL, SLOWLOG, etc. | Administration |
| `@dangerous` | KEYS, FLUSHALL, DEBUG, etc. | Potentially harmful |
| `@fast` | O(1) commands | Low-latency requirements |
| `@slow` | O(N) commands | May need restrictions |
| `@pubsub` | SUBSCRIBE, PUBLISH, etc. | Messaging only |
| `@scripting` | EVAL, EVALSHA, etc. | Lua scripting |

**Key pattern restrictions:**

```
# User can only access keys starting with "user:1001:"
ACL SETUSER limited-user on >password ~user:1001:* +@all -@admin

# Multiple key patterns
ACL SETUSER multi-tenant on >password ~tenant:acme:* ~shared:* +@all -@admin

# Read from one pattern, write to another
ACL SETUSER writer on >password %R~reports:* %W~cache:* +@all -@admin
```

**Channel restrictions (Pub/Sub):**

```
# User can only subscribe to specific channels
ACL SETUSER subscriber on >password &events:* +SUBSCRIBE +PSUBSCRIBE -@all

# User can only publish to specific channels
ACL SETUSER publisher on >password &notifications:* +PUBLISH -@all
```

**Test ACL rules safely:**

```python
# Dry run to test if command would be allowed
result = admin.acl_dryrun('app', 'SET', 'app:key', 'value')
# Returns 'OK' or error message

# Test with a forbidden command
result = admin.acl_dryrun('app', 'FLUSHALL')
# Returns error about permission denied
```

**ACL logging for security monitoring:**

```
# Enable ACL logging in redis.conf
acllog-max-len 128

# View ACL log (failed auth attempts, denied commands)
ACL LOG 10
```

```python
# Check ACL log programmatically
logs = admin.acl_log(10)
for entry in logs:
    print(f"User: {entry['username']}, Command: {entry['object']}, Reason: {entry['reason']}")
```

**Persist ACL configuration:**

```
# Save ACLs to file
ACL SAVE

# In redis.conf, specify ACL file
aclfile /etc/redis/users.acl
```

Reference: [Redis ACL](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/)

---

## 11. Observability

**Impact:** MEDIUM

*SLOWLOG, INFO, MEMORY commands, monitoring metrics, and Redis Insight.*

### Monitor Key Redis Metrics

**Impact: MEDIUM** (Proactive alerting prevents outages)

## Monitor Key Redis Metrics

Set up monitoring and alerts for critical Redis metrics to catch issues before they become outages.

**Critical metrics to monitor:**

| Metric | Warning Threshold | Critical Threshold | Why |
|--------|-------------------|-------------------|-----|
| Memory usage % | >70% | >85% | Prevent OOM |
| Connected clients | >80% of max | >90% of max | Connection exhaustion |
| Blocked clients | >0 | >10 | Blocking operations |
| Command latency (p99) | >10ms | >50ms | Performance degradation |
| Keyspace hit ratio | <90% | <80% | Cache efficiency |
| Replication lag | >1s | >10s | Data consistency |
| Evicted keys/s | >100 | >1000 | Memory pressure |

**Collect metrics via INFO:**

```python
import redis
import time

def collect_redis_metrics(r):
    """Collect key Redis metrics for monitoring."""
    info = r.info()
    
    metrics = {
        # Memory
        "used_memory_bytes": info["used_memory"],
        "used_memory_peak_bytes": info["used_memory_peak"],
        "mem_fragmentation_ratio": info["mem_fragmentation_ratio"],
        
        # Connections
        "connected_clients": info["connected_clients"],
        "blocked_clients": info["blocked_clients"],
        "rejected_connections": info.get("rejected_connections", 0),
        
        # Performance
        "instantaneous_ops_per_sec": info["instantaneous_ops_per_sec"],
        "total_commands_processed": info["total_commands_processed"],
        
        # Keys
        "expired_keys": info["expired_keys"],
        "evicted_keys": info["evicted_keys"],
        
        # Replication
        "connected_slaves": info.get("connected_slaves", 0),
        
        # Persistence
        "rdb_last_bgsave_status": info.get("rdb_last_bgsave_status", "ok"),
    }
    
    # Calculate hit ratio
    hits = info.get("keyspace_hits", 0)
    misses = info.get("keyspace_misses", 0)
    if hits + misses > 0:
        metrics["hit_ratio"] = hits / (hits + misses)
    
    return metrics
```

**Prometheus exporter example:**

```python
from prometheus_client import Gauge, Counter, start_http_server
import redis
import time

# Define metrics
redis_memory_used = Gauge('redis_memory_used_bytes', 'Memory used by Redis')
redis_connected_clients = Gauge('redis_connected_clients', 'Number of connected clients')
redis_commands_processed = Counter('redis_commands_processed_total', 'Total commands processed')
redis_keyspace_hits = Counter('redis_keyspace_hits_total', 'Keyspace hits')
redis_keyspace_misses = Counter('redis_keyspace_misses_total', 'Keyspace misses')

def update_metrics(r):
    """Update Prometheus metrics from Redis INFO."""
    info = r.info()
    
    redis_memory_used.set(info['used_memory'])
    redis_connected_clients.set(info['connected_clients'])
    
    # Counters need special handling
    # (In production, use redis_exporter instead)

# Start metrics server
start_http_server(9090)

r = redis.Redis(host='localhost', port=6379)
while True:
    update_metrics(r)
    time.sleep(15)
```

**Alerting rules (Prometheus/Grafana):**

```yaml
# prometheus-alerts.yml
groups:
  - name: redis
    rules:
      - alert: RedisMemoryHigh
        expr: redis_memory_used_bytes / redis_memory_max_bytes > 0.85
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Redis memory usage is above 85%"
          
      - alert: RedisBlockedClients
        expr: redis_blocked_clients > 10
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Redis has blocked clients"
          
      - alert: RedisReplicationLag
        expr: redis_replication_lag_seconds > 10
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Redis replication lag is high"
          
      - alert: RedisLowHitRatio
        expr: redis_keyspace_hits_total / (redis_keyspace_hits_total + redis_keyspace_misses_total) < 0.8
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Redis cache hit ratio is low"
```

**Health check endpoint:**

```python
from flask import Flask, jsonify
import redis

app = Flask(__name__)
r = redis.Redis(host='localhost', port=6379)

@app.route('/health/redis')
def redis_health():
    """Redis health check endpoint."""
    try:
        # Check connectivity
        r.ping()
        
        info = r.info()
        
        # Check memory
        used_memory = info['used_memory']
        max_memory = info.get('maxmemory', 0)
        
        if max_memory > 0:
            memory_percent = (used_memory / max_memory) * 100
            if memory_percent > 85:
                return jsonify({
                    "status": "degraded",
                    "reason": f"Memory at {memory_percent:.1f}%"
                }), 503
        
        # Check blocked clients
        if info['blocked_clients'] > 10:
            return jsonify({
                "status": "degraded",
                "reason": f"{info['blocked_clients']} blocked clients"
            }), 503
        
        return jsonify({"status": "healthy"}), 200
        
    except redis.ConnectionError:
        return jsonify({"status": "unhealthy", "reason": "Connection failed"}), 503
```

**Use redis_exporter for production:**

```bash
# Deploy redis_exporter alongside Redis
docker run -d --name redis_exporter \
  -p 9121:9121 \
  oliver006/redis_exporter \
  --redis.addr redis://localhost:6379
```

Reference: [Redis Metrics](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency-monitor/)

---

### Use Observability Commands for Debugging

**Impact: MEDIUM** (Essential for troubleshooting production issues)

## Use Observability Commands for Debugging

Use Redis's built-in observability commands to diagnose performance issues and monitor health.

**Essential monitoring commands:**

```python
import redis

r = redis.Redis(host='localhost', port=6379)

# 1. SLOWLOG - Find slow commands
slowlog = r.slowlog_get(10)  # Get last 10 slow commands
for entry in slowlog:
    print(f"Command: {entry['command']}")
    print(f"Duration: {entry['duration']}µs")
    print(f"Time: {entry['start_time']}")
    print("---")

# 2. INFO - Server statistics
info = r.info()
print(f"Connected clients: {info['connected_clients']}")
print(f"Used memory: {info['used_memory_human']}")
print(f"Total commands processed: {info['total_commands_processed']}")

# Specific sections
memory_info = r.info('memory')
replication_info = r.info('replication')
stats_info = r.info('stats')
```

**Memory analysis:**

```python
# Memory usage summary
memory_info = r.info('memory')
print(f"Used memory: {memory_info['used_memory_human']}")
print(f"Peak memory: {memory_info['used_memory_peak_human']}")
print(f"Fragmentation ratio: {memory_info['mem_fragmentation_ratio']}")

# Memory usage of specific key
usage = r.memory_usage("mykey")
print(f"Key 'mykey' uses {usage} bytes")

# Memory doctor (diagnose issues)
r.execute_command("MEMORY", "DOCTOR")
```

**Client connection monitoring:**

```python
# List all connected clients
clients = r.client_list()
for client in clients:
    print(f"Client: {client['addr']}, Cmd: {client['cmd']}, Age: {client['age']}s")

# Get current client info
print(r.client_info())

# Set client name for easier debugging
r.client_setname("my-app-worker-1")
```

**Command statistics:**

```python
# Command stats (how often each command is called)
cmdstats = r.info('commandstats')
for cmd, stats in cmdstats.items():
    print(f"{cmd}: calls={stats['calls']}, usec_per_call={stats.get('usec_per_call', 'N/A')}")
```

**MONITOR for debugging (use carefully!):**

```python
# WARNING: MONITOR impacts performance significantly!
# Use only for debugging, never in production continuously

import threading

def monitor_commands():
    """Monitor all commands (debug only!)."""
    monitor = r.monitor()
    for command in monitor.listen():
        print(f"[{command['time']}] {command['client_address']}: {command['command']}")
        # Stop after 100 commands
        if command['seq'] > 100:
            break

# Run briefly for debugging
thread = threading.Thread(target=monitor_commands, daemon=True)
thread.start()
```

**Key-space analysis:**

```python
# Scan for keys matching pattern (production-safe)
def count_keys_by_pattern(pattern):
    count = 0
    cursor = 0
    while True:
        cursor, keys = r.scan(cursor=cursor, match=pattern, count=1000)
        count += len(keys)
        if cursor == 0:
            break
    return count

# Count keys by prefix
user_keys = count_keys_by_pattern("user:*")
cache_keys = count_keys_by_pattern("cache:*")
print(f"User keys: {user_keys}, Cache keys: {cache_keys}")

# Database size
dbsize = r.dbsize()
print(f"Total keys: {dbsize}")
```

**Configure SLOWLOG:**

```
# In redis.conf
slowlog-log-slower-than 10000  # Log commands > 10ms
slowlog-max-len 128            # Keep 128 entries

# Via command
CONFIG SET slowlog-log-slower-than 10000
```

Reference: [Redis Monitoring](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency-monitor/)

---

## References

- [Redis Documentation](https://redis.io/docs/)
- [Redis Best Practices](https://redis.io/docs/latest/develop/get-started/data-store/)
- [Redis Query Engine](https://redis.io/docs/latest/develop/interact/search-and-query/)
- [RedisVL Documentation](https://redis.io/docs/latest/integrate/redisvl/)
- [Redis Security](https://redis.io/docs/latest/operate/oss_and_stack/management/security/)