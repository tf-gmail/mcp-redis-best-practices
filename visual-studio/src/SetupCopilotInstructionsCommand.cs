using System.Diagnostics;
using Microsoft.VisualStudio.Extensibility;
using Microsoft.VisualStudio.Extensibility.Commands;
using Microsoft.VisualStudio.Extensibility.Shell;

namespace RedisBestPracticesMCP;

/// <summary>
/// Command to setup the .github/copilot-instructions.md file for Redis best practices.
/// </summary>
[VisualStudioContribution]
public class SetupCopilotInstructionsCommand : Command
{
    private const string CopilotInstructionsContent = """
# Copilot Instructions

These instructions help GitHub Copilot provide better assistance for this project.

## Redis Development

When writing, reviewing, or debugging code that uses Redis:
1. Use the `get_best_practice` tool to check relevant patterns
2. Use the `get_anti_patterns` tool to avoid common mistakes  
3. Use the `get_code_example` tool for production-ready snippets

Always consult Redis best practices for: connection pooling, key naming,
data structure selection, memory management, and security.
""";

    /// <inheritdoc/>
    public override CommandConfiguration CommandConfiguration => new("%RedisBestPracticesMCP.SetupCopilotInstructionsCommand.DisplayName%")
    {
        Placements = new[] { CommandPlacement.KnownPlacements.ToolsMenu },
        Icon = new(ImageMoniker.KnownValues.Settings, IconSettings.IconAndText),
    };

    /// <inheritdoc/>
    public override async Task ExecuteCommandAsync(IClientContext context, CancellationToken cancellationToken)
    {
        try
        {
            var message = $"""
To add Redis Best Practices to Copilot instructions:

1. Create a folder named '.github' in your solution folder
2. Create a file named 'copilot-instructions.md' inside it
3. Add this content:

{CopilotInstructionsContent}

This ensures Copilot will suggest using Redis best practices tools.
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
