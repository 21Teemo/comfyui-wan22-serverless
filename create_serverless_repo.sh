#!/bin/bash
# Create a clean serverless deployment repository

set -e

REPO_NAME="${1:-comfyui-wan22-serverless}"
REPO_DIR="../${REPO_NAME}"

echo "🚀 Creating clean serverless repository: $REPO_NAME"
echo ""

# Create directory
if [ -d "$REPO_DIR" ]; then
    echo "⚠️  Directory $REPO_DIR already exists"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    mkdir -p "$REPO_DIR"
fi

cd "$REPO_DIR"

# Initialize git
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
    git branch -M main
fi

# Copy necessary files
echo "📋 Copying files..."

# Copy Dockerfile
if [ -f "../ComfyUI/Dockerfile" ]; then
    cp ../ComfyUI/Dockerfile .
    echo "  ✅ Dockerfile"
else
    echo "  ❌ Dockerfile not found!"
    exit 1
fi

# Copy handler
if [ -f "../ComfyUI/handler.py" ]; then
    cp ../ComfyUI/handler.py .
    echo "  ✅ handler.py"
else
    echo "  ❌ handler.py not found!"
    exit 1
fi

# Copy workflow
mkdir -p user/default/workflows
if [ -f "../ComfyUI/user/default/workflows/iraKim_text_to_video_wan .json" ]; then
    cp "../ComfyUI/user/default/workflows/iraKim_text_to_video_wan .json" "user/default/workflows/"
    echo "  ✅ Workflow file"
else
    echo "  ⚠️  Workflow file not found - you'll need to add it manually"
fi

# Copy .gitignore
if [ -f "../ComfyUI/.gitignore.serverless" ]; then
    cp ../ComfyUI/.gitignore.serverless .gitignore
    echo "  ✅ .gitignore"
else
    # Create basic .gitignore
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/

# Models
*.safetensors
*.ckpt
*.pt
*.pth

# Outputs
output/
*.mp4
*.png
*.jpg

# Logs
*.log

# IDE
.vscode/
.idea/
.DS_Store
EOF
    echo "  ✅ .gitignore (created)"
fi

# Copy README
if [ -f "../ComfyUI/README.md" ]; then
    cp ../ComfyUI/README.md .
    echo "  ✅ README.md"
fi

echo ""
echo "✅ Repository structure created!"
echo ""
echo "📁 Location: $(pwd)"
echo ""
echo "Next steps:"
echo ""
echo "1. Review files:"
echo "   ls -la"
echo ""
echo "2. Create GitHub repository:"
echo "   - Go to https://github.com/new"
echo "   - Name: $REPO_NAME"
echo "   - Don't initialize with anything"
echo ""
echo "3. Add and push:"
echo "   git add ."
echo "   git commit -m 'Initial ComfyUI serverless setup'"
echo "   git remote add origin https://github.com/21Teemo/$REPO_NAME.git"
echo "   git push -u origin main"
echo ""
echo "4. Deploy on RunPod:"
echo "   - Import GitHub Repository"
echo "   - Select: $REPO_NAME"
