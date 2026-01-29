# ComfyUI Setup for Your LoRA

## ✅ Installation Complete

ComfyUI has been installed at: `/Users/michaelluts/IdeaProjects/ComfyUI`

Your LoRA files have been copied to: `ComfyUI/models/lora/`

## 📁 LoRA Files Location

- `ComfyUI/models/lora/iraKim-flux-high-noise.safetensors`
- `ComfyUI/models/lora/iraKim-flux-low-noise.safetensors`

## 🚀 Running ComfyUI

### Basic Setup

1. **Install dependencies**:
```bash
cd /Users/michaelluts/IdeaProjects/ComfyUI
# Install PyTorch (for macOS MPS support):
pip install torch torchvision torchaudio
# Or for NVIDIA GPUs (Linux/Windows):
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Install all ComfyUI dependencies:
pip install -r requirements.txt
```

2. **Run ComfyUI**:
```bash
cd /Users/michaelluts/IdeaProjects/ComfyUI
# Use the Python version that has packages installed (may be python3.11):
python3.11 main.py
# Or if python3 points to the correct version:
# python3 main.py
```

3. **Access the UI**: Open `http://127.0.0.1:8188` in your browser

## 🎨 Using Your LoRA with FLUX.1 Kontext

### Important Notes:

1. **FLUX.1 Kontext Support**: ComfyUI needs the FLUX.1 Kontext custom nodes to use your LoRA. You may need to install:
   - [ComfyUI-FLUX](https://github.com/black-forest-labs/ComfyUI-FLUX) or similar FLUX support nodes

2. **Using Your LoRA**:
   - Load your LoRA using the "Load LoRA" node
   - Use the trigger token `iraKim` in your prompts
   - Example prompt: `iraKim, 1girl, long black hair, smooth skin, soft facial features, large eyes, natural makeup, glossy lips, soft smile, close-up portrait, selfie pose, casual outfit, indoor setting, soft indoor lighting`

3. **LoRA Strength**: 
   - High noise LoRA: Use for higher noise/guidance settings
   - Low noise LoRA: Use for lower noise/guidance settings
   - You can adjust the strength (0.0 to 1.0) in the LoRA loader node

## 📚 Resources

- ComfyUI Repository: https://github.com/Comfy-Org/ComfyUI
- ComfyUI Documentation: https://www.comfy.org/
- FLUX.1 Kontext: Check for ComfyUI custom nodes that support FLUX.1 Kontext

## 🔄 Alternative: Use Original LoRA Files

If you prefer to keep LoRA files in your Avatars directory, you can create symlinks:

```bash
cd /Users/michaelluts/IdeaProjects/ComfyUI/models/lora
ln -s /Users/michaelluts/IdeaProjects/Avatars/iraKim-flux-high-noise.safetensors
ln -s /Users/michaelluts/IdeaProjects/Avatars/iraKim-flux-low-noise.safetensors
```

This way, updates to your LoRA files in the Avatars directory will be reflected in ComfyUI.
