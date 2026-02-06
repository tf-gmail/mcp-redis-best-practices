import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

let statusBarItem: vscode.StatusBarItem;

export async function activate(context: vscode.ExtensionContext) {
    console.log('Redis Best Practices MCP extension is activating...');

    // Create status bar item
    statusBarItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Right,
        100
    );
    statusBarItem.text = '$(sync~spin) Redis MCP';
    statusBarItem.tooltip = 'Redis Best Practices MCP Server - Setting up...';
    statusBarItem.command = 'redis-best-practices.showTopics';
    context.subscriptions.push(statusBarItem);
    statusBarItem.show();

    // Get configuration
    const config = vscode.workspace.getConfiguration('redisBestPractices');
    const enabled = config.get<boolean>('enabled', true);

    if (enabled) {
        // Register the MCP server
        const success = await registerMCPServer(context);
        if (success) {
            statusBarItem.text = '$(database) Redis MCP ✓';
            statusBarItem.tooltip = 'Redis Best Practices MCP Server - Running';
        } else {
            statusBarItem.text = '$(database) Redis MCP ✗';
            statusBarItem.tooltip = 'Redis Best Practices MCP Server - Setup failed';
            statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
        }
    } else {
        statusBarItem.hide();
    }

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('redis-best-practices.showTopics', showTopics),
        vscode.commands.registerCommand('redis-best-practices.restartServer', () => restartServer(context)),
        vscode.commands.registerCommand('redis-best-practices.setupCopilotInstructions', setupCopilotInstructions)
    );

    // Listen for configuration changes
    context.subscriptions.push(
        vscode.workspace.onDidChangeConfiguration(async (e) => {
            if (e.affectsConfiguration('redisBestPractices.enabled')) {
                const newEnabled = config.get<boolean>('enabled', true);
                if (newEnabled) {
                    await registerMCPServer(context);
                    statusBarItem.show();
                } else {
                    statusBarItem.hide();
                }
            }
        })
    );

    console.log('Redis Best Practices MCP extension activated');
}

async function registerMCPServer(context: vscode.ExtensionContext): Promise<boolean> {
    const mcpServerPath = path.join(context.extensionPath, 'dist', 'mcp', 'server.js');
    
    // Check if the MCP server exists
    if (!fs.existsSync(mcpServerPath)) {
        vscode.window.showErrorMessage(
            'Redis Best Practices: MCP server not found. Please reinstall the extension.'
        );
        return false;
    }

    // Write MCP configuration to workspace
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (workspaceFolders && workspaceFolders.length > 0) {
        const vscodePath = path.join(workspaceFolders[0].uri.fsPath, '.vscode');
        const mcpConfigPath = path.join(vscodePath, 'mcp.json');

        // Create .vscode folder if it doesn't exist
        if (!fs.existsSync(vscodePath)) {
            fs.mkdirSync(vscodePath, { recursive: true });
        }

        let existingConfig: { servers?: Record<string, unknown> } = { servers: {} };
        
        if (fs.existsSync(mcpConfigPath)) {
            try {
                const content = fs.readFileSync(mcpConfigPath, 'utf8');
                existingConfig = JSON.parse(content);
            } catch {
                // If parsing fails, start fresh
            }
        }

        // Add our server configuration
        existingConfig.servers = existingConfig.servers || {};
        existingConfig.servers['redis-best-practices'] = {
            command: 'node',
            args: [mcpServerPath],
            description: 'Redis development best practices as MCP tools'
        };
        
        fs.writeFileSync(
            mcpConfigPath,
            JSON.stringify(existingConfig, null, 2)
        );
    }

    return true;
}

