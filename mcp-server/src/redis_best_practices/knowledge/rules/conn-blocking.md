---
title: Avoid Slow Commands in Production
impact: HIGH
impactDescription: Prevents blocking that can take down entire Redis instance
tags: performance, blocking, keys-command, smembers, slow-commands
---

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
