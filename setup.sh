#!/bin/bash
set -e

echo "=== localcode setup ==="
echo ""

# Install system dependencies
install_deps() {
    local missing=()

    command -v pdftotext &> /dev/null || missing+=(poppler-utils)
    command -v python3 &> /dev/null || missing+=(python3)
    command -v curl &> /dev/null || missing+=(curl)

    if [ ${#missing[@]} -eq 0 ]; then
        echo "System dependencies: all present (python3, pdftotext, curl)"
    else
        echo "Installing system packages: ${missing[*]}"
        if command -v apt-get &> /dev/null; then
            sudo apt-get update -qq && sudo apt-get install -y -qq "${missing[@]}"
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y "${missing[@]}"
        elif command -v pacman &> /dev/null; then
            # poppler-utils is just "poppler" on Arch
            local arch_pkgs=("${missing[@]/poppler-utils/poppler}")
            sudo pacman -S --noconfirm "${arch_pkgs[@]}"
        elif command -v brew &> /dev/null; then
            local brew_pkgs=("${missing[@]/poppler-utils/poppler}")
            brew install "${brew_pkgs[@]}"
        else
            echo "Warning: Could not install ${missing[*]} — install manually"
        fi
    fi
}

install_deps

# Check for Ollama
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "Ollama: installed ($(ollama --version 2>/dev/null || echo 'unknown version'))"
fi

# Start Ollama if not running
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "Starting Ollama..."
    ollama serve &> /dev/null &
    sleep 3
fi

# Detect available RAM and recommend model
detect_model() {
    if [ -n "$LOCALCODE_MODEL" ]; then
        echo "$LOCALCODE_MODEL"
        return
    fi

    local ram_gb
    if [ -f /proc/meminfo ]; then
        ram_gb=$(awk '/MemTotal/ {printf "%d", $2/1024/1024}' /proc/meminfo)
    elif command -v sysctl &> /dev/null; then
        ram_gb=$(sysctl -n hw.memsize 2>/dev/null | awk '{printf "%d", $1/1024/1024/1024}')
    else
        ram_gb=8
    fi

    echo "Detected RAM: ${ram_gb}GB" >&2

    if [ "$ram_gb" -ge 32 ]; then
        echo "qwen3-coder:30b"
    elif [ "$ram_gb" -ge 16 ]; then
        echo "qwen3:14b"
    else
        echo "qwen3:8b"
    fi
}

MODEL=$(detect_model)
echo "Selected model: $MODEL"
echo ""

# Check for GPU
if command -v nvidia-smi &> /dev/null && nvidia-smi &> /dev/null; then
    echo "GPU: NVIDIA detected (GPU acceleration enabled)"
elif [ -d /sys/class/drm ] && ls /sys/class/drm/card*/device/vendor 2>/dev/null | xargs grep -l 0x1002 &>/dev/null; then
    echo "GPU: AMD detected (ROCm may be available)"
else
    echo "GPU: None detected (using CPU - inference will be slower but works fine)"
    echo "     With ${ram_gb:-64}GB RAM, the $MODEL model will use ~$(echo $MODEL | grep -oP '\d+' | tail -1 | awk '{printf "%d", $1 * 0.7}')GB"
fi
echo ""

# Pull the model
echo "Pulling model: $MODEL (this may take a while on first run)..."
ollama pull "$MODEL"

# Also pull a fast model for quick tasks
FAST_MODEL="qwen3:8b"
if [ "$MODEL" != "$FAST_MODEL" ]; then
    echo ""
    echo "Also pulling fast model for quick tasks: $FAST_MODEL..."
    ollama pull "$FAST_MODEL"
fi

# Make the CLI executable and install to PATH
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
chmod +x "$SCRIPT_DIR/localcode"

if [ -d /usr/local/bin ] && [ -w /usr/local/bin ]; then
    ln -sf "$SCRIPT_DIR/localcode" /usr/local/bin/localcode
    echo "Installed: localcode → /usr/local/bin/localcode"
elif sudo -n true 2>/dev/null; then
    sudo ln -sf "$SCRIPT_DIR/localcode" /usr/local/bin/localcode
    echo "Installed: localcode → /usr/local/bin/localcode"
else
    echo "To use from anywhere, run:"
    echo "  sudo ln -s $SCRIPT_DIR/localcode /usr/local/bin/localcode"
fi

echo ""
echo "Done. Run with:"
echo "  localcode                       # from any project directory"
echo "  LOCALCODE_MODEL=qwen3:8b localcode  # fast mode"
echo ""
echo "Available models after setup:"
ollama list 2>/dev/null | grep -i qwen || true
