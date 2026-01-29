# RunPod Serverless Setup Guide

## Why Serverless?

**Benefits:**
- **Pay per execution** (~$0.00031/second) - only pay when generating
- **No idle costs** - unlike pods that charge 24/7
- **Auto-scaling** - handles traffic spikes automatically
- **80%+ cost savings** for variable workloads
- **Production-ready API** - instant endpoints

**Best for:**
- API-based workflows
- Occasional generation
- Variable/infrequent usage
- Production deployments

**Not ideal for:**
- Interactive experimentation (use Pods instead)
- LoRA training (needs long sessions)
- Real-time monitoring/debugging

---

## Quick Start (5 minutes)

### Option 1: Pre-built Image (Easiest)

1. **Go to RunPod Hub:**
   - Visit https://www.runpod.io/console/serverless
   - Search for "ComfyUI" or go to https://www.runpod.io/console/serverless/templates

2. **Deploy:**
   - Click on a ComfyUI template (e.g., `runpod/worker-comfyui:flux1-schnell`)
   - Click "Deploy"
   - Click "Next" → "Create Endpoint"
   - Your endpoint is live!

3. **Get API endpoint:**
   - Copy the endpoint URL (e.g., `https://api.runpod.ai/v2/YOUR_ENDPOINT_ID`)
   - Get your API key from RunPod dashboard → Settings → API Keys

### Option 2: Custom Deployment (For Your Workflow)

Use ComfyUI-to-API tool to auto-generate a deployment:

1. **Visit:** https://comfy.getrunpod.io
2. **Upload your workflow:** `iraKim_text_to_video_wan.json`
3. **Configure:**
   - Select GPU (RTX 3090/4090 recommended for WAN 2.2)
   - Add network volume for models
   - Set environment variables if needed
4. **Deploy:** Get GitHub repo → Deploy to RunPod

---

## Full Custom Setup

### Step 1: Create Network Volume (For Models)

Models persist across deployments:

