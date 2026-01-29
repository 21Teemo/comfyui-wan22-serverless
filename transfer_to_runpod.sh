#!/bin/bash
# Transfer iraKim workflow and models to RunPod

POD_IP="213.192.2.84"
POD_PORT="40106"
POD_USER="root"
POD_PATH="/workspace/ComfyUI"
LOCAL_PATH="/Volumes/Misha/ComfyUI"

echo "🚀 Transferring workflow and models to RunPod..."
echo ""

# Transfer workflow
echo "📄 Transferring workflow file..."
scp -P $POD_PORT "${LOCAL_PATH}/user/default/workflows/iraKim_text_to_video_wan .json" ${POD_USER}@${POD_IP}:${POD_PATH}/iraKim_text_to_video_wan.json

# Create model directories
echo "📁 Creating model directories on pod..."
ssh -p $POD_PORT ${POD_USER}@${POD_IP} "mkdir -p ${POD_PATH}/models/{text_encoders,vae,diffusion_models,lora}"

# Transfer models (you can comment out ones you don't need)
echo ""
echo "📦 Transferring models (this will take a while)..."
echo ""

echo "1️⃣ Text encoder (6.3 GB) - this will take ~5-10 minutes..."
scp -P $POD_PORT "${LOCAL_PATH}/models/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors" ${POD_USER}@${POD_IP}:${POD_PATH}/models/text_encoders/ 2>&1 | grep -E "(%|ETA|error)" || echo "✅ Text encoder uploaded"

echo ""
echo "2️⃣ VAE (242 MB) - this will take ~1 minute..."
scp -P $POD_PORT "${LOCAL_PATH}/models/vae/wan_2.1_vae.safetensors" ${POD_USER}@${POD_IP}:${POD_PATH}/models/vae/ 2>&1 | grep -E "(%|ETA|error)" || echo "✅ VAE uploaded"

echo ""
echo "3️⃣ Diffusion model (13.3 GB) - this will take 15-30 minutes..."
echo "   ⚠️  This is the largest file. Be patient!"
scp -P $POD_PORT "${LOCAL_PATH}/models/diffusion_models/wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors" ${POD_USER}@${POD_IP}:${POD_PATH}/models/diffusion_models/ 2>&1 | grep -E "(%|ETA|error)" || echo "✅ Diffusion model uploaded"

echo ""
echo "4️⃣ LoRAs (293 MB each) - this will take ~2 minutes each..."
scp -P $POD_PORT "${LOCAL_PATH}/models/lora/iraKim-flux-low-noise.safetensors" ${POD_USER}@${POD_IP}:${POD_PATH}/models/lora/ 2>&1 | grep -E "(%|ETA|error)" || echo "✅ Low noise LoRA uploaded"
scp -P $POD_PORT "${LOCAL_PATH}/models/lora/iraKim-flux-high-noise.safetensors" ${POD_USER}@${POD_IP}:${POD_PATH}/models/lora/ 2>&1 | grep -E "(%|ETA|error)" || echo "✅ High noise LoRA uploaded"

echo ""
echo "✅ Transfer complete!"
echo ""
echo "📝 Next steps:"
echo "1. Open ComfyUI on RunPod: https://4kzeoxwub993vi-8188.proxy.runpod.net"
echo "2. Load workflow: Menu → Load → iraKim_text_to_video_wan.json"
echo "3. Verify models are found (nodes should be green)"
echo "4. Run your workflow!"
