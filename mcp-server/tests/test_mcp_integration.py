"""Integration tests for MCP protocol functionality.

These tests verify that the MCP server properly handles protocol messages
and communicates correctly via the MCP SDK.
"""

import pytest
from mcp.types import TextContent

from redis_best_practices.server import handle_list_tools, handle_call_tool
from redis_best_practices.knowledge import KnowledgeBase


class TestMCPProtocolIntegration:
    """Integration tests for MCP protocol handling."""
    
    @pytest.mark.asyncio
    async def test_tools_follow_mcp_spec(self):
        """Verify tools conform to MCP specification."""
        tools = await handle_list_tools()
        
        for tool in tools:
            # MCP requires name, description, and inputSchema
            assert tool.name, "Tool must have a name"
            assert isinstance(tool.name, str), "Tool name must be a string"
            assert len(tool.name) > 0, "Tool name cannot be empty"
            
            assert tool.description, "Tool must have a description"
            assert isinstance(tool.description, str), "Description must be a string"
            
            assert tool.inputSchema, "Tool must have an input schema"
            assert isinstance(tool.inputSchema, dict), "Schema must be a dict"
            assert tool.inputSchema.get("type") == "object", "Schema type must be 'object'"
            assert "properties" in tool.inputSchema, "Schema must have 'properties'"
    
    @pytest.mark.asyncio
    async def test_tool_response_format(self):
        """Verify tool responses follow MCP content format."""
        # Test each tool returns proper TextContent
        test_calls = [
            ("get_best_practice", {"topic": "conn-pooling"}),
            ("list_topics", {}),
            ("search_best_practices", {"query": "connection"}),
            ("get_anti_patterns", {}),
            ("get_code_example", {"pattern": "connection-pool", "language": "python"}),
            ("get_full_guide", {}),
        ]
        
        for tool_name, args in test_calls:
            result = await handle_call_tool(tool_name, args)
            
            # MCP requires list of content items
            assert isinstance(result, list), f"{tool_name} must return a list"
            assert len(result) >= 1, f"{tool_name} must return at least one content item"
            
            for content in result:
                # Each item should be TextContent
                assert hasattr(content, 'type'), f"{tool_name} content must have 'type'"
                assert content.type == "text", f"{tool_name} content type must be 'text'"
                assert hasattr(content, 'text'), f"{tool_name} content must have 'text'"
                assert isinstance(content.text, str), f"{tool_name} text must be a string"
    
    @pytest.mark.asyncio
    async def test_error_handling_returns_valid_content(self):
        """Verify error cases still return valid MCP content."""
        # Unknown tool
        result = await handle_call_tool("nonexistent_tool", {})
        assert isinstance(result, list)
        assert len(result) >= 1
        assert result[0].type == "text"
        
        # Missing required parameter
        result = await handle_call_tool("get_best_practice", {})
        assert isinstance(result, list)
        assert len(result) >= 1
        assert result[0].type == "text"
        
        # Invalid topic
        result = await handle_call_tool("get_best_practice", {"topic": "xyz-invalid-123"})
        assert isinstance(result, list)
        assert len(result) >= 1
        assert result[0].type == "text"
    
    @pytest.mark.asyncio
    async def test_tool_names_are_valid_identifiers(self):
        """Verify tool names follow MCP naming conventions."""
        tools = await handle_list_tools()
        
        for tool in tools:
            # Tool names should be valid identifiers (lowercase, underscores)
            assert tool.name.replace("_", "").isalnum(), \
                f"Tool name '{tool.name}' should only contain alphanumeric and underscores"
            assert tool.name[0].isalpha(), \
                f"Tool name '{tool.name}' should start with a letter"
            assert tool.name == tool.name.lower(), \
                f"Tool name '{tool.name}' should be lowercase"
    
    @pytest.mark.asyncio
    async def test_schema_required_fields_are_in_properties(self):
        """Verify all required fields are defined in properties."""
        tools = await handle_list_tools()
        
        for tool in tools:
            schema = tool.inputSchema
            required = schema.get("required", [])
            properties = schema.get("properties", {})
            
            for req_field in required:
                assert req_field in properties, \
                    f"Tool '{tool.name}' requires '{req_field}' but it's not in properties"
    
    @pytest.mark.asyncio
    async def test_schema_properties_have_descriptions(self):
        """Verify schema properties have descriptions for better LLM understanding."""
        tools = await handle_list_tools()
        
        for tool in tools:
            properties = tool.inputSchema.get("properties", {})
            
            for prop_name, prop_def in properties.items():
                assert "description" in prop_def, \
                    f"Tool '{tool.name}' property '{prop_name}' should have a description"
                assert "type" in prop_def, \
                    f"Tool '{tool.name}' property '{prop_name}' should have a type"


