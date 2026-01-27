#!/bin/bash
# Alternative: Upload models via temporary RunPod Pod
# This method works when S3 API access isn't available

set -e

echo "📦 Upload Models via Temporary RunPod Pod"
echo ""
echo "This script helps you upload models using a temporary pod with the network volume mounted."
echo ""

# Check if user has a pod running
echo "Step 1: Create or use an existing RunPod Pod"
echo "  - Go to: https://www.runpod.io/console/pods"
echo "  - Create a new pod (any GPU type, smallest is fine)"
echo "  - Attach network volume: ira_kim_volume"
echo "  - Note the pod's SSH connection details"
echo ""

read -p "Enter pod hostname (ssh.runpod.io or IP): " POD_HOST
POD_HOST=${POD_HOST:-ssh.runpod.io}
read -p "Enter SSH port (usually 22): " POD_PORT
POD_PORT=${POD_PORT:-22}
read -p "Enter SSH user (e.g., 4kzeoxwub993vi-64410b18): " POD_USER
read -p "Enter SSH key path (default: ~/.ssh/id_ed25519): " SSH_KEY
SSH_KEY=${SSH_KEY:-$HOME/.ssh/id_ed25519}

echo ""
echo "Step 2: Create directories on the pod"
ssh -i $SSH_KEY -p $POD_PORT ${POD_USER}@${POD_HOST} "mkdir -p /workspace/models/{text_encoders,vae,diffusion_models,loras}"

echo ""
echo "Step 3: Upload models (this will take a while)..."
echo ""

LOCAL_BASE="/Volumes/Misha/ComfyUI/models"

# Text Encoder
TEXT_ENCODER="${LOCAL_BASE}/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors"
if [ -f "$TEXT_ENCODER" ]; then
    echo "1️⃣  Text Encoder (6.3 GB)..."
    scp -i $SSH_KEY -P $POD_PORT "$TEXT_ENCODER" ${POD_USER}@${POD_HOST}:/workspace/models/text_encoders/
    echo "   ✅ Uploaded"
else
    TEXT_ENCODER_ALT="${LOCAL_BASE}/text_encoders/umt5_xxl_fp16.safetensors"
    if [ -f "$TEXT_ENCODER_ALT" ]; then
        echo "1️⃣  Text Encoder (umt5_xxl_fp16.safetensors)..."
        scp -P $POD_PORT "$TEXT_ENCODER_ALT" ${POD_USER}@${POD_IP}:/workspace/models/text_encoders/
        echo "   ✅ Uploaded"
    fi
fi

echo ""

# VAE
VAE="${LOCAL_BASE}/vae/wan_2.1_vae.safetensors"
if [ -f "$VAE" ]; then
    echo "2️⃣  VAE (242 MB)..."
    scp -i $SSH_KEY -P $POD_PORT "$VAE" ${POD_USER}@${POD_HOST}:/workspace/models/vae/
    echo "   ✅ Uploaded"
fi

echo ""

# Diffusion Model
DIFFUSION="${LOCAL_BASE}/diffusion_models/wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors"
if [ -f "$DIFFUSION" ]; then
    echo "3️⃣  Diffusion Model (13.3 GB) - this will take 15-30 minutes..."
    scp -i $SSH_KEY -P $POD_PORT "$DIFFUSION" ${POD_USER}@${POD_HOST}:/workspace/models/diffusion_models/
    echo "   ✅ Uploaded"
fi

echo ""

# LoRA
LORA="${LOCAL_BASE}/loras/iraKim-flux-high-noise.safetensors"
if [ -f "$LORA" ]; then
    echo "4️⃣  LoRA (293 MB)..."
    scp -i $SSH_KEY -P $POD_PORT "$LORA" ${POD_USER}@${POD_HOST}:/workspace/models/loras/
    echo "   ✅ Uploaded"
fi

echo ""
echo "✅ Upload complete!"
echo ""
echo "📝 Verify files on pod:"
echo "   ssh -i $SSH_KEY ${POD_USER}@${POD_HOST}"
echo "   ls -lh /workspace/models/text_encoders/"
echo "   ls -lh /workspace/models/vae/"
echo "   ls -lh /workspace/models/diffusion_models/"
echo "   ls -lh /workspace/models/loras/"
echo ""
echo "💡 Note: Files are now on the network volume and will persist even if you delete the pod."
