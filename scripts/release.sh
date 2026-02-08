#!/bin/bash
#
# Release script for Redis Best Practices MCP Extension
# Handles version bumping and publishing to VS Code and Visual Studio Marketplaces
#
# Usage:
#   ./scripts/release.sh [patch|minor|major]    # Bump version and publish
#   ./scripts/release.sh --publish-only         # Publish without version bump
#   ./scripts/release.sh --dry-run [patch|minor|major]  # Preview changes
#
# Environment variables:
#   VSCE_PAT          - VS Code Marketplace Personal Access Token
#   VSIX_PAT          - Visual Studio Marketplace Personal Access Token (optional)
#   SKIP_VSCODE       - Set to 1 to skip VS Code publishing
#   SKIP_VS           - Set to 1 to skip Visual Studio publishing
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}ℹ${NC} $1"; }
log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }

# Current versions
get_vscode_version() {
    node -p "require('$ROOT_DIR/extension/package.json').version"
}

get_mcp_version() {
    node -p "require('$ROOT_DIR/packages/mcp-server/package.json').version"
}

get_vs_version() {
    grep '<Version>' "$ROOT_DIR/visual-studio/RedisBestPracticesMCP.csproj" 2>/dev/null | sed 's/.*<Version>\([^<]*\)<\/Version>.*/\1/' || echo "1.0.0"
}

# Version bumping
bump_version() {
    local version=$1
    local bump_type=$2
    
    IFS='.' read -ra parts <<< "$version"
    local major="${parts[0]}"
    local minor="${parts[1]}"
    local patch="${parts[2]}"
    
    case "$bump_type" in
        major) echo "$((major + 1)).0.0" ;;
        minor) echo "$major.$((minor + 1)).0" ;;
        patch) echo "$major.$minor.$((patch + 1))" ;;
        *) echo "$version" ;;
    esac
}

update_vscode_version() {
    local new_version=$1
    cd "$ROOT_DIR/extension"
    npm version "$new_version" --no-git-tag-version
    log_success "VS Code extension version updated to $new_version"
}

update_mcp_version() {
    local new_version=$1
    cd "$ROOT_DIR/packages/mcp-server"
    npm version "$new_version" --no-git-tag-version
    log_success "MCP server version updated to $new_version"
}

update_vs_version() {
    local new_version=$1
    local csproj="$ROOT_DIR/visual-studio/RedisBestPracticesMCP.csproj"
    
    if grep -q '<Version>' "$csproj"; then
        # macOS compatible sed (uses -i '' instead of -i.bak)
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|<Version>[^<]*</Version>|<Version>$new_version</Version>|g" "$csproj"
        else
            sed -i "s|<Version>[^<]*</Version>|<Version>$new_version</Version>|g" "$csproj"
        fi
    else
        # Add version property if not present
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|<AssemblyName>|<Version>$new_version</Version>\n    <AssemblyName>|g" "$csproj"
        else
            sed -i "s|<AssemblyName>|<Version>$new_version</Version>\n    <AssemblyName>|g" "$csproj"
        fi
    fi
    log_success "Visual Studio extension version updated to $new_version"
}

update_root_version() {
    local new_version=$1
    cd "$ROOT_DIR"
    npm version "$new_version" --no-git-tag-version
    log_success "Root package version updated to $new_version"
}

# Build functions
build_all() {
    log_info "Building all packages..."
    cd "$ROOT_DIR"
    
    # Build MCP server first (dependency)
    log_info "Building MCP server..."
    pnpm --filter @redis-best-practices/mcp-server build
    log_success "MCP server built"
    
    # Build VS Code extension
    log_info "Building VS Code extension..."
    pnpm --filter redis-best-practices-mcp build
    log_success "VS Code extension built"
    
    # Package VS Code extension
    log_info "Packaging VS Code extension..."
    cd "$ROOT_DIR/extension"
    npx vsce package --no-dependencies
    log_success "VS Code extension packaged"
    
    cd "$ROOT_DIR"
}

# Publishing functions
publish_vscode() {
    if [[ "${SKIP_VSCODE:-0}" == "1" ]]; then
        log_warn "Skipping VS Code Marketplace (SKIP_VSCODE=1)"
        return 0
    fi
    
    if [[ -z "${VSCE_PAT:-}" ]]; then
        log_error "VSCE_PAT environment variable not set"
        log_info "Get a PAT from: https://dev.azure.com/your-org/_usersSettings/tokens"
        log_info "Required scopes: Marketplace > Manage"
        return 1
    fi
    
    log_info "Publishing to VS Code Marketplace..."
    cd "$ROOT_DIR/extension"
    npx vsce publish --pat "$VSCE_PAT" --no-dependencies
    log_success "Published to VS Code Marketplace"
}

