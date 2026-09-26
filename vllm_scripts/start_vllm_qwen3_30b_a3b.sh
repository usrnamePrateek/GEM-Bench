#!/bin/bash
# Start vLLM server with Qwen3-30B-A3B (MoE: 30B total, 3B active)

MODEL="Qwen/Qwen3-30B-A3B"
PORT=8000

echo "Starting vLLM OpenAI-compatible server on port $PORT..."
echo "Model: $MODEL"

# Run vllm serve. 
unset LD_LIBRARY_PATH
/home/gpuuser7/gpuuser7_a/prateek/LLM_with_ads/.lmarena-env/bin/vllm serve "$MODEL" \
    --port "$PORT" \
    --max-model-len 16384
