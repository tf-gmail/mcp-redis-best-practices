---
title: Use Hash Tags for Multi-Key Operations
impact: MEDIUM
impactDescription: Enables multi-key operations in Redis Cluster
tags: cluster, hash-tags, sharding, multi-key, crossslot
---

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