async function showTopics(): Promise<void> {
    const topics = [
        { label: '$(key) Key Naming', description: 'Best practices for Redis key naming conventions', topic: 'data-key-naming' },
        { label: '$(list-tree) Data Structures', description: 'Choosing the right Redis data structure', topic: 'data-choose-structure' },
        { label: '$(plug) Connection Pooling', description: 'Connection pool configuration', topic: 'conn-pooling' },
        { label: '$(layers) Pipelining', description: 'Batch operations with pipelines', topic: 'conn-pipelining' },
        { label: '$(watch) Timeouts', description: 'Connection and command timeouts', topic: 'conn-timeouts' },
        { label: '$(warning) Blocking Commands', description: 'Handling blocking operations', topic: 'conn-blocking' },
        { label: '$(dashboard) Memory Limits', description: 'Memory management and limits', topic: 'ram-limits' },
        { label: '$(clock) TTL & Expiration', description: 'Key expiration strategies', topic: 'ram-ttl' },
        { label: '$(shield) Authentication', description: 'Redis authentication setup', topic: 'security-auth' },
        { label: '$(lock) ACLs', description: 'Access Control Lists', topic: 'security-acls' },
        { label: '$(globe) Network Security', description: 'Network security configuration', topic: 'security-network' },
        { label: '$(json) JSON vs Hash', description: 'When to use JSON vs Hash', topic: 'json-vs-hash' },
        { label: '$(search) Query Engine', description: 'Redis Query Engine indexing', topic: 'rqe-index-creation' },
        { label: '$(symbol-array) Vector Search', description: 'Vector similarity search', topic: 'vector-algorithm-choice' },
        { label: '$(lightbulb) Semantic Cache', description: 'Semantic caching patterns', topic: 'semantic-cache-best-practices' },
    ];

    const selected = await vscode.window.showQuickPick(topics, {
        placeHolder: 'Select a Redis best practice topic',
        matchOnDescription: true
    });

    if (selected) {
        // Open the topic in a webview or show in output
        const message = `Ask GitHub Copilot: "What are the best practices for ${selected.label.replace(/\$\([^)]+\)\s*/, '')}?"`;
        
        const action = await vscode.window.showInformationMessage(
            message,
            'Copy to Clipboard',
            'Open Chat'
        );

        if (action === 'Copy to Clipboard') {
            await vscode.env.clipboard.writeText(
                `@workspace What are the Redis best practices for ${selected.topic}?`
            );
            vscode.window.showInformationMessage('Copied to clipboard!');
        } else if (action === 'Open Chat') {
            // Try to open Copilot chat with the query
            vscode.commands.executeCommand('workbench.action.chat.open', {
                query: `What are the Redis best practices for ${selected.topic}?`
            });
        }
    }
}

async function restartServer(context: vscode.ExtensionContext): Promise<void> {
    statusBarItem.text = '$(sync~spin) Redis MCP';
    statusBarItem.tooltip = 'Redis Best Practices MCP Server - Restarting...';
    const success = await registerMCPServer(context);
    if (success) {
        statusBarItem.text = '$(database) Redis MCP ✓';
        statusBarItem.tooltip = 'Redis Best Practices MCP Server - Running';
        statusBarItem.backgroundColor = undefined;
        vscode.window.showInformationMessage('Redis Best Practices MCP server restarted');
    } else {
        statusBarItem.text = '$(database) Redis MCP ✗';
        statusBarItem.tooltip = 'Redis Best Practices MCP Server - Failed';
        statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
    }
}

const COPILOT_INSTRUCTIONS_CONTENT = `
## Redis Development

When writing, reviewing, or debugging code that uses Redis:
1. Use the \`get_best_practice\` tool to check relevant patterns
2. Use the \`get_anti_patterns\` tool to avoid common mistakes  
3. Use the \`get_code_example\` tool for production-ready snippets

Always consult Redis best practices for: connection pooling, key naming,
data structure selection, memory management, and security.
`;

async function setupCopilotInstructions(): Promise<void> {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders || workspaceFolders.length === 0) {
        vscode.window.showErrorMessage('No workspace folder open. Please open a folder first.');
        return;
    }

    const workspacePath = workspaceFolders[0].uri.fsPath;
    const githubPath = path.join(workspacePath, '.github');
    const instructionsPath = path.join(githubPath, 'copilot-instructions.md');

    // Create .github folder if it doesn't exist
    if (!fs.existsSync(githubPath)) {
        fs.mkdirSync(githubPath, { recursive: true });
    }

    if (fs.existsSync(instructionsPath)) {
        // Check if Redis instructions already exist
        const existingContent = fs.readFileSync(instructionsPath, 'utf8');
        if (existingContent.includes('Redis Development') || existingContent.includes('get_best_practice')) {
            vscode.window.showInformationMessage('Redis instructions already exist in copilot-instructions.md');
            return;
        }

        // Append to existing file
        const newContent = existingContent + '\n' + COPILOT_INSTRUCTIONS_CONTENT;
        fs.writeFileSync(instructionsPath, newContent);
        vscode.window.showInformationMessage('Redis instructions added to existing copilot-instructions.md');
    } else {
        // Create new file
        const header = '# Copilot Instructions\n\nThese instructions help GitHub Copilot provide better assistance for this project.\n';
        fs.writeFileSync(instructionsPath, header + COPILOT_INSTRUCTIONS_CONTENT);
        vscode.window.showInformationMessage('Created .github/copilot-instructions.md with Redis instructions');
    }

    // Open the file
    const doc = await vscode.workspace.openTextDocument(instructionsPath);
    await vscode.window.showTextDocument(doc);
}

export function deactivate() {
    if (statusBarItem) {
        statusBarItem.dispose();
    }
}
