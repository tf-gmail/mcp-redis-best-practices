using System.Text.Json;
using System.Text.Json.Nodes;
using Microsoft.VisualStudio.Extensibility;
using Microsoft.VisualStudio.Extensibility.Commands;
using Microsoft.VisualStudio.Extensibility.Shell;

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
            // Get the bundled MCP server path
            var extensionDir = Path.GetDirectoryName(typeof(SetupMCPServerCommand).Assembly.Location)!;
            var mcpServerPath = Path.Combine(extensionDir, "mcp-bundle", "cli.js").Replace("\\", "/");

            var configSample = $$"""
{
  "servers": {
    "redis-best-practices": {
      "command": "node",
      "args": ["{{mcpServerPath}}"]
    }
  }
}
""";

            var message = $"""
To enable Redis Best Practices MCP tools:

1. Create a file named '.mcp.json' in your solution folder
2. Add this configuration:

{configSample}

3. Restart Visual Studio

The MCP server is bundled at:
{mcpServerPath}
""";

            await this.Extensibility.Shell().ShowPromptAsync(
                message,
                PromptOptions.OK,
                cancellationToken);
        }
        catch (Exception ex)
        {
            await this.Extensibility.Shell().ShowPromptAsync(
                $"Error: {ex.Message}",
                PromptOptions.OK,
                cancellationToken);
        }
    }
}
