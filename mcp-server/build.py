#!/usr/bin/env python3
"""Build script to compile AGENTS.md from individual rule files.

This script reads all rule markdown files from the rules/ directory,
parses their frontmatter and content, and generates a single compiled
AGENTS.md file organized by section.
"""

import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class Rule:
    """A single best practice rule."""
    prefix: str
    title: str
    impact: str
    impact_description: str
    tags: list[str]
    content: str
    section_num: int = 0


@dataclass
class Section:
    """A section containing multiple rules."""
    number: int
    name: str
    prefix: str
    impact: str
    description: str
    rules: list[Rule] = field(default_factory=list)


def parse_sections(content: str) -> dict[str, Section]:
    """Parse section definitions from _sections.md."""
    sections = {}
    
    pattern = r"## (\d+)\. ([^(]+)\((\w+(?:-\w+)?)\)\s*\n\*\*Impact:\*\* (\w+)\s*\n\*\*Description:\*\* (.+)"
    
    for match in re.finditer(pattern, content):
        number = int(match.group(1))
        name = match.group(2).strip()
        prefix = match.group(3).strip()
        impact = match.group(4).strip()
        description = match.group(5).strip()
        
        sections[prefix] = Section(
            number=number,
            name=name,
            prefix=prefix,
            impact=impact,
            description=description,
        )
    
    return sections


def parse_rule_file(file_path: Path) -> Rule | None:
    """Parse a rule file and return a Rule object."""
    content = file_path.read_text()
    
    # Parse frontmatter
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if not match:
        print(f"Warning: Could not parse frontmatter in {file_path}")
        return None
    
    frontmatter = match.group(1)
    body = match.group(2)
    
    # Extract fields
    title_match = re.search(r"title:\s*(.+)", frontmatter)
    impact_match = re.search(r"impact:\s*(\w+)", frontmatter)
    impact_desc_match = re.search(r"impactDescription:\s*(.+)", frontmatter)
    tags_match = re.search(r"tags:\s*(.+)", frontmatter)
    
    if not title_match or not impact_match:
        print(f"Warning: Missing required fields in {file_path}")
        return None
    
    return Rule(
        prefix=file_path.stem,
        title=title_match.group(1).strip(),
        impact=impact_match.group(1).strip(),
        impact_description=impact_desc_match.group(1).strip() if impact_desc_match else "",
        tags=[t.strip() for t in tags_match.group(1).split(",")] if tags_match else [],
        content=body.strip(),
    )


def generate_agents_md(sections: dict[str, Section]) -> str:
    """Generate the compiled AGENTS.md content."""
    lines = [
        "# Redis Development Best Practices",
        "",
        "**Version 0.1.0**  ",
        "MCP Redis Best Practices  ",
        datetime.now().strftime("%B %Y"),
        "",
        "> **Note:**  ",
        "> This document is optimized for AI agents and LLMs to follow when",
        "> generating or refactoring Redis applications. Humans may also find",
        "> it useful, but guidance here is optimized for automation and consistency.",
        "",
        "---",
        "",
        "## Abstract",
        "",
        "Best practices for Redis including data structures, memory management,",
        "connection handling, Redis Query Engine (RQE), vector search with RedisVL,",
        "semantic caching with LangCache, security, and performance optimization.",
        "",
        "---",
        "",
        "## Table of Contents",
        "",
    ]
    
    # Generate TOC
    sorted_sections = sorted(sections.values(), key=lambda s: s.number)
    for section in sorted_sections:
        anchor = section.name.lower().replace(" ", "-").replace("&", "").replace("/", "")
        lines.append(f"{section.number}. [{section.name}](#{section.number}-{anchor}) — **{section.impact}**")
        
        for rule in sorted(section.rules, key=lambda r: r.title):
            rule_anchor = rule.title.lower().replace(" ", "-")
            lines.append(f"   - [{rule.title}](#{rule_anchor})")
    
    lines.extend(["", "---", ""])
    
    # Generate sections
    for section in sorted_sections:
        anchor = section.name.lower().replace(" ", "-").replace("&", "").replace("/", "")
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
    
    # Add references section
    lines.extend([
        "## References",
        "",
        "- [Redis Documentation](https://redis.io/docs/)",
        "- [Redis Best Practices](https://redis.io/docs/latest/develop/get-started/data-store/)",
        "- [Redis Query Engine](https://redis.io/docs/latest/develop/interact/search-and-query/)",
        "- [RedisVL Documentation](https://redis.io/docs/latest/integrate/redisvl/)",
        "- [Redis Security](https://redis.io/docs/latest/operate/oss_and_stack/management/security/)",
    ])
    
    return "\n".join(lines)


def main():
    """Main build function."""
    # Determine paths
    if len(sys.argv) > 1:
        rules_dir = Path(sys.argv[1])
    else:
        rules_dir = Path(__file__).parent / "src" / "redis_best_practices" / "knowledge" / "rules"
    
    output_dir = rules_dir.parent
    
    print(f"Building AGENTS.md from {rules_dir}")
    
    # Load sections
    sections_file = rules_dir / "_sections.md"
    if not sections_file.exists():
        print(f"Error: {sections_file} not found")
        sys.exit(1)
    
    sections = parse_sections(sections_file.read_text())
    print(f"Loaded {len(sections)} sections")
    
    # Load rules
    rule_count = 0
    for rule_file in sorted(rules_dir.glob("*.md")):
        if rule_file.name.startswith("_"):
            continue
        
        rule = parse_rule_file(rule_file)
        if rule:
            # Determine section from prefix (handle multi-part prefixes like "semantic-cache")
            prefix_parts = rule.prefix.split("-")
            section_prefix = prefix_parts[0]
            
            # Check for compound prefixes
            if len(prefix_parts) > 1:
                compound_prefix = f"{prefix_parts[0]}-{prefix_parts[1]}"
                if compound_prefix in sections:
                    section_prefix = compound_prefix
            
            if section_prefix in sections:
                sections[section_prefix].rules.append(rule)
                rule.section_num = sections[section_prefix].number
                rule_count += 1
            else:
                print(f"Warning: Unknown section prefix '{section_prefix}' for {rule_file.name}")
    
    print(f"Loaded {rule_count} rules")
    
    # Generate output
    output = generate_agents_md(sections)
    
    # Write output
    output_file = output_dir / "AGENTS.md"
    output_file.write_text(output)
    print(f"Generated {output_file}")
    
    # Print summary
    print("\nSummary:")
    for section in sorted(sections.values(), key=lambda s: s.number):
        print(f"  {section.number}. {section.name}: {len(section.rules)} rules")


if __name__ == "__main__":
    main()
