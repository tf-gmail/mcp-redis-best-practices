"""Pytest configuration and fixtures for Redis Best Practices MCP Server tests."""

import sys
from pathlib import Path

import pytest

# Add the src directory to the path so we can import the package
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session")
def knowledge_base():
    """Create a KnowledgeBase instance shared across all tests in a session."""
    from redis_best_practices.knowledge import KnowledgeBase
    return KnowledgeBase()


@pytest.fixture
def sample_rule_content():
    """Sample rule content for testing parsing."""
    return """---
title: Sample Rule
impact: HIGH
tags:
  - testing
  - sample
---

## Rule Description

This is a sample rule for testing purposes.

## Best Practice

Always write tests for your code.

### Good Pattern
```python
def test_example():
    assert True
```

### Anti-Pattern
```python
# No tests at all
pass
```

## Code Examples

```python
import pytest

def test_something():
    result = do_something()
    assert result == expected
```
"""


@pytest.fixture
def sample_section_content():
    """Sample section content for testing parsing."""
    return """---
sections:
  - number: 1
    prefix: test
    name: Testing
    description: Testing best practices
---
"""
