# MCP Redis Best Practices

> Model Context Protocol (MCP) server providing Redis development best practices as AI tools. Integrates with GitHub Copilot, Claude Desktop, and other MCP-compatible clients.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.0-green.svg)](https://modelcontextprotocol.io/)

## Overview

This project provides an MCP server that exposes Redis best practices as callable tools. Instead of relying on potentially outdated AI training data, developers get authoritative, up-to-date guidance on Redis patterns, anti-patterns, and optimizations directly in their coding workflow.

**Inspired by:** [Redis Agent Skills](https://redis.io/blog/we-built-an-agent-skill-so-ai-writes-redis-code/) - The approach of providing AI agents with expert knowledge through structured best practices.

## Features

- 🎯 **On-Demand Best Practices** - Get expert guidance when you need it
- 📚 **Comprehensive Knowledge Base** - 23 rules across 11 categories
- 🔍 **Searchable** - Find practices by keyword or use case
- 💡 **Code Examples** - Real-world Python examples for every pattern
- ⚠️ **Anti-Patterns** - Learn what to avoid
- 🔄 **Always Current** - Knowledge base updated independently of AI models

## Knowledge Base Coverage

| Category | Topics | Impact |
|----------|--------|--------|
| **Data Structures** | Structure selection, key naming | HIGH |
| **Connections** | Pooling, pipelining, blocking commands, timeouts | HIGH |
| **Memory Management** | Limits, TTL strategies | HIGH |
| **Security** | Authentication, network, ACLs | HIGH |
| **JSON** | Hash vs JSON, partial updates | MEDIUM |
| **Streams** | Pattern selection | MEDIUM |
| **Clustering** | Hash tags, read replicas | MEDIUM |
| **Observability** | Commands, metrics | MEDIUM |
| **Redis Query Engine** | Field types, index creation | HIGH |
| **Vector Search** | Algorithm choice, RAG patterns | HIGH |
| **Semantic Cache** | Caching best practices | MEDIUM |

---

## Quick Start

### VS Code / GitHub Copilot

1. **Clone the repository:**
   ```bash
   git clone https://github.com/tf-gmail/mcp-redis-best-practices.git
   cd mcp-redis-best-practices
   ```

2. **Install the MCP server:**
   ```bash
   cd mcp-server
   pip install -e ".[dev]"
   ```

3. **Open VS Code in the project directory.** The `.vscode/mcp.json` will automatically configure the MCP server.

4. **Ask GitHub Copilot** about Redis:
   ```
   What's the best practice for Redis connection pooling?
   Show me anti-patterns for Redis key naming
   How should I structure keys for a multi-tenant application?
   ```

### Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "redis-best-practices": {
      "command": "python",
      "args": ["-m", "redis_best_practices"],
      "cwd": "/path/to/mcp-redis-best-practices/mcp-server"
    }
  }
}
```

See [docs/claude-desktop-config.md](docs/claude-desktop-config.md) for detailed setup instructions.

### Standalone Usage

```bash
# Run the MCP server
cd mcp-server
python -m redis_best_practices

# Or using the installed command
mcp-redis-best-practices
```

---

## Available Tools

The MCP server exposes 6 tools:

### `get_best_practice`
Get detailed best practices for a specific topic.

```
Parameters:
  - topic (required): Topic identifier (e.g., "conn-pooling", "data-key-naming")
```

### `list_topics`
List all available topics, optionally filtered by category.

```
Parameters:
  - category (optional): Filter by category (e.g., "security", "connection")
```

### `search_best_practices`
Search across all practices by keyword.

```
Parameters:
  - query (required): Search query
  - max_results (optional): Maximum results (default: 5)
```

### `get_anti_patterns`
Get common anti-patterns to avoid.

```
Parameters:
  - topic (optional): Filter by topic
```

### `get_code_example`
Get code examples for a specific pattern.

```
Parameters:
  - pattern (required): Pattern name (e.g., "connection-pool", "pipeline")
  - language (required): Programming language (e.g., "python")
```

### `get_full_guide`
Get the complete Redis best practices guide.

```
Parameters: none
```

---

## Development

### Project Structure

```
mcp-redis-best-practices/
├── mcp-server/
│   ├── pyproject.toml              # Package configuration
│   ├── build.py                    # AGENTS.md generator
│   ├── AGENTS.md                   # Compiled knowledge base
│   ├── src/
│   │   └── redis_best_practices/
│   │       ├── __init__.py
│   │       ├── __main__.py         # Entry point for -m execution
│   │       ├── server.py           # MCP server implementation
│   │       ├── tools.py            # Tool definitions
│   │       └── knowledge/
│   │           ├── __init__.py     # KnowledgeBase class
│   │           └── rules/          # Individual rule files
│   │               ├── _sections.md
│   │               ├── conn-pooling.md
│   │               ├── data-key-naming.md
│   │               └── ...
│   └── tests/
│       ├── conftest.py
│       ├── test_knowledge.py
│       ├── test_server.py
│       └── test_agents.py
├── .vscode/
│   ├── mcp.json                    # MCP server configuration
│   ├── extensions.json             # Recommended extensions
│   └── settings.json               # VS Code settings
└── docs/
    └── claude-desktop-config.md    # Claude Desktop setup guide
```

### Building AGENTS.md

The `AGENTS.md` file is compiled from individual rule files:

```bash
cd mcp-server
python build.py
```

### Running Tests

```bash
cd mcp-server
pip install -e ".[dev]"
pytest
```

### Adding New Rules

1. Create a new markdown file in `mcp-server/src/redis_best_practices/knowledge/rules/`
2. Use the naming convention: `{prefix}-{rule-name}.md`
3. Include YAML frontmatter with title, impact, and tags
4. Rebuild AGENTS.md: `python build.py`

**Rule template:**

```markdown
---
title: Your Rule Title
impact: HIGH | MEDIUM | LOW
tags:
  - relevant
  - tags
---

## Overview

Brief description of the rule.

## Best Practice

Detailed explanation.

### Good Pattern
```python
# Example code
```

### Anti-Pattern
```python
# What to avoid
```

## Code Examples

Additional examples...
```

---

## Configuration

### VS Code Settings

The `.vscode/mcp.json` file configures the MCP server:

```json
{
  "servers": {
    "redis-best-practices": {
      "command": "python3",
      "args": ["-m", "redis_best_practices"],
      "cwd": "${workspaceFolder}/mcp-server"
    }
  }
}
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |

---

## Example Queries

Once installed, ask your AI assistant:

- *"What are Redis key naming conventions?"*
- *"When should I use a Hash vs a String in Redis?"*
- *"How do I implement pipelining in Redis?"*
- *"What are common Redis anti-patterns to avoid?"*
- *"Show me connection pooling best practices for Redis"*
- *"How should I handle Redis key expiration?"*
- *"What's the best algorithm for vector search in Redis?"*
- *"How do I set up semantic caching with Redis?"*

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add/update rules in the knowledge base
4. Run tests: `pytest`
5. Submit a pull request

### Rule Guidelines

- Each rule should focus on ONE specific topic
- Include practical code examples
- Explain WHY the practice is important
- Document anti-patterns to avoid
- Use HIGH impact for critical best practices

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Resources

- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification
- [Redis Documentation](https://redis.io/docs/) - Official Redis docs
- [Redis Agent Skills Blog](https://redis.io/blog/we-built-an-agent-skill-so-ai-writes-redis-code/) - Inspiration for this project
