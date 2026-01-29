# Using Custom Docker Image with RunPod Serverless

## Short Answer

**No, RunPod can't connect to your local Docker container directly.** But you **CAN** use your own Docker image by:
1. Building it locally
2. Pushing to Docker Hub (or another registry)
3. Deploying it on RunPod serverless

---

## Step-by-Step: Build & Deploy Custom Image

### Step 1: Create Dockerfile

Create a `Dockerfile` for your ComfyUI setup:

```dockerfile
# Dockerfile
FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Clone ComfyUI
RUN git clone https://github.com/comfyanonymous/ComfyUI.git /workspace/ComfyUI

WORKDIR /workspace/ComfyUI

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install any custom nodes you need
# RUN git clone https://github.com/user/custom-node.git custom_nodes/custom-node

# Copy your workflow files (optional)
# COPY workflows/ /workspace/ComfyUI/user/default/workflows/

# Expose port
EXPOSE 8188

# RunPod serverless handler
COPY handler.py /workspace/handler.py

# Start command (RunPod will override this with handler)
CMD ["python", "main.py", "--listen", "0.0.0.0", "--port", "8188"]
```

### Step 2: Create RunPod Handler

Create `handler.py` for serverless:

```python
# handler.py
import runpod
import subprocess
import time
import requests
import json
import os

def handler(event):
    """
    RunPod serverless handler for ComfyUI
    """
    input_data = event.get("input", {})
    
    # Start ComfyUI in background if not running
    try:
        requests.get("http://localhost:8188", timeout=2)
    except:
        # Start ComfyUI
        subprocess.Popen([
            "python", "main.py",
            "--listen", "0.0.0.0",
            "--port", "8188"
        ], cwd="/workspace/ComfyUI")
        
        # Wait for server to start
        for _ in range(30):
            try:
                requests.get("http://localhost:8188", timeout=2)
                break
            except:
                time.sleep(1)
    
    # Get workflow and prompt
    workflow = input_data.get("workflow")
    prompt = input_data.get("prompt", {})
    
    if not prompt:
        return {"error": "No prompt provided"}
    
    # Queue prompt to ComfyUI
    response = requests.post(
        "http://localhost:8188/prompt",
        json={"prompt": prompt}
    )
    
    if response.status_code != 200:
        return {"error": f"Failed to queue prompt: {response.text}"}
    
    prompt_id = response.json()["prompt_id"]
    
    # Poll for completion
    max_wait = 600  # 10 minutes max
    waited = 0
    
    while waited < max_wait:
        history = requests.get(
            f"http://localhost:8188/history/{prompt_id}"
        ).json()
        
        if prompt_id in history:
            execution = history[prompt_id]
            if execution.get("status", {}).get("completed", False):
                # Get output images
                outputs = execution.get("outputs", {})
                images = []
                
                for node_id, node_output in outputs.items():
                    if "images" in node_output:
                        for img in node_output["images"]:
                            images.append({
                                "filename": img["filename"],
                                "subfolder": img.get("subfolder", ""),
                                "type": img.get("type", "output")
                            })
                
                return {
                    "status": "completed",
                    "prompt_id": prompt_id,
                    "images": images
                }
        
        time.sleep(2)
        waited += 2
    
    return {"status": "timeout", "prompt_id": prompt_id}

runpod.serverless.start({"handler": handler})
```

### Step 3: Build Docker Image

```bash
# Build your image
docker build -t your-username/comfyui-custom:latest .

# Test locally (optional)
docker run -p 8188:8188 your-username/comfyui-custom:latest
```

### Step 4: Push to Docker Hub

```bash
# Login to Docker Hub
docker login

# Tag and push
docker push your-username/comfyui-custom:latest
```

### Step 5: Deploy on RunPod

1. **RunPod Dashboard** → "Serverless" → "New Endpoint"
2. **Container Image:** `your-username/comfyui-custom:latest`
3. **GPU:** RTX 3090/4090 (or A100 for large models)
4. **Network Volume:** Attach volume with your models
5. **Volume Path:** `/workspace/models` (or wherever you mount models)
6. **Handler Path:** `/workspace/handler.py`
7. **Create Endpoint**

