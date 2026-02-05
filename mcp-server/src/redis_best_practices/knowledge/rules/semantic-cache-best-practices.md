---
title: Configure Semantic Cache Properly
impact: MEDIUM
impactDescription: Reduces LLM costs and latency through intelligent caching
tags: semantic-cache, llm, langcache, embeddings, caching
---

## Configure Semantic Cache Properly

Use semantic caching to reduce LLM API costs by returning cached responses for semantically similar queries.

**Correct:** Configure LangCache with appropriate thresholds.

```python
from langcache import LangCache
import openai

# Initialize semantic cache
cache = LangCache(
    redis_url="redis://localhost:6379",
    
    # Distance threshold: lower = stricter matching
    # 0.1 = very similar, 0.3 = somewhat similar
    distance_threshold=0.15,
    
    # TTL for cached responses
    ttl=86400,  # 24 hours
    
    # Embedding model
    embedding_model="text-embedding-3-small"
)

# Wrap your LLM calls
@cache.cache
def ask_llm(question: str) -> str:
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": question}]
    )
    return response.choices[0].message.content

# First call: hits LLM API
answer1 = ask_llm("What is the capital of France?")

# Similar query: returns cached response (no API call!)
answer2 = ask_llm("What's the capital city of France?")

# Different query: hits LLM API
answer3 = ask_llm("What is the population of France?")
```

**Incorrect:** Semantic cache with wrong threshold.

```python
# Bad: Threshold too high - returns irrelevant cached responses
cache = LangCache(
    distance_threshold=0.8  # Too permissive!
)

# "What is Python?" might return cached answer for "What is Java?"

# Bad: Threshold too low - rarely hits cache
cache = LangCache(
    distance_threshold=0.01  # Too strict!
)

# Only exact matches will hit cache, defeating the purpose
```

**Threshold guidelines:**

| Threshold | Behavior | Use Case |
|-----------|----------|----------|
| 0.05-0.10 | Very strict | Factual Q&A, exact matches |
| 0.10-0.20 | Balanced | General conversation |
| 0.20-0.30 | Permissive | Creative tasks, summaries |
| >0.30 | Too loose | Risk of wrong cached answers |

**Manual semantic cache with Redis:**

```python
import redis
import numpy as np
from openai import OpenAI

r = redis.Redis(host='localhost', port=6379)
client = OpenAI()

def get_embedding(text: str) -> np.ndarray:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(response.data[0].embedding, dtype=np.float32)

def semantic_cache_get(query: str, threshold: float = 0.15):
    """Check semantic cache for similar query."""
    query_embedding = get_embedding(query)
    
    # Search for similar cached queries
    results = r.execute_command(
        'FT.SEARCH', 'idx:llm_cache',
        f'*=>[KNN 1 @embedding $vec AS distance]',
        'PARAMS', '2', 'vec', query_embedding.tobytes(),
        'RETURN', '2', 'response', 'distance',
        'DIALECT', '2'
    )
    
    if results[0] > 0:
        distance = float(results[2][3])
        if distance <= threshold:
            return results[2][1]  # Return cached response
    
    return None

def semantic_cache_set(query: str, response: str, ttl: int = 86400):
    """Store query-response pair in semantic cache."""
    query_embedding = get_embedding(query)
    key = f"cache:{hash(query)}"
    
    r.hset(key, mapping={
        "query": query,
        "response": response,
        "embedding": query_embedding.tobytes()
    })
    r.expire(key, ttl)
```

**Cache with context awareness:**

```python
# Include relevant context in cache key
def ask_with_context(question: str, context: str) -> str:
    # Combine question + context for cache lookup
    cache_input = f"Context: {context[:500]}\nQuestion: {question}"
    
    cached = semantic_cache_get(cache_input)
    if cached:
        return cached
    
    response = call_llm(question, context)
    semantic_cache_set(cache_input, response)
    return response
```

**Monitor cache effectiveness:**

```python
# Track hit rate
hits = r.incr("cache:stats:hits")
misses = r.incr("cache:stats:misses")
hit_rate = hits / (hits + misses)

# Track cost savings
# Average cost per API call * number of cache hits
```

Reference: [Redis Semantic Cache](https://redis.io/docs/latest/integrate/redisvl/user-guide/semantic-caching/)
