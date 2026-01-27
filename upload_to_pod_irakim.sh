#!/bin/bash
# Upload models to RunPod pod: ira_kim (4kzeoxwub993vi)
# This uses SCP over SSH - no SSL issues!

set -e

echo "📦 Upload Models to RunPod Pod: ira_kim"
echo ""

# Pod details - UPDATE THESE after starting your pod
POD_HOST="ssh.runpod.io"  # RunPod SSH gateway
POD_USER="4kzeoxwub993vi-64410b18"  # Your pod SSH user
POD_PORT="22"  # Standard SSH port
SSH_KEY="$HOME/.ssh/id_ed25519"  # Your SSH key

echo "Pod: $POD_USER@$POD_HOST:$POD_PORT"
echo ""

# Test SSH connection (ignore PTY warnings from RunPod)
echo "🔌 Testing SSH connection..."
SSH_CMD="ssh -i $SSH_KEY -p $POD_PORT -o ConnectTimeout=5 ${POD_USER}@${POD_HOST}"
# RunPod shows PTY warnings but commands still work - ignore stderr for test
if $SSH_CMD "echo Connected" 2>/dev/null | grep -q "Connected" || $SSH_CMD "true" 2>&1 | grep -v "PTY" >/dev/null; then
    echo "   ✅ SSH connection works (PTY warnings are normal)"
else
    echo "   ⚠️  SSH test inconclusive, but continuing anyway..."
    echo "   (RunPod shows PTY warnings but commands still work)"
fi

echo ""

# Determine network volume mount path
echo "🔍 Finding network volume mount path..."
# Get all mount points and find the 100GB volume
VOLUME_PATH=$($SSH_CMD "df -h 2>/dev/null | grep -E '100G|ira_kim' | awk '{print \$6}' | head -1" 2>&1 | grep -v "PTY" | grep -v "^$" | grep -v "Error" | head -1)

if [ -z "$VOLUME_PATH" ] || [ "$VOLUME_PATH" = "" ]; then
    echo "   ⚠️  Could not auto-detect network volume path"
    echo "   Using default: /workspace (pod's local storage)"
    VOLUME_PATH="/workspace"
else
    echo "   ✅ Network volume found at: $VOLUME_PATH"
fi

MODELS_PATH="${VOLUME_PATH}/models"
echo "   Models will be uploaded to: $MODELS_PATH"
echo ""

# Create directories on pod (suppress PTY warnings)
echo "📁 Creating model directories on pod..."
$SSH_CMD "mkdir -p ${MODELS_PATH}/{text_encoders,vae,diffusion_models,loras}" 2>&1 | grep -v "PTY" || true
echo "   ✅ Directories created"
echo ""

# Local paths
LOCAL_BASE="/Volumes/Misha/ComfyUI/models"

# Upload models (smallest first for faster testing)
echo "📤 Uploading models (this will take 20-40 minutes)..."
echo ""

# 1. VAE (242 MB) - ~1 minute
VAE="${LOCAL_BASE}/vae/wan_2.1_vae.safetensors"
if [ -f "$VAE" ]; then
    echo "1️⃣  VAE (242 MB)..."
    scp -T -i $SSH_KEY -P $POD_PORT "$VAE" ${POD_USER}@${POD_HOST}:${MODELS_PATH}/vae/ 2>&1 | grep -v "PTY" || true
    echo "   ✅ VAE uploaded"
else
    echo "   ⚠️  VAE not found: $VAE"
fi
echo ""

# 2. LoRA (293 MB) - ~2 minutes
LORA="${LOCAL_BASE}/loras/iraKim-flux-high-noise.safetensors"
if [ -f "$LORA" ]; then
    echo "2️⃣  LoRA (293 MB)..."
    scp -T -i $SSH_KEY -P $POD_PORT "$LORA" ${POD_USER}@${POD_HOST}:${MODELS_PATH}/loras/ 2>&1 | grep -v "PTY" || true
    echo "   ✅ LoRA uploaded"
else
    echo "   ⚠️  LoRA not found: $LORA"
fi
echo ""

# 3. Text Encoder (6.3 GB) - ~5-10 minutes
TEXT_ENCODER="${LOCAL_BASE}/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors"
if [ -f "$TEXT_ENCODER" ]; then
    echo "3️⃣  Text Encoder (6.3 GB) - this will take 5-10 minutes..."
    scp -T -i $SSH_KEY -P $POD_PORT "$TEXT_ENCODER" ${POD_USER}@${POD_HOST}:${MODELS_PATH}/text_encoders/ 2>&1 | grep -v "PTY" || true
    echo "   ✅ Text Encoder uploaded"
else
    TEXT_ENCODER_ALT="${LOCAL_BASE}/text_encoders/umt5_xxl_fp16.safetensors"
    if [ -f "$TEXT_ENCODER_ALT" ]; then
        echo "3️⃣  Text Encoder (umt5_xxl_fp16.safetensors)..."
        scp -T -i $SSH_KEY -P $POD_PORT "$TEXT_ENCODER_ALT" ${POD_USER}@${POD_HOST}:${MODELS_PATH}/text_encoders/ 2>&1 | grep -v "PTY" || true
        echo "   ✅ Text Encoder uploaded"
    else
        echo "   ⚠️  Text Encoder not found"
    fi
fi
echo ""

# 4. Diffusion Model (13.3 GB) - ~15-30 minutes
DIFFUSION="${LOCAL_BASE}/diffusion_models/wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors"
if [ -f "$DIFFUSION" ]; then
    echo "4️⃣  Diffusion Model (13.3 GB) - this will take 15-30 minutes..."
    echo "   ⚠️  This is the largest file. Be patient!"
    scp -T -i $SSH_KEY -P $POD_PORT "$DIFFUSION" ${POD_USER}@${POD_HOST}:${MODELS_PATH}/diffusion_models/ 2>&1 | grep -v "PTY" || true
    echo "   ✅ Diffusion Model uploaded"
else
    echo "   ⚠️  Diffusion Model not found: $DIFFUSION"
fi
echo ""

echo "✅ Upload complete!"
echo ""
echo "📝 Verify files on pod:"
echo "   ssh -i $SSH_KEY ${POD_USER}@${POD_HOST}"
echo "   ls -lh ${MODELS_PATH}/text_encoders/"
echo "   ls -lh ${MODELS_PATH}/vae/"
echo "   ls -lh ${MODELS_PATH}/diffusion_models/"
echo "   ls -lh ${MODELS_PATH}/loras/"
echo ""
echo "💡 Note: Files are on the pod's volume and will persist even if you stop/restart the pod."
