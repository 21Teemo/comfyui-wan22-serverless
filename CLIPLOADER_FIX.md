# Fixing CLIPLoader Error for Wan 2.2

## Error
```
'NoneType' object has no attribute 'Params'
```

## Cause
Your workflow is using `CLIPLoader` which is trying to load a CLIP model, but Wan 2.2 uses **UMT5** text encoders, not CLIP.

## Solution

### Option 1: Update CLIPLoader Settings (Recommended)

In your workflow's CLIPLoader node:

1. **Set clip_name to 'umt5 xxl'**:
   - Look for the `clip_name` parameter in the CLIPLoader node
   - Change it from `clip-l` or `clip-g` to `umt5 xxl` or `umt5xxl`

2. **Verify text_encoder_path**:
   - Should point to: `models/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors`
   - File is present: ✓ (6.3 GB)

### Option 2: Use Wan-Specific Nodes

If your workflow template supports it, use Wan-specific text encoder nodes instead of CLIPLoader:
- Look for nodes like `WanTextEncoder` or `UMT5Loader` in the node list
- Replace CLIPLoader with the appropriate Wan node

### Option 3: Check Workflow Template

The workflow might be expecting a different text encoder configuration. Check:
- The workflow template documentation
- Example workflows for Wan 2.2 in ComfyUI

## Current Text Encoder File

✅ **Present**: `models/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors` (6.3 GB)

## Quick Fix Steps

1. Open your workflow in ComfyUI
2. Find the CLIPLoader node causing the error
3. Check the `clip_name` dropdown/field
4. Change it to `umt5 xxl` or `umt5xxl`
5. Save and try again

The file is already downloaded and in the correct location - you just need to tell CLIPLoader to use UMT5 instead of CLIP.
