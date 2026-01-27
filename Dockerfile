# Dockerfile for ComfyUI WAN 2.2 Text-to-Video Workflow
# Based on RunPod PyTorch base image with CUDA support

FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Clone ComfyUI to runpod-slim (matching template structure)
RUN git clone https://github.com/comfyanonymous/ComfyUI.git /workspace/runpod-slim

WORKDIR /workspace/runpod-slim

# Upgrade pip first
RUN pip install --no-cache-dir --upgrade pip

# Upgrade PyTorch to 2.2.0+ (required for comfy-kitchen custom_op)
# Uninstall existing torch first, then install 2.2.0+
# Use cu118 index since base image has CUDA 11.8
RUN pip uninstall -y torch torchvision torchaudio || true && \
    pip install --no-cache-dir torch>=2.2.0 torchvision>=0.17.0 torchaudio>=2.2.0 --index-url https://download.pytorch.org/whl/cu118 && \
    python -c "import torch; print(f'PyTorch version: {torch.__version__}')" && \
    python -c "import torch.library; print('torch.library.custom_op available:', hasattr(torch.library, 'custom_op'))"

# Install Python dependencies (this will install comfy-kitchen which needs PyTorch 2.2.0+)
RUN pip install --no-cache-dir -r requirements.txt

# Install RunPod serverless SDK
RUN pip install --no-cache-dir runpod

# Copy workflow file (handle filename with space)
# Create directory structure and copy workflow
RUN mkdir -p /workspace/runpod-slim/user/default/workflows
COPY user/default/workflows/ /workspace/runpod-slim/user/default/workflows/

# Copy handler
COPY handler.py /workspace/handler.py

# Models will be symlinked from network volume at /workspace/iraKim_volume/models
# No need to create here - handler will create symlink at runtime

# Expose ComfyUI port
EXPOSE 8188

# Set working directory for handler
WORKDIR /workspace

# Run handler (RunPod will call this)
CMD ["python", "/workspace/handler.py"]
