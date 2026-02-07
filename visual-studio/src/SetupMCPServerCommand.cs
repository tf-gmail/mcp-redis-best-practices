using System.Text.Json;
using System.Text.Json.Nodes;
using Microsoft.VisualStudio.Extensibility;
using Microsoft.VisualStudio.Extensibility.Commands;
using Microsoft.VisualStudio.Extensibility.Shell;
using Microsoft.VisualStudio.ProjectSystem.Query;

namespace RedisBestPracticesMCP;

/// <summary>
/// Command to configure the MCP server in the solution's .mcp.json file.
/// </summary>
[VisualStudioContribution]
public class SetupMCPServerCommand : Command
{
    /// <inheritdoc/>
    public override CommandConfiguration CommandConfiguration => new("%RedisBestPracticesMCP.SetupMCPServerCommand.DisplayName%")
    {
        Placements = new[] { CommandPlacement.KnownPlacements.ToolsMenu },
        Icon = new(ImageMoniker.KnownValues.Database, IconSettings.IconAndText),
    };

    /// <inheritdoc/>
    public override async Task ExecuteCommandAsync(IClientContext context, CancellationToken cancellationToken)
    {
        try
        {
            // Query for the solution path using ProjectSystem.Query
            string? solutionDir = null;
            
            var result = await this.Extensibility.Workspaces().QuerySolutionAsync(
                solution => solution.With(s => s.Path),
                cancellationToken);
            
            if (result?.Path != null)
            {
                solutionDir = Path.GetDirectoryName(result.Path);
            }

            if (string.IsNullOrEmpty(solutionDir))
            {
                await this.Extensibility.Shell().ShowPromptAsync(
                    "No solution is currently open. Please open a solution first.",
                    PromptOptions.OK,
                    cancellationToken);
                return;
            }

            var mcpConfigPath = Path.Combine(solutionDir, ".mcp.json");

            // Get the bundled MCP server path
            var extensionDir = Path.GetDirectoryName(typeof(SetupMCPServerCommand).Assembly.Location)!;
            var mcpServerPath = Path.Combine(extensionDir, "mcp-bundle", "cli.js");

            JsonObject config;
            
            if (File.Exists(mcpConfigPath))
            {
                var existingContent = await File.ReadAllTextAsync(mcpConfigPath, cancellationToken);
                config = JsonNode.Parse(existingContent)?.AsObject() ?? new JsonObject();
            }
            else
            {
                config = new JsonObject();
            }

            // Ensure servers object exists
            if (!config.ContainsKey("servers"))
            {
                config["servers"] = new JsonObject();
            }

            var servers = config["servers"]!.AsObject();
            
            // Check if already configured
            if (servers.ContainsKey("redis-best-practices"))
            {
                await this.Extensibility.Shell().ShowPromptAsync(
                    "Redis Best Practices MCP server is already configured in .mcp.json",
                    PromptOptions.OK,
                    cancellationToken);
                return;
            }

            // Add our server configuration
            servers["redis-best-practices"] = new JsonObject
            {
                ["command"] = "node",
                ["args"] = new JsonArray { mcpServerPath },
                ["description"] = "Redis development best practices as MCP tools"
            };

            // Write the updated config
            var options = new JsonSerializerOptions { WriteIndented = true };
            var json = JsonSerializer.Serialize(config, options);
            await File.WriteAllTextAsync(mcpConfigPath, json, cancellationToken);

            await this.Extensibility.Shell().ShowPromptAsync(
                "Redis Best Practices MCP server configured in .mcp.json\n\nRestart Copilot Chat to activate the new tools.",
                PromptOptions.OK,
                cancellationToken);
        }
        catch (Exception ex)
        {
            await this.Extensibility.Shell().ShowPromptAsync(
                $"Error configuring MCP server: {ex.Message}",
                PromptOptions.OK,
                cancellationToken);
        }
    }
}
