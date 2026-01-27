#!/bin/bash
# Upload models using rsync (works better with RunPod SSH gateway)

set -e

POD_HOST="ssh.runpod.io"
POD_USER="4kzeoxwub993vi-64410b18"
POD_PORT="22"
SSH_KEY="$HOME/.ssh/id_ed25519"
LOCAL_BASE="/Volumes/Misha/ComfyUI/models"
REMOTE_BASE="/workspace/models"

echo "📦 Upload Models to RunPod Pod using rsync"
echo "   Pod: $POD_USER@$POD_HOST:$POD_PORT"
echo ""

# Test SSH
echo "🔌 Testing SSH connection..."
if ssh -i $SSH_KEY -p $POD_PORT ${POD_USER}@${POD_HOST} "echo OK" 2>&1 | grep -q "OK"; then
    echo "   ✅ SSH works"
else
    echo "   ❌ SSH failed - make sure pod is running"
    exit 1
fi

# Create directories
echo "📁 Creating directories..."
ssh -i $SSH_KEY -p $POD_PORT ${POD_USER}@${POD_HOST} "mkdir -p ${REMOTE_BASE}/{text_encoders,vae,diffusion_models,loras}" 2>&1 | grep -v "PTY" || true
echo "   ✅ Directories created"
echo ""

# Upload using rsync (handles PTY better)
echo "📤 Uploading models with rsync..."
echo ""

# VAE
if [ -f "${LOCAL_BASE}/vae/wan_2.1_vae.safetensors" ]; then
    echo "1️⃣  VAE (242 MB)..."
    rsync -avz -e "ssh -i $SSH_KEY -p $POD_PORT" \
        "${LOCAL_BASE}/vae/wan_2.1_vae.safetensors" \
        ${POD_USER}@${POD_HOST}:${REMOTE_BASE}/vae/ 2>&1 | grep -v "PTY" || true
    echo "   ✅ VAE uploaded"
fi

echo ""

# LoRA
if [ -f "${LOCAL_BASE}/loras/iraKim-flux-high-noise.safetensors" ]; then
    echo "2️⃣  LoRA (293 MB)..."
    rsync -avz -e "ssh -i $SSH_KEY -p $POD_PORT" \
        "${LOCAL_BASE}/loras/iraKim-flux-high-noise.safetensors" \
        ${POD_USER}@${POD_HOST}:${REMOTE_BASE}/loras/ 2>&1 | grep -v "PTY" || true
    echo "   ✅ LoRA uploaded"
fi

echo ""

# Text Encoder
TEXT_ENCODER="${LOCAL_BASE}/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors"
if [ -f "$TEXT_ENCODER" ]; then
    echo "3️⃣  Text Encoder (6.3 GB)..."
    rsync -avz -e "ssh -i $SSH_KEY -p $POD_PORT" \
        "$TEXT_ENCODER" \
        ${POD_USER}@${POD_HOST}:${REMOTE_BASE}/text_encoders/ 2>&1 | grep -v "PTY" || true
    echo "   ✅ Text Encoder uploaded"
else
    TEXT_ENCODER_ALT="${LOCAL_BASE}/text_encoders/umt5_xxl_fp16.safetensors"
    if [ -f "$TEXT_ENCODER_ALT" ]; then
        echo "3️⃣  Text Encoder (umt5_xxl_fp16.safetensors)..."
        rsync -avz -e "ssh -i $SSH_KEY -p $POD_PORT" \
            "$TEXT_ENCODER_ALT" \
            ${POD_USER}@${POD_HOST}:${REMOTE_BASE}/text_encoders/ 2>&1 | grep -v "PTY" || true
        echo "   ✅ Text Encoder uploaded"
    fi
fi

echo ""

# Diffusion Model
if [ -f "${LOCAL_BASE}/diffusion_models/wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors" ]; then
    echo "4️⃣  Diffusion Model (13.3 GB)..."
    rsync -avz -e "ssh -i $SSH_KEY -p $POD_PORT" \
        "${LOCAL_BASE}/diffusion_models/wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors" \
        ${POD_USER}@${POD_HOST}:${REMOTE_BASE}/diffusion_models/ 2>&1 | grep -v "PTY" || true
    echo "   ✅ Diffusion Model uploaded"
fi

echo ""
echo "✅ Upload complete!"
