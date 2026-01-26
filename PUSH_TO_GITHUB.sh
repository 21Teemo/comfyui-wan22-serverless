#!/bin/bash
# Quick script to push to GitHub

set -e

echo "🚀 Pushing to GitHub..."
echo ""

# Check if remote exists
if git remote get-url origin > /dev/null 2>&1; then
    echo "Remote already set: $(git remote get-url origin)"
    read -p "Update remote? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote set-url origin https://github.com/21Teemo/comfyui-wan22-serverless.git
    fi
else
    echo "Adding remote..."
    git remote add origin https://github.com/21Teemo/comfyui-wan22-serverless.git
fi

echo ""
echo "📋 Current status:"
git status --short

echo ""
read -p "Continue with commit and push? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "📦 Adding files..."
git add .

echo "💾 Committing..."
git commit -m "Initial ComfyUI WAN 2.2 serverless setup"

echo "📤 Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ Pushed to GitHub!"
echo ""
echo "Next: Deploy on RunPod"
echo "1. Go to RunPod Dashboard → Serverless → New Endpoint"
echo "2. Click 'Import GitHub Repository'"
echo "3. Select: 21Teemo/comfyui-wan22-serverless"
echo "4. Configure endpoint settings"
