#!/bin/bash
# Download Qwen3-32B model using huggingface-cli
# Make sure your HF_TOKEN is set in your environment if the model requires authentication.

MODEL="Qwen/Qwen3-32B"

echo "Downloading $MODEL..."
hf download "$MODEL"

echo "Download complete!"
