"""Tool definitions for the Redis Best Practices MCP Server.

This module defines all available MCP tools and their implementations.
"""

from typing import TYPE_CHECKING

from mcp.types import Tool

if TYPE_CHECKING:
    from redis_best_practices.knowledge import KnowledgeBase


# Tool definitions following MCP specification
TOOLS = [
    Tool(
        name="get_best_practice",
        description="""Get Redis best practices for a specific topic.

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
- Security configuration""",
        inputSchema={
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The topic to get best practices for. Examples: 'key-naming', 'data-structures', 'connection-pooling', 'pipelining', 'memory', 'ttl', 'security', 'json', 'streams', 'pub-sub', 'clustering', 'vector-search', 'semantic-cache'"
                }
            },
            "required": ["topic"]
        }
    ),
    Tool(
        name="list_topics",
        description="""List all available Redis best practice topics.

Returns topics organized by category and impact level:
- HIGH impact: Data structures, connections, memory, security, query engine, vector search
- MEDIUM impact: JSON, streams, pub/sub, clustering, semantic caching, observability

Optionally filter by category to see only relevant topics.""",
        inputSchema={
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Optional category filter. One of: 'data', 'connection', 'memory', 'security', 'json', 'streams', 'clustering', 'vector', 'semantic-cache', 'observability'",
                    "enum": ["data", "connection", "memory", "security", "json", "streams", "clustering", "vector", "semantic-cache", "observability"]
                }
            },
            "required": []
        }
    ),
    Tool(
        name="search_best_practices",
        description="""Search across all Redis best practices using keywords.

Performs a semantic search across all rules and returns matching practices
ranked by relevance. Use this when you're not sure which topic to look up
or when searching for specific patterns like:
- "how to avoid hot keys"
- "rate limiting"
- "cache stampede"
- "KEYS command alternatives"
- "large values"
- "blocking operations" """,
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query - can be a question, keyword, or description of what you're looking for"
                }
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="get_anti_patterns",
        description="""Get common Redis anti-patterns and mistakes to avoid.

Returns a list of things NOT to do, organized by category:
- Blocking commands in production (KEYS *, SMEMBERS on large sets)
- Missing key expiration leading to memory bloat
- Connection leaks from not using pools
- Big keys that cause latency spikes
- Inefficient data structure choices

Optionally filter by topic to see category-specific anti-patterns.""",
        inputSchema={
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Optional topic filter for anti-patterns. Examples: 'commands', 'memory', 'connections', 'data-structures', 'security'"
                }
            },
            "required": []
        }
    ),
    Tool(
        name="get_code_example",
        description="""Get working code examples for a specific Redis pattern.

Returns production-ready code snippets with:
- Complete, runnable examples
- Comments explaining each step
- Error handling patterns
- Configuration options

Supports multiple languages: Python (redis-py), Node.js (ioredis), Java (Jedis/Lettuce).""",
        inputSchema={
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "The pattern to get code for. Examples: 'connection-pool', 'pipeline', 'transaction', 'pub-sub', 'stream-consumer', 'rate-limiter', 'cache-aside', 'session-store', 'leaderboard', 'vector-search'"
                },
                "language": {
                    "type": "string",
                    "description": "Programming language for the example",
                    "enum": ["python", "javascript", "java"],
                    "default": "python"
                }
            },
            "required": ["pattern"]
        }
    ),
    Tool(
        name="get_full_guide",
        description="""Get the complete Redis best practices guide.

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
11. Observability (MEDIUM)""",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
]


def get_best_practice(kb: "KnowledgeBase", topic: str) -> str:
    """Get best practices for a specific topic.
    
    Args:
        kb: The knowledge base instance
        topic: The topic to look up
        
    Returns:
        Formatted best practice content or error message
    """
    # Normalize topic name
    topic_normalized = topic.lower().strip().replace(" ", "-").replace("_", "-")
    
    # Try to find exact match first
    rule = kb.get_rule_by_topic(topic_normalized)
    if rule:
        return rule.to_markdown()
    
    # Try fuzzy match
    matches = kb.search_rules(topic)
    if matches:
        # Return the best match
        return matches[0].to_markdown()
    
    # List available topics as fallback
    available = kb.list_all_topics()
    return f"""Topic '{topic}' not found.

Available topics:
{chr(10).join(f"  - {t}" for t in available)}

Tip: Use 'search_best_practices' to search by keyword, or 'list_topics' to browse by category."""


