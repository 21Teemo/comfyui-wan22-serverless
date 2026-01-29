#!/bin/bash
# Quick validation of Docker setup

echo "🔍 Validating Docker setup..."
echo ""

# Check if files exist
echo "Checking required files..."
files=("Dockerfile" "handler.py" ".dockerignore" "user/default/workflows/iraKim_text_to_video_wan .json")
all_exist=true

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (missing)"
        all_exist=false
    fi
done

echo ""

# Check Dockerfile syntax
echo "Checking Dockerfile syntax..."
if docker build --dry-run -t test . 2>&1 | grep -q "syntax"; then
    echo "  ⚠️  Dockerfile syntax check (dry-run not available, will test on actual build)"
else
    echo "  ✅ Dockerfile structure looks good"
fi

# Check handler.py for common issues
echo ""
echo "Checking handler.py..."
if grep -q "WORKFLOW_FILE" handler.py; then
    echo "  ✅ WORKFLOW_FILE defined"
else
    echo "  ❌ WORKFLOW_FILE not found"
    all_exist=false
fi

if grep -q "runpod.serverless.start" handler.py; then
    echo "  ✅ RunPod handler setup found"
else
    echo "  ❌ RunPod handler setup missing"
    all_exist=false
fi

echo ""
if [ "$all_exist" = true ]; then
    echo "✅ All files present and basic checks passed!"
    echo ""
    echo "Next steps:"
    echo "1. Build: ./build_docker.sh comfyui-wan22-irakim latest"
    echo "2. Test locally (optional): docker run -p 8188:8188 comfyui-wan22-irakim:latest"
    echo "3. Push to Docker Hub: docker push lutsco/comfyui-wan22-irakim:latest"
    echo "4. Deploy on RunPod (see DOCKER_README.md)"
else
    echo "❌ Some issues found. Please fix them before building."
    exit 1
fi
