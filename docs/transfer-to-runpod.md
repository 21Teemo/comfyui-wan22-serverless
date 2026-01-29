# Transfer Workflow & Models to RunPod

## Quick Steps to Run Your iraKim Text-to-Video Workflow

### Step 1: Find Your Workflow File

Your workflow JSON file might be:
- Saved in ComfyUI (check browser downloads or ComfyUI's saved workflows)
- In your local ComfyUI directory
- Or you can export it from your local ComfyUI

**To export from local ComfyUI:**
1. Open your local ComfyUI: http://127.0.0.1:8188
2. Load your `iraKim_text_to_video_wan` workflow
3. Click the menu → "Save" or use `Ctrl+S`
4. Save it as `iraKim_text_to_video_wan.json`

### Step 2: Transfer Workflow to RunPod

**Option A: Using SCP (from your Mac terminal):**
```bash
# Replace with your actual workflow file path
scp -P 40106 /path/to/iraKim_text_to_video_wan.json root@213.192.2.84:/workspace/ComfyUI/
```

**Option B: Using RunPod Cloud Sync:**
1. Go to RunPod pod page → "Cloud Sync" button
2. Upload your workflow JSON file
3. It will sync to `/workspace` on the pod

**Option C: Copy-paste (for small files):**
1. Open workflow JSON in a text editor
2. Copy all content
3. SSH into pod: `ssh -p 40106 root@213.192.2.84`
4. Create file: `nano /workspace/ComfyUI/iraKim_text_to_video_wan.json`
5. Paste content, save (Ctrl+X, Y, Enter)

### Step 3: Transfer Models to RunPod

You need to transfer these models from your local machine:

**Required Models:**
- Text Encoder: `models/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors` (6.3 GB)
- VAE: `models/vae/wan_2.1_vae.safetensors` (242 MB)
- Diffusion Model: `models/diffusion_models/wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors` (13.3 GB)
- Your LoRA: `models/lora/iraKim-flux-low-noise.safetensors` (293 MB)
- Your LoRA: `models/lora/iraKim-flux-high-noise.safetensors` (293 MB)

**Best Method: Use RunPod Network Volume (Recommended)**

1. **Create Network Volume in RunPod:**
   - Go to RunPod dashboard → "Network Volumes"
   - Create new volume (20-50 GB recommended)
   - Attach it to your pod

2. **Upload models via Cloud Sync or SCP:**
   ```bash
   # From your Mac, upload models to the network volume
   # First, SSH and check where volume is mounted (usually /workspace or /data)
   ssh -p 40106 root@213.192.2.84
   # Check mounted volumes
   df -h
   
   # Then from your Mac, upload models:
   scp -P 40106 /Volumes/Misha/ComfyUI/models/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors root@213.192.2.84:/workspace/models/text_encoders/
   scp -P 40106 /Volumes/Misha/ComfyUI/models/vae/wan_2.1_vae.safetensors root@213.192.2.84:/workspace/models/vae/
   scp -P 40106 /Volumes/Misha/ComfyUI/models/diffusion_models/wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors root@213.192.2.84:/workspace/models/diffusion_models/
   scp -P 40106 /Volumes/Misha/ComfyUI/models/lora/iraKim-flux-low-noise.safetensors root@213.192.2.84:/workspace/models/lora/
   scp -P 40106 /Volumes/Misha/ComfyUI/models/lora/iraKim-flux-high-noise.safetensors root@213.192.2.84:/workspace/models/lora/
   ```

**Alternative: Use rclone or rsync for faster transfers:**
```bash
# Install rclone on pod first, then sync
rsync -avz -e "ssh -p 40106" /Volumes/Misha/ComfyUI/models/ root@213.192.2.84:/workspace/ComfyUI/models/
```

### Step 4: Load Workflow in RunPod ComfyUI

1. **Open ComfyUI on RunPod:**
   - Use the RunPod proxy URL (e.g., `https://4kzeoxwub993vi-8188.proxy.runpod.net`)

2. **Load your workflow:**
   - Click menu (top right) → "Load" or press `Ctrl+O`
   - Navigate to `/workspace/ComfyUI/iraKim_text_to_video_wan.json`
   - Or drag-drop the JSON file into the browser

3. **Verify models are loaded:**
   - Check that all model nodes show green (models found)
   - If red, verify model paths match your upload locations

### Step 5: Run Your Workflow

1. Set your prompt (include `iraKim` trigger token)
2. Adjust settings (duration, resolution, etc.)
3. Click "Queue Prompt" or press `Ctrl+Enter`
4. Wait for generation (video generation takes longer than images)

---

## Quick Transfer Script

Save this as `transfer_to_runpod.sh` on your Mac and run it:

```bash
#!/bin/bash
POD_IP="213.192.2.84"
POD_PORT="40106"
POD_USER="root"
POD_PATH="/workspace/ComfyUI"
LOCAL_PATH="/Volumes/Misha/ComfyUI"

echo "Transferring workflow..."
scp -P $POD_PORT "${LOCAL_PATH}/iraKim_text_to_video_wan.json" ${POD_USER}@${POD_IP}:${POD_PATH}/

echo "Creating model directories on pod..."
ssh -p $POD_PORT ${POD_USER}@${POD_IP} "mkdir -p ${POD_PATH}/models/{text_encoders,vae,diffusion_models,lora}"

echo "Transferring models (this will take a while)..."
echo "Text encoder (6.3 GB)..."
scp -P $POD_PORT "${LOCAL_PATH}/models/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors" ${POD_USER}@${POD_IP}:${POD_PATH}/models/text_encoders/

echo "VAE (242 MB)..."
scp -P $POD_PORT "${LOCAL_PATH}/models/vae/wan_2.1_vae.safetensors" ${POD_USER}@${POD_IP}:${POD_PATH}/models/vae/

echo "Diffusion model (13.3 GB - this will take 10-20 minutes)..."
scp -P $POD_PORT "${LOCAL_PATH}/models/diffusion_models/wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors" ${POD_USER}@${POD_IP}:${POD_PATH}/models/diffusion_models/

echo "LoRAs (293 MB each)..."
scp -P $POD_PORT "${LOCAL_PATH}/models/lora/iraKim-flux-low-noise.safetensors" ${POD_USER}@${POD_IP}:${POD_PATH}/models/lora/
scp -P $POD_PORT "${LOCAL_PATH}/models/lora/iraKim-flux-high-noise.safetensors" ${POD_USER}@${POD_IP}:${POD_PATH}/models/lora/

echo "✅ Transfer complete!"
echo "Now load the workflow in ComfyUI on RunPod"
```

**Note:** Large file transfers (13+ GB) can take 10-30 minutes depending on your connection speed.

---

## Alternative: Use Network Volume (Faster for Large Files)

If you have a RunPod Network Volume:

1. **Mount volume to pod** (in RunPod UI)
2. **Upload via Cloud Sync** or use RunPod's file manager
3. **Symlink models** in ComfyUI:
   ```bash
   ssh -p 40106 root@213.192.2.84
   cd /workspace/ComfyUI
   # If volume is at /workspace/models, create symlinks:
   ln -s /workspace/models/text_encoders models/text_encoders
   ln -s /workspace/models/vae models/vae
   ln -s /workspace/models/diffusion_models models/diffusion_models
   ln -s /workspace/models/lora models/lora
   ```

This way models persist even if you delete/recreate the pod!
