---
title: Secure Network Access
impact: HIGH
impactDescription: Prevents network-level attacks and unauthorized access
tags: security, network, tls, ssl, firewall, binding
---

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
