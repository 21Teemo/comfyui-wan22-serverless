# Wan 2.2 Models for ComfyUI

## 📥 Required Models

ComfyUI needs these models for Wan 2.2:

### Text Encoder
- **File**: `umt5_xxl_fp8_e4m3fn_scaled.safetensors`
- **Size**: 6.27 GB
- **Location**: `models/text_encoders/`

### VAE
- **File**: `wan_2.1_vae.safetensors`
- **Size**: 242.06 MB
- **Location**: `models/vae/`

### Diffusion Models
- **File**: `wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors`
- **Size**: 13.31 GB
- **Location**: `models/diffusion_models/`

- **File**: `wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors`
- **Size**: 13.31 GB
- **Location**: `models/diffusion_models/`

### LoRAs (Optional, but recommended)
- **File**: `wan2.2_t2v_lightx2v_4steps_lora_v1.1_high_noise.safetensors`
- **Size**: 1.14 GB
- **Location**: `models/lora/`

- **File**: `wan2.2_t2v_lightx2v_4steps_lora_v1.1_low_noise.safetensors`
- **Size**: 1.14 GB
- **Location**: `models/lora/`

## 🔗 Download Source

**Repository**: `black-forest-labs/Wan2.2-14B` on HuggingFace

## 📋 Total Size

- **Total**: ~35 GB

## 🚀 Manual Download (if script fails)

1. Go to: https://huggingface.co/black-forest-labs/Wan2.2-14B
2. Accept the model license (if gated)
3. Download each file to the appropriate directory:
   - Text encoder → `models/text_encoders/`
   - VAE → `models/vae/`
   - Diffusion models → `models/diffusion_models/`
   - LoRAs → `models/lora/`

## ⚠️ Note

Make sure you have enough space on the Misha drive (~35 GB free).
