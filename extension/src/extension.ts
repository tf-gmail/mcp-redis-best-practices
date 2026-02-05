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
    statusBarItem.text = '$(database) Redis MCP';
    statusBarItem.tooltip = 'Redis Best Practices MCP Server';
    statusBarItem.command = 'redis-best-practices.showTopics';
    context.subscriptions.push(statusBarItem);

    // Get configuration
    const config = vscode.workspace.getConfiguration('redisBestPractices');
    const enabled = config.get<boolean>('enabled', true);

    if (enabled) {
        // Register the MCP server
        await registerMCPServer(context);
        statusBarItem.show();
    }

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('redis-best-practices.showTopics', showTopics),
        vscode.commands.registerCommand('redis-best-practices.restartServer', () => restartServer(context))
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

async function registerMCPServer(context: vscode.ExtensionContext): Promise<void> {
    const config = vscode.workspace.getConfiguration('redisBestPractices');
    const pythonPath = config.get<string>('pythonPath', 'python3');

    // Get the path to the bundled MCP server
    const mcpServerPath = path.join(context.extensionPath, 'mcp-server');
    
    // Check if mcp-server exists
    if (!fs.existsSync(mcpServerPath)) {
        vscode.window.showWarningMessage(
            'Redis Best Practices: MCP server not found. Please reinstall the extension.'
        );
        return;
    }

    // The MCP server configuration is registered via .vscode/mcp.json
    // For VS Code's built-in MCP support, we update the workspace configuration
    try {
        const mcpConfig = {
            servers: {
                'redis-best-practices': {
                    command: pythonPath,
                    args: ['-m', 'redis_best_practices'],
                    cwd: mcpServerPath
                }
            }
        };

        // Write MCP configuration to workspace if it doesn't exist
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (workspaceFolders && workspaceFolders.length > 0) {
            const vscodePath = path.join(workspaceFolders[0].uri.fsPath, '.vscode');
            const mcpConfigPath = path.join(vscodePath, 'mcp.json');

            // Only create if .vscode folder exists and mcp.json doesn't have our server
            if (fs.existsSync(vscodePath)) {
                let existingConfig: any = { servers: {} };
                
                if (fs.existsSync(mcpConfigPath)) {
                    try {
                        const content = fs.readFileSync(mcpConfigPath, 'utf8');
                        existingConfig = JSON.parse(content);
                    } catch {
                        // If parsing fails, start fresh
                    }
                }

                // Add our server if not present
                if (!existingConfig.servers?.['redis-best-practices']) {
                    existingConfig.servers = existingConfig.servers || {};
                    existingConfig.servers['redis-best-practices'] = mcpConfig.servers['redis-best-practices'];
                    
                    fs.writeFileSync(
                        mcpConfigPath,
                        JSON.stringify(existingConfig, null, 2)
                    );
                }
            }
        }

        statusBarItem.text = '$(database) Redis MCP ✓';
        statusBarItem.backgroundColor = undefined;
    } catch (error) {
        console.error('Failed to register MCP server:', error);
        statusBarItem.text = '$(database) Redis MCP ✗';
        statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
    }
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
    await registerMCPServer(context);
    vscode.window.showInformationMessage('Redis Best Practices MCP server restarted');
}

export function deactivate() {
    if (statusBarItem) {
        statusBarItem.dispose();
    }
}
