"""MCP Server implementation for Redis Best Practices.

This module implements the Model Context Protocol server that exposes
Redis best practices as callable tools for AI assistants.
"""

import asyncio
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
)

from redis_best_practices.knowledge import KnowledgeBase
from redis_best_practices.tools import (
    TOOLS,
    get_anti_patterns,
    get_best_practice,
    get_code_example,
    get_full_guide,
    list_topics,
    search_best_practices,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the MCP server
server = Server("redis-best-practices")

# Initialize knowledge base
knowledge_base = KnowledgeBase()


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List all available tools.
    
    Returns a list of Tool objects describing each available tool,
    including its name, description, and input schema.
    """
    return TOOLS


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    """Handle tool execution requests.
    
    Args:
        name: The name of the tool to execute
        arguments: The arguments to pass to the tool
        
    Returns:
        A list of TextContent objects containing the tool's response
    """
    arguments = arguments or {}
    
    try:
        if name == "get_best_practice":
            topic = arguments.get("topic", "")
            result = get_best_practice(knowledge_base, topic)
        elif name == "list_topics":
            category = arguments.get("category")
            result = list_topics(knowledge_base, category)
        elif name == "search_best_practices":
            query = arguments.get("query", "")
            result = search_best_practices(knowledge_base, query)
        elif name == "get_anti_patterns":
            topic = arguments.get("topic")
            result = get_anti_patterns(knowledge_base, topic)
        elif name == "get_code_example":
            pattern = arguments.get("pattern", "")
            language = arguments.get("language", "python")
            result = get_code_example(knowledge_base, pattern, language)
        elif name == "get_full_guide":
            result = get_full_guide(knowledge_base)
        else:
            result = f"Unknown tool: {name}"
            
        return [TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def run_server():
    """Run the MCP server using stdio transport."""
    logger.info("Starting Redis Best Practices MCP Server...")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main():
    """Entry point for the MCP server."""
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
