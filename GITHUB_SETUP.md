# GitHub Repository Setup for RunPod

## Quick Setup Guide

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `comfyui-wan22-serverless` (or your choice)
3. Choose **Private** (recommended) or Public
4. **Don't** initialize with README, .gitignore, or license (we have these)
5. Click "Create repository"

### Step 2: Prepare Local Repository

```bash
cd /Volumes/Misha/ComfyUI

# Initialize git if not already done
git init

# Add only the files needed for serverless deployment
git add Dockerfile
git add handler.py
git add user/default/workflows/
git add .gitignore
git add README.md

# Commit
git commit -m "Initial ComfyUI WAN 2.2 serverless setup"
```

### Step 3: Connect to GitHub

```bash
# Set main branch
git branch -M main

# Add remote
git remote add origin https://github.com/21Teemo/comfyui-wan22-serverless.git

# Push to GitHub
git push -u origin main
```

### Step 4: Deploy on RunPod

1. **RunPod Dashboard** → Serverless → New Endpoint
2. Click **"Import GitHub Repository"**
3. **Authorize RunPod** to access your GitHub (if first time)
4. **Select your repository**: `comfyui-wan22-serverless`
5. **Configure endpoint:**
   - **Handler Path:** `/workspace/handler.py`
   - **GPU:** RTX 3090/4090 or A100
   - **Container Disk:** 30GB
   - **Network Volume:** Mount at `/workspace/models`
6. **Create Endpoint**

RunPod will build the Docker image from your GitHub repo automatically!

## Updating Your Deployment

After making changes:

```bash
# Make your changes to handler.py, Dockerfile, etc.
git add .
git commit -m "Update handler with better logging"
git push
```

Then in RunPod:
- Go to your endpoint
- Click **"Releases"** tab
- Click **"Redeploy"** or **"Build New Release"**
- RunPod rebuilds from latest GitHub commit

## Repository Structure

Your GitHub repo should contain:

```
comfyui-wan22-serverless/
├── Dockerfile                    # Required
├── handler.py                    # Required
├── .gitignore                   # Recommended
├── README.md                    # Recommended
└── user/
    └── default/
        └── workflows/
            └── iraKim_text_to_video_wan .json  # Required
```

## What NOT to Include

Don't commit:
- ❌ Full ComfyUI codebase (it's cloned in Dockerfile)
- ❌ Models (use network volume)
- ❌ Output files
- ❌ Local test files
- ❌ `.venv/` or virtual environments

## Benefits of GitHub Integration

✅ **Faster iterations:**
- Push code → RunPod rebuilds
- No local Docker builds
- No Docker Hub pushes

✅ **Version control:**
- Track all changes
- Easy rollback
- Collaboration ready

✅ **Automatic builds:**
- Option to auto-rebuild on commits
- Or manual trigger

## Troubleshooting

**Build fails?**
- Check RunPod build logs
- Verify Dockerfile syntax
- Ensure all required files are in repo

**Handler not found?**
- Verify Handler Path: `/workspace/handler.py`
- Check file is committed to GitHub

**Models not loading?**
- Verify network volume is mounted
- Check volume path: `/workspace/models`
