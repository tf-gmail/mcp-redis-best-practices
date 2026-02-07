# @redis-best-practices/mcp-server

> Redis Best Practices as an MCP server for AI assistants.

[![npm version](https://img.shields.io/npm/v/@redis-best-practices/mcp-server)](https://www.npmjs.com/package/@redis-best-practices/mcp-server)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
# Use with npx (no install needed)
npx @redis-best-practices/mcp-server

# Or install globally
npm install -g @redis-best-practices/mcp-server
redis-best-practices-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop config:

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

## Usage with VS Code

Install the [Redis Best Practices MCP](https://marketplace.visualstudio.com/items?itemName=ThomasFindelkind.redis-best-practices-mcp) extension instead.

## Usage with Visual Studio

Install the [Redis Best Practices MCP](https://marketplace.visualstudio.com/items?itemName=ThomasFindelkind.redis-best-practices-vs) extension, or add to your solution's `.mcp.json`:

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

## Available Tools

| Tool | Description |
|------|-------------|
| `get_best_practice` | Get detailed guidance for a specific Redis topic |
| `list_topics` | Browse all 29 best practice topics by category |
| `search_best_practices` | Search across all practices with keywords |
| `get_anti_patterns` | Learn what NOT to do with Redis |
| `get_code_example` | Get production-ready code snippets |
| `get_full_guide` | Get the complete best practices document |

## Programmatic Usage

```typescript
import { KnowledgeBase, getBestPractice } from '@redis-best-practices/mcp-server';

const kb = new KnowledgeBase();
const practice = getBestPractice(kb, 'conn-pooling');
console.log(practice);
```

## License

MIT