publish_vs() {
    if [[ "${SKIP_VS:-0}" == "1" ]]; then
        log_warn "Skipping Visual Studio Marketplace (SKIP_VS=1)"
        return 0
    fi
    
    # Visual Studio Marketplace requires manual upload or VsixPublisher.exe (Windows only)
    log_warn "Visual Studio Marketplace publishing requires manual steps:"
    echo ""
    echo "  1. Build on Windows: dotnet publish -c Release"
    echo "  2. Go to: https://marketplace.visualstudio.com/manage/publishers/ThomasFindelkind"
    echo "  3. Upload the VSIX from: visual-studio/bin/Release/net8.0-windows/publish/"
    echo ""
    echo "  Or use VsixPublisher.exe on Windows:"
    echo "  VsixPublisher.exe publish -payload <vsix> -publishManifest <manifest.json> -personalAccessToken <PAT>"
    echo ""
}

# Git operations
git_commit_and_tag() {
    local version=$1
    
    cd "$ROOT_DIR"
    
    log_info "Creating git commit and tag..."
    git add -A
    git commit -m "chore: release v$version" -m "
- VS Code extension: v$version
- MCP server: v$version
- Visual Studio extension: v$version
"
    git tag -a "v$version" -m "Release v$version"
    log_success "Created commit and tag v$version"
    
    log_info "Push with: git push && git push --tags"
}

# Main function
main() {
    local bump_type=""
    local dry_run=false
    local publish_only=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --dry-run)
                dry_run=true
                shift
                ;;
            --publish-only)
                publish_only=true
                shift
                ;;
            patch|minor|major)
                bump_type="$1"
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [options] [patch|minor|major]"
                echo ""
                echo "Options:"
                echo "  --dry-run        Preview changes without making them"
                echo "  --publish-only   Publish current version without bumping"
                echo "  -h, --help       Show this help"
                echo ""
                echo "Environment variables:"
                echo "  VSCE_PAT         VS Code Marketplace PAT (required for publishing)"
                echo "  SKIP_VSCODE      Set to 1 to skip VS Code publishing"
                echo "  SKIP_VS          Set to 1 to skip VS Marketplace publishing"
                exit 0
                ;;
            *)
                log_error "Unknown argument: $1"
                exit 1
                ;;
        esac
    done
    
    # Show current versions
    echo ""
    log_info "Current versions:"
    echo "  VS Code extension: $(get_vscode_version)"
    echo "  MCP server:        $(get_mcp_version)"
    echo "  VS extension:      $(get_vs_version || echo 'not set')"
    echo ""
    
    if [[ "$publish_only" == "true" ]]; then
        log_info "Publishing current version..."
        build_all
        publish_vscode
        publish_vs
        log_success "Publishing complete!"
        exit 0
    fi
    
    if [[ -z "$bump_type" ]]; then
        log_error "Please specify version bump type: patch, minor, or major"
        exit 1
    fi
    
    # Calculate new version
    local current_version
    current_version=$(get_vscode_version)
    local new_version
    new_version=$(bump_version "$current_version" "$bump_type")
    
    echo ""
    log_info "Version bump: $current_version → $new_version ($bump_type)"
    echo ""
    
    if [[ "$dry_run" == "true" ]]; then
        log_warn "Dry run - no changes will be made"
        echo ""
        echo "Would update:"
        echo "  - extension/package.json"
        echo "  - packages/mcp-server/package.json"
        echo "  - visual-studio/RedisBestPracticesMCP.csproj"
        echo "  - package.json (root)"
        echo ""
        echo "Would create:"
        echo "  - Git commit: 'chore: release v$new_version'"
        echo "  - Git tag: v$new_version"
        echo ""
        exit 0
    fi
    
    # Ensure clean working directory
    if [[ -n "$(git status --porcelain)" ]]; then
        log_warn "Working directory has uncommitted changes"
        read -p "Continue anyway? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Update all versions
    log_info "Updating versions..."
    update_mcp_version "$new_version"
    update_vscode_version "$new_version"
    update_vs_version "$new_version"
    update_root_version "$new_version"
    
    # Build everything
    build_all
    
    # Create git commit and tag
    git_commit_and_tag "$new_version"
    
    # Publish
    echo ""
    read -p "Publish to marketplaces? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        publish_vscode
        publish_vs
    else
        log_info "Skipping publish. Run './scripts/release.sh --publish-only' later."
    fi
    
    echo ""
    log_success "Release v$new_version complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Review the changes: git show"
    echo "  2. Push to remote: git push && git push --tags"
    echo "  3. Create GitHub release: https://github.com/tf-gmail/mcp-redis-best-practices/releases/new"
}

main "$@"
