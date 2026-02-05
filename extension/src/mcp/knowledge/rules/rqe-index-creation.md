---
title: Index Only Fields You Query
impact: HIGH
impactDescription: Reduces memory usage and indexing overhead
tags: rqe, indexing, performance, memory, optimization
---

## Index Only Fields You Query

Only create indexes on fields you actually query. Extra indexes waste memory and slow writes.

**Correct:** Index only queried fields.

```python
import redis

r = redis.Redis(host='localhost', port=6379)

# Only index fields that will be searched or filtered
r.execute_command(
    'FT.CREATE', 'idx:orders',
    'ON', 'JSON',
    'PREFIX', '1', 'order:',
    'SCHEMA',
    # Fields we'll query:
    '$.status', 'AS', 'status', 'TAG',           # Filter by status
    '$.customer_id', 'AS', 'customer_id', 'TAG', # Filter by customer
    '$.total', 'AS', 'total', 'NUMERIC', 'SORTABLE',  # Sort by total
    '$.created_at', 'AS', 'created_at', 'NUMERIC', 'SORTABLE'  # Sort by date
    # NOT indexed: order_items, shipping_address, internal_notes
    # These are stored but not searched
)
```

**Incorrect:** Indexing everything.

```python
# Bad: Indexes fields that are never queried
r.execute_command(
    'FT.CREATE', 'idx:orders', 'ON', 'JSON',
    'SCHEMA',
    '$.status', 'AS', 'status', 'TAG',
    '$.customer_id', 'AS', 'customer_id', 'TAG',
    '$.total', 'AS', 'total', 'NUMERIC',
    '$.shipping_address.street', 'AS', 'street', 'TEXT',  # Never searched!
    '$.shipping_address.city', 'AS', 'city', 'TEXT',      # Never searched!
    '$.shipping_address.zip', 'AS', 'zip', 'TAG',         # Never searched!
    '$.internal_notes', 'AS', 'notes', 'TEXT',            # Never searched!
    '$.items[*].sku', 'AS', 'sku', 'TAG',                 # Never searched!
    '$.items[*].name', 'AS', 'item_name', 'TEXT'          # Never searched!
)
# Result: 4x memory usage, slower writes, no benefit
```

**Check index memory usage:**

```python
# See how much memory the index uses
info = r.execute_command('FT.INFO', 'idx:orders')
# Look for: "index_data_size_mb"

# Compare before and after adding fields
# Rule of thumb: TEXT fields use more memory than TAG
```

**Partial indexing with FILTER:**

```python
# Only index active orders (not archived)
r.execute_command(
    'FT.CREATE', 'idx:active_orders',
    'ON', 'JSON',
    'PREFIX', '1', 'order:',
    'FILTER', '@status!="archived"',  # Only index non-archived
    'SCHEMA',
    '$.status', 'AS', 'status', 'TAG',
    '$.customer_id', 'AS', 'customer_id', 'TAG'
)
```

**NOINDEX for stored-only fields:**

```python
# Store field for retrieval but don't index it
r.execute_command(
    'FT.CREATE', 'idx:products',
    'ON', 'JSON',
    'SCHEMA',
    '$.name', 'AS', 'name', 'TEXT',
    '$.price', 'AS', 'price', 'NUMERIC', 'SORTABLE',
    '$.long_description', 'AS', 'description', 'TEXT', 'NOINDEX'  # Stored, not indexed
)
```

**Index optimization tips:**

| Scenario | Recommendation |
|----------|----------------|
| High write volume | Fewer indexed fields |
| Read-heavy | Index what you query |
| Large TEXT fields | Consider NOINDEX or TAG |
| Array fields | Index only if queried |
| Nested objects | Index leaf fields only |

**Monitor index performance:**

```python
# Check indexing lag
info = r.execute_command('FT.INFO', 'idx:orders')
# Look for:
# - "indexing" (should be "complete")
# - "percent_indexed" (should be 100%)
# - "number_of_uses" (query count)

# Profile slow queries
r.execute_command('FT.PROFILE', 'idx:products', 'SEARCH', 'QUERY', '@name:headphones')
```

Reference: [Redis Index Creation](https://redis.io/docs/latest/develop/interact/search-and-query/indexing/)
