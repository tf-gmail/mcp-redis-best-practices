"""Tests for the MCP Server implementation."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from redis_best_practices.server import handle_list_tools, handle_call_tool
from redis_best_practices.knowledge import KnowledgeBase


class TestHandleListTools:
    """Tests for the handle_list_tools function."""
    
    @pytest.mark.asyncio
    async def test_returns_tool_list(self):
        """Test that handle_list_tools returns a list of tools."""
        tools = await handle_list_tools()
        
        assert len(tools) == 6
        tool_names = [tool.name for tool in tools]
        
        # Verify all expected tools are present
        assert "get_best_practice" in tool_names
        assert "list_topics" in tool_names
        assert "search_best_practices" in tool_names
        assert "get_anti_patterns" in tool_names
        assert "get_code_example" in tool_names
        assert "get_full_guide" in tool_names
    
    @pytest.mark.asyncio
    async def test_tools_have_descriptions(self):
        """Test that all tools have descriptions."""
        tools = await handle_list_tools()
        
        for tool in tools:
            assert tool.description, f"Tool {tool.name} missing description"
            assert len(tool.description) > 10, f"Tool {tool.name} has too short description"
    
    @pytest.mark.asyncio
    async def test_tools_have_schemas(self):
        """Test that all tools have input schemas."""
        tools = await handle_list_tools()
        
        for tool in tools:
            assert tool.inputSchema, f"Tool {tool.name} missing inputSchema"
            assert tool.inputSchema.get("type") == "object"


class TestHandleCallTool:
    """Tests for the handle_call_tool function."""
    
    @pytest.fixture
    def mock_kb(self):
        """Create a mock KnowledgeBase."""
        kb = MagicMock(spec=KnowledgeBase)
        return kb
    
    @pytest.mark.asyncio
    async def test_get_best_practice_found(self):
        """Test getting a best practice that exists."""
        result = await handle_call_tool("get_best_practice", {"topic": "conn-pooling"})
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Connection Pooling" in result[0].text or "pool" in result[0].text.lower()
    
    @pytest.mark.asyncio
    async def test_get_best_practice_not_found(self):
        """Test getting a best practice that doesn't exist."""
        result = await handle_call_tool("get_best_practice", {"topic": "nonexistent-xyz"})
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "not found" in result[0].text.lower() or "no" in result[0].text.lower()
    
    @pytest.mark.asyncio
    async def test_list_topics_all(self):
        """Test listing all topics."""
        result = await handle_call_tool("list_topics", {})
        
        assert len(result) == 1
        assert result[0].type == "text"
        # Should contain category headers
        assert "Data" in result[0].text or "Connections" in result[0].text
    
    @pytest.mark.asyncio
    async def test_list_topics_filtered(self):
        """Test listing topics filtered by category."""
        result = await handle_call_tool("list_topics", {"category": "security"})
        
        assert len(result) == 1
        assert result[0].type == "text"
        # Should contain security-related content
        assert "security" in result[0].text.lower() or "Security" in result[0].text
    
    @pytest.mark.asyncio
    async def test_search_best_practices(self):
        """Test searching best practices."""
        result = await handle_call_tool("search_best_practices", {"query": "connection"})
        
        assert len(result) == 1
        assert result[0].type == "text"
        # Should find connection-related results
        content = result[0].text.lower()
        assert "connection" in content or "pool" in content or "timeout" in content
    
    @pytest.mark.asyncio
    async def test_get_anti_patterns(self):
        """Test getting anti-patterns."""
        result = await handle_call_tool("get_anti_patterns", {})
        
        assert len(result) == 1
        assert result[0].type == "text"
    
    @pytest.mark.asyncio
    async def test_get_code_example(self):
        """Test getting a code example."""
        result = await handle_call_tool("get_code_example", {
            "pattern": "connection-pool",
            "language": "python"
        })
        
        assert len(result) == 1
        assert result[0].type == "text"
    
    @pytest.mark.asyncio
    async def test_get_full_guide(self):
        """Test getting the full guide."""
        result = await handle_call_tool("get_full_guide", {})
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert len(result[0].text) > 1000  # Guide should be substantial
    
    @pytest.mark.asyncio
    async def test_unknown_tool(self):
        """Test calling an unknown tool."""
        result = await handle_call_tool("unknown_tool_xyz", {})
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "unknown" in result[0].text.lower() or "error" in result[0].text.lower()


class TestToolSchemas:
    """Tests for tool input schema validation."""
    
    @pytest.mark.asyncio
    async def test_get_best_practice_schema(self):
        """Test get_best_practice schema."""
        tools = await handle_list_tools()
        tool = next(t for t in tools if t.name == "get_best_practice")
        
        schema = tool.inputSchema
        assert "topic" in schema.get("required", [])
        assert "properties" in schema
        assert "topic" in schema["properties"]
    
    @pytest.mark.asyncio
    async def test_search_best_practices_schema(self):
        """Test search_best_practices schema."""
        tools = await handle_list_tools()
        tool = next(t for t in tools if t.name == "search_best_practices")
        
        schema = tool.inputSchema
        assert "query" in schema.get("required", [])
        assert "properties" in schema
        assert "query" in schema["properties"]
    
    @pytest.mark.asyncio
    async def test_get_code_example_schema(self):
        """Test get_code_example schema."""
        tools = await handle_list_tools()
        tool = next(t for t in tools if t.name == "get_code_example")
        
        schema = tool.inputSchema
        assert "pattern" in schema.get("required", [])
        # language has a default so may not be required
        assert "properties" in schema
        assert "pattern" in schema["properties"]
        assert "language" in schema["properties"]
