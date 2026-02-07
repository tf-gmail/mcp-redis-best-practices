---
title: Use Read Replicas for Read-Heavy Workloads
impact: MEDIUM
impactDescription: Scales read throughput and reduces primary load
tags: cluster, replication, read-replicas, scaling, high-availability
---

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
