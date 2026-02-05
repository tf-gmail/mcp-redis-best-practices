"""MCP Redis Best Practices Server.

A Model Context Protocol server that provides Redis development best practices
as callable tools for AI assistants like GitHub Copilot and Claude.
"""

from redis_best_practices.server import main

__version__ = "0.1.0"
__all__ = ["main"]
