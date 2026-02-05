---
title: Configure Memory Limits and Eviction Policies
impact: HIGH
impactDescription: Prevents out-of-memory crashes and unpredictable behavior
tags: memory, maxmemory, eviction, oom, configuration
---

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
