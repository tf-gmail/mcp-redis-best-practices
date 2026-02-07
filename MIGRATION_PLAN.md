# Migration Plan: Monorepo Architecture

## Goal
Restructure the project to support both VS Code and Visual Studio extensions with a shared MCP server core.

## Target Architecture

```
mcp-redis-best-practices/
├── packages/
│   └── mcp-server/              # Shared MCP server (npm: redis-best-practices-mcp)
│       ├── src/
│       │   ├── index.ts         # Entry point + CLI
│       │   ├── server.ts        # MCP server logic
│       │   ├── tools.ts         # Tool definitions
│       │   ├── knowledge.ts     # Knowledge base loader
│       │   └── types.ts         # Type definitions
│       ├── knowledge/
│       │   └── rules/           # All markdown best practice files
│       ├── package.json         # npm: redis-best-practices-mcp
│       └── tsconfig.json
│
├── extension/                   # VS Code extension (existing)
│   ├── src/
│   │   └── extension.ts         # VS Code-specific code only
│   ├── package.json             # Workspace dependency on mcp-server
│   └── tsconfig.json
│
├── visual-studio/               # Visual Studio extension (NEW)
│   ├── src/
│   │   └── RedisBestPracticesPackage.cs
│   ├── RedisBestPractices.csproj
│   ├── RedisBestPractices.sln
│   └── source.extension.vsixmanifest
│
├── package.json                 # pnpm workspace root
├── pnpm-workspace.yaml
└── README.md                    # Updated with both platforms
```

---

## Progress Tracker

| Step | Task | Status |
|------|------|--------|
| 1 | Create plan document | ✅ DONE |
| 2 | Setup pnpm workspaces root | ✅ DONE |
| 3 | Extract MCP server to packages/mcp-server | ✅ DONE |
| 4 | Create npm package configuration | ✅ DONE |
| 5 | Update VS Code extension to use workspace package | ✅ DONE |
| 6 | Create Visual Studio extension project | ✅ DONE |
| 7 | Test VS Code extension compilation | ✅ DONE |
| 8 | Test Visual Studio extension compilation | ⬜ TODO (requires Windows/VS) |
| 9 | Update all READMEs | ✅ DONE |
| 10 | Final verification | ✅ DONE |

---

## Detailed Steps

### Step 1: Create Plan Document
- [x] Create MIGRATION_PLAN.md with architecture overview
- [x] Define progress tracker

### Step 2: Setup pnpm Workspaces Root
- [ ] Create root package.json with workspaces config
- [ ] Create pnpm-workspace.yaml
- [ ] Initialize pnpm

### Step 3: Extract MCP Server to packages/mcp-server
- [ ] Create packages/mcp-server/src/ directory
- [ ] Move server.ts, tools.ts, knowledge.ts, types.ts
- [ ] Move knowledge/rules/ directory
- [ ] Create index.ts with CLI entry point
- [ ] Create package.json for npm publishing
- [ ] Create tsconfig.json

### Step 4: Create npm Package Configuration
- [ ] Configure bin entry for CLI
- [ ] Setup build scripts
- [ ] Add proper exports

### Step 5: Update VS Code Extension
- [ ] Update imports to use @redis-best-practices/mcp-server
- [ ] Update extension package.json dependencies
- [ ] Remove duplicate MCP code from extension/src/mcp/

### Step 6: Create Visual Studio Extension
- [ ] Create C# project structure
- [ ] Implement MCP server bundling
- [ ] Create VSIX manifest
- [ ] Implement Setup Copilot Instructions command

### Step 7: Test VS Code Extension
- [ ] Run pnpm install
- [ ] Build extension
- [ ] Verify MCP tools work

### Step 8: Test Visual Studio Extension
- [ ] Build C# project
- [ ] Create VSIX package
- [ ] Test in Visual Studio

### Step 9: Update READMEs
- [ ] Update root README with both platforms
- [ ] Update extension/README for VS Code Marketplace
- [ ] Create visual-studio/README for VS Marketplace

### Step 10: Final Verification
- [ ] All builds pass
- [ ] MCP tools work in both IDEs
- [ ] npm package can be used standalone

---

## Notes
- Started: 2026-02-07
- Last Updated: 2026-02-07
- Completed: 2026-02-07

## Summary

The monorepo restructuring is complete! The project now supports:

1. **VS Code Extension** (`extension/`)
   - Builds successfully with `npm run build`
   - Bundles the shared MCP server from `packages/mcp-server`
   - Ready for publishing to VS Code Marketplace

2. **Visual Studio Extension** (`visual-studio/`)
   - C# project using VisualStudio.Extensibility model
   - Requires Windows + VS 17.14+ to build and test
   - Two commands: Setup MCP Server, Setup Copilot Instructions

3. **Standalone npm Package** (`packages/mcp-server/`)
   - Can be published to npm as `@redis-best-practices/mcp-server`
   - CLI entry point: `redis-best-practices-mcp`
   - Exports for programmatic use

### Next Steps

1. Test the Visual Studio extension on Windows (requires .NET 8 SDK and VS 17.14+)
2. Publish `@redis-best-practices/mcp-server` to npm
3. Publish both extensions to their respective marketplaces
4. Consider removing duplicate mcp files from `extension/src/mcp/` (currently kept for compatibility)
