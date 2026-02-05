#!/bin/bash
# Build script for the Redis Best Practices MCP VS Code extension

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Building Redis Best Practices MCP Extension..."

# Navigate to extension directory
cd "$SCRIPT_DIR"

# Install dependencies
echo "Installing dependencies..."
npm install

# Compile TypeScript
echo "Compiling TypeScript..."
npm run compile

# Copy MCP server to extension
echo "Bundling MCP server..."
rm -rf mcp-server
mkdir -p mcp-server

# Copy the Python MCP server
cp -r "$ROOT_DIR/mcp-server/src" mcp-server/
cp "$ROOT_DIR/mcp-server/pyproject.toml" mcp-server/

# Install Python dependencies in the bundled server (for standalone use)
echo "Setting up Python environment..."
cd mcp-server
python3 -m venv .venv
source .venv/bin/activate
pip install -e . --quiet
deactivate
cd ..

# Package the extension
echo "Packaging extension..."
npm run package

echo ""
echo "✅ Build complete!"
echo ""
echo "Output: $(ls -1 *.vsix 2>/dev/null || echo 'No .vsix file found')"
echo ""
echo "To install locally:"
echo "  code --install-extension redis-best-practices-mcp-*.vsix"
echo ""
echo "To publish to marketplace:"
echo "  npm run publish"
