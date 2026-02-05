/**
 * Knowledge base for Redis best practices.
 * 
 * This module handles loading, parsing, and querying the Redis best practices
 * knowledge base from markdown files.
 */

import * as fs from 'fs';
import * as path from 'path';
import {
    Rule,
    Section,
    AntiPattern,
    CodeExample,
    Reference,
    CATEGORY_MAP,
    PATTERN_MAP,
    CODE_EXAMPLE_PATTERNS,
    RULE_PREFIXES,
} from './types';

/**
 * Knowledge base for Redis best practices.
 * Loads and indexes rules from markdown files for efficient querying.
 */
export class KnowledgeBase {
    private knowledgeDir: string;
    private rulesDir: string;
    private sections: Map<string, Section> = new Map();
    private rules: Map<string, Rule> = new Map();
    private rulesByTag: Map<string, Rule[]> = new Map();
    private fullGuide: string = '';

    constructor(knowledgeDir?: string) {
        if (knowledgeDir) {
            this.knowledgeDir = knowledgeDir;
        } else {
            // Default to bundled knowledge directory
            this.knowledgeDir = path.join(__dirname, 'knowledge');
        }
        this.rulesDir = path.join(this.knowledgeDir, 'rules');
        this.loadKnowledgeBase();
    }

    private loadKnowledgeBase(): void {
        this.loadSections();
        this.loadRules();
        this.loadFullGuide();
    }

    private loadSections(): void {
        const sectionsFile = path.join(this.rulesDir, '_sections.md');
        if (!fs.existsSync(sectionsFile)) {
            return;
        }

        const content = fs.readFileSync(sectionsFile, 'utf-8');

        // Parse sections
        const sectionPattern = /## (\d+)\. ([^(]+)\((\w+(?:-\w+)?)\)\s*\n\*\*Impact:\*\* (\w+)\s*\n\*\*Description:\*\* (.+)/g;

        let match;
        while ((match = sectionPattern.exec(content)) !== null) {
            const number = parseInt(match[1], 10);
            const name = match[2].trim();
            const prefix = match[3].trim();
            const impact = match[4].trim();
            const description = match[5].trim();

            this.sections.set(prefix, {
                number,
                name,
                prefix,
                impact,
                description,
                rules: [],
            });
        }
    }

    private loadRules(): void {
        if (!fs.existsSync(this.rulesDir)) {
            return;
        }

        const files = fs.readdirSync(this.rulesDir);
        for (const file of files) {
            // Skip special files
            if (file.startsWith('_')) {
                continue;
            }
            if (!file.endsWith('.md')) {
                continue;
            }

            const filePath = path.join(this.rulesDir, file);
            const rule = this.parseRuleFile(filePath);
            if (rule) {
                this.rules.set(rule.prefix, rule);

                // Index by tags
                for (const tag of rule.tags) {
                    if (!this.rulesByTag.has(tag)) {
                        this.rulesByTag.set(tag, []);
                    }
                    this.rulesByTag.get(tag)!.push(rule);
                }

                // Add to section
                const sectionPrefix = this.getSectionPrefix(rule.prefix);
                const section = this.sections.get(sectionPrefix);
                if (section) {
                    section.rules.push(rule);
                    rule.sectionNumber = section.number;
                }
            }
        }
    }

    private getSectionPrefix(rulePrefix: string): string {
        // Handle compound prefixes like 'semantic-cache-best-practices'
        for (const prefix of ['semantic-cache', 'data', 'conn', 'ram', 'json', 'rqe', 'vector', 'stream', 'cluster', 'security', 'observe']) {
            if (rulePrefix.startsWith(prefix + '-') || rulePrefix === prefix) {
                return prefix;
            }
        }
        return rulePrefix.split('-')[0];
    }

