---
title: Always Use Authentication in Production
impact: HIGH
impactDescription: Prevents unauthorized access to data
tags: security, authentication, password, requirepass, acl
---

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
