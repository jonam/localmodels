#!/bin/bash
set -e

echo "=== localcode setup ==="
echo ""

# Check for Ollama
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "Ollama: installed"
fi

# Start Ollama if not running
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "Starting Ollama..."
    ollama serve &> /dev/null &
    sleep 2
fi

# Pull the model
MODEL="${LOCALCODE_MODEL:-qwen2.5-coder:7b}"
echo "Pulling model: $MODEL (this may take a few minutes on first run)..."
ollama pull "$MODEL"

# Make the CLI executable
chmod +x "$(dirname "$0")/localcode"

echo ""
echo "Done. Run with:"
echo "  ./localcode"
