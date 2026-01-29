#!/bin/bash
# Setup script to prepare GitHub repository for RunPod deployment

set -e

REPO_NAME="${1:-comfyui-wan22-serverless}"

echo "🚀 Setting up GitHub repository structure..."
echo ""

# Check if we're in a git repo
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
fi

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p user/default/workflows

# Check if workflow file exists
if [ ! -f "user/default/workflows/iraKim_text_to_video_wan .json" ]; then
    echo "⚠️  Warning: Workflow file not found at user/default/workflows/iraKim_text_to_video_wan .json"
    echo "   Make sure to add it before pushing to GitHub"
fi

# Verify required files exist
echo ""
echo "✅ Checking required files..."
REQUIRED_FILES=("Dockerfile" "handler.py")
MISSING_FILES=()

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (missing)"
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo ""
    echo "❌ Missing required files. Please create them first."
    exit 1
fi

echo ""
echo "📝 Repository structure ready!"
echo ""
echo "Next steps:"
echo ""
echo "1. Create GitHub repository:"
echo "   - Go to https://github.com/new"
echo "   - Name: $REPO_NAME"
echo "   - Choose Private or Public"
echo "   - Don't initialize with README (we have one)"
echo ""
echo "2. Add files and push:"
echo "   git add Dockerfile handler.py user/ .gitignore README.md"
echo "   git commit -m 'Initial ComfyUI serverless setup'"
echo "   git branch -M main"
echo "   git remote add origin https://github.com/YOUR_USERNAME/$REPO_NAME.git"
echo "   git push -u origin main"
echo ""
echo "3. Deploy on RunPod:"
echo "   - RunPod Dashboard → Serverless → New Endpoint"
echo "   - Import GitHub Repository"
echo "   - Select your repository"
echo "   - Configure endpoint settings"
echo ""
echo "💡 Tip: Use 'git status' to see what will be committed"
