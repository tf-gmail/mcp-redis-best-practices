/**
 * Tool definitions for the Redis Best Practices MCP Server.
 * 
 * This module defines all available MCP tools and their implementations.
 */

import { KnowledgeBase } from './knowledge.js';

/**
 * Tool definitions following MCP specification.
 */
export const TOOLS = [
    {
        name: 'get_best_practice',
        description: `Get Redis best practices for a specific topic.

Returns detailed guidance including:
- Why the practice matters
- Correct code examples with explanations
- Incorrect patterns to avoid (anti-patterns)
- Performance impact and quantified benefits
- Links to official Redis documentation

Use this when you need specific guidance on a Redis topic like:
- Key naming conventions
- Data structure selection
- Connection pooling
- Pipelining
- Memory management
- Security configuration`,
        inputSchema: {
            type: 'object',
            properties: {
                topic: {
                    type: 'string',
                    description: "The topic to get best practices for. Examples: 'key-naming', 'data-structures', 'connection-pooling', 'pipelining', 'memory', 'ttl', 'security', 'json', 'streams', 'pub-sub', 'clustering', 'vector-search', 'semantic-cache'",
                },
            },
            required: ['topic'],
        },
    },
    {
        name: 'list_topics',
        description: `List all available Redis best practice topics.

Returns topics organized by category and impact level:
- HIGH impact: Data structures, connections, memory, security, query engine, vector search
- MEDIUM impact: JSON, streams, pub/sub, clustering, semantic caching, observability

Optionally filter by category to see only relevant topics.`,
        inputSchema: {
            type: 'object',
            properties: {
                category: {
                    type: 'string',
                    description: "Optional category filter. One of: 'data', 'connection', 'memory', 'security', 'json', 'streams', 'clustering', 'vector', 'semantic-cache', 'observability'",
                    enum: ['data', 'connection', 'memory', 'security', 'json', 'streams', 'clustering', 'vector', 'semantic-cache', 'observability'],
                },
            },
            required: [],
        },
    },
    {
        name: 'search_best_practices',
        description: `Search across all Redis best practices using keywords.

Performs a semantic search across all rules and returns matching practices
ranked by relevance. Use this when you're not sure which topic to look up
or when searching for specific patterns like:
- "how to avoid hot keys"
- "rate limiting"
- "cache stampede"
- "KEYS command alternatives"
- "large values"
- "blocking operations"`,
        inputSchema: {
            type: 'object',
            properties: {
                query: {
                    type: 'string',
                    description: "Search query - can be a question, keyword, or description of what you're looking for",
                },
            },
            required: ['query'],
        },
    },
    {
        name: 'get_anti_patterns',
        description: `Get common Redis anti-patterns and mistakes to avoid.

Returns a list of things NOT to do, organized by category:
- Blocking commands in production (KEYS *, SMEMBERS on large sets)
- Missing key expiration leading to memory bloat
- Connection leaks from not using pools
- Big keys that cause latency spikes
- Inefficient data structure choices

Optionally filter by topic to see category-specific anti-patterns.`,
        inputSchema: {
            type: 'object',
            properties: {
                topic: {
                    type: 'string',
                    description: "Optional topic filter for anti-patterns. Examples: 'commands', 'memory', 'connections', 'data-structures', 'security'",
                },
            },
            required: [],
        },
    },
    {
        name: 'get_code_example',
        description: `Get working code examples for a specific Redis pattern.

Returns production-ready code snippets with:
- Complete, runnable examples
- Comments explaining each step
- Error handling patterns
- Configuration options

Supports multiple languages: Python (redis-py), Node.js (ioredis), Java (Jedis/Lettuce).`,
        inputSchema: {
            type: 'object',
            properties: {
                pattern: {
                    type: 'string',
                    description: "The pattern to get code for. Examples: 'connection-pool', 'pipeline', 'transaction', 'pub-sub', 'stream-consumer', 'rate-limiter', 'cache-aside', 'session-store', 'leaderboard', 'vector-search'",
                },
                language: {
                    type: 'string',
                    description: 'Programming language for the example',
                    enum: ['python', 'javascript', 'java'],
                    default: 'python',
                },
            },
            required: ['pattern'],
        },
    },
    {
        name: 'get_full_guide',
        description: `Get the complete Redis best practices guide.

Returns the full AGENTS.md document containing all 29 rules across 11 categories.
Use this when you need comprehensive context about Redis best practices or
when working on a large Redis implementation that touches multiple areas.

Categories included:
1. Data Structures & Keys (HIGH)
2. Memory & Expiration (HIGH)
3. Connection & Performance (HIGH)
4. JSON Documents (MEDIUM)
5. Redis Query Engine (HIGH)
6. Vector Search & RedisVL (HIGH)
7. Semantic Caching (MEDIUM)
8. Streams & Pub/Sub (MEDIUM)
9. Clustering & Replication (MEDIUM)
10. Security (HIGH)
11. Observability (MEDIUM)`,
        inputSchema: {
            type: 'object',
            properties: {},
            required: [],
        },
    },
];

