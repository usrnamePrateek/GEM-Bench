#!/bin/bash
# Script to download Gemma-4-31B Dense model using huggingface-cli

# You can change the model ID here if the exact name on Hugging Face differs
MODEL_ID="google/gemma-4-31B-it"

echo "Downloading $MODEL_ID from Hugging Face..."
echo "Note: If this requires a Hugging Face login or token, make sure you've run 'hf auth login' first."

# Download using hf
hf download "$MODEL_ID"

echo "Download complete! You can verify it by checking ~/.cache/huggingface/hub/"
