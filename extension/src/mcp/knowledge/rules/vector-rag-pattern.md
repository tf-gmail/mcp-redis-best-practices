---
title: Implement RAG Pattern Correctly
impact: HIGH
impactDescription: Effective retrieval-augmented generation for LLM applications
tags: vector, rag, llm, embeddings, semantic-search, redisvl
---

## Implement RAG Pattern Correctly

Use Redis as a vector database for retrieval-augmented generation (RAG) to ground LLM responses in your data.

**Correct:** Complete RAG implementation with RedisVL.

```python
from redisvl.index import SearchIndex
from redisvl.query import VectorQuery
from redisvl.utils.vectorize import OpenAITextVectorizer
import redis
import openai

# 1. Define schema
schema = {
    "index": {
        "name": "docs",
        "prefix": "doc:",
    },
    "fields": [
        {"name": "content", "type": "text"},
        {"name": "source", "type": "tag"},
        {"name": "embedding", "type": "vector",
         "attrs": {
             "dims": 1536,
             "distance_metric": "cosine",
             "algorithm": "hnsw",
             "datatype": "float32"
         }}
    ]
}

# 2. Create index
index = SearchIndex.from_dict(schema)
index.connect("redis://localhost:6379")
index.create(overwrite=True)

# 3. Vectorizer (using OpenAI embeddings)
vectorizer = OpenAITextVectorizer(
    model="text-embedding-3-small",
    api_config={"api_key": os.environ["OPENAI_API_KEY"]}
)

# 4. Index documents
def index_documents(documents):
    for doc in documents:
        embedding = vectorizer.embed(doc["content"])
        index.load([{
            "content": doc["content"],
            "source": doc["source"],
            "embedding": embedding
        }])

# 5. RAG query function
def rag_query(question: str, k: int = 5) -> str:
    # Generate query embedding
    query_embedding = vectorizer.embed(question)
    
    # Search for relevant documents
    query = VectorQuery(
        vector=query_embedding,
        vector_field_name="embedding",
        return_fields=["content", "source"],
        num_results=k
    )
    
    results = index.query(query)
    
    # Build context from retrieved documents
    context = "\n\n".join([
        f"Source: {r['source']}\n{r['content']}"
        for r in results
    ])
    
    # Generate response with LLM
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"Answer based on this context:\n\n{context}"},
            {"role": "user", "content": question}
        ]
    )
    
    return response.choices[0].message.content
```

**Incorrect:** RAG without proper chunking or retrieval.

```python
# Bad: Embedding entire documents (too long, loses precision)
embedding = get_embedding(entire_document)  # 10,000+ tokens

# Bad: No relevance filtering
results = index.query(query)  # Returns irrelevant results

# Bad: No source tracking
context = " ".join([r["content"] for r in results])  # Can't verify sources
```

**Chunking strategies:**

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Good chunking for RAG
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,       # ~100-500 tokens per chunk
    chunk_overlap=50,     # Overlap to maintain context
    separators=["\n\n", "\n", ". ", " ", ""]
)

chunks = splitter.split_text(document)

# Index with metadata
for i, chunk in enumerate(chunks):
    embedding = vectorizer.embed(chunk)
    index.load([{
        "content": chunk,
        "source": doc_id,
        "chunk_index": i,
        "embedding": embedding
    }])
```

**Hybrid search (vector + keyword):**

```python
from redisvl.query import FilterQuery

# Combine vector similarity with keyword filters
query = VectorQuery(
    vector=query_embedding,
    vector_field_name="embedding",
    return_fields=["content", "source"],
    num_results=10,
    filter_expression="@source:{technical_docs}"  # Pre-filter by source
)

# Or post-filter with score threshold
results = [r for r in index.query(query) if r["vector_distance"] < 0.3]
```

**RAG best practices:**

| Practice | Why |
|----------|-----|
| Chunk size 100-500 tokens | Balances context and precision |
| Overlap chunks 10-20% | Maintains context across chunks |
| Store metadata | Enable filtering and attribution |
| Use hybrid search | Combine semantic + keyword |
| Set similarity threshold | Filter irrelevant results |
| Include source in prompt | LLM can cite sources |

Reference: [RedisVL Documentation](https://redis.io/docs/latest/integrate/redisvl/)
