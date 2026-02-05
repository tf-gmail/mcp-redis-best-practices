---
title: Choose JSON vs Hash Appropriately
impact: MEDIUM
impactDescription: Optimal storage for document data
tags: json, hash, documents, nested, redisjson
---

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
