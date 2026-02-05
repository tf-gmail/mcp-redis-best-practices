---
title: Configure Connection Timeouts
impact: HIGH
impactDescription: Prevents hanging connections and cascading failures
tags: connections, timeouts, reliability, socket
---

## Configure Connection Timeouts

Always set socket and connection timeouts to prevent hanging connections from cascading into application failures.

**Correct:** Configure all relevant timeouts.

```python
import redis

# Good: Explicit timeouts for all connection aspects
pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    
    # Connection establishment timeout
    socket_connect_timeout=2.0,  # Fail fast if can't connect in 2s
    
    # Operation timeout (read/write)
    socket_timeout=5.0,  # Fail if operation takes > 5s
    
    # Keep-alive settings
    socket_keepalive=True,
    socket_keepalive_options={
        # TCP_KEEPIDLE: Start keepalive after 60s idle
        1: 60,
        # TCP_KEEPINTVL: Send keepalive every 15s
        2: 15,
        # TCP_KEEPCNT: Close after 3 failed probes
        3: 3,
    },
    
    # Connection pool settings
    max_connections=20,
    
    # Retry configuration
    retry_on_timeout=True,
    retry_on_error=[redis.ConnectionError, redis.TimeoutError],
)

r = redis.Redis(connection_pool=pool)
```

**Incorrect:** No timeout configuration.

```python
# Bad: No timeouts - can hang forever
r = redis.Redis(host='localhost', port=6379)

# If Redis is unresponsive, this blocks indefinitely
result = r.get("key")  # Could hang forever!
```

**Timeout recommendations by use case:**

| Use Case | Connect Timeout | Operation Timeout |
|----------|-----------------|-------------------|
| Web request handler | 1-2s | 2-5s |
| Background job | 5s | 30s |
| Real-time features | 0.5-1s | 1-2s |
| Batch processing | 5s | 60s |
| Health check | 1s | 1s |

**Handle timeout errors gracefully:**

```python
import redis
from redis.exceptions import TimeoutError, ConnectionError

r = redis.Redis(
    host='localhost',
    socket_timeout=2.0,
    socket_connect_timeout=1.0
)

def get_with_fallback(key, default=None):
    """Get value with graceful degradation on timeout."""
    try:
        return r.get(key)
    except TimeoutError:
        logger.warning(f"Redis timeout getting {key}")
        return default
    except ConnectionError:
        logger.error(f"Redis connection error getting {key}")
        return default
```

**Circuit breaker pattern:**

```python
import time
from functools import wraps

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.last_failure_time = None
        self.state = "CLOSED"
    
    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF-OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "HALF-OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except (TimeoutError, ConnectionError) as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            raise

# Usage
circuit_breaker = CircuitBreaker()
result = circuit_breaker.call(r.get, "key")
```

Reference: [Redis Connection Handling](https://redis.io/docs/latest/develop/clients/)
