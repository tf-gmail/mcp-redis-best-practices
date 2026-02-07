using Microsoft.VisualStudio.Extensibility;

namespace RedisBestPracticesMCP;

/// <summary>
/// Redis Best Practices MCP extension for Visual Studio.
/// Provides Redis development best practices as MCP tools for GitHub Copilot.
/// </summary>
[VisualStudioContribution]
public class RedisBestPracticesExtension : Extension
{
    /// <inheritdoc/>
    public override ExtensionConfiguration ExtensionConfiguration => new()
    {
        Metadata = new(
            id: "RedisBestPracticesMCP.A1B2C3D4-E5F6-7890-ABCD-EF1234567890",
            version: this.ExtensionAssemblyVersion,
            publisherName: "Thomas Findelkind",
            displayName: "Redis Best Practices MCP",
            description: "Get expert Redis guidance in your IDE. 29 best practices for data structures, memory, security, vector search, and more - powered by MCP for GitHub Copilot.")
    };
}
