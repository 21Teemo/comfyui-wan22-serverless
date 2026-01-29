# Wan 2.2 Model Download Instructions

## ⚠️ Repository Not Found

The repository `black-forest-labs/Wan2.2-14B` appears to not exist or be gated.

## 🔍 Finding the Correct Repository

You need to manually check HuggingFace for the correct Wan 2.2 repository. Here's how:

### Option 1: Check ComfyUI Workflow/Error Message
The error message in ComfyUI might have a "Copy URL" button that shows the exact HuggingFace repository path. Use that URL.

### Option 2: Search HuggingFace
1. Go to https://huggingface.co/models
2. Search for: `Wan2.2` or `Wan 2.2` or `black-forest-labs Wan`
3. Look for the official Black Forest Labs repository
4. Check the repository files to find the exact filenames

### Option 3: Check ComfyUI Documentation
ComfyUI might have documentation or workflow examples that show the correct repository path.

## 📥 Manual Download

Once you find the correct repository:

1. **Go to the HuggingFace repository page**
2. **Accept the model license** (if gated)
3. **Download each file** to the correct directory:
   - `umt5_xxl_fp8_e4m3fn_scaled.safetensors` → `models/text_encoders/`
   - `wan_2.1_vae.safetensors` → `models/vae/`
   - `wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors` → `models/diffusion_models/`
   - `wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors` → `models/diffusion_models/`
   - `wan2.2_t2v_lightx2v_4steps_lora_v1.1_high_noise.safetensors` → `models/lora/`
   - `wan2.2_t2v_lightx2v_4steps_lora_v1.1_low_noise.safetensors` → `models/lora/`

## 🎯 Using ComfyUI's "Copy URL" Button

If ComfyUI shows "Copy URL" buttons in the error dialog:
1. Click each "Copy URL" button
2. The URL will show the exact repository and filename
3. Use those URLs to download the files
4. Or use the URLs with `huggingface-cli` or `wget`

## 💡 Alternative: Use HuggingFace CLI

If you have the correct repository:
```bash
cd /Volumes/Misha/ComfyUI
huggingface-cli login
huggingface-cli download [REPOSITORY_NAME] [FILE_NAME] --local-dir models/[DIRECTORY]
```

Replace `[REPOSITORY_NAME]` and `[FILE_NAME]` with the actual values from HuggingFace.
