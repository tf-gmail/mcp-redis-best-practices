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
            // Get the solution directory
            var solutionPath = await this.Extensibility.Workspaces().GetSolutionPathAsync(cancellationToken);
            
            if (string.IsNullOrEmpty(solutionPath))
            {
                await this.Extensibility.Shell().ShowPromptAsync(
                    "No solution is currently open. Please open a solution first.",
                    PromptOptions.OK,
                    cancellationToken);
                return;
            }

            var solutionDir = Path.GetDirectoryName(solutionPath)!;
            var githubDir = Path.Combine(solutionDir, ".github");
            var instructionsPath = Path.Combine(githubDir, "copilot-instructions.md");

            // Create .github directory if needed
            if (!Directory.Exists(githubDir))
            {
                Directory.CreateDirectory(githubDir);
            }

            if (File.Exists(instructionsPath))
            {
                // Check if Redis instructions already exist
                var existingContent = await File.ReadAllTextAsync(instructionsPath, cancellationToken);
                if (existingContent.Contains("Redis Development") || existingContent.Contains("get_best_practice"))
                {
                    await this.Extensibility.Shell().ShowPromptAsync(
                        "Redis instructions already exist in copilot-instructions.md",
                        PromptOptions.OK,
                        cancellationToken);
                    return;
                }

                // Append to existing file
                var newContent = existingContent + "\n" + CopilotInstructionsContent;
                await File.WriteAllTextAsync(instructionsPath, newContent, cancellationToken);
                
                await this.Extensibility.Shell().ShowPromptAsync(
                    "Redis instructions added to existing copilot-instructions.md",
                    PromptOptions.OK,
                    cancellationToken);
            }
            else
            {
                // Create new file
                var header = "# Copilot Instructions\n\nThese instructions help GitHub Copilot provide better assistance for this project.\n";
                await File.WriteAllTextAsync(instructionsPath, header + CopilotInstructionsContent, cancellationToken);
                
                await this.Extensibility.Shell().ShowPromptAsync(
                    "Created .github/copilot-instructions.md with Redis instructions",
                    PromptOptions.OK,
                    cancellationToken);
            }
        }
        catch (Exception ex)
        {
            await this.Extensibility.Shell().ShowPromptAsync(
                $"Error setting up Copilot instructions: {ex.Message}",
                PromptOptions.OK,
                cancellationToken);
        }
    }
}
