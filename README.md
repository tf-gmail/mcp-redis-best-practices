# MCP Redis Best Practices

> Model Context Protocol (MCP) server providing Redis development best practices as AI tools. Integrates with GitHub Copilot, Claude Desktop, and other MCP-compatible clients.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-1.0-green.svg)](https://modelcontextprotocol.io/)
[![VS Code](https://img.shields.io/badge/VS%20Code-Extension-blue.svg)](https://marketplace.visualstudio.com/items?itemName=tf-gmail.redis-best-practices-mcp)

## Overview

This project provides an MCP server that exposes Redis best practices as callable tools. Instead of relying on potentially outdated AI training data, developers get authoritative, up-to-date guidance on Redis patterns, anti-patterns, and optimizations directly in their coding workflow.

**Inspired by:** [Redis Agent Skills](https://redis.io/blog/we-built-an-agent-skill-so-ai-writes-redis-code/) - The approach of providing AI agents with expert knowledge through structured best practices.

## Features

- 🎯 **On-Demand Best Practices** - Get expert guidance when you need it
- 📚 **Comprehensive Knowledge Base** - 23 rules across 11 categories
- 🔍 **Searchable** - Find practices by keyword or use case
- 💡 **Code Examples** - Real-world examples for every pattern
- ⚠️ **Anti-Patterns** - Learn what to avoid
- 🚀 **No Dependencies** - Pure TypeScript/Node.js, no Python required
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

### VS Code Extension (Recommended)

The easiest way to use Redis Best Practices MCP:

1. **Install from VS Code Marketplace:**
   - Search for "Redis Best Practices MCP" in the Extensions view
   - Or install from [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=tf-gmail.redis-best-practices-mcp)

2. **Ask GitHub Copilot** about Redis:
   ```
   What's the best practice for Redis connection pooling?
   Show me anti-patterns for Redis key naming
   How should I structure keys for a multi-tenant application?
   ```

### Manual Setup (Development)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/tf-gmail/mcp-redis-best-practices.git
   cd mcp-redis-best-practices
   ```

2. **Install and build:**
   ```bash
   cd extension
   npm install
   npm run compile
   npm run copy-knowledge
   ```

3. **Open VS Code in the project directory.** The `.vscode/mcp.json` will automatically configure the MCP server.

### Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "redis-best-practices": {
      "command": "node",
      "args": ["/path/to/mcp-redis-best-practices/extension/dist/mcp/server.js"]
    }
  }
}
```

See [docs/claude-desktop-config.md](docs/claude-desktop-config.md) for detailed setup instructions.

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
├── extension/                      # VS Code Extension (TypeScript)
│   ├── package.json                # Extension manifest
│   ├── tsconfig.json               # TypeScript configuration
│   ├── src/
│   │   ├── extension.ts            # VS Code extension entry
│   │   └── mcp/
│   │       ├── server.ts           # MCP server implementation
│   │       ├── tools.ts            # Tool definitions
│   │       ├── knowledge.ts        # KnowledgeBase class
│   │       ├── types.ts            # Type definitions
│   │       └── knowledge/rules/    # Markdown rule files
│   │           ├── _sections.md
│   │           ├── conn-pooling.md
│   │           ├── data-key-naming.md
│   │           └── ...
│   └── dist/                       # Compiled output
├── mcp-server/                     # Legacy Python implementation
├── .vscode/
│   ├── mcp.json                    # MCP server configuration
│   └── settings.json               # VS Code settings
└── docs/
    └── claude-desktop-config.md    # Claude Desktop setup guide
```

### Building the Extension

```bash
cd extension
npm install
npm run compile
npm run copy-knowledge
```

### Packaging for Distribution

```bash
cd extension
npm run package
# Creates redis-best-practices-mcp-X.X.X.vsix
```

### Running Tests

```bash
cd extension
npm test
```

### Adding New Rules

1. Create a new markdown file in `extension/src/mcp/knowledge/rules/`
2. Use the naming convention: `{prefix}-{rule-name}.md`
3. Include YAML frontmatter with title, impact, and tags
4. Rebuild: `npm run compile && npm run copy-knowledge`

**Rule template:**

```markdown
---
title: Your Rule Title
impact: HIGH
impactDescription: Short description of impact
tags: relevant, tags, here
---

## Overview

Brief description of the rule.

**Correct:** Description of correct approach.

```python
# Example correct code
```

**Incorrect:** Description of what to avoid.

```python
# Example incorrect code
```

Reference: [Link Title](https://url)
```

---

## Configuration

### VS Code Settings

The `.vscode/mcp.json` file configures the MCP server:

```json
{
  "servers": {
    "redis-best-practices": {
      "command": "node",
      "args": ["${workspaceFolder}/extension/dist/mcp/server.js"],
      "description": "Redis development best practices as MCP tools"
    }
  }
}
```

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