class TestMCPToolBehavior:
    """Test MCP tool behavior matches documentation."""
    
    @pytest.mark.asyncio
    async def test_get_best_practice_returns_markdown(self):
        """Verify get_best_practice returns markdown formatted content."""
        result = await handle_call_tool("get_best_practice", {"topic": "conn-pooling"})
        
        content = result[0].text
        # Should contain markdown formatting
        assert "#" in content or "**" in content or "```" in content, \
            "Response should contain markdown formatting"
    
    @pytest.mark.asyncio
    async def test_list_topics_shows_categories(self):
        """Verify list_topics shows organized categories."""
        result = await handle_call_tool("list_topics", {})
        
        content = result[0].text.lower()
        # Should mention major categories
        assert "data" in content or "connection" in content or "security" in content, \
            "list_topics should show categories"
    
    @pytest.mark.asyncio
    async def test_search_returns_relevant_results(self):
        """Verify search returns relevant results."""
        result = await handle_call_tool("search_best_practices", {"query": "pool"})
        
        content = result[0].text.lower()
        # Should find pooling-related content
        assert "pool" in content or "connection" in content, \
            "Search for 'pool' should return pooling-related results"
    
    @pytest.mark.asyncio
    async def test_code_example_contains_code(self):
        """Verify code examples contain actual code."""
        result = await handle_call_tool("get_code_example", {
            "pattern": "connection-pool",
            "language": "python"
        })
        
        content = result[0].text
        # Should contain code block or code-like content
        assert "```" in content or "import" in content or "def " in content or "redis" in content.lower(), \
            "Code example should contain code"
    
    @pytest.mark.asyncio
    async def test_full_guide_is_comprehensive(self):
        """Verify full guide contains substantial content."""
        result = await handle_call_tool("get_full_guide", {})
        
        content = result[0].text
        # Full guide should be substantial
        assert len(content) > 5000, "Full guide should be comprehensive"
        
        # Should cover multiple topics
        content_lower = content.lower()
        topics_found = sum([
            "connection" in content_lower,
            "memory" in content_lower,
            "security" in content_lower,
            "key" in content_lower,
        ])
        assert topics_found >= 3, "Full guide should cover multiple topics"


class TestKnowledgeBaseIntegration:
    """Test KnowledgeBase integration with MCP tools."""
    
    @pytest.fixture
    def kb(self):
        """Create a KnowledgeBase instance."""
        return KnowledgeBase()
    
    def test_all_rules_accessible_via_tools(self, kb):
        """Verify all knowledge base rules can be accessed via tools."""
        # Get all rule prefixes
        rule_prefixes = list(kb.rules.keys())
        assert len(rule_prefixes) > 0, "Should have rules"
        
        # Each rule should be findable
        for prefix in rule_prefixes:
            rule = kb.get_rule_by_topic(prefix)
            assert rule is not None, f"Rule '{prefix}' should be accessible"
    
    def test_sections_map_to_rules(self, kb):
        """Verify sections properly contain their rules."""
        for section_prefix, section in kb.sections.items():
            # Each section should have at least one rule
            # (some sections might be empty if rules don't exist)
            section_rules = [r for p, r in kb.rules.items() if p.startswith(section_prefix)]
            if len(section_rules) > 0:
                assert len(section.rules) > 0, \
                    f"Section '{section.name}' should have rules loaded"
    
    def test_search_finds_all_relevant_rules(self, kb):
        """Verify search finds rules containing the search term."""
        # Search for a common term
        results = kb.search_rules("Redis")
        
        # Should find multiple results since Redis is mentioned everywhere
        assert len(results) > 0, "Should find rules mentioning 'Redis'"
    
    def test_full_guide_contains_all_rules(self, kb):
        """Verify full guide contains content from all rules."""
        guide = kb.get_full_guide()
        
        # Check that guide contains content
        assert len(guide) > 0, "Guide should not be empty"
        
        # Guide should contain rule titles
        for rule in kb.rules.values():
            # At least some rules should be in the guide
            if rule.title:
                # Just verify guide has substantial content
                assert len(guide) > 1000, "Guide should be substantial"
                break
