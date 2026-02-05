---
title: Choose the Correct Field Type
impact: HIGH
impactDescription: Correct field types enable efficient querying and indexing
tags: rqe, indexing, field-types, search, query-engine
---

## Choose the Correct Field Type

Select the right field type in FT.CREATE for optimal query performance.

**Field types and their use cases:**

| Type | Use Case | Operations | Example |
|------|----------|------------|---------|
| `TEXT` | Full-text search | Tokenized search, stemming | Product descriptions |
| `TAG` | Exact match, categories | Exact match, IN clauses | Status, categories |
| `NUMERIC` | Numbers, ranges | Range queries, sorting | Price, age, count |
| `GEO` | Coordinates | Radius search | Store locations |
| `VECTOR` | Embeddings | KNN, similarity | Semantic search |

**Correct:** Match field type to query patterns.

```python
import redis

r = redis.Redis(host='localhost', port=6379)

# Create index with appropriate field types
r.execute_command(
    'FT.CREATE', 'idx:products',
    'ON', 'JSON',
    'PREFIX', '1', 'product:',
    'SCHEMA',
    # TEXT for full-text search
    '$.name', 'AS', 'name', 'TEXT', 'WEIGHT', '2.0',
    '$.description', 'AS', 'description', 'TEXT',
    
    # TAG for exact match / filtering
    '$.category', 'AS', 'category', 'TAG',
    '$.brand', 'AS', 'brand', 'TAG',
    '$.status', 'AS', 'status', 'TAG',
    
    # NUMERIC for ranges and sorting
    '$.price', 'AS', 'price', 'NUMERIC', 'SORTABLE',
    '$.rating', 'AS', 'rating', 'NUMERIC', 'SORTABLE',
    '$.stock', 'AS', 'stock', 'NUMERIC',
    
    # GEO for location queries
    '$.location', 'AS', 'location', 'GEO'
)
```

**Incorrect:** Using TEXT for categorical data.

```python
# Bad: TEXT tokenizes values, breaks exact match
r.execute_command(
    'FT.CREATE', 'idx:products', 'ON', 'JSON',
    'SCHEMA',
    '$.status', 'AS', 'status', 'TEXT'  # Wrong! "in stock" becomes two tokens
)

# This won't work as expected:
# FT.SEARCH idx:products "@status:in stock"  # Searches for "in" AND "stock"
```

**TAG vs TEXT comparison:**

```python
# Store product
r.json().set("product:1", "$", {
    "name": "Wireless Bluetooth Headphones",  # TEXT: searchable words
    "category": "electronics>audio>headphones",  # TAG: exact hierarchy
    "tags": ["wireless", "bluetooth", "premium"],  # TAG array
    "status": "in stock"  # TAG: exact match
})

# TEXT search: finds "bluetooth" in name
r.execute_command('FT.SEARCH', 'idx:products', '@name:bluetooth')

# TAG exact match: finds exact category
r.execute_command('FT.SEARCH', 'idx:products', '@category:{electronics>audio>headphones}')

# TAG with multiple values
r.execute_command('FT.SEARCH', 'idx:products', '@tags:{wireless|premium}')
```

**SORTABLE for sorting fields:**

```python
# Add SORTABLE for fields you'll ORDER BY
r.execute_command(
    'FT.CREATE', 'idx:products', 'ON', 'JSON',
    'SCHEMA',
    '$.price', 'AS', 'price', 'NUMERIC', 'SORTABLE',  # Will sort by price
    '$.created_at', 'AS', 'created_at', 'NUMERIC', 'SORTABLE'  # Will sort by date
)

# Now sorting works efficiently
r.execute_command('FT.SEARCH', 'idx:products', '*', 'SORTBY', 'price', 'ASC')
```

**INDEX vs NOINDEX:**

```python
# Only index fields you'll actually query
r.execute_command(
    'FT.CREATE', 'idx:users', 'ON', 'JSON',
    'SCHEMA',
    '$.email', 'AS', 'email', 'TAG',  # Indexed: will search
    '$.name', 'AS', 'name', 'TEXT',  # Indexed: will search
    '$.internal_notes', 'AS', 'notes', 'TEXT', 'NOINDEX'  # Not indexed: just stored
)
```

Reference: [Redis Query Engine Field Types](https://redis.io/docs/latest/develop/interact/search-and-query/basic-constructs/field-and-type-options/)