---

## Alternative: Use Existing Base + Customize

Instead of building from scratch, extend RunPod's base image:

```dockerfile
FROM runpod/worker-comfyui:base

# Add your custom nodes
RUN cd /workspace/ComfyUI && \
    git clone https://github.com/user/custom-node.git custom_nodes/custom-node

# Install additional dependencies
RUN pip install some-package

# Copy your workflows
COPY workflows/ /workspace/ComfyUI/user/default/workflows/
```

---

## Including Models in Image (Not Recommended)

**Don't** include large models in the Docker image:
- Images become huge (10GB+)
- Slow to build/push/pull
- Wastes storage

**Instead:**
- Use **Network Volumes** for models
- Mount volume at `/workspace/models` or `/models`
- Models persist across deployments

---

## Local Development Workflow

1. **Develop locally:**
   ```bash
   docker build -t comfyui-local .
   docker run -p 8188:8188 -v /path/to/models:/workspace/models comfyui-local
   ```

2. **Test your handler:**
   ```python
   # test_handler.py
   event = {
       "input": {
           "prompt": {...}  # Your workflow API format
       }
   }
   result = handler(event)
   print(result)
   ```

3. **When ready, push and deploy:**
   ```bash
   docker push your-username/comfyui-custom:latest
   # Update RunPod endpoint to use new image
   ```

---

## Using Private Registries

RunPod supports private Docker registries:

1. **Docker Hub Private:**
   - Push to private repo: `docker push your-username/comfyui-custom:latest`
   - In RunPod, use: `your-username/comfyui-custom:latest`
   - Add Docker Hub credentials in RunPod settings

2. **Other Registries (GHCR, ECR, etc.):**
   - Use full image path: `ghcr.io/username/repo:tag`
   - Add registry credentials in RunPod

---

## Cost Considerations

**Custom images:**
- Same pricing as pre-built (~$0.00031/sec)
- First pull adds ~30-60s to cold start
- Subsequent requests use cached image (faster)

**Network volumes:**
- $0.10/GB/month storage
- Free data transfer within RunPod
- Models persist across container restarts

---

## Troubleshooting

**Image too large?**
- Use multi-stage builds
- Exclude models (use volumes instead)
- Use `.dockerignore` to exclude unnecessary files

**Build fails?**
- Check base image compatibility
- Verify Python/CUDA versions match
- Test locally first

**Handler not working?**
- Check logs in RunPod dashboard
- Verify handler path is correct
- Test handler locally with `runpod.serverless.start()`

**Models not found?**
- Verify volume mount path
- Check volume is attached to endpoint
- Confirm models are in correct subdirectories

---

## Example: Full Custom Setup

```dockerfile
# Dockerfile
FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

WORKDIR /workspace

# Install dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Clone ComfyUI
RUN git clone https://github.com/comfyanonymous/ComfyUI.git /workspace/ComfyUI

WORKDIR /workspace/ComfyUI

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt

# Install runpod SDK
RUN pip install runpod

# Copy handler
COPY handler.py /workspace/handler.py

# Models will be mounted from network volume at /workspace/models
# ComfyUI will find them automatically if volume is mounted correctly

EXPOSE 8188

CMD ["python", "/workspace/handler.py"]
```

---

## Quick Reference

**Build & Push:**
```bash
docker build -t username/comfyui-custom:latest .
docker push username/comfyui-custom:latest
```

**Deploy on RunPod:**
- Container: `username/comfyui-custom:latest`
- Handler: `/workspace/handler.py`
- Volume: Mount at `/workspace/models`

**Test API:**
```python
import requests

response = requests.post(
    "https://api.runpod.ai/v2/YOUR_ENDPOINT/run",
    headers={"Authorization": "Bearer YOUR_API_KEY"},
    json={
        "input": {
            "prompt": {...}  # Your workflow
        }
    }
)
```
