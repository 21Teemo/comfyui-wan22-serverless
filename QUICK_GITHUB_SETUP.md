# Quick GitHub Setup for RunPod

## Option 1: Create Separate Repository (Recommended)

Run this script to create a clean repo with only serverless files:

```bash
./create_serverless_repo.sh comfyui-wan22-serverless
```

This creates `../comfyui-wan22-serverless/` with:
- Dockerfile
- handler.py
- user/default/workflows/ (with your workflow)
- .gitignore
- README.md

Then:
1. Create GitHub repo at https://github.com/new
2. Push the new directory to GitHub
3. Import in RunPod

## Option 2: Use Current Directory (If you want)

If you want to use the current ComfyUI repo:

```bash
# Add only serverless files
git add Dockerfile handler.py user/default/workflows/ .gitignore README.md

# Commit
git commit -m "Add serverless deployment files"

# Push to new branch
git checkout -b serverless-deployment
git push -u origin serverless-deployment
```

Then in RunPod, select the `serverless-deployment` branch.

## Recommended: Option 1

**Why separate repo?**
- Clean separation
- Only serverless files
- Easier to manage
- No ComfyUI repo clutter

## Files Needed in GitHub

Minimum required:
- ✅ `Dockerfile`
- ✅ `handler.py`
- ✅ `user/default/workflows/iraKim_text_to_video_wan .json`

Recommended:
- ✅ `.gitignore`
- ✅ `README.md`

## After GitHub Setup

1. **RunPod** → Serverless → New Endpoint
2. **Import GitHub Repository**
3. **Select your repo**
4. **Configure:**
   - Handler Path: `/workspace/handler.py`
   - GPU: RTX 3090/4090 or A100
   - Container Disk: 30GB
   - Network Volume: `/workspace/models`

Done! 🎉
