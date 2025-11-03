# Installing Local LLM (Llama) on Jetson Orin

This guide covers installing and running a local Large Language Model like Llama on your NVIDIA Jetson Orin device for the soil sensor agent.

## Prerequisites

- **Jetson Device**: Jetson AGX Orin (64GB/32GB), Jetson Orin NX (16GB), or Jetson Orin Nano (8GB)
- **JetPack**: JetPack 5 (L4T r35.x) or JetPack 6 (L4T r36.x)
- **Storage**: NVMe SSD recommended (models are 5-15GB+)
- **Memory**: At least 8GB RAM (16GB+ recommended for larger models)

## Method 1: Ollama (Recommended - Easiest)

Ollama is the simplest way to run local LLMs on Jetson Orin with minimal setup.

### Installation

1. **SSH into your Jetson Orin** (or work directly on the device)

2. **Install Ollama**:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

3. **Start Ollama service** (usually auto-starts):
   ```bash
   ollama serve
   ```
   
   Or run in background:
   ```bash
   systemctl start ollama
   ```

### Download Models

For Jetson Orin with limited memory, use quantized models:

```bash
# Llama 3.2 3B (good for 8GB+ RAM) - ~2GB
ollama pull llama3.2:3b

# Llama 3.2 1B (for 8GB RAM) - ~1.2GB
ollama pull llama3.2:1b

# Mistral 7B 4-bit quantized (for 16GB+ RAM) - ~4.1GB
ollama pull mistral:7b

# Phi-3 Mini (for 8GB RAM) - ~2.3GB
ollama pull phi3:mini
```

### Test Installation

```bash
# Test with a simple prompt
ollama run llama3.2:3b "Hello, can you help with soil sensor analysis?"
```

### Usage in Python

Install the Ollama Python client:
```bash
pip install ollama
```

Example Python code:
```python
import ollama

response = ollama.chat(model='llama3.2:3b', messages=[
    {
        'role': 'user',
        'content': 'Analyze this soil sensor data...',
    },
])

print(response['message']['content'])
```

## Method 2: TensorRT-LLM (Advanced - Best Performance)

TensorRT-LLM provides the best performance on Jetson Orin but requires more setup.

### Installation

1. **Check JetPack version**:
   ```bash
   cat /etc/nv_tegra_release
   ```

2. **Install TensorRT-LLM** (official NVIDIA method):
   ```bash
   # Install via pip (JetPack 6)
   pip3 install tensorrt-llm --extra-index-url https://pypi.nvidia.com
   
   # Or build from source for JetPack 5
   # See: https://github.com/NVIDIA/TensorRT-LLM/blob/main/docs/source/installation/build.md
   ```

3. **Convert Llama model to TensorRT format**:
   ```bash
   # Download Llama model from HuggingFace
   # Convert using TensorRT-LLM build tools
   ```

### Resources

- TensorRT-LLM Documentation: https://github.com/NVIDIA/TensorRT-LLM
- Jetson Generative AI Playground: https://tokk-nv.github.io/jetson-generative-ai-playground/

## Method 3: llama.cpp (Lightweight Alternative)

For a lightweight, CPU-optimized approach:

1. **Build llama.cpp**:
   ```bash
   git clone https://github.com/ggerganov/llama.cpp.git
   cd llama.cpp
   make
   ```

2. **Download quantized model**:
   ```bash
   # Download from HuggingFace or use official Llama weights
   ```

3. **Run model**:
   ```bash
   ./llama -m model.gguf -p "Your prompt here"
   ```

## Model Recommendations by RAM

| RAM | Recommended Model | Size | Quantization |
|-----|------------------|------|--------------|
| 8GB | Llama 3.2 1B, Phi-3 Mini | 1-2GB | 4-bit Q4_0 |
| 16GB | Llama 3.2 3B, Mistral 7B | 2-4GB | 4-bit Q4_0 |
| 32GB+ | Llama 3.2 8B, Mistral 7B | 4-8GB | 4-bit or 8-bit |

## Integration with Soil Sensor Agent

See `soil_agent_local_llm.py` for an example implementation using Ollama instead of OpenAI.

## Performance Optimization

1. **Free up memory** before running models:
   ```bash
   sudo systemctl stop nvgetty
   sudo systemctl stop bluetooth
   ```

2. **Set maximum performance mode**:
   ```bash
   sudo nvpmodel -m 0
   sudo jetson_clocks
   ```

3. **Monitor GPU/CPU usage**:
   ```bash
   tegrastats
   ```

## Troubleshooting

### Out of Memory Errors

- Use smaller models (1B or 3B instead of 7B+)
- Use 4-bit quantized models
- Close other applications
- Reduce batch size in inference

### Slow Performance

- Enable GPU acceleration (ensure CUDA is working)
- Use TensorRT-LLM for best performance
- Use quantized models (4-bit is faster than 8-bit)
- Consider smaller models if latency is critical

### Model Not Found

- Check model is downloaded: `ollama list`
- Download model explicitly: `ollama pull <model>`
- Verify you have enough disk space

## Next Steps

1. Choose an installation method (Ollama recommended for simplicity)
2. Download an appropriate model for your Jetson Orin RAM
3. Test the installation with a simple prompt
4. Modify `soil_agent.py` to use the local LLM (see example code)
5. Test with your soil sensor data

## References

- Ollama: https://ollama.com
- TensorRT-LLM: https://github.com/NVIDIA/TensorRT-LLM
- Jetson Generative AI Playground: https://tokk-nv.github.io/jetson-generative-ai-playground/
- llama.cpp: https://github.com/ggerganov/llama.cpp

