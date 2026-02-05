---
title: Use ACLs for Fine-Grained Access Control
impact: HIGH
impactDescription: Principle of least privilege - limit damage from compromised credentials
tags: security, acl, authorization, permissions, users
---

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
