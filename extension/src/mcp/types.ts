/**
 * Type definitions for Redis Best Practices MCP Server.
 */

/**
 * A reference link to documentation.
 */
export interface Reference {
    title: string;
    url: string;
}

/**
 * A code example with metadata.
 */
export interface CodeExample {
    title: string;
    description: string;
    code: string;
    language: string;
    notes: string[];
    references: Reference[];
}

/**
 * An anti-pattern to avoid.
 */
export interface AntiPattern {
    title: string;
    reason: string;
    badCode: string;
    goodCode: string;
    language: string;
    category: string;
}

/**
 * A single best practice rule.
 */
export interface Rule {
    prefix: string;
    title: string;
    impact: string;
    impactDescription: string;
    tags: string[];
    content: string;
    summary: string;
    sectionNumber: number;
}

/**
 * A section containing multiple rules.
 */
export interface Section {
    number: number;
    name: string;
    prefix: string;
    impact: string;
    description: string;
    rules: Rule[];
}

/**
 * Category mapping for filtering sections.
 */
export const CATEGORY_MAP: Record<string, string> = {
    'data': 'data',
    'connection': 'conn',
    'memory': 'ram',
    'security': 'security',
    'json': 'json',
    'streams': 'stream',
    'clustering': 'cluster',
    'vector': 'vector',
    'semantic-cache': 'semantic-cache',
    'observability': 'observe',
};

/**
 * Pattern to rule prefix mapping.
 */
export const PATTERN_MAP: Record<string, string> = {
    'connection-pool': 'conn-pooling',
    'pipeline': 'conn-pipelining',
    'pipelining': 'conn-pipelining',
    'transaction': 'conn-pipelining',
    'pub-sub': 'stream-choosing-pattern',
    'pubsub': 'stream-choosing-pattern',
    'stream-consumer': 'stream-choosing-pattern',
    'streams': 'stream-choosing-pattern',
    'rate-limiter': 'data-choose-structure',
    'cache-aside': 'ram-ttl',
    'session-store': 'data-choose-structure',
    'leaderboard': 'data-choose-structure',
    'vector-search': 'vector-algorithm-choice',
    'semantic-cache': 'semantic-cache-best-practices',
    'key-naming': 'data-key-naming',
    'hash-tags': 'cluster-hash-tags',
};

/**
 * Available code example patterns.
 */
export const CODE_EXAMPLE_PATTERNS = [
    'connection-pool',
    'pipeline',
    'pub-sub',
    'stream-consumer',
    'rate-limiter',
    'cache-aside',
    'session-store',
    'leaderboard',
    'vector-search',
    'semantic-cache',
    'key-naming',
    'hash-tags',
];

/**
 * Common prefixes for rule lookup.
 */
export const RULE_PREFIXES = [
    'data-',
    'conn-',
    'ram-',
    'json-',
    'rqe-',
    'vector-',
    'semantic-cache-',
    'stream-',
    'cluster-',
    'security-',
    'observe-',
];