    private parseRuleFile(filePath: string): Rule | null {
        const content = fs.readFileSync(filePath, 'utf-8');

        // Parse frontmatter
        const frontmatterMatch = content.match(/^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$/);
        if (!frontmatterMatch) {
            return null;
        }

        const frontmatter = frontmatterMatch[1];
        const body = frontmatterMatch[2];

        // Extract frontmatter fields
        const titleMatch = frontmatter.match(/title:\s*(.+)/);
        const impactMatch = frontmatter.match(/impact:\s*(\w+)/);
        const impactDescMatch = frontmatter.match(/impactDescription:\s*(.+)/);
        const tagsMatch = frontmatter.match(/tags:\s*(.+)/);

        if (!titleMatch || !impactMatch) {
            return null;
        }

        const title = titleMatch[1].trim();
        const impact = impactMatch[1].trim();
        const impactDescription = impactDescMatch ? impactDescMatch[1].trim() : '';
        const tags = tagsMatch ? tagsMatch[1].split(',').map(t => t.trim()) : [];

        // Extract prefix from filename
        const prefix = path.basename(filePath, '.md');

        // Extract summary (first paragraph of body after first heading)
        const summaryMatch = body.match(/##[^\n]+\n+([^\n#]+)/);
        const summary = summaryMatch ? summaryMatch[1].trim() : '';

        return {
            prefix,
            title,
            impact,
            impactDescription,
            tags,
            content: body,
            summary,
            sectionNumber: 0,
        };
    }

    private loadFullGuide(): void {
        const agentsFile = path.join(this.knowledgeDir, 'AGENTS.md');
        if (fs.existsSync(agentsFile)) {
            this.fullGuide = fs.readFileSync(agentsFile, 'utf-8');
        } else {
            this.fullGuide = this.generateFullGuide();
        }
    }

    private generateFullGuide(): string {
        const lines: string[] = [
            '# Redis Development Best Practices',
            '',
            '**Version 0.1.0**',
            'MCP Redis Best Practices',
            '',
            '> **Note:**',
            '> This document is optimized for AI agents and LLMs to follow when',
            '> generating or refactoring Redis applications.',
            '',
            '---',
            '',
            '## Abstract',
            '',
            'Best practices for Redis including data structures, memory management,',
            'connection handling, security, and performance optimization.',
            '',
            '---',
            '',
            '## Table of Contents',
            '',
        ];

        // Add TOC
        const sortedSections = Array.from(this.sections.values())
            .sort((a, b) => a.number - b.number);

        for (const section of sortedSections) {
            const anchor = `${section.number}-${section.name.toLowerCase().replace(/ /g, '-')}`;
            lines.push(`${section.number}. [${section.name}](#${anchor}) — **${section.impact}**`);
            for (const rule of section.rules.sort((a, b) => a.title.localeCompare(b.title))) {
                const ruleAnchor = rule.title.toLowerCase().replace(/ /g, '-');
                lines.push(`   - [${rule.title}](#${ruleAnchor})`);
            }
        }

        lines.push('');
        lines.push('---');
        lines.push('');

        // Add sections
        for (const section of sortedSections) {
            lines.push(`## ${section.number}. ${section.name}`);
            lines.push('');
            lines.push(`**Impact:** ${section.impact}`);
            lines.push('');
            lines.push(`*${section.description}*`);
            lines.push('');

            for (const rule of section.rules.sort((a, b) => a.title.localeCompare(b.title))) {
                lines.push(`### ${rule.title}`);
                lines.push('');
                lines.push(`**Impact: ${rule.impact}** (${rule.impactDescription})`);
                lines.push('');
                lines.push(rule.content);
                lines.push('');
                lines.push('---');
                lines.push('');
            }
        }

        return lines.join('\n');
    }

    /**
     * Convert a rule to markdown format.
     */
    ruleToMarkdown(rule: Rule): string {
        const lines: string[] = [`# ${rule.title}\n`];
        lines.push(`**Impact:** ${rule.impact} (${rule.impactDescription})\n`);
        lines.push(`**Tags:** ${rule.tags.join(', ')}\n`);
        lines.push('---\n');
        lines.push(rule.content);
        return lines.join('\n');
    }

    /**
     * Get a rule by its topic/prefix.
     */
    getRuleByTopic(topic: string): Rule | null {
        // Direct lookup
        if (this.rules.has(topic)) {
            return this.rules.get(topic)!;
        }

        // Try with common prefixes
        for (const prefix of RULE_PREFIXES) {
            const fullKey = `${prefix}${topic}`;
            if (this.rules.has(fullKey)) {
                return this.rules.get(fullKey)!;
            }
        }

        return null;
    }

    /**
     * Search rules by query string.
     */
    searchRules(query: string): Rule[] {
        const queryLower = query.toLowerCase();
        const queryWords = new Set(queryLower.split(/\s+/));

        const scoredRules: Array<{ score: number; rule: Rule }> = [];

        for (const rule of this.rules.values()) {
            let score = 0;

            // Title match (highest weight)
            if (rule.title.toLowerCase().includes(queryLower)) {
                score += 10;
            }

            // Exact title word match
            const titleWords = new Set(rule.title.toLowerCase().split(/\s+/));
            for (const word of queryWords) {
                if (titleWords.has(word)) {
                    score += 5;
                }
            }

            // Tag match
            for (const tag of rule.tags) {
                if (tag.toLowerCase().includes(queryLower)) {
                    score += 3;
                }
                if (queryWords.has(tag.toLowerCase())) {
                    score += 2;
                }
            }

            // Content match
            if (rule.content.toLowerCase().includes(queryLower)) {
                score += 1;
            }

            // Impact description match
            if (rule.impactDescription.toLowerCase().includes(queryLower)) {
                score += 2;
            }

            if (score > 0) {
                scoredRules.push({ score, rule });
            }
        }

        // Sort by score descending
        scoredRules.sort((a, b) => b.score - a.score);

        return scoredRules.map(sr => sr.rule);
    }

    /**
     * List all available topics.
     */
    listAllTopics(): string[] {
        return Array.from(this.rules.keys()).sort();
    }

    /**
     * Get all sections, optionally filtered by category.
     */
    getSections(category?: string): Section[] {
        let sections = Array.from(this.sections.values())
            .sort((a, b) => a.number - b.number);

        if (category) {
            const prefix = CATEGORY_MAP[category] || category;
            sections = sections.filter(s => s.prefix === prefix);
        }

        return sections;
    }

    /**
     * Get anti-patterns, optionally filtered by topic.
     */
    getAntiPatterns(topic?: string): Record<string, AntiPattern[]> {
        const antiPatterns: Record<string, AntiPattern[]> = {};

        for (const rule of this.rules.values()) {
            // Filter by topic if specified
            if (topic) {
                const topicLower = topic.toLowerCase();
                if (!rule.prefix.includes(topicLower) && 
                    !rule.tags.join(' ').toLowerCase().includes(topicLower)) {
                    continue;
                }
            }

            // Find incorrect patterns in content
            const incorrectPattern = /\*\*Incorrect[^*]*\*\*[:\s]*([^\n]*)\n+```(\w+)\n([\s\S]*?)```/g;
            const correctPattern = /\*\*Correct[^*]*\*\*[:\s]*([^\n]*)\n+```(\w+)\n([\s\S]*?)```/g;

            const incorrectMatches: RegExpExecArray[] = [];
            const correctMatches: RegExpExecArray[] = [];

            let match;
            while ((match = incorrectPattern.exec(rule.content)) !== null) {
                incorrectMatches.push(match);
            }
            while ((match = correctPattern.exec(rule.content)) !== null) {
                correctMatches.push(match);
            }

            if (incorrectMatches.length > 0 && correctMatches.length > 0) {
                const sectionPrefix = this.getSectionPrefix(rule.prefix);
                const section = this.sections.get(sectionPrefix);
                const category = section?.name || 'Other';

                if (!antiPatterns[category]) {
                    antiPatterns[category] = [];
                }

                for (let i = 0; i < Math.min(incorrectMatches.length, correctMatches.length); i++) {
                    const inc = incorrectMatches[i];
                    const cor = correctMatches[i];
                    antiPatterns[category].push({
                        title: inc[1].trim() || rule.title,
                        reason: rule.impactDescription,
                        badCode: inc[3].trim(),
                        goodCode: cor[3].trim(),
                        language: inc[2],
                        category,
                    });
                }
            }
        }

        return antiPatterns;
    }

    /**
     * Get a code example for a specific pattern.
     */
    getCodeExample(pattern: string, language: string = 'python'): CodeExample | null {
        // Normalize pattern
        const patternNormalized = pattern.toLowerCase().replace(/_/g, '-').replace(/ /g, '-');
        const rulePrefix = PATTERN_MAP[patternNormalized] || patternNormalized;

        const rule = this.getRuleByTopic(rulePrefix);
        if (!rule) {
            return null;
        }

        // Extract code example from rule
        const codePattern = new RegExp(`\`\`\`${language}\\n([\\s\\S]*?)\`\`\``, 'g');
        let match = codePattern.exec(rule.content);

        if (!match) {
            // Try any code block
            const anyCodePattern = /```\w*\n([\s\S]*?)```/;
            match = anyCodePattern.exec(rule.content);
        }

        if (!match) {
            return null;
        }

        // Extract references
        const refs: Reference[] = [];
        const refPattern = /Reference:\s*\[([^\]]+)\]\(([^)]+)\)/g;
        let refMatch;
        while ((refMatch = refPattern.exec(rule.content)) !== null) {
            refs.push({
                title: refMatch[1],
                url: refMatch[2],
            });
        }

        return {
            title: rule.title,
            description: rule.summary || rule.impactDescription,
            code: match[1].trim(),
            language,
            notes: [],
            references: refs,
        };
    }

    /**
     * List all available code example patterns.
     */
    listCodeExamples(): string[] {
        return CODE_EXAMPLE_PATTERNS;
    }

    /**
     * Get the complete best practices guide.
     */
    getFullGuide(): string {
        return this.fullGuide;
    }
}
