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
        description: `**CALL THIS TOOL** when writing, reviewing, or debugging code that uses Redis clients like StackExchange.Redis, ioredis, redis-py, Jedis, Lettuce, or go-redis.

Trigger scenarios:
1. Implementing connection multiplexing or connection pooling
2. Designing key naming strategies (namespace:entity:id patterns)
3. Choosing between Redis data structures (String vs Hash vs Sorted Set)
4. Implementing caching patterns (cache-aside, write-through, TTL strategy)
5. Optimizing Redis Query Engine (RQE) indexes and FT.SEARCH queries
6. Setting up vector similarity search with HNSW or FLAT indexes
7. Configuring Redis Sentinel or Cluster sharding
8. Implementing rate limiting or session storage

Returns: Best practices with correct/incorrect code examples, performance impact, and official Redis documentation links.`,
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
        description: `Browse available Redis best practice topics by category.

Use this to discover what guidance is available when:
- Starting a new Redis integration project
- Conducting a Redis code review
- Planning Redis architecture for a new service

Categories: data structures, connections, memory, TTL, security, JSON, streams, clustering, vector search, semantic caching, observability.`,
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
        description: `Search Redis best practices by keyword or problem description.

**HIGH-PRIORITY SIGNALS** - Call this tool when you see:
- Performance issues: "hot keys", "cache stampede", "thundering herd", "latency spikes"
- Memory concerns: "memory leak", "OOM", "eviction", "big keys", "large values"
- Dangerous operations: "KEYS *", "SMEMBERS on large set", "HGETALL", "FLUSHALL"
- Architecture questions: "Redis Sentinel", "Cluster sharding", "pipelining", "Lua scripting"
- Data modeling: "choose data structure", "sorted set vs list", "hash vs string"

Returns ranked matches with relevance scores.`,
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
        description: `**MANDATORY CHECK** before generating Redis code that uses potentially dangerous operations.

**MUST CALL THIS TOOL** when code contains:
- KEYS * or KEYS pattern (use SCAN instead)
- SMEMBERS/HGETALL/LRANGE 0 -1 on potentially large collections
- FLUSHALL or FLUSHDB in production code
- Missing EXPIRE/PEXPIRE on cached data
- Single connection without pooling under load
- Synchronous operations in async contexts
- Unbounded memory growth patterns

Returns: Anti-patterns with severity, correct alternatives, and O(n) complexity warnings.`,
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
        description: `Get production-ready Redis code examples for common patterns.

Call when implementing:
- Connection pooling setup (redis-py, ioredis, Jedis, Lettuce)
- Pipelining for batch operations (reduce RTT by 10-100x)
- Transactions with MULTI/EXEC and optimistic locking
- Pub/Sub messaging patterns
- Stream consumers with consumer groups (XREADGROUP)
- Rate limiting with sliding window or token bucket
- Cache-aside pattern with proper invalidation
- Session storage with automatic expiration
- Leaderboards with ZADD/ZRANGE
- Vector similarity search with RedisVL

Returns: Complete, runnable code with error handling and comments. Languages: Python, JavaScript/Node.js, Java.`,
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
        description: `Get the complete Redis best practices guide (all 29 rules).

**Call when:**
- Starting a brand new Redis integration project
- Conducting a comprehensive Redis architecture review
- Preparing Redis production readiness checklist
- Onboarding developers to Redis best practices

Returns the full AGENTS.md document with 11 categories:
Data Structures, Memory/TTL, Connections, JSON, Query Engine, Vector Search, Semantic Caching, Streams, Clustering, Security, Observability.`,
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
