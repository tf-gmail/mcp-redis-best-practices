# Redis Best Practices MCP Server

This is the core MCP server that provides Redis best practices as callable tools.

## Installation

```bash
# Install in development mode
pip install -e ".[dev]"

# Or install from the package
pip install .
```

## Running the Server

```bash
# Using the module entry point
python -m redis_best_practices

# Using the installed script
mcp-redis-best-practices
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=redis_best_practices

# Run specific test file
pytest tests/test_knowledge.py
```

## Building AGENTS.md

The `AGENTS.md` file is a compiled version of all rule files for quick reference:

```bash
python build.py
```

## Project Structure

```
mcp-server/
├── pyproject.toml              # Package configuration
├── build.py                    # AGENTS.md generator
├── AGENTS.md                   # Compiled knowledge base
├── src/
│   └── redis_best_practices/
│       ├── __init__.py         # Package init, exports main()
│       ├── __main__.py         # Entry point for -m execution
│       ├── server.py           # MCP server implementation
│       ├── tools.py            # Tool definitions
│       └── knowledge/
│           ├── __init__.py     # KnowledgeBase class
│           └── rules/          # Individual rule markdown files
└── tests/
    ├── conftest.py             # Pytest configuration
    ├── test_knowledge.py       # KnowledgeBase tests
    ├── test_server.py          # Server tests
    └── test_agents.py          # AGENTS.md generation tests
```

## Available Tools

| Tool | Description |
|------|-------------|
| `get_best_practice` | Get best practices for a specific topic |
| `list_topics` | List all available topics |
| `search_best_practices` | Search across all practices |
| `get_anti_patterns` | Get common anti-patterns |
| `get_code_example` | Get code examples for a pattern |
| `get_full_guide` | Get the complete guide |

## Adding New Rules

1. Create a markdown file in `src/redis_best_practices/knowledge/rules/`
2. Use naming convention: `{section-prefix}-{rule-name}.md`
3. Include YAML frontmatter:
   ```yaml
   ---
   title: Rule Title
   impact: HIGH | MEDIUM | LOW
   tags:
     - tag1
     - tag2
   ---
   ```
4. Rebuild: `python build.py`
