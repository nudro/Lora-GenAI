# Quick Start: Local LLM on Jetson Orin

This is a quick guide to get a local LLM running on your Jetson Orin for the soil sensor agent.

## Quick Installation (5 minutes)

### Step 1: Install Ollama on Jetson Orin

SSH into your Jetson Orin and run:

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Or use the provided script
chmod +x install_jetson_llm.sh
./install_jetson_llm.sh
```

### Step 2: Download a Model

Choose based on your Jetson Orin RAM:

**For 8GB RAM (Orin Nano):**
```bash
ollama pull llama3.2:1b
```

**For 16GB RAM (Orin NX):**
```bash
ollama pull llama3.2:3b
```

**For 32GB+ RAM (AGX Orin):**
```bash
ollama pull llama3.2:3b
# or
ollama pull mistral:7b
```

### Step 3: Test Ollama

```bash
ollama run llama3.2:3b "Hello, can you analyze soil sensor data?"
```

If this works, Ollama is installed correctly!

### Step 4: Install Python Dependencies

On your Jetson Orin:

```bash
cd ~/path/to/agent  # Navigate to agent directory
pip install langchain-community ollama requests
```

### Step 5: Run the Local LLM Agent

```bash
python soil_agent_local_llm.py
```

The script will automatically:
- Try to connect to Ollama (local LLM)
- Fall back to OpenAI if Ollama is not available
- Use the specified model (default: `llama3.2:3b`)

## Changing the Model

Edit `soil_agent_local_llm.py` and change this line:

```python
llm = initialize_llm(model_name="llama3.2:3b", use_local=True)
```

To use a different model:
- `llama3.2:1b` - Smaller, faster (good for 8GB RAM)
- `llama3.2:3b` - Balanced (good for 16GB RAM)
- `mistral:7b` - Larger, more capable (needs 16GB+ RAM)

Make sure you've downloaded the model first: `ollama pull <model_name>`

## Troubleshooting

### "Cannot connect to Ollama"

1. Check if Ollama is running:
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. Start Ollama if not running:
   ```bash
   ollama serve
   ```

### "Model not found"

1. List installed models:
   ```bash
   ollama list
   ```

2. Download the model:
   ```bash
   ollama pull llama3.2:3b
   ```

### Out of Memory

- Use a smaller model (e.g., `llama3.2:1b`)
- Close other applications
- Free up memory:
  ```bash
  sudo systemctl stop nvgetty
  sudo systemctl stop bluetooth
  ```

## Next Steps

- See `README_JETSON_LLM.md` for detailed information
- Modify `soil_agent_local_llm.py` to customize behavior
- Integrate with your soil sensor data collection pipeline

