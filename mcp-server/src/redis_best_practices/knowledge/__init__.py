"""Knowledge base for Redis best practices.

This module handles loading, parsing, and querying the Redis best practices
knowledge base from markdown files.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator


@dataclass
class Reference:
    """A reference link to documentation."""
    title: str
    url: str


@dataclass
class CodeExample:
    """A code example with metadata."""
    title: str
    description: str
    code: str
    language: str = "python"
    notes: list[str] = field(default_factory=list)
    references: list[Reference] = field(default_factory=list)


@dataclass
class AntiPattern:
    """An anti-pattern to avoid."""
    title: str
    reason: str
    bad_code: str
    good_code: str
    language: str = "python"
    category: str = ""


@dataclass
class Rule:
    """A single best practice rule."""
    prefix: str
    title: str
    impact: str
    impact_description: str
    tags: list[str]
    content: str
    summary: str = ""
    section_number: int = 0
    
    def to_markdown(self) -> str:
        """Convert rule to markdown format."""
        lines = [f"# {self.title}\n"]
        lines.append(f"**Impact:** {self.impact} ({self.impact_description})\n")
        lines.append(f"**Tags:** {', '.join(self.tags)}\n")
        lines.append("---\n")
        lines.append(self.content)
        return "\n".join(lines)


@dataclass
class Section:
    """A section containing multiple rules."""
    number: int
    name: str
    prefix: str
    impact: str
    description: str
    rules: list[Rule] = field(default_factory=list)


class KnowledgeBase:
    """Knowledge base for Redis best practices.
    
    Loads and indexes rules from markdown files for efficient querying.
    """
    
    def __init__(self, knowledge_dir: Path | None = None):
        """Initialize the knowledge base.
        
        Args:
            knowledge_dir: Path to the knowledge directory. If None, uses the
                          bundled knowledge directory.
        """
        if knowledge_dir is None:
            # This file is at knowledge/__init__.py, so parent is the knowledge dir
            knowledge_dir = Path(__file__).parent
        
        self.knowledge_dir = knowledge_dir
        self.rules_dir = knowledge_dir / "rules"
        self.sections: dict[str, Section] = {}
        self.rules: dict[str, Rule] = {}
        self.rules_by_tag: dict[str, list[Rule]] = {}
        self._full_guide: str = ""
        
        self._load_knowledge_base()
    
    def _load_knowledge_base(self) -> None:
        """Load all knowledge base content from files."""
        # Load sections definition
        self._load_sections()
        
        # Load all rule files
        self._load_rules()
        
        # Load compiled guide
        self._load_full_guide()
    
    def _load_sections(self) -> None:
        """Load section definitions from _sections.md."""
        sections_file = self.rules_dir / "_sections.md"
        if not sections_file.exists():
            return
        
        content = sections_file.read_text()
        
        # Parse sections
        section_pattern = r"## (\d+)\. ([^(]+)\((\w+)\)\s*\n\*\*Impact:\*\* (\w+)\s*\n\*\*Description:\*\* (.+)"
        
        for match in re.finditer(section_pattern, content):
            number = int(match.group(1))
            name = match.group(2).strip()
            prefix = match.group(3).strip()
            impact = match.group(4).strip()
            description = match.group(5).strip()
            
            self.sections[prefix] = Section(
                number=number,
                name=name,
                prefix=prefix,
                impact=impact,
                description=description,
            )
    
    def _load_rules(self) -> None:
        """Load all rule files from the rules directory."""
        if not self.rules_dir.exists():
            return
        
        for rule_file in self.rules_dir.glob("*.md"):
            # Skip special files
            if rule_file.name.startswith("_"):
                continue
            
            rule = self._parse_rule_file(rule_file)
            if rule:
                self.rules[rule.prefix] = rule
                
                # Index by tags
                for tag in rule.tags:
                    if tag not in self.rules_by_tag:
                        self.rules_by_tag[tag] = []
                    self.rules_by_tag[tag].append(rule)
                
                # Add to section
                section_prefix = rule.prefix.split("-")[0]
                if section_prefix in self.sections:
                    self.sections[section_prefix].rules.append(rule)
                    rule.section_number = self.sections[section_prefix].number
    
    def _parse_rule_file(self, file_path: Path) -> Rule | None:
        """Parse a rule file and return a Rule object.
        
        Args:
            file_path: Path to the rule markdown file
            
        Returns:
            Rule object or None if parsing fails
        """
        content = file_path.read_text()
        
        # Parse frontmatter
        frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
        if not frontmatter_match:
            return None
        
        frontmatter = frontmatter_match.group(1)
        body = frontmatter_match.group(2)
        
        # Extract frontmatter fields
        title_match = re.search(r"title:\s*(.+)", frontmatter)
        impact_match = re.search(r"impact:\s*(\w+)", frontmatter)
        impact_desc_match = re.search(r"impactDescription:\s*(.+)", frontmatter)
        tags_match = re.search(r"tags:\s*(.+)", frontmatter)
        
        if not title_match or not impact_match:
            return None
        
        title = title_match.group(1).strip()
        impact = impact_match.group(1).strip()
        impact_description = impact_desc_match.group(1).strip() if impact_desc_match else ""
        tags = [t.strip() for t in tags_match.group(1).split(",")] if tags_match else []
        
        # Extract prefix from filename
        prefix = file_path.stem
        
        # Extract summary (first paragraph of body)
        summary_match = re.search(r"##[^\n]+\n+([^\n#]+)", body)
        summary = summary_match.group(1).strip() if summary_match else ""
        
        return Rule(
            prefix=prefix,
            title=title,
            impact=impact,
            impact_description=impact_description,
            tags=tags,
            content=body,
            summary=summary,
        )
    
    def _load_full_guide(self) -> None:
        """Load the compiled AGENTS.md guide."""
        agents_file = self.knowledge_dir / "AGENTS.md"
        if agents_file.exists():
            self._full_guide = agents_file.read_text()
        else:
            # Generate from rules
            self._full_guide = self._generate_full_guide()
    
    def _generate_full_guide(self) -> str:
        """Generate the full guide from loaded rules."""
        lines = [
            "# Redis Development Best Practices",
            "",
            "**Version 0.1.0**",
            "MCP Redis Best Practices",
            "",
            "> **Note:**",
            "> This document is optimized for AI agents and LLMs to follow when",
            "> generating or refactoring Redis applications.",
            "",
            "---",
            "",
            "## Abstract",
            "",
            "Best practices for Redis including data structures, memory management,",
            "connection handling, security, and performance optimization.",
            "",
            "---",
            "",
            "## Table of Contents",
            "",
        ]
        
        # Add TOC
        for section in sorted(self.sections.values(), key=lambda s: s.number):
            lines.append(f"{section.number}. [{section.name}](#{section.number}-{section.name.lower().replace(' ', '-')}) — **{section.impact}**")
            for rule in sorted(section.rules, key=lambda r: r.title):
                anchor = rule.title.lower().replace(" ", "-")
                lines.append(f"   - [{rule.title}](#{anchor})")
        
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Add sections
        for section in sorted(self.sections.values(), key=lambda s: s.number):
            lines.append(f"## {section.number}. {section.name}")
            lines.append("")
            lines.append(f"**Impact:** {section.impact}")
            lines.append("")
            lines.append(f"*{section.description}*")
            lines.append("")
            
            for rule in sorted(section.rules, key=lambda r: r.title):
                lines.append(f"### {rule.title}")
                lines.append("")
                lines.append(f"**Impact: {rule.impact}** ({rule.impact_description})")
                lines.append("")
                lines.append(rule.content)
                lines.append("")
                lines.append("---")
                lines.append("")
        
        return "\n".join(lines)
    
    def get_rule_by_topic(self, topic: str) -> Rule | None:
        """Get a rule by its topic/prefix.
        
        Args:
            topic: The topic or prefix to look up
            
        Returns:
            Rule object or None if not found
        """
        # Direct lookup
        if topic in self.rules:
            return self.rules[topic]
        
        # Try with common prefixes
        for prefix in ["data-", "conn-", "ram-", "json-", "rqe-", "vector-", 
                       "semantic-cache-", "stream-", "cluster-", "security-", "observe-"]:
            full_key = f"{prefix}{topic}"
            if full_key in self.rules:
                return self.rules[full_key]
        
        return None
    
    def search_rules(self, query: str) -> list[Rule]:
        """Search rules by query string.
        
        Args:
            query: Search query
            
        Returns:
            List of matching rules, sorted by relevance
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        scored_rules: list[tuple[float, Rule]] = []
        
        for rule in self.rules.values():
            score = 0.0
            
            # Title match (highest weight)
            if query_lower in rule.title.lower():
                score += 10.0
            
            # Exact title word match
            title_words = set(rule.title.lower().split())
            title_overlap = len(query_words & title_words)
            score += title_overlap * 5.0
            
            # Tag match
            for tag in rule.tags:
                if query_lower in tag.lower():
                    score += 3.0
                if tag.lower() in query_words:
                    score += 2.0
            
            # Content match
            if query_lower in rule.content.lower():
                score += 1.0
            
            # Impact description match
            if query_lower in rule.impact_description.lower():
                score += 2.0
            
            if score > 0:
                scored_rules.append((score, rule))
        
        # Sort by score descending
        scored_rules.sort(key=lambda x: x[0], reverse=True)
        
        return [rule for _, rule in scored_rules]
    
    def list_all_topics(self) -> list[str]:
        """List all available topics.
        
        Returns:
            List of topic prefixes
        """
        return sorted(self.rules.keys())
    
    def get_sections(self, category: str | None = None) -> list[Section]:
        """Get all sections, optionally filtered by category.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of sections
        """
        sections = sorted(self.sections.values(), key=lambda s: s.number)
        
        if category:
            # Map category names to prefixes
            category_map = {
                "data": "data",
                "connection": "conn",
                "memory": "ram",
                "security": "security",
                "json": "json",
                "streams": "stream",
                "clustering": "cluster",
                "vector": "vector",
                "semantic-cache": "semantic-cache",
                "observability": "observe",
            }
            prefix = category_map.get(category, category)
            sections = [s for s in sections if s.prefix == prefix]
        
        return sections
    
    def get_anti_patterns(self, topic: str | None = None) -> dict[str, list[AntiPattern]]:
        """Get anti-patterns, optionally filtered by topic.
        
        Args:
            topic: Optional topic filter
            
        Returns:
            Dictionary of category to anti-patterns
        """
        # Extract anti-patterns from rules (look for **Incorrect** sections)
        anti_patterns: dict[str, list[AntiPattern]] = {}
        
        for rule in self.rules.values():
            # Filter by topic if specified
            if topic:
                topic_lower = topic.lower()
                if topic_lower not in rule.prefix and topic_lower not in " ".join(rule.tags).lower():
                    continue
            
            # Find incorrect patterns in content
            incorrect_pattern = r"\*\*Incorrect[^*]*\*\*[:\s]*([^\n]*)\n+```(\w+)\n(.*?)```"
            correct_pattern = r"\*\*Correct[^*]*\*\*[:\s]*([^\n]*)\n+```(\w+)\n(.*?)```"
            
            incorrect_matches = list(re.finditer(incorrect_pattern, rule.content, re.DOTALL))
            correct_matches = list(re.finditer(correct_pattern, rule.content, re.DOTALL))
            
            if incorrect_matches and correct_matches:
                section_prefix = rule.prefix.split("-")[0]
                category = self.sections.get(section_prefix, Section(0, "Other", "", "", "")).name
                
                if category not in anti_patterns:
                    anti_patterns[category] = []
                
                for inc, cor in zip(incorrect_matches, correct_matches):
                    anti_patterns[category].append(AntiPattern(
                        title=inc.group(1).strip() or rule.title,
                        reason=rule.impact_description,
                        bad_code=inc.group(3).strip(),
                        good_code=cor.group(3).strip(),
                        language=inc.group(2),
                        category=category,
                    ))
        
        return anti_patterns
    
    def get_code_example(self, pattern: str, language: str = "python") -> CodeExample | None:
        """Get a code example for a specific pattern.
        
        Args:
            pattern: The pattern to get code for
            language: Programming language
            
        Returns:
            CodeExample or None if not found
        """
        # Map pattern names to rule prefixes
        pattern_map = {
            "connection-pool": "conn-pooling",
            "pipeline": "conn-pipelining",
            "pipelining": "conn-pipelining",
            "transaction": "conn-pipelining",
            "pub-sub": "stream-choosing-pattern",
            "pubsub": "stream-choosing-pattern",
            "stream-consumer": "stream-choosing-pattern",
            "streams": "stream-choosing-pattern",
            "rate-limiter": "data-choose-structure",
            "cache-aside": "ram-ttl",
            "session-store": "data-choose-structure",
            "leaderboard": "data-choose-structure",
            "vector-search": "vector-algorithm-choice",
            "semantic-cache": "semantic-cache-best-practices",
            "key-naming": "data-key-naming",
            "hash-tags": "cluster-hash-tags",
        }
        
        # Normalize pattern
        pattern_normalized = pattern.lower().replace("_", "-").replace(" ", "-")
        rule_prefix = pattern_map.get(pattern_normalized, pattern_normalized)
        
        rule = self.get_rule_by_topic(rule_prefix)
        if not rule:
            return None
        
        # Extract code example from rule
        code_pattern = rf"```{language}\n(.*?)```"
        match = re.search(code_pattern, rule.content, re.DOTALL)
        
        if not match:
            # Try any code block
            match = re.search(r"```\w*\n(.*?)```", rule.content, re.DOTALL)
        
        if not match:
            return None
        
        # Extract references
        refs = []
        ref_pattern = r"Reference:\s*\[([^\]]+)\]\(([^)]+)\)"
        for ref_match in re.finditer(ref_pattern, rule.content):
            refs.append(Reference(
                title=ref_match.group(1),
                url=ref_match.group(2),
            ))
        
        return CodeExample(
            title=rule.title,
            description=rule.summary or rule.impact_description,
            code=match.group(1).strip(),
            language=language,
            references=refs,
        )
    
    def list_code_examples(self) -> list[str]:
        """List all available code example patterns.
        
        Returns:
            List of pattern names
        """
        return [
            "connection-pool",
            "pipeline",
            "pub-sub",
            "stream-consumer",
            "rate-limiter",
            "cache-aside",
            "session-store",
            "leaderboard",
            "vector-search",
            "semantic-cache",
            "key-naming",
            "hash-tags",
        ]
    
    def get_full_guide(self) -> str:
        """Get the complete best practices guide.
        
        Returns:
            Full AGENTS.md content
        """
        return self._full_guide
