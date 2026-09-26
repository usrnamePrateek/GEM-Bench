#!/bin/bash
# Start vLLM server with DeepSeek R1 32B Distill Qwen in FP16

MODEL="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
PORT=8080

echo "Starting vLLM OpenAI-compatible server on port $PORT..."
echo "Model: $MODEL"
echo "Precision: FP16"

# Run vllm serve. 
# --dtype half forces FP16 as requested.
# --max-model-len is set to 8192 to save VRAM, you can increase it if you have sufficient memory.
# --tensor-parallel-size can be added if you want to span multiple GPUs (e.g., -tp 2)
unset LD_LIBRARY_PATH
/home/gpuuser7/gpuuser7_a/prateek/LLM_with_ads/.lmarena-env/bin/vllm serve "$MODEL" \
    --dtype half \
    --port "$PORT" \
    --max-model-len 16384
