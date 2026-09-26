#!/bin/bash
# Start vLLM server with Llama 3.3 70B FP8

# We use the NeuralMagic FP8 quantized version which is highly optimized for vLLM
MODEL="nvidia/Llama-3.3-70B-Instruct-FP8"
PORT=8080

echo "Starting vLLM OpenAI-compatible server on port $PORT..."
echo "Model: $MODEL"
echo "Precision: FP8"

# Run vllm serve. 
# --quantization fp8 tells vLLM to use the FP8 kernels.
# --max-model-len is set to 8192 to save VRAM.
# Note on hardware: A 70B FP8 model requires around 70-75GB of VRAM. 
# It will fit on 1x 80GB GPU (e.g. H100/A100 80GB) or 2x 40GB GPUs. 
# If using multiple GPUs, you MUST add `--tensor-parallel-size 2` (or the number of GPUs you have).
unset LD_LIBRARY_PATH
/home/gpuuser7/gpuuser7_a/prateek/LLM_with_ads/.lmarena-env/bin/vllm serve "$MODEL" \
    --port "$PORT" \
    --max-model-len 16384
