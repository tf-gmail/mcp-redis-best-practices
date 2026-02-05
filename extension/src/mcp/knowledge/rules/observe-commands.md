---
title: Use Observability Commands for Debugging
impact: MEDIUM
impactDescription: Essential for troubleshooting production issues
tags: observability, debugging, slowlog, info, memory, monitoring
---

## Use Observability Commands for Debugging

Use Redis's built-in observability commands to diagnose performance issues and monitor health.

**Essential monitoring commands:**

```python
import redis

r = redis.Redis(host='localhost', port=6379)

# 1. SLOWLOG - Find slow commands
slowlog = r.slowlog_get(10)  # Get last 10 slow commands
for entry in slowlog:
    print(f"Command: {entry['command']}")
    print(f"Duration: {entry['duration']}µs")
    print(f"Time: {entry['start_time']}")
    print("---")

# 2. INFO - Server statistics
info = r.info()
print(f"Connected clients: {info['connected_clients']}")
print(f"Used memory: {info['used_memory_human']}")
print(f"Total commands processed: {info['total_commands_processed']}")

# Specific sections
memory_info = r.info('memory')
replication_info = r.info('replication')
stats_info = r.info('stats')
```

**Memory analysis:**

```python
# Memory usage summary
memory_info = r.info('memory')
print(f"Used memory: {memory_info['used_memory_human']}")
print(f"Peak memory: {memory_info['used_memory_peak_human']}")
print(f"Fragmentation ratio: {memory_info['mem_fragmentation_ratio']}")

# Memory usage of specific key
usage = r.memory_usage("mykey")
print(f"Key 'mykey' uses {usage} bytes")

# Memory doctor (diagnose issues)
r.execute_command("MEMORY", "DOCTOR")
```

**Client connection monitoring:**

```python
# List all connected clients
clients = r.client_list()
for client in clients:
    print(f"Client: {client['addr']}, Cmd: {client['cmd']}, Age: {client['age']}s")

# Get current client info
print(r.client_info())

# Set client name for easier debugging
r.client_setname("my-app-worker-1")
```

**Command statistics:**

```python
# Command stats (how often each command is called)
cmdstats = r.info('commandstats')
for cmd, stats in cmdstats.items():
    print(f"{cmd}: calls={stats['calls']}, usec_per_call={stats.get('usec_per_call', 'N/A')}")
```

**MONITOR for debugging (use carefully!):**

```python
# WARNING: MONITOR impacts performance significantly!
# Use only for debugging, never in production continuously

import threading

def monitor_commands():
    """Monitor all commands (debug only!)."""
    monitor = r.monitor()
    for command in monitor.listen():
        print(f"[{command['time']}] {command['client_address']}: {command['command']}")
        # Stop after 100 commands
        if command['seq'] > 100:
            break

# Run briefly for debugging
thread = threading.Thread(target=monitor_commands, daemon=True)
thread.start()
```

**Key-space analysis:**

```python
# Scan for keys matching pattern (production-safe)
def count_keys_by_pattern(pattern):
    count = 0
    cursor = 0
    while True:
        cursor, keys = r.scan(cursor=cursor, match=pattern, count=1000)
        count += len(keys)
        if cursor == 0:
            break
    return count

# Count keys by prefix
user_keys = count_keys_by_pattern("user:*")
cache_keys = count_keys_by_pattern("cache:*")
print(f"User keys: {user_keys}, Cache keys: {cache_keys}")

# Database size
dbsize = r.dbsize()
print(f"Total keys: {dbsize}")
```

**Configure SLOWLOG:**

```
# In redis.conf
slowlog-log-slower-than 10000  # Log commands > 10ms
slowlog-max-len 128            # Keep 128 entries

# Via command
CONFIG SET slowlog-log-slower-than 10000
```

Reference: [Redis Monitoring](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency-monitor/)
