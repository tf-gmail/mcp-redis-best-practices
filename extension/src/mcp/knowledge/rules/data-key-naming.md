---
title: Use Consistent Key Naming Conventions
impact: MEDIUM
impactDescription: Improved maintainability and debugging
tags: keys, naming, conventions, prefixes, namespacing
---

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
