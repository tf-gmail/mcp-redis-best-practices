#!/usr/bin/env node
/**
 * MCP Server implementation for Redis Best Practices.
 * 
 * This module implements the Model Context Protocol server that exposes
 * Redis best practices as callable tools for AI assistants.
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
    CallToolRequestSchema,
    ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

import { KnowledgeBase } from './knowledge.js';
import {
    TOOLS,
    getBestPractice,
    listTopics,
    searchBestPractices,
    getAntiPatterns,
    getCodeExample,
    getFullGuide,
} from './tools.js';

// Initialize the MCP server
const server = new Server(
    {
        name: 'redis-best-practices',
        version: '0.1.0',
    },
    {
        capabilities: {
            tools: {},
        },
    }
);

// Initialize knowledge base
const knowledgeBase = new KnowledgeBase();

/**
 * List all available tools.
 */
server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
        tools: TOOLS,
    };
});

/**
 * Handle tool execution requests.
 */
server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    try {
        let result: string;

        switch (name) {
            case 'get_best_practice': {
                const topic = (args?.topic as string) || '';
                result = getBestPractice(knowledgeBase, topic);
                break;
            }
            case 'list_topics': {
                const category = args?.category as string | undefined;
                result = listTopics(knowledgeBase, category);
                break;
            }
            case 'search_best_practices': {
                const query = (args?.query as string) || '';
                result = searchBestPractices(knowledgeBase, query);
                break;
            }
            case 'get_anti_patterns': {
                const topic = args?.topic as string | undefined;
                result = getAntiPatterns(knowledgeBase, topic);
                break;
            }
            case 'get_code_example': {
                const pattern = (args?.pattern as string) || '';
                const language = (args?.language as string) || 'python';
                result = getCodeExample(knowledgeBase, pattern, language);
                break;
            }
            case 'get_full_guide': {
                result = getFullGuide(knowledgeBase);
                break;
            }
            default:
                result = `Unknown tool: ${name}`;
        }

        return {
            content: [
                {
                    type: 'text',
                    text: result,
                },
            ],
        };
    } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        console.error(`Error executing tool ${name}:`, error);
        return {
            content: [
                {
                    type: 'text',
                    text: `Error: ${errorMessage}`,
                },
            ],
            isError: true,
        };
    }
});

/**
 * Run the MCP server using stdio transport.
 */
async function main() {
    console.error('Starting Redis Best Practices MCP Server...');

    const transport = new StdioServerTransport();
    await server.connect(transport);

    console.error('Redis Best Practices MCP Server running on stdio');
}

main().catch((error) => {
    console.error('Fatal error:', error);
    process.exit(1);
});
