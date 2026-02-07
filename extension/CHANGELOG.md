# Changelog

All notable changes to the "Redis Best Practices MCP" extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-02-07

### Added

- **6 new best practice rules** from official Redis Agent Skills:
  - `rqe-dialect` - Use DIALECT 2 for query syntax
  - `rqe-index-management` - Index lifecycle management
  - `rqe-query-optimization` - Query performance optimization
  - `semantic-cache-langcache-usage` - LangCache usage patterns
  - `vector-hybrid-search` - Hybrid search with filters
  - `vector-index-creation` - Vector index configuration
- Now includes all 29 rules from the official Redis Agent Skills repository

## [0.1.4] - 2026-02-06

### Changed

- Added prominent TIP at top of README highlighting "Redis: Setup Copilot Instructions" command
- Improved discoverability of auto-trigger feature

## [0.1.3] - 2026-02-06

### Added

- New command: "Redis: Setup Copilot Instructions" - automatically creates/updates `.github/copilot-instructions.md`
- Makes Copilot automatically use Redis best practice tools when working with Redis code

## [0.1.2] - 2026-02-06

### Added

- Added "Pro Tip" section in README for auto-triggering best practices via copilot-instructions.md
- Example configuration for making Copilot automatically consult Redis tools

## [0.1.1] - 2026-02-06

### Fixed

- Fixed publisher ID consistency in package.json and README badges
- Updated marketplace links to use correct extension identifier

## [0.1.0] - 2026-02-05

### Added

- **MCP Server** - Model Context Protocol server for AI assistant integration
- **6 Tools** for accessing Redis best practices:
  - `get_best_practice` - Get detailed guidance on specific topics
  - `list_topics` - Browse all available topics by category
  - `search_best_practices` - Search across all rules by keyword
  - `get_anti_patterns` - Learn common mistakes to avoid
  - `get_code_example` - Get production-ready code snippets (Python, JavaScript, Java)
  - `get_full_guide` - Get the complete 29-rule best practices guide
- **29 Best Practice Rules** across 11 categories:
  - Data Structures & Keys
  - Memory & Expiration
  - Connection & Performance
  - JSON Documents
  - Redis Query Engine
  - Vector Search & RedisVL
  - Semantic Caching
  - Streams & Pub/Sub
  - Clustering & Replication
  - Security
  - Observability
- **VS Code Commands**:
  - `Redis: Show Best Practice Topics` - Quick topic browser
  - `Redis: Restart MCP Server` - Server management
- **Status Bar Indicator** - Shows MCP server status
- **Configuration Options** - Enable/disable the extension

### Technical

- Pure TypeScript/Node.js implementation
- Zero external dependencies
- Compatible with VS Code 1.99.0+
- Works with GitHub Copilot and MCP-compatible AI assistants
