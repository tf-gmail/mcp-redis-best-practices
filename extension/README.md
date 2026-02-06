# Redis Best Practices MCP

> Get expert Redis guidance directly in your IDE through GitHub Copilot and AI assistants.

[![Visual Studio Marketplace Version](https://img.shields.io/visual-studio-marketplace/v/ThomasFindelkind.redis-best-practices-mcp)](https://marketplace.visualstudio.com/items?itemName=ThomasFindelkind.redis-best-practices-mcp)
[![Visual Studio Marketplace Installs](https://img.shields.io/visual-studio-marketplace/i/ThomasFindelkind.redis-best-practices-mcp)](https://marketplace.visualstudio.com/items?itemName=ThomasFindelkind.redis-best-practices-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Features

### 🎯 AI-Powered Redis Expertise
Ask GitHub Copilot about Redis best practices and get instant, accurate answers with code examples.

### 📚 Comprehensive Knowledge Base
**29 rules** across **11 categories** covering everything from basic key naming to advanced vector search patterns.

### 🛠️ Six Powerful Tools

| Tool | Description |
|------|-------------|
| `get_best_practice` | Get detailed guidance on specific topics |
| `list_topics` | Browse all available topics by category |
| `search_best_practices` | Search across all rules by keyword |
| `get_anti_patterns` | Learn what NOT to do |
| `get_code_example` | Get production-ready code snippets |
| `get_full_guide` | Get the complete best practices guide |

### ⚡ Zero Configuration
Just install and start asking questions. No setup required.

### 🚀 Lightweight
Pure TypeScript/Node.js. No Python, no Docker, no external dependencies.

---

## 📖 Usage

### Ask GitHub Copilot

Simply ask Copilot about Redis in natural language:

```
"What are the best practices for Redis connection pooling?"

"How should I name Redis keys?"

"When should I use Hash vs JSON in Redis?"

"Show me anti-patterns for Redis memory management"

"Give me a Python example for pipelining"
```

### Use Commands

Open the Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`):

- **Redis: Show Best Practice Topics** - Browse all available topics
- **Redis: Restart MCP Server** - Restart the MCP server if needed

---

## 📋 Topics Covered

### 🔴 High Impact

| Category | Topics |
|----------|--------|
| **Data Structures & Keys** | Structure selection, key naming conventions |
| **Memory & Expiration** | Memory limits, eviction policies, TTL strategies |
| **Connection & Performance** | Pooling, pipelining, timeouts, blocking commands |
| **Security** | Authentication, ACLs, network security, TLS |
| **Redis Query Engine** | Field types, index creation, query optimization |
| **Vector Search** | HNSW vs FLAT, RAG patterns, RedisVL |

### 🟡 Medium Impact

| Category | Topics |
|----------|--------|
| **JSON Documents** | Hash vs JSON, partial updates, path queries |
| **Semantic Caching** | LangCache, distance thresholds |
| **Streams & Pub/Sub** | Pattern selection, consumer groups |
| **Clustering** | Hash tags, read replicas |
| **Observability** | SLOWLOG, INFO, metrics monitoring |

---

## 💡 Examples

### Get Best Practices
Ask: *"What's the best practice for Redis key naming?"*

Response includes:
- ✅ Correct patterns with examples
- ❌ Anti-patterns to avoid
- 📊 Performance impact
- 🔗 Links to official Redis docs

### Get Code Examples
Ask: *"Show me a Python example for connection pooling"*

```python
import redis

# Good: Connection pool - reuses existing connections
pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    max_connections=50,
    decode_responses=True
)
r = redis.Redis(connection_pool=pool)
```

### Search Across All Practices
Ask: *"Search for cache stampede prevention"*

Finds relevant rules even if you don't know the exact topic name.

---

## ⚙️ Requirements

- **VS Code** 1.99.0 or later
- **GitHub Copilot** extension (recommended)

---

## 🔧 Extension Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `redisBestPractices.enabled` | `true` | Enable/disable the MCP server |

---

## 🤝 Contributing

Found an issue or want to add more best practices?

1. Open an issue on [GitHub](https://github.com/tf-gmail/mcp-redis-best-practices/issues)
2. Submit a pull request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🔗 Resources

- [Redis Documentation](https://redis.io/docs/)
- [Redis Best Practices](https://redis.io/docs/latest/develop/get-started/best-practices/)
- [MCP Specification](https://modelcontextprotocol.io/)
- [GitHub Repository](https://github.com/tf-gmail/mcp-redis-best-practices)
