# Claude Desktop Configuration

To use the Redis Best Practices MCP server with Claude Desktop, add the following to your `claude_desktop_config.json`:

## Location

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

## Configuration

### Option 1: Using uvx (Recommended)

```json
{
  "mcpServers": {
    "redis-best-practices": {
      "command": "uvx",
      "args": ["mcp-redis-best-practices"]
    }
  }
}
```

### Option 2: Using pip installed package

```json
{
  "mcpServers": {
    "redis-best-practices": {
      "command": "python",
      "args": ["-m", "redis_best_practices"]
    }
  }
}
```

### Option 3: Using local development version

```json
{
  "mcpServers": {
    "redis-best-practices": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/mcp-redis-best-practices/mcp-server", "mcp-redis-best-practices"]
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

1. Check that Python 3.10+ is installed
2. Verify the path in the configuration is correct
3. Check Claude Desktop logs for errors
4. Try running the server manually to verify it works:
   ```bash
   uvx mcp-redis-best-practices
   ```
