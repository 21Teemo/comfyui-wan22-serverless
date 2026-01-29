# ComfyUI Location

## ✅ ComfyUI Moved

ComfyUI has been moved from:
- **Old location**: `/Users/michaelluts/IdeaProjects/ComfyUI`
- **New location**: `/Volumes/Misha/ComfyUI`

## 📁 Current Structure

All ComfyUI files are now on the **Misha** external drive at:
```
/Volumes/Misha/ComfyUI/
```

### Key Directories:
- **models/**: All model files (LoRAs, checkpoints, VAE, etc.)
- **venv/**: Python virtual environment
- **comfy/**: Core ComfyUI code
- **main.py**: Main entry point

## 🚀 Running ComfyUI

To start ComfyUI from the new location:

```bash
cd /Volumes/Misha/ComfyUI
source venv/bin/activate
python main.py --listen 127.0.0.1 --port 8188 --cpu
```

Or create a startup script for convenience.

## 📝 Important Notes

1. **LoRA Files**: Your LoRA files are still in `models/lora/`:
   - `iraKim-flux-low-noise.safetensors`
   - `iraKim-flux-high-noise.safetensors`

2. **Models**: All models are preserved:
   - VAE: `models/vae/ae.safetensors`
   - Text encoders: `models/text_encoders/` (empty, ready for Wan 2.2)
   - Checkpoints: `models/checkpoints/` (ready for Wan 2.2 base model)

3. **Virtual Environment**: The venv is preserved and should work from the new location.

## 💡 Quick Access

To quickly access ComfyUI:
```bash
cd /Volumes/Misha/ComfyUI
```

## 🔗 Related

- **Avatars project**: `/Volumes/Misha/Avatars/`
- Both projects are now on the same drive for easy access
