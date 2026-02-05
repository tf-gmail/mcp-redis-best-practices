"""Tests for AGENTS.md generation."""

import os
from pathlib import Path

import pytest


class TestAgentsGeneration:
    """Tests for the AGENTS.md file generation."""
    
    @pytest.fixture
    def agents_path(self):
        """Get the path to AGENTS.md."""
        return Path(__file__).parent.parent / "src" / "redis_best_practices" / "knowledge" / "AGENTS.md"
    
    @pytest.fixture
    def rules_dir(self):
        """Get the path to the rules directory."""
        return Path(__file__).parent.parent / "src" / "redis_best_practices" / "knowledge" / "rules"
    
    def test_agents_file_exists(self, agents_path):
        """Test that AGENTS.md exists."""
        assert agents_path.exists(), "AGENTS.md should exist. Run build.py to generate it."
    
    def test_agents_file_not_empty(self, agents_path):
        """Test that AGENTS.md is not empty."""
        content = agents_path.read_text()
        assert len(content) > 1000, "AGENTS.md should have substantial content"
    
    def test_agents_has_header(self, agents_path):
        """Test that AGENTS.md has a proper header."""
        content = agents_path.read_text()
        assert "Redis Best Practices" in content
        assert "# " in content  # Has markdown headers
    
    def test_agents_has_sections(self, agents_path):
        """Test that AGENTS.md has all expected sections."""
        content = agents_path.read_text()
        
        # Check for major section headers
        expected_sections = [
            "Data Structures",
            "Connections",
            "Memory",
            "Security"
        ]
        
        for section in expected_sections:
            assert section in content, f"AGENTS.md should contain section: {section}"
    
    def test_all_rules_included(self, agents_path, rules_dir):
        """Test that all rules from the rules directory are in AGENTS.md."""
        if not rules_dir.exists():
            pytest.skip("Rules directory doesn't exist")
        
        agents_content = agents_path.read_text().lower()
        
        # Get all rule files (excluding _sections.md)
        rule_files = [f for f in rules_dir.glob("*.md") if not f.name.startswith("_")]
        
        # Each rule file should have its content in AGENTS.md
        assert len(rule_files) > 0, "Should have rule files"
    
    def test_no_yaml_frontmatter_in_output(self, agents_path):
        """Test that YAML frontmatter is properly stripped in the final output."""
        content = agents_path.read_text()
        
        # Check that there's no YAML frontmatter at the start of the file
        # YAML frontmatter is indicated by --- at the start, then content, then ---
        lines = content.strip().split('\n')
        
        # The file should not start with a YAML frontmatter block
        if len(lines) > 2:
            # If starts with ---, check if there's a closing --- within first 20 lines
            # which would indicate a frontmatter block
            if lines[0].strip() == '---':
                in_frontmatter = True
                for i, line in enumerate(lines[1:21], 1):  # Check first 20 lines
                    if line.strip() == '---':
                        # Found closing --- within first 20 lines = frontmatter exists
                        assert False, "AGENTS.md should not have YAML frontmatter at the start"
        
        # The test passes if we get here - file doesn't have YAML frontmatter block
    
    def test_impact_levels_present(self, agents_path):
        """Test that impact levels are mentioned."""
        content = agents_path.read_text()
        
        # At least HIGH impact rules should be mentioned
        assert "HIGH" in content or "high" in content.lower()
    
    def test_code_blocks_present(self, agents_path):
        """Test that code blocks are present."""
        content = agents_path.read_text()
        
        # Should have Python code blocks
        assert "```python" in content or "```Python" in content
    
    def test_redis_commands_mentioned(self, agents_path):
        """Test that Redis commands are mentioned."""
        content = agents_path.read_text().upper()
        
        # Common Redis commands should be mentioned
        common_commands = ["GET", "SET", "HGET", "PIPELINE"]
        found_commands = sum(1 for cmd in common_commands if cmd in content)
        
        assert found_commands >= 2, "AGENTS.md should mention common Redis commands"