1. **RunPod Dashboard** → "Network Volumes" → "Create Volume"
2. **Size:** 50-100GB (for WAN 2.2 models ~20GB total)
3. **Name it:** `comfyui-models` or similar
4. **Note the volume ID** (you'll need it)

### Step 2: Upload Models to Network Volume

**Option A: Via RunPod Cloud Sync**
1. Go to volume page → "Cloud Sync"
2. Upload your models:
   - `models/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors`
   - `models/vae/wan_2.1_vae.safetensors`
   - `models/diffusion_models/wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors`
   - `models/lora/iraKim-flux-low-noise.safetensors`
   - `models/lora/iraKim-flux-high-noise.safetensors`

**Option B: Via Temporary Pod**
```bash
# Create a temporary pod, mount volume, upload via SCP
# Then delete pod (models stay on volume)
```

### Step 3: Create Serverless Endpoint

1. **RunPod Dashboard** → "Serverless" → "New Endpoint"

2. **Configure:**
   - **Name:** `comfyui-irakim-wan`
   - **GPU:** RTX 3090 (24GB) or RTX 4090 (24GB)
   - **Container Image:** `runpod/worker-comfyui:base` (or custom)
   - **Network Volume:** Select your `comfyui-models` volume
   - **Volume Path:** `/workspace/models` (or `/models`)

3. **Environment Variables:**
   ```
   COMFYUI_PORT=8188
   ```

4. **Handler Path:** `/handler.py` (if using custom handler)

5. **Create Endpoint**

### Step 4: Custom Handler (If Needed)

If you need custom logic, create a handler:

```python
# handler.py
import runpod
import requests
import json

def handler(event):
    """
    Process ComfyUI workflow via API
    """
    workflow = event.get("input", {}).get("workflow")
    prompt = event.get("input", {}).get("prompt", {})
    
    # Queue prompt to ComfyUI
    response = requests.post(
        "http://localhost:8188/prompt",
        json={"prompt": prompt}
    )
    
    prompt_id = response.json()["prompt_id"]
    
    # Poll for completion
    # ... (implementation)
    
    return {"status": "completed", "prompt_id": prompt_id}

runpod.serverless.start({"handler": handler})
```

---

## Using Your Serverless Endpoint

### API Call Example

```python
import requests
import json
import time

ENDPOINT_ID = "your-endpoint-id"
API_KEY = "your-api-key"
RUNPOD_API = f"https://api.runpod.ai/v2/{ENDPOINT_ID}"

# Load your workflow
with open("iraKim_text_to_video_wan.json", "r") as f:
    workflow = json.load(f)

# Extract prompt from workflow (or modify it)
# For ComfyUI, you need the API format, not the full workflow JSON
# Export API format from ComfyUI: File → Export (API)

prompt_api_format = {
    "3": {
        "class_type": "KSampler",
        "inputs": {
            # ... your workflow nodes
        }
    }
}

# Submit job
response = requests.post(
    f"{RUNPOD_API}/run",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "input": {
            "prompt": prompt_api_format,
            "workflow_file": "iraKim_text_to_video_wan.json"  # if using file-based
        }
    }
)

job_id = response.json()["id"]

# Poll for status
while True:
    status = requests.get(
        f"{RUNPOD_API}/status/{job_id}",
        headers={"Authorization": f"Bearer {API_KEY}"}
    ).json()
    
    if status["status"] == "COMPLETED":
        # Get output
        output = requests.get(
            f"{RUNPOD_API}/stream/{job_id}",
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        break
    elif status["status"] == "FAILED":
        raise Exception("Job failed")
    
    time.sleep(2)
```

### Using ComfyUI API Format

Your workflow JSON needs to be converted to ComfyUI's API format:

1. **In ComfyUI UI:**
   - Load your workflow
   - Go to: File → Export (API)
   - Save as `iraKim_text_to_video_wan_api.json`

2. **Use that format** in your API calls

---

## Cost Comparison

**Scenario: 10 video generations/week, ~2 minutes each**

- **Dedicated Pod (24/7):** ~$200/month
- **Dedicated Pod (On-Demand, 10hrs/week):** ~$12/month
- **Serverless:** ~$0.37/month (10 jobs × 2min × $0.00031/sec)

**For occasional use, serverless is 97% cheaper!**

---

## Model Management

### Network Volume Structure

```
/workspace/models/
├── text_encoders/
│   └── umt5_xxl_fp8_e4m3fn_scaled.safetensors
├── vae/
│   └── wan_2.1_vae.safetensors
├── diffusion_models/
│   └── wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors
└── lora/
    ├── iraKim-flux-low-noise.safetensors
    └── iraKim-flux-high-noise.safetensors
```

### Updating Models

1. Upload new model to network volume via Cloud Sync
2. Models are immediately available to all workers
3. No need to rebuild containers

---

## Troubleshooting

**Cold starts slow?**
- First request: 10-30s (container spin-up)
- Subsequent requests: Instant (container stays warm for ~5min)
- Use "Always Ready" workers (costs more but no cold starts)

**Out of memory?**
- Use larger GPU (A100 40GB/80GB)
- Or split workflow into smaller chunks

**Models not found?**
- Check volume mount path in endpoint config
- Verify models are in correct subdirectories
- Check ComfyUI logs: RunPod → Endpoint → Logs

**API errors?**
- Verify workflow is in API format (not full JSON)
- Check that all required models are on volume
- Review handler logs in RunPod dashboard

---

## Migration Checklist

- [ ] Create RunPod account
- [ ] Create network volume (50-100GB)
- [ ] Upload models to network volume
- [ ] Export workflow to API format
- [ ] Create serverless endpoint
- [ ] Test with simple API call
- [ ] Update your scripts to use endpoint
- [ ] Monitor costs in RunPod dashboard

---

## Next Steps

1. **Test locally first:** Use ComfyUI API locally to verify workflow works
2. **Deploy to serverless:** Start with pre-built image
3. **Customize if needed:** Add custom nodes, handlers
4. **Scale:** Add more workers for concurrent requests

---

## Resources

- [RunPod Serverless Docs](https://docs.runpod.io/tutorials/serverless/comfyui)
- [ComfyUI-to-API Tool](https://comfy.getrunpod.io)
- [RunPod API Reference](https://docs.runpod.io/serverless/endpoints/endpoint-reference)
- [ComfyUI API Examples](../script_examples/basic_api_example.py)