/**
 * Get best practices for a specific topic.
 */
export function getBestPractice(kb: KnowledgeBase, topic: string): string {
    // Normalize topic name
    const topicNormalized = topic.toLowerCase().trim().replace(/ /g, '-').replace(/_/g, '-');

    // Try to find exact match first
    const rule = kb.getRuleByTopic(topicNormalized);
    if (rule) {
        return kb.ruleToMarkdown(rule);
    }

    // Try fuzzy match
    const matches = kb.searchRules(topic);
    if (matches.length > 0) {
        return kb.ruleToMarkdown(matches[0]);
    }

    // List available topics as fallback
    const available = kb.listAllTopics();
    return `Topic '${topic}' not found.

Available topics:
${available.map(t => `  - ${t}`).join('\n')}

Tip: Use 'search_best_practices' to search by keyword, or 'list_topics' to browse by category.`;
}

/**
 * List all available topics, optionally filtered by category.
 */
export function listTopics(kb: KnowledgeBase, category?: string): string {
    const sections = kb.getSections(category);

    const lines: string[] = ['# Redis Best Practices Topics\n'];

    for (const section of sections) {
        const impactBadge = section.impact === 'HIGH' ? '🔴' : section.impact === 'MEDIUM' ? '🟡' : '🟢';
        lines.push(`\n## ${section.number}. ${section.name} (${impactBadge} ${section.impact})`);
        lines.push(`*${section.description}*\n`);

        for (const rule of section.rules) {
            lines.push(`  - \`${rule.prefix}\` - ${rule.title}`);
        }
    }

    return lines.join('\n');
}

/**
 * Search across all best practices.
 */
export function searchBestPractices(kb: KnowledgeBase, query: string): string {
    if (!query.trim()) {
        return 'Please provide a search query.';
    }

    const matches = kb.searchRules(query);

    if (matches.length === 0) {
        return `No results found for '${query}'.

Try:
- Different keywords (e.g., 'cache' instead of 'caching')
- Broader terms (e.g., 'memory' instead of 'maxmemory')
- Use 'list_topics' to browse available topics`;
    }

    const lines: string[] = [`# Search Results for '${query}'\n`];
    lines.push(`Found ${matches.length} matching practice(s):\n`);

    // Top 5 results
    for (let i = 0; i < Math.min(matches.length, 5); i++) {
        const rule = matches[i];
        lines.push(`## ${i + 1}. ${rule.title}`);
        lines.push(`**Impact:** ${rule.impact} - ${rule.impactDescription}`);
        lines.push(`**Tags:** ${rule.tags.join(', ')}\n`);
        lines.push(rule.summary);
        lines.push(`\n*Use \`get_best_practice('${rule.prefix}')\` for full details.*\n`);
        lines.push('---\n');
    }

    return lines.join('\n');
}

/**
 * Get common anti-patterns and mistakes.
 */
export function getAntiPatterns(kb: KnowledgeBase, topic?: string): string {
    const antiPatterns = kb.getAntiPatterns(topic);

    const lines: string[] = ['# Redis Anti-Patterns to Avoid\n'];

    if (topic) {
        lines.push(`*Filtered by: ${topic}*\n`);
    }

    for (const [category, patterns] of Object.entries(antiPatterns)) {
        lines.push(`\n## ${category}\n`);
        for (const pattern of patterns) {
            lines.push(`### ❌ ${pattern.title}`);
            lines.push(`**Why it's bad:** ${pattern.reason}`);
            lines.push(`\n\`\`\`${pattern.language}`);
            lines.push(pattern.badCode);
            lines.push('```\n');
            lines.push('**Instead, do this:**\n');
            lines.push(`\`\`\`${pattern.language}`);
            lines.push(pattern.goodCode);
            lines.push('```\n');
        }
    }

    return lines.join('\n');
}

/**
 * Get code examples for a specific pattern.
 */
export function getCodeExample(kb: KnowledgeBase, pattern: string, language: string = 'python'): string {
    const example = kb.getCodeExample(pattern, language);

    if (!example) {
        const available = kb.listCodeExamples();
        return `No code example found for pattern '${pattern}' in ${language}.

Available patterns:
${available.map(p => `  - ${p}`).join('\n')}

Available languages: python, javascript, java`;
    }

    const lines: string[] = [`# ${example.title}\n`];
    lines.push(`**Pattern:** ${pattern}`);
    lines.push(`**Language:** ${language}\n`);
    lines.push(example.description);
    lines.push(`\n\`\`\`${language}`);
    lines.push(example.code);
    lines.push('```\n');

    if (example.notes.length > 0) {
        lines.push('## Notes\n');
        for (const note of example.notes) {
            lines.push(`- ${note}`);
        }
    }

    if (example.references.length > 0) {
        lines.push('\n## References\n');
        for (const ref of example.references) {
            lines.push(`- [${ref.title}](${ref.url})`);
        }
    }

    return lines.join('\n');
}

/**
 * Get the complete best practices guide.
 */
export function getFullGuide(kb: KnowledgeBase): string {
    return kb.getFullGuide();
}
