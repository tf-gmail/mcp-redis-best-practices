# Claude Desktop Configuration

To use the Redis Best Practices MCP server with Claude Desktop, add the following to your `claude_desktop_config.json`:

## Location

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

## Configuration

### Option 1: Using local clone (Recommended)

First, clone and build the repository:

```bash
git clone https://github.com/tf-gmail/mcp-redis-best-practices.git
cd mcp-redis-best-practices/extension
npm install
npm run compile
npm run copy-knowledge
```

Then add to your Claude config:

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

Replace `/path/to` with the actual path to where you cloned the repository.

### Option 2: Using npx (if published to npm)

```json
{
  "mcpServers": {
    "redis-best-practices": {
      "command": "npx",
      "args": ["mcp-redis-best-practices"]
    }
  }
}
```

## Verification

After configuring, restart Claude Desktop. You should see the Redis Best Practices tools available when you ask Claude about Redis topics:

- "What are Redis key naming best practices?"
- "How should I implement connection pooling in Redis?"
- "What are common Redis anti-patterns to avoid?"

## Troubleshooting

If the MCP server doesn't appear:

1. Check that Node.js is installed (`node --version`)
2. Verify the path in the configuration is correct
3. Check Claude Desktop logs for errors
4. Try running the server manually to verify it works:
   ```bash
   cd /path/to/mcp-redis-best-practices/extension
   node dist/mcp/server.js
   ```
