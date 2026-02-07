#!/usr/bin/env node
/**
 * CLI entry point for Redis Best Practices MCP Server.
 * 
 * Usage:
 *   npx @redis-best-practices/mcp-server
 *   redis-best-practices-mcp
 */

import { runServer } from './server.js';

runServer().catch((error) => {
    console.error('Fatal error:', error);
    process.exit(1);
});
