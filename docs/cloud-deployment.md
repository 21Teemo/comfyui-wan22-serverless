# Cloud Deployment Guide for ComfyUI

## Memory Issues Solutions

If you don't have enough local memory/VRAM, here are your options:

### Local Memory Optimization (If you have a GPU)

First, try these flags before going to cloud:

```bash
# Split UNet to use less VRAM
--lowvram

# When lowvram isn't enough
--novram

# Reserve specific VRAM for OS/other apps
--reserve-vram 2.0  # Reserve 2GB

# Run VAE on CPU to save VRAM
--cpu-vae

# Disable smart memory (more aggressive offloading)
--disable-smart-memory

# Use RAM pressure caching (frees RAM when needed)
--cache-ram 4.0  # Threshold in GB
```

**Example optimized startup:**
```bash
python main.py --listen 127.0.0.1 --port 8188 --lowvram --cpu-vae --reserve-vram 1.0
```

---

## Cloud Solutions

### Option 1: RunPod (Recommended)

RunPod offers flexible GPU rentals with persistent storage.

#### Setup Steps:

1. **Create RunPod Account**
   - Sign up at https://runpod.io
   - Add payment method

2. **Launch a Pod**
   - Go to "Pods" → "Deploy Pod"
   - Choose GPU: Start with RTX 3090 (24GB) or RTX 4090 (24GB) for most workflows
   - Select template: `RunPod PyTorch` or `RunPod Stable Diffusion`
   - Or use community template: Search "ComfyUI" in templates

3. **Install ComfyUI on the Pod**
   
   SSH into your pod and run:
   
   ```bash
   # Install dependencies
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   pip install -r requirements.txt
   
   # Or clone ComfyUI if not already installed
   git clone https://github.com/comfyanonymous/ComfyUI.git
   cd ComfyUI
   pip install -r requirements.txt
   ```

4. **Setup Persistent Storage**
   - Create a Network Volume for models
   - Mount it to `/workspace/models` or similar
   - This keeps your models between pod restarts

5. **Start ComfyUI**
   ```bash
   python main.py --listen 0.0.0.0 --port 8188
   ```

6. **Access Your Instance**
   - RunPod provides a public URL: `https://[pod-id]-8188.proxy.runpod.net`
   - Or use SSH tunnel if you prefer localhost

#### Pricing (Approx):
- RTX 3090 (24GB): ~$0.29/hr ($7/day if running 24/7)
- RTX 4090 (24GB): ~$0.39/hr
- A100 (40GB): ~$1.19/hr
- A100 (80GB): ~$1.79/hr

**Money-saving tip**: Use "Flex" workers (pause when idle) or "On-Demand" (pay per second when active).

#### RunPod Serverless (API Mode)

For API-based workflows, use RunPod's ComfyUI-to-Serverless:
- Visit https://comfy.getrunpod.io
- Upload your workflow.json
- Get an API endpoint
- Pay only for execution time (cold starts add ~10-30s)

---

### Option 2: RunComfy

Dedicated ComfyUI cloud service - easiest setup.

**Setup:**
1. Sign up at https://www.runcomfy.com
2. Choose GPU size (16GB, 24GB, 48GB, 80GB, 141GB)
3. Start using immediately - everything preconfigured

**Pros:**
- Zero setup time
- Models/nodes persist automatically
- Built for ComfyUI specifically

**Cons:**
- Less customization than RunPod
- Pricing less transparent upfront

---

### Option 3: Vast.ai or Lambda Labs

Cheaper alternatives with less polish:

**Vast.ai:**
- Often 50-70% cheaper than RunPod
- More technical setup required
- Spot instances can be interrupted

**Lambda Labs:**
- Good for longer-term rentals
- More predictable pricing
- Less GPU variety

---

## Recommended Approach

1. **Try local optimization first** (--lowvram, --cpu-vae)
2. **For learning/training**: RunPod Pod (24GB, pause between sessions) - best for interactive experimentation
3. **For occasional inference**: RunPod On-Demand or Flex workers
4. **For API/automation**: RunPod Serverless
5. **For hassle-free**: RunComfy
6. **For budget**: Vast.ai spot instances

**Note for LoRA training**: Use **Pods**, not serverless, because training needs long interactive sessions, real-time progress monitoring, and iterative experimentation.

---

## Quick RunPod Deployment Script

Save this as `setup_runpod.sh` and run it on a fresh RunPod instance:

```bash
#!/bin/bash
# RunPod ComfyUI Setup Script

# Install system dependencies
apt-get update && apt-get install -y git python3-pip

# Clone ComfyUI
cd /workspace
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install ComfyUI requirements
pip install -r requirements.txt

# Create models directory structure
mkdir -p models/checkpoints models/vae models/loras models/controlnet

# Start ComfyUI
echo "Starting ComfyUI..."
python main.py --listen 0.0.0.0 --port 8188
```

---

## Transferring Your Local Setup

To move your local ComfyUI setup to RunPod:

1. **Upload models** (use RunPod Network Volume or S3 sync)
2. **Export custom nodes list**: 
   ```bash
   ls custom_nodes/ > custom_nodes_list.txt
   ```
3. **Reinstall on RunPod**:
   - Install custom nodes from your list
   - Copy workflow JSON files
   - Sync models directory

---

## Cost Estimation

For 10 hours/week usage:
- **RunPod RTX 3090 (On-Demand)**: ~$2.90/week = ~$12.50/month
- **RunPod RTX 4090 (On-Demand)**: ~$3.90/week = ~$17/month  
- **RunPod Serverless**: Pay per execution (varies by workflow complexity)
- **24/7 instance**: ~$200-300/month depending on GPU

---

## Troubleshooting

**Cold starts slow?**
- Use persistent pods instead of serverless
- Pre-warm the instance

**Out of memory?**
- Use larger GPU (48GB+)
- Or use --lowvram/--novram flags
- Split workflows into smaller chunks

**Can't access pod?**
- Check firewall settings
- Verify port forwarding (RunPod handles this automatically)
- Use SSH tunnel: `ssh -L 8188:localhost:8188 root@pod-ip`
