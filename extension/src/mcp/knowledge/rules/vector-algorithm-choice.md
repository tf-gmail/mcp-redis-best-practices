---
title: Choose HNSW vs FLAT Based on Requirements
impact: HIGH
impactDescription: Right algorithm choice affects latency, accuracy, and memory
tags: vector, hnsw, flat, knn, similarity-search, embeddings
---

## Choose HNSW vs FLAT Based on Requirements

Select the right vector index algorithm based on your dataset size, accuracy needs, and latency requirements.

**HNSW vs FLAT comparison:**

| Feature | HNSW | FLAT |
|---------|------|------|
| Algorithm | Approximate KNN | Exact KNN |
| Accuracy | ~95-99% | 100% |
| Latency | O(log n) | O(n) |
| Memory | Higher | Lower |
| Build time | Longer | Instant |
| Best for | >10K vectors | <10K vectors |
| Updates | Slower | Instant |

**Correct:** Use HNSW for large datasets.

```python
import redis
import numpy as np

r = redis.Redis(host='localhost', port=6379)

# HNSW for large-scale similarity search (>10K vectors)
r.execute_command(
    'FT.CREATE', 'idx:embeddings',
    'ON', 'HASH',
    'PREFIX', '1', 'doc:',
    'SCHEMA',
    'embedding', 'VECTOR', 'HNSW', '10',
        'TYPE', 'FLOAT32',
        'DIM', '384',           # Embedding dimension
        'DISTANCE_METRIC', 'COSINE',
        'M', '16',              # Connections per layer (16-64)
        'EF_CONSTRUCTION', '200', # Build-time quality (100-500)
    'content', 'TEXT'
)

# Query with HNSW
embedding = get_embedding("search query")
results = r.execute_command(
    'FT.SEARCH', 'idx:embeddings',
    f'*=>[KNN 10 @embedding $vec AS score]',
    'PARAMS', '2', 'vec', embedding.tobytes(),
    'SORTBY', 'score',
    'RETURN', '2', 'content', 'score',
    'DIALECT', '2'
)
```

**Correct:** Use FLAT for small datasets or 100% accuracy.

```python
# FLAT for small datasets (<10K) or when exact results needed
r.execute_command(
    'FT.CREATE', 'idx:products_flat',
    'ON', 'HASH',
    'PREFIX', '1', 'product:',
    'SCHEMA',
    'embedding', 'VECTOR', 'FLAT', '6',
        'TYPE', 'FLOAT32',
        'DIM', '384',
        'DISTANCE_METRIC', 'COSINE'
)
```

**HNSW parameter tuning:**

```python
# High accuracy, slower build
r.execute_command(
    'FT.CREATE', 'idx:high_accuracy',
    'ON', 'HASH', 'SCHEMA',
    'embedding', 'VECTOR', 'HNSW', '10',
        'TYPE', 'FLOAT32',
        'DIM', '384',
        'DISTANCE_METRIC', 'COSINE',
        'M', '32',              # Higher M = more accurate, more memory
        'EF_CONSTRUCTION', '400' # Higher = better index, slower build
)

# At query time, increase EF_RUNTIME for better accuracy
results = r.execute_command(
    'FT.SEARCH', 'idx:high_accuracy',
    f'*=>[KNN 10 @embedding $vec EF_RUNTIME 250 AS score]',
    'PARAMS', '2', 'vec', embedding.tobytes(),
    'DIALECT', '2'
)
```

**Distance metrics:**

| Metric | Use Case | Range |
|--------|----------|-------|
| `COSINE` | Text embeddings, semantic search | 0-2 (lower=similar) |
| `L2` (Euclidean) | Image embeddings, general | 0-∞ (lower=similar) |
| `IP` (Inner Product) | When vectors are normalized | Higher=similar |

**Memory estimation:**

```python
# HNSW memory per vector (approximate):
# base_size = dim * 4 bytes (FLOAT32)
# hnsw_overhead = M * 2 * 4 bytes per layer
# Example: 384-dim, M=16, 1M vectors
# Memory ≈ 1M * (384 * 4 + 16 * 2 * 4 * avg_layers) ≈ 2-3 GB

# FLAT memory per vector:
# Memory = dim * 4 bytes per vector
# Example: 384-dim, 1M vectors
# Memory ≈ 1M * 384 * 4 = 1.5 GB
```

**When to choose:**

| Scenario | Algorithm |
|----------|-----------|
| <10K vectors | FLAT |
| 10K-10M vectors | HNSW |
| Need 100% accuracy | FLAT |
| Need low latency at scale | HNSW |
| Frequent vector updates | FLAT (or accept HNSW rebuild) |
| Memory constrained | FLAT |

Reference: [Redis Vector Similarity](https://redis.io/docs/latest/develop/interact/search-and-query/advanced-concepts/vectors/)
