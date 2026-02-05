---
title: Monitor Key Redis Metrics
impact: MEDIUM
impactDescription: Proactive alerting prevents outages
tags: observability, metrics, alerting, monitoring, prometheus
---

## Monitor Key Redis Metrics

Set up monitoring and alerts for critical Redis metrics to catch issues before they become outages.

**Critical metrics to monitor:**

| Metric | Warning Threshold | Critical Threshold | Why |
|--------|-------------------|-------------------|-----|
| Memory usage % | >70% | >85% | Prevent OOM |
| Connected clients | >80% of max | >90% of max | Connection exhaustion |
| Blocked clients | >0 | >10 | Blocking operations |
| Command latency (p99) | >10ms | >50ms | Performance degradation |
| Keyspace hit ratio | <90% | <80% | Cache efficiency |
| Replication lag | >1s | >10s | Data consistency |
| Evicted keys/s | >100 | >1000 | Memory pressure |

**Collect metrics via INFO:**

```python
import redis
import time

def collect_redis_metrics(r):
    """Collect key Redis metrics for monitoring."""
    info = r.info()
    
    metrics = {
        # Memory
        "used_memory_bytes": info["used_memory"],
        "used_memory_peak_bytes": info["used_memory_peak"],
        "mem_fragmentation_ratio": info["mem_fragmentation_ratio"],
        
        # Connections
        "connected_clients": info["connected_clients"],
        "blocked_clients": info["blocked_clients"],
        "rejected_connections": info.get("rejected_connections", 0),
        
        # Performance
        "instantaneous_ops_per_sec": info["instantaneous_ops_per_sec"],
        "total_commands_processed": info["total_commands_processed"],
        
        # Keys
        "expired_keys": info["expired_keys"],
        "evicted_keys": info["evicted_keys"],
        
        # Replication
        "connected_slaves": info.get("connected_slaves", 0),
        
        # Persistence
        "rdb_last_bgsave_status": info.get("rdb_last_bgsave_status", "ok"),
    }
    
    # Calculate hit ratio
    hits = info.get("keyspace_hits", 0)
    misses = info.get("keyspace_misses", 0)
    if hits + misses > 0:
        metrics["hit_ratio"] = hits / (hits + misses)
    
    return metrics
```

**Prometheus exporter example:**

```python
from prometheus_client import Gauge, Counter, start_http_server
import redis
import time

# Define metrics
redis_memory_used = Gauge('redis_memory_used_bytes', 'Memory used by Redis')
redis_connected_clients = Gauge('redis_connected_clients', 'Number of connected clients')
redis_commands_processed = Counter('redis_commands_processed_total', 'Total commands processed')
redis_keyspace_hits = Counter('redis_keyspace_hits_total', 'Keyspace hits')
redis_keyspace_misses = Counter('redis_keyspace_misses_total', 'Keyspace misses')

def update_metrics(r):
    """Update Prometheus metrics from Redis INFO."""
    info = r.info()
    
    redis_memory_used.set(info['used_memory'])
    redis_connected_clients.set(info['connected_clients'])
    
    # Counters need special handling
    # (In production, use redis_exporter instead)

# Start metrics server
start_http_server(9090)

r = redis.Redis(host='localhost', port=6379)
while True:
    update_metrics(r)
    time.sleep(15)
```

**Alerting rules (Prometheus/Grafana):**

```yaml
# prometheus-alerts.yml
groups:
  - name: redis
    rules:
      - alert: RedisMemoryHigh
        expr: redis_memory_used_bytes / redis_memory_max_bytes > 0.85
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Redis memory usage is above 85%"
          
      - alert: RedisBlockedClients
        expr: redis_blocked_clients > 10
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Redis has blocked clients"
          
      - alert: RedisReplicationLag
        expr: redis_replication_lag_seconds > 10
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Redis replication lag is high"
          
      - alert: RedisLowHitRatio
        expr: redis_keyspace_hits_total / (redis_keyspace_hits_total + redis_keyspace_misses_total) < 0.8
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Redis cache hit ratio is low"
```

**Health check endpoint:**

```python
from flask import Flask, jsonify
import redis

app = Flask(__name__)
r = redis.Redis(host='localhost', port=6379)

@app.route('/health/redis')
def redis_health():
    """Redis health check endpoint."""
    try:
        # Check connectivity
        r.ping()
        
        info = r.info()
        
        # Check memory
        used_memory = info['used_memory']
        max_memory = info.get('maxmemory', 0)
        
        if max_memory > 0:
            memory_percent = (used_memory / max_memory) * 100
            if memory_percent > 85:
                return jsonify({
                    "status": "degraded",
                    "reason": f"Memory at {memory_percent:.1f}%"
                }), 503
        
        # Check blocked clients
        if info['blocked_clients'] > 10:
            return jsonify({
                "status": "degraded",
                "reason": f"{info['blocked_clients']} blocked clients"
            }), 503
        
        return jsonify({"status": "healthy"}), 200
        
    except redis.ConnectionError:
        return jsonify({"status": "unhealthy", "reason": "Connection failed"}), 503
```

**Use redis_exporter for production:**

```bash
# Deploy redis_exporter alongside Redis
docker run -d --name redis_exporter \
  -p 9121:9121 \
  oliver006/redis_exporter \
  --redis.addr redis://localhost:6379
```

Reference: [Redis Metrics](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency-monitor/)
