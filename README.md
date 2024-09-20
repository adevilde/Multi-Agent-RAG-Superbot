# Multi-Agent-RAG-Superbot

### 1. Create a conda environment and install these dependencies

```bash
# Create and activate a conda environment
conda create -n RAG_agents python=3.12
conda activate RAG_agents

# Lite-LLM proxy server for Ollama
pip install 'litellm[proxy]'

# Install Ollama
pip install ollama

# Microsoft AutoGen
pip install pyautogen "pyautogen[retrievechat]" 

# Microsoft GraphRAG
pip install graphrag

# Text-Token Encoder-Decoder
pip install tiktoken

# Chainlit Python application
pip install chainlit

# (BONUS) To Convert PDF files to Markdown for GraphRAG 
pip install marker-pdf

# (BONUS) Only if you installed Marker-pdf since it removes GPU CUDA support by default
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
```

### 2. Requirements

- litellm[proxy]
- ollama
- pyautogen[retrievechat]
- tiktoken
- chainlit
- graphrag
- marker-pdf
- torch

