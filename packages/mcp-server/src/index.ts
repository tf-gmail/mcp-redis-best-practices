/**
 * Redis Best Practices MCP Server
 * 
 * Provides Redis development best practices as MCP tools for AI assistants.
 * 
 * @packageDocumentation
 */

// Re-export everything from server module
export {
    createServer,
    runServer,
    KnowledgeBase,
    TOOLS,
    getBestPractice,
    listTopics,
    searchBestPractices,
    getAntiPatterns,
    getCodeExample,
    getFullGuide,
} from './server.js';

// Re-export types
export type {
    Rule,
    Section,
    AntiPattern,
    CodeExample,
    Reference,
} from './types.js';
