# MCP Redis Best Practices

> Model Context Protocol (MCP) server providing Redis development best practices as AI tools. Integrates with GitHub Copilot in **VS Code** and **Visual Studio**, Claude Desktop, and other MCP-compatible clients.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-1.0-green.svg)](https://modelcontextprotocol.io/)
[![VS Code](https://img.shields.io/badge/VS%20Code-Extension-blue.svg)](https://marketplace.visualstudio.com/items?itemName=ThomasFindelkind.redis-best-practices-mcp)
[![Visual Studio](https://img.shields.io/badge/Visual%20Studio-Extension-purple.svg)](https://marketplace.visualstudio.com/items?itemName=ThomasFindelkind.redis-best-practices-vs)
[![npm](https://img.shields.io/badge/npm-@redis--best--practices/mcp--server-red.svg)](https://www.npmjs.com/package/@redis-best-practices/mcp-server)

## Overview

This project provides an MCP server that exposes Redis best practices as callable tools. Instead of relying on potentially outdated AI training data, developers get authoritative, up-to-date guidance on Redis patterns, anti-patterns, and optimizations directly in their coding workflow.

**Inspired by:** [Redis Agent Skills](https://redis.io/blog/we-built-an-agent-skill-so-ai-writes-redis-code/) - The approach of providing AI agents with expert knowledge through structured best practices.

## Features

- 🎯 **On-Demand Best Practices** - Get expert guidance when you need it
- 📚 **Comprehensive Knowledge Base** - 29 rules across 11 categories
- 🔍 **Searchable** - Find practices by keyword or use case
- 💡 **Code Examples** - Real-world examples for every pattern
- ⚠️ **Anti-Patterns** - Learn what to avoid
- 🚀 **No Dependencies** - Pure TypeScript/Node.js, no Python required
- 🔄 **Always Current** - Knowledge base updated independently of AI models
- 💻 **Multi-IDE Support** - Works in VS Code AND Visual Studio

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
| **Redis Query Engine** | Dialect, field types, index creation, optimization | HIGH |
| **Vector Search** | Algorithm choice, RAG patterns, hybrid search, index creation | HIGH |
| **Semantic Cache** | LangCache usage, caching best practices | MEDIUM |

---

## Quick Start

### VS Code (Recommended)

1. **Install from VS Code Marketplace:**
   - Search for "Redis Best Practices MCP" in the Extensions view
   - Or install from [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=ThomasFindelkind.redis-best-practices-mcp)

2. **Run the setup command:**
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Run **"Redis: Setup Copilot Instructions"**

3. **Ask GitHub Copilot** about Redis:
   ```
   What's the best practice for Redis connection pooling?
   Show me anti-patterns for Redis key naming
   How should I structure keys for a multi-tenant application?
   ```

### Visual Studio (2022 v17.14+)

1. **Install from VS Marketplace:**
   - Go to **Extensions** → **Manage Extensions**
   - Search for "Redis Best Practices MCP"
   - Or install from [Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=ThomasFindelkind.redis-best-practices-vs)

2. **Configure the MCP server:**
   - Go to **Tools** → **Redis: Setup MCP Server**
   - Go to **Tools** → **Redis: Setup Copilot Instructions**

3. **Restart Copilot Chat** and start asking Redis questions!

### Standalone npm Package

Use with any MCP-compatible client:

```bash
npx @redis-best-practices/mcp-server
```

Or install globally:

```bash
npm install -g @redis-best-practices/mcp-server
redis-best-practices-mcp
```

### Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "redis-best-practices": {
      "command": "npx",
      "args": ["-y", "@redis-best-practices/mcp-server"]
    }
  }
}
```

See [docs/claude-desktop-config.md](docs/claude-desktop-config.md) for detailed setup instructions.

---

## Available Tools

The MCP server exposes 6 tools:

| Tool | Description |
|------|-------------|
| `get_best_practice` | Get detailed guidance for a specific Redis topic |
| `list_topics` | Browse all 29 best practice topics by category |
| `search_best_practices` | Search across all practices with keywords |
| `get_anti_patterns` | Learn what NOT to do with Redis |
| `get_code_example` | Get production-ready code snippets |
| `get_full_guide` | Get the complete best practices document |

### Tool Details

#### `get_best_practice`
```
Parameters:
  - topic (required): Topic identifier (e.g., "conn-pooling", "data-key-naming")
```

#### `list_topics`
```
Parameters:
  - category (optional): Filter by category (e.g., "security", "connection")
```

#### `search_best_practices`
```
Parameters:
  - query (required): Search query
```

#### `get_anti_patterns`
```
Parameters:
  - topic (optional): Filter by topic
```

#### `get_code_example`
```
Parameters:
  - pattern (required): Pattern name (e.g., "connection-pool", "pipeline")
  - language (required): Programming language ("python", "javascript", "java")
```

#### `get_full_guide`
```
Parameters: none
```

---

## Project Structure

This is a monorepo supporting multiple deployment targets:

```
mcp-redis-best-practices/
├── packages/
│   └── mcp-server/              # Shared MCP server (npm package)
│       ├── src/
│       │   ├── index.ts         # Package exports
│       │   ├── cli.ts           # CLI entry point
│       │   ├── server.ts        # MCP server implementation
│       │   ├── tools.ts         # Tool definitions
│       │   ├── knowledge.ts     # Knowledge base loader
│       │   └── types.ts         # Type definitions
│       └── knowledge/rules/     # 29 markdown best practice files
│
├── extension/                   # VS Code extension
│   ├── src/
│   │   └── extension.ts         # VS Code-specific code
│   └── package.json
│
├── visual-studio/               # Visual Studio extension
│   ├── src/
│   │   ├── RedisBestPracticesExtension.cs
│   │   ├── SetupCopilotInstructionsCommand.cs
│   │   └── SetupMCPServerCommand.cs
│   └── RedisBestPracticesMCP.csproj
│
├── package.json                 # pnpm workspace root
├── pnpm-workspace.yaml
└── docs/
```

---

## Development

### Prerequisites

- Node.js 18+
- pnpm 8+ (recommended) or npm
- .NET 8 SDK (for Visual Studio extension)

### Building Everything

```bash
# Install dependencies
pnpm install

# Build all packages
pnpm build

# Or build individually:
pnpm build:server      # MCP server package
pnpm build:vscode      # VS Code extension
pnpm build:vs          # Visual Studio extension
```

### Building the VS Code Extension

```bash
cd extension
npm install
npm run build
npm run package  # Creates .vsix file
```

### Building the Visual Studio Extension

```bash
cd visual-studio
dotnet build
# VSIX will be in bin/Debug or bin/Release
```

### Running Tests

```bash
cd extension
npm test
```

### Adding New Rules

1. Create a new markdown file in `packages/mcp-server/knowledge/rules/`
2. Use the naming convention: `{prefix}-{rule-name}.md`
3. Include YAML frontmatter with title, impact, and tags
4. Rebuild: `pnpm build`

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

\`\`\`python
# Example correct code
\`\`\`

**Incorrect:** Description of what to avoid.

\`\`\`python
# Example incorrect code
\`\`\`

Reference: [Link Title](https://url)
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
4. Run tests
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