def list_topics(kb: "KnowledgeBase", category: str | None = None) -> str:
    """List all available topics, optionally filtered by category.
    
    Args:
        kb: The knowledge base instance
        category: Optional category filter
        
    Returns:
        Formatted list of topics by category
    """
    sections = kb.get_sections(category)
    
    lines = ["# Redis Best Practices Topics\n"]
    
    for section in sections:
        impact_badge = "🔴" if section.impact == "HIGH" else "🟡" if section.impact == "MEDIUM" else "🟢"
        lines.append(f"\n## {section.number}. {section.name} ({impact_badge} {section.impact})")
        lines.append(f"*{section.description}*\n")
        
        for rule in section.rules:
            lines.append(f"  - `{rule.prefix}` - {rule.title}")
    
    return "\n".join(lines)


def search_best_practices(kb: "KnowledgeBase", query: str) -> str:
    """Search across all best practices.
    
    Args:
        kb: The knowledge base instance
        query: Search query
        
    Returns:
        Formatted search results
    """
    if not query.strip():
        return "Please provide a search query."
    
    matches = kb.search_rules(query)
    
    if not matches:
        return f"""No results found for '{query}'.

Try:
- Different keywords (e.g., 'cache' instead of 'caching')
- Broader terms (e.g., 'memory' instead of 'maxmemory')
- Use 'list_topics' to browse available topics"""
    
    lines = [f"# Search Results for '{query}'\n"]
    lines.append(f"Found {len(matches)} matching practice(s):\n")
    
    for i, rule in enumerate(matches[:5], 1):  # Top 5 results
        lines.append(f"## {i}. {rule.title}")
        lines.append(f"**Impact:** {rule.impact} - {rule.impact_description}")
        lines.append(f"**Tags:** {', '.join(rule.tags)}\n")
        lines.append(rule.summary)
        lines.append(f"\n*Use `get_best_practice('{rule.prefix}')` for full details.*\n")
        lines.append("---\n")
    
    return "\n".join(lines)


def get_anti_patterns(kb: "KnowledgeBase", topic: str | None = None) -> str:
    """Get common anti-patterns and mistakes.
    
    Args:
        kb: The knowledge base instance
        topic: Optional topic filter
        
    Returns:
        Formatted anti-patterns content
    """
    anti_patterns = kb.get_anti_patterns(topic)
    
    lines = ["# Redis Anti-Patterns to Avoid\n"]
    
    if topic:
        lines.append(f"*Filtered by: {topic}*\n")
    
    for category, patterns in anti_patterns.items():
        lines.append(f"\n## {category}\n")
        for pattern in patterns:
            lines.append(f"### ❌ {pattern.title}")
            lines.append(f"**Why it's bad:** {pattern.reason}")
            lines.append(f"\n```{pattern.language}")
            lines.append(pattern.bad_code)
            lines.append("```\n")
            lines.append(f"**Instead, do this:**\n")
            lines.append(f"```{pattern.language}")
            lines.append(pattern.good_code)
            lines.append("```\n")
    
    return "\n".join(lines)


def get_code_example(kb: "KnowledgeBase", pattern: str, language: str = "python") -> str:
    """Get code examples for a specific pattern.
    
    Args:
        kb: The knowledge base instance
        pattern: The pattern to get code for
        language: Programming language
        
    Returns:
        Code example with explanations
    """
    example = kb.get_code_example(pattern, language)
    
    if not example:
        available = kb.list_code_examples()
        return f"""No code example found for pattern '{pattern}' in {language}.

Available patterns:
{chr(10).join(f"  - {p}" for p in available)}

Available languages: python, javascript, java"""
    
    lines = [f"# {example.title}\n"]
    lines.append(f"**Pattern:** {pattern}")
    lines.append(f"**Language:** {language}\n")
    lines.append(example.description)
    lines.append(f"\n```{language}")
    lines.append(example.code)
    lines.append("```\n")
    
    if example.notes:
        lines.append("## Notes\n")
        for note in example.notes:
            lines.append(f"- {note}")
    
    if example.references:
        lines.append("\n## References\n")
        for ref in example.references:
            lines.append(f"- [{ref.title}]({ref.url})")
    
    return "\n".join(lines)


def get_full_guide(kb: "KnowledgeBase") -> str:
    """Get the complete best practices guide.
    
    Args:
        kb: The knowledge base instance
        
    Returns:
        Complete AGENTS.md content
    """
    return kb.get_full_guide()
