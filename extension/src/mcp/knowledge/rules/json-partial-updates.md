---
title: Use JSON Paths for Partial Updates
impact: MEDIUM
impactDescription: Reduces bandwidth and enables atomic nested updates
tags: json, partial-updates, jsonpath, redisjson
---

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
