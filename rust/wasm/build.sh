#!/bin/bash
# Build script for Replicant WASM

set -e

echo "🧬 Building Replicant WASM..."

# Build with wasm-pack
wasm-pack build --target web --out-dir www --scope replicant

# Copy HTML files if not already there
cp index.html.working www/

echo "✅ WASM build complete!"
echo "📁 Files in wasm/www/"
echo "🌐 Serve with: python -m http.server 8080 --directory wasm/www"
