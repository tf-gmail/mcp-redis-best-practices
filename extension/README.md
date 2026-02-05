# Redis Best Practices MCP

> VS Code extension providing Redis best practices through MCP (Model Context Protocol) for GitHub Copilot and AI assistants.

[![Visual Studio Marketplace](https://img.shields.io/visual-studio-marketplace/v/tf-gmail.redis-best-practices-mcp)](https://marketplace.visualstudio.com/items?itemName=tf-gmail.redis-best-practices-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🎯 **On-Demand Best Practices** - Get expert Redis guidance in your coding workflow
- 🤖 **AI-Powered** - Works with GitHub Copilot and other MCP-compatible AI assistants
- 📚 **Comprehensive** - 23 rules across 11 categories
- ⚡ **Zero Configuration** - Just install and start asking questions

## Usage

Once installed, ask GitHub Copilot about Redis:

- *"What are the best practices for Redis connection pooling?"*
- *"How should I name Redis keys?"*
- *"When should I use Hash vs JSON in Redis?"*
- *"What are common Redis anti-patterns to avoid?"*

Or use the command palette:

- `Redis: Show Best Practice Topics` - Browse available topics
- `Redis: Restart MCP Server` - Restart the MCP server

## Topics Covered

| Category | Topics |
|----------|--------|
| **Data Structures** | Key naming, structure selection |
| **Connections** | Pooling, pipelining, timeouts, blocking commands |
| **Memory** | Limits, TTL strategies |
| **Security** | Authentication, ACLs, network |
| **JSON** | Hash vs JSON, partial updates |
| **Query Engine** | Field types, index creation |
| **Vector Search** | Algorithm choice, RAG patterns |
| **Semantic Cache** | Caching patterns |
| **Streams** | Pattern selection |
| **Clustering** | Hash tags, read replicas |
| **Observability** | Commands, metrics |

## Requirements

- VS Code 1.99.0 or later
- Python 3.10+ installed

## Extension Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `redisBestPractices.enabled` | `true` | Enable/disable the MCP server |
| `redisBestPractices.pythonPath` | `python3` | Path to Python interpreter |

## License

MIT License - see [LICENSE](LICENSE) for details.
