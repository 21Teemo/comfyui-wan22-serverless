# Missing Wan 2.2 Models

## ✅ Downloaded

1. **Text Encoder**: `umt5_xxl_fp8_e4m3fn_scaled.safetensors` ✓
   - Location: `models/text_encoders/`

2. **VAE**: `wan_2.1_vae.safetensors` ✓
   - Location: `models/vae/`

## ❌ Still Missing

The following Wan 2.2 models need to be downloaded from the correct repository:

### Diffusion Models
- `wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors` (13.31 GB)
- `wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors` (13.31 GB)
- **Location**: `models/diffusion_models/`

### LoRAs
- `wan2.2_t2v_lightx2v_4steps_lora_v1.1_high_noise.safetensors` (1.14 GB)
- `wan2.2_t2v_lightx2v_4steps_lora_v1.1_low_noise.safetensors` (1.14 GB)
- **Location**: `models/lora/`

## 🔍 Finding the Correct Repository

The repository `Comfy-Org/Wan_2.1_ComfyUI_repackaged` only contains Wan 2.1 models, not Wan 2.2.

**To find the correct repository:**

1. **Use ComfyUI's "Copy URL" button** in the Missing Models dialog
   - This will give you the exact HuggingFace repository URL

2. **Check the HuggingFace model card** for Wan 2.2
   - Search for: `Wan2.2 14B` or `wan2.2_t2v` on HuggingFace

3. **The repository might be**:
   - A different Comfy-Org repository
   - Or a Black Forest Labs repository with a different name

## 📥 Download Instructions

Once you have the correct repository URL from "Copy URL":

1. Go to the HuggingFace repository
2. Accept the model license (if gated)
3. Download the files to:
   - Diffusion models → `models/diffusion_models/`
   - LoRAs → `models/lora/`

## 💡 Alternative

If you can share the URLs from the "Copy URL" buttons in ComfyUI, I can help download them automatically.
