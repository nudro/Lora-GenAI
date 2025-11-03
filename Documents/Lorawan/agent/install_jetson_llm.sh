#!/bin/bash
# Installation script for local LLM (Ollama) on Jetson Orin
# Run this script on your Jetson Orin device

set -e

echo "========================================="
echo "Jetson Orin Local LLM Installation"
echo "========================================="
echo ""

# Check if running on Jetson
if [ ! -f /etc/nv_tegra_release ]; then
    echo "Warning: This script is designed for Jetson devices."
    echo "Continue anyway? (y/n)"
    read -r response
    if [ "$response" != "y" ]; then
        exit 1
    fi
fi

# Display system info
echo "System Information:"
echo "  JetPack version: $(cat /etc/nv_tegra_release 2>/dev/null || echo 'Unknown')"
echo "  Available RAM: $(free -h | awk '/^Mem:/ {print $2}')"
echo "  Available disk: $(df -h / | awk 'NR==2 {print $4}')"
echo ""

# Check if Ollama is already installed
if command -v ollama &> /dev/null; then
    echo "Ollama is already installed."
    echo "Current version: $(ollama --version 2>/dev/null || echo 'unknown')"
    echo ""
    echo "Do you want to reinstall? (y/n)"
    read -r reinstall
    if [ "$reinstall" != "y" ]; then
        echo "Skipping Ollama installation."
        SKIP_OLLAMA=true
    fi
fi

# Install Ollama if needed
if [ "$SKIP_OLLAMA" != "true" ]; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    
    # Start Ollama service
    echo "Starting Ollama service..."
    systemctl enable ollama 2>/dev/null || true
    systemctl start ollama 2>/dev/null || sudo service ollama start 2>/dev/null || true
    
    # Wait for Ollama to start
    echo "Waiting for Ollama to start..."
    sleep 5
    
    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✓ Ollama is running!"
    else
        echo "Warning: Ollama may not be running. Try: ollama serve"
    fi
fi

echo ""
echo "Available models recommendation based on RAM:"
RAM_GB=$(free -g | awk '/^Mem:/ {print $2}')

if [ "$RAM_GB" -ge 32 ]; then
    echo "  Recommended: llama3.2:3b or mistral:7b (use: ollama pull llama3.2:3b)"
elif [ "$RAM_GB" -ge 16 ]; then
    echo "  Recommended: llama3.2:3b (use: ollama pull llama3.2:3b)"
elif [ "$RAM_GB" -ge 8 ]; then
    echo "  Recommended: llama3.2:1b or phi3:mini (use: ollama pull llama3.2:1b)"
else
    echo "  Recommended: llama3.2:1b (use: ollama pull llama3.2:1b)"
fi

echo ""
echo "Do you want to download a model now? (y/n)"
read -r download
if [ "$download" = "y" ]; then
    echo "Enter model name (e.g., llama3.2:3b):"
    read -r model_name
    if [ -n "$model_name" ]; then
        echo "Downloading $model_name (this may take a while)..."
        ollama pull "$model_name"
        echo "✓ Model downloaded!"
    fi
fi

echo ""
echo "========================================="
echo "Installation Summary"
echo "========================================="
echo "Ollama installed: ✓"
echo ""
echo "To test Ollama, run:"
echo "  ollama run llama3.2:3b 'Hello, world'"
echo ""
echo "To see installed models:"
echo "  ollama list"
echo ""
echo "To start Ollama server (if not running):"
echo "  ollama serve"
echo "  # or"
echo "  systemctl start ollama"
echo ""
echo "For Python integration, install:"
echo "  pip install langchain-community ollama"
echo ""
echo "========================================="

