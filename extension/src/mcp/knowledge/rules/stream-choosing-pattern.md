---
title: Choose Streams vs Pub/Sub Appropriately
impact: MEDIUM
impactDescription: Right messaging pattern for durability and delivery requirements
tags: streams, pubsub, messaging, consumer-groups, events
---

## Choose Streams vs Pub/Sub Appropriately

Use Streams for durable messaging with delivery guarantees. Use Pub/Sub for ephemeral real-time notifications.

**When to use Streams:**

- Message persistence required
- Consumer groups needed
- At-least-once delivery guarantees
- Message replay capability
- Slow/offline consumers

**When to use Pub/Sub:**

- Real-time notifications
- Fire-and-forget messages
- No persistence needed
- Broadcast to all subscribers
- Simple fan-out pattern

**Comparison:**

| Feature | Streams | Pub/Sub |
|---------|---------|---------|
| Persistence | ✅ Yes | ❌ No |
| Message replay | ✅ Yes | ❌ No |
| Consumer groups | ✅ Yes | ❌ No |
| Delivery guarantee | At-least-once | At-most-once |
| Offline consumers | ✅ Messages wait | ❌ Messages lost |
| Memory usage | Higher | Lower |
| Use case | Event sourcing, queues | Notifications, cache invalidation |

**Correct:** Use Streams for durable message processing.

```python
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Producer: Add message to stream
message_id = r.xadd("events:orders", {
    "type": "order_created",
    "order_id": "12345",
    "user_id": "1001",
    "amount": "99.99"
})

# Create consumer group (run once)
try:
    r.xgroup_create("events:orders", "order-processors", id="0", mkstream=True)
except redis.ResponseError as e:
    if "BUSYGROUP" not in str(e):
        raise

# Consumer: Read from group with acknowledgment
def process_messages():
    while True:
        # Read messages (block up to 5 seconds)
        messages = r.xreadgroup(
            groupname="order-processors",
            consumername="worker-1",
            streams={"events:orders": ">"},
            count=10,
            block=5000
        )
        
        for stream, message_list in messages:
            for message_id, data in message_list:
                try:
                    # Process message
                    process_order(data)
                    # Acknowledge successful processing
                    r.xack("events:orders", "order-processors", message_id)
                except Exception as e:
                    print(f"Failed to process {message_id}: {e}")
                    # Message will be redelivered to another consumer
```

**Correct:** Use Pub/Sub for real-time notifications.

```python
import redis
import threading

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Subscriber (runs in separate thread)
def subscriber():
    pubsub = r.pubsub()
    pubsub.subscribe("notifications:user:1001")
    
    for message in pubsub.listen():
        if message["type"] == "message":
            print(f"Received: {message['data']}")

# Start subscriber in background
thread = threading.Thread(target=subscriber, daemon=True)
thread.start()

# Publisher: Send notification
r.publish("notifications:user:1001", "You have a new message!")
```

**Stream with trimming (bounded memory):**

```python
# Keep only last 10000 messages
r.xadd("events:logs", {"level": "info", "msg": "test"}, maxlen=10000)

# Approximate trimming (faster, ~10000 messages)
r.xadd("events:logs", fields, maxlen=10000, approximate=True)

# Trim by time (keep last 24 hours)
min_id = f"{int(time.time() - 86400) * 1000}-0"
r.xtrim("events:logs", minid=min_id)
```

**Claim pending messages (handle failed consumers):**

```python
# Find stuck messages (pending > 60 seconds)
pending = r.xpending_range(
    "events:orders",
    "order-processors",
    min="-",
    max="+",
    count=10
)

# Claim messages from failed consumer
for entry in pending:
    if entry["time_since_delivered"] > 60000:  # > 60 seconds
        r.xclaim(
            "events:orders",
            "order-processors",
            "worker-2",  # New consumer
            min_idle_time=60000,
            message_ids=[entry["message_id"]]
        )
```

Reference: [Redis Streams](https://redis.io/docs/latest/develop/data-types/streams/)
