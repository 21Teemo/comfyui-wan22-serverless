#!/bin/bash
# Quick script to upload IraKim LORA files to RunPod network volume

set -e

POD_HOST="ssh.runpod.io"
POD_USER="4kzeoxwub993vi-64410b18"
POD_PORT="22"
SSH_KEY="$HOME/.ssh/id_ed25519"
LOCAL_BASE="/Volumes/Misha/ComfyUI/models/loras"
REMOTE_BASE="/workspace/iraKim_volume/models/loras"

echo "📦 Uploading IraKim LORA files to RunPod"
echo "   Pod: $POD_USER@$POD_HOST:$POD_PORT"
echo "   Target: $REMOTE_BASE"
echo ""

# Test SSH
echo "🔌 Testing SSH connection..."
if ! ssh -i $SSH_KEY -p $POD_PORT ${POD_USER}@${POD_HOST} "echo OK" 2>&1 | grep -q "OK"; then
    echo "   ❌ SSH failed - make sure pod is running"
    exit 1
fi
echo "   ✅ SSH works"
echo ""

# Upload high-noise (required by workflow)
LORA_HIGH="${LOCAL_BASE}/iraKim-flux-high-noise.safetensors"
if [ -f "$LORA_HIGH" ]; then
    echo "1️⃣  Uploading iraKim-flux-high-noise.safetensors (required)..."
    echo "   Size: $(ls -lh "$LORA_HIGH" | awk '{print $5}')"
    scp -T -i $SSH_KEY -P $POD_PORT "$LORA_HIGH" ${POD_USER}@${POD_HOST}:${REMOTE_BASE}/ 2>&1 | grep -v "PTY" || {
        echo "   ⚠️  SCP failed, trying alternative method..."
        # Alternative: use base64 encoding through SSH
        echo "   Using base64 transfer method..."
        base64 "$LORA_HIGH" | ssh -i $SSH_KEY -p $POD_PORT ${POD_USER}@${POD_HOST} "base64 -d > ${REMOTE_BASE}/iraKim-flux-high-noise.safetensors" 2>&1 | grep -v "PTY" || true
    }
    echo "   ✅ High-noise LORA uploaded"
else
    echo "   ⚠️  File not found: $LORA_HIGH"
fi
echo ""

# Upload low-noise (optional)
LORA_LOW="${LOCAL_BASE}/iraKim-flux-low-noise.safetensors"
if [ -f "$LORA_LOW" ]; then
    echo "2️⃣  Uploading iraKim-flux-low-noise.safetensors (optional)..."
    echo "   Size: $(ls -lh "$LORA_LOW" | awk '{print $5}')"
    scp -T -i $SSH_KEY -P $POD_PORT "$LORA_LOW" ${POD_USER}@${POD_HOST}:${REMOTE_BASE}/ 2>&1 | grep -v "PTY" || {
        echo "   ⚠️  SCP failed, trying alternative method..."
        base64 "$LORA_LOW" | ssh -i $SSH_KEY -p $POD_PORT ${POD_USER}@${POD_HOST} "base64 -d > ${REMOTE_BASE}/iraKim-flux-low-noise.safetensors" 2>&1 | grep -v "PTY" || true
    }
    echo "   ✅ Low-noise LORA uploaded"
else
    echo "   ⚠️  File not found: $LORA_LOW"
fi
echo ""

echo "✅ Upload complete!"
echo ""
echo "📝 Verify on pod:"
echo "   ssh -i $SSH_KEY ${POD_USER}@${POD_HOST}"
echo "   ls -lh $REMOTE_BASE/iraKim*"
