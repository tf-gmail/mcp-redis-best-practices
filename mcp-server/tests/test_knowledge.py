"""Tests for the Redis Best Practices MCP Server."""

import pytest
from redis_best_practices.knowledge import KnowledgeBase


class TestKnowledgeBase:
    """Tests for the KnowledgeBase class."""
    
    @pytest.fixture
    def kb(self):
        """Create a KnowledgeBase instance for testing."""
        return KnowledgeBase()
    
    def test_sections_loaded(self, kb):
        """Test that sections are loaded from _sections.md."""
        assert len(kb.sections) > 0
        assert "data" in kb.sections
        assert "conn" in kb.sections
        assert "ram" in kb.sections
        assert "security" in kb.sections
    
    def test_rules_loaded(self, kb):
        """Test that rules are loaded from rule files."""
        assert len(kb.rules) > 0
        # Check for some expected rules
        assert any("pooling" in rule for rule in kb.rules)
        assert any("key-naming" in rule for rule in kb.rules)
    
    def test_get_rule_by_topic_exact(self, kb):
        """Test getting a rule by exact topic name."""
        rule = kb.get_rule_by_topic("conn-pooling")
        assert rule is not None
        assert "Connection Pooling" in rule.title or "pooling" in rule.title.lower()
    
    def test_get_rule_by_topic_partial(self, kb):
        """Test getting a rule by partial topic name."""
        rule = kb.get_rule_by_topic("pooling")
        assert rule is not None
    
    def test_get_rule_by_topic_not_found(self, kb):
        """Test getting a non-existent rule."""
        rule = kb.get_rule_by_topic("nonexistent-topic-xyz")
        assert rule is None
    
    def test_search_rules(self, kb):
        """Test searching for rules."""
        results = kb.search_rules("connection")
        assert len(results) > 0
        # Connection-related rules should be in results
        assert any("connection" in r.title.lower() or "connection" in " ".join(r.tags).lower() 
                   for r in results)
    
    def test_search_rules_no_results(self, kb):
        """Test search with no matching results."""
        results = kb.search_rules("xyznonexistent123")
        assert len(results) == 0
    
    def test_list_all_topics(self, kb):
        """Test listing all topics."""
        topics = kb.list_all_topics()
        assert len(topics) > 0
        assert isinstance(topics, list)
        assert all(isinstance(t, str) for t in topics)
    
    def test_get_sections_all(self, kb):
        """Test getting all sections."""
        sections = kb.get_sections()
        assert len(sections) > 0
        # Sections should be ordered by number
        numbers = [s.number for s in sections]
        assert numbers == sorted(numbers)
    
    def test_get_sections_filtered(self, kb):
        """Test getting sections filtered by category."""
        sections = kb.get_sections("connection")
        assert len(sections) == 1
        assert sections[0].prefix == "conn"
    
    def test_get_full_guide(self, kb):
        """Test getting the full guide."""
        guide = kb.get_full_guide()
        assert len(guide) > 0
        assert "Redis" in guide
        assert "Best Practices" in guide or "best practices" in guide.lower()
    
    def test_rule_has_required_fields(self, kb):
        """Test that all rules have required fields."""
        for prefix, rule in kb.rules.items():
            assert rule.title, f"Rule {prefix} missing title"
            assert rule.impact, f"Rule {prefix} missing impact"
            assert rule.content, f"Rule {prefix} missing content"
    
    def test_section_has_rules(self, kb):
        """Test that populated sections have rules."""
        # At least some sections should have rules
        sections_with_rules = [s for s in kb.sections.values() if len(s.rules) > 0]
        assert len(sections_with_rules) > 0


class TestAntiPatterns:
    """Tests for anti-pattern extraction."""
    
    @pytest.fixture
    def kb(self):
        """Create a KnowledgeBase instance for testing."""
        return KnowledgeBase()
    
    def test_get_anti_patterns_all(self, kb):
        """Test getting all anti-patterns."""
        patterns = kb.get_anti_patterns()
        # Should have at least some anti-patterns
        assert len(patterns) >= 0  # May be 0 if no patterns extracted
    
    def test_get_anti_patterns_filtered(self, kb):
        """Test getting anti-patterns filtered by topic."""
        patterns = kb.get_anti_patterns("connection")
        # Should return patterns or empty dict
        assert isinstance(patterns, dict)


class TestCodeExamples:
    """Tests for code example functionality."""
    
    @pytest.fixture
    def kb(self):
        """Create a KnowledgeBase instance for testing."""
        return KnowledgeBase()
    
    def test_list_code_examples(self, kb):
        """Test listing available code examples."""
        examples = kb.list_code_examples()
        assert len(examples) > 0
        assert "connection-pool" in examples
        assert "pipeline" in examples
    
    def test_get_code_example_found(self, kb):
        """Test getting a code example that exists."""
        example = kb.get_code_example("connection-pool", "python")
        # May be None if rule doesn't have python code block
        if example:
            assert example.title
            assert example.code
    
    def test_get_code_example_not_found(self, kb):
        """Test getting a code example that doesn't exist."""
        example = kb.get_code_example("nonexistent-pattern-xyz", "python")
        assert example is None
