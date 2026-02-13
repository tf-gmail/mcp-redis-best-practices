const esbuild = require('esbuild');
const fs = require('fs');
const path = require('path');

async function bundle() {
  const outDir = path.join(__dirname, '..', 'dist', 'mcp');
  const knowledgeOut = path.join(outDir, 'knowledge');
  const knowledgeSrc = path.join(__dirname, '..', '..', 'packages', 'mcp-server', 'knowledge');

  // Ensure output directories exist
  fs.mkdirSync(outDir, { recursive: true });
  fs.mkdirSync(knowledgeOut, { recursive: true });

  // Bundle the MCP server with all dependencies
  await esbuild.build({
    entryPoints: [path.join(__dirname, '..', '..', 'packages', 'mcp-server', 'src', 'cli.ts')],
    bundle: true,
    platform: 'node',
    target: 'node18',
    outfile: path.join(outDir, 'server.js'),
    format: 'cjs',
    sourcemap: true,
    external: [], // Bundle everything
    minify: false
  });

  console.log('✓ Bundled MCP server');

  // Copy knowledge files
  copyDirRecursive(knowledgeSrc, knowledgeOut);
  console.log('✓ Copied knowledge files');
}

function copyDirRecursive(src, dest) {
  if (!fs.existsSync(src)) {
    console.warn(`Source directory not found: ${src}`);
    return;
  }
  
  fs.mkdirSync(dest, { recursive: true });
  
  for (const item of fs.readdirSync(src)) {
    const srcPath = path.join(src, item);
    const destPath = path.join(dest, item);
    
    if (fs.statSync(srcPath).isDirectory()) {
      copyDirRecursive(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

bundle().catch(err => {
  console.error('Bundle failed:', err);
  process.exit(1);
});
