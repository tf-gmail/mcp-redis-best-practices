# Redis Best Practices MCP - Visual Studio Extension

Get expert Redis guidance in Visual Studio via GitHub Copilot. 29 best practices for data structures, memory, security, vector search, and more - powered by MCP (Model Context Protocol).

## Features

This extension provides two commands in the **Tools** menu:

1. **Redis: Setup MCP Server** - Configures the Redis Best Practices MCP server in your solution's `.mcp.json` file
2. **Redis: Setup Copilot Instructions** - Creates/updates `.github/copilot-instructions.md` to auto-trigger Redis tools

## Requirements

- Visual Studio 2022 version 17.14 or later
- GitHub Copilot extension installed and active
- Node.js 18+ installed (for MCP server runtime)

## Installation

### From Visual Studio Marketplace

1. Open Visual Studio
2. Go to **Extensions** → **Manage Extensions**
3. Search for "Redis Best Practices MCP"
4. Click **Download** and restart Visual Studio

### Manual Installation

1. Download the `.vsix` file from the [releases page](https://github.com/tf-gmail/mcp-redis-best-practices/releases)
2. Double-click the `.vsix` file to install

## Quick Start

### Option 1: Use the Setup Commands (Recommended)

1. Open your solution in Visual Studio
2. Go to **Tools** → **Redis: Setup MCP Server**
3. Go to **Tools** → **Redis: Setup Copilot Instructions**
4. Restart Copilot Chat
5. Start asking Redis questions - Copilot will automatically use the Redis tools!

### Option 2: Manual Configuration

Create `.mcp.json` in your solution root:

```json
{
  "servers": {
    "redis-best-practices": {
      "command": "npx",
      "args": ["-y", "@redis-best-practices/mcp-server"]
    }
  }
}
```

## Available MCP Tools

Once configured, Copilot has access to these tools:

| Tool | Description |
|------|-------------|
| `get_best_practice` | Get detailed guidance for a specific Redis topic |
| `list_topics` | Browse all 29 best practice topics by category |
| `search_best_practices` | Search across all practices with keywords |
| `get_anti_patterns` | Learn what NOT to do with Redis |
| `get_code_example` | Get production-ready code snippets |
| `get_full_guide` | Get the complete best practices document |

## Topics Covered

### HIGH Impact
- Data Structures & Key Naming
- Connection Pooling & Pipelining
- Memory Management & TTLs
- Security (Auth, ACLs, Network)
- Redis Query Engine (RQE)
- Vector Search & RedisVL

### MEDIUM Impact
- JSON Documents
- Streams & Pub/Sub
- Clustering & Replication
- Semantic Caching
- Observability

## Example Copilot Conversations

```
"What's the best way to structure Redis keys for a multi-tenant app?"

"How should I configure connection pooling in C#?"

"Show me anti-patterns for Redis memory management"

"Generate a rate limiter using Redis"
```

## Also Available For

- **VS Code**: [Redis Best Practices MCP](https://marketplace.visualstudio.com/items?itemName=ThomasFindelkind.redis-best-practices-mcp)
- **CLI/Standalone**: `npx @redis-best-practices/mcp-server`

## Building from Source

```bash
# Clone the repo
git clone https://github.com/tf-gmail/mcp-redis-best-practices.git
cd mcp-redis-best-practices

# Install dependencies
pnpm install

# Build the MCP server (required first)
pnpm build:server

# Build the Visual Studio extension
cd visual-studio
dotnet build
```

## Contributing

Contributions welcome! Please see the [main repository](https://github.com/tf-gmail/mcp-redis-best-practices) for guidelines.

## License

MIT License - see [LICENSE](../LICENSE) for details.
