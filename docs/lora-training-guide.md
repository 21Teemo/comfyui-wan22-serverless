# LoRA Training & Usage Guide

## For Learning LoRA Training

### Recommendation: Start Local, Move to Cloud When Needed

**Learning phase needs:**
- Interactive experimentation (try different settings)
- Long sessions (30 min - 2 hours per training run)
- Iterative workflow testing
- Need to see logs/progress in real-time

**Memory requirements for training:**
- **Inference only**: 8-12GB VRAM (for using LoRAs)
- **Training**: 16-24GB VRAM minimum (24GB+ recommended)
- Training needs to load full model + gradients + optimizer states

---

## Step-by-Step Learning Path

### Phase 1: Learn to Use LoRAs Locally (What you're doing now)

You already have LoRA files in `models/lora/`. This is the cheapest way to start:

1. **Load and test LoRAs** in ComfyUI
2. **Experiment with strength values** (0.5-1.5 range)
3. **Learn prompting techniques** with LoRAs
4. **Understand how LoRAs affect output**

**Cost**: $0 (just your local machine)

**When you'll need cloud**: If your local GPU can't run inference smoothly or you want better quality.

---

### Phase 2: Learn Training (Start Local, Then Cloud)

#### Option A: Try Local First (if you have a GPU)

ComfyUI has built-in LoRA training nodes (`TrainLoraNode`):

**Memory optimization for local training:**
```bash
python main.py --lowvram --cpu-vae --reserve-vram 1.0
```

**Training workflow needs:**
- Training images (prepared dataset)
- Base model (checkpoint)
- Training nodes configured
- Save LoRA node to output

**If local training fails/too slow:**
- Move to cloud pod (see below)

#### Option B: Cloud Pod (Best for Learning)

For learning training, **use a Pod (not serverless)** because:

✅ **Interactive**: You need to see training progress, adjust settings, test outputs  
✅ **Long sessions**: Training runs 15-60+ minutes  
✅ **Iterative**: You'll run many training attempts with different settings  
✅ **Cost effective**: ~$0.29/hr, pause when not using  

**Recommended setup:**

1. **Start with RTX 3090 (24GB)** pod - ~$0.29/hr
   - Enough VRAM for most LoRA training
   - Good balance of cost/performance

2. **Use "Pause" feature** - pause pod when done to save money
   - You only pay for storage (~$0.10/month for 20GB)

3. **Set up persistent storage** for:
   - Your training datasets
   - Trained LoRA files
   - Checkpoints/experiments

4. **Session pattern for learning:**
   ```
   Day 1: 3 hours experimenting = $0.87
   Day 2: 2 hours refining = $0.58  
   Day 3: 4 hours finalizing = $1.16
   Total week: ~$10-15 (pausing between sessions)
   ```

**Why NOT serverless for learning:**
- ❌ Cold starts slow down experimentation
- ❌ Hard to debug/see progress interactively  
- ❌ More expensive for long training sessions
- ❌ Can't easily adjust settings mid-training

---

### Phase 3: Production/API (Serverless)

Once you've learned and have stable workflows, **then** use serverless:
- Automated training pipelines
- API endpoints for inference
- Only pay per execution

---

## ComfyUI LoRA Training Resources

### Built-in Training Node

ComfyUI has a `Train LoRA` node (experimental) in the training category:

**Key settings:**
- **Rank**: 4-32 (lower = smaller file, less detail; higher = more capacity)
- **Learning rate**: 0.0001-0.001 (start with 0.0005)
- **Steps**: 500-2000+ (depends on dataset size)
- **Batch size**: 1-4 (limited by VRAM)

**Training dataset preparation:**
- Images: 512x512 or 768x768 (or bucket mode for multi-res)
- Captions: Text files with same name as images
- Recommended: 10-50 images per concept

### Alternative Training Tools

If ComfyUI's built-in training is too experimental:

1. **Kohya SS** (separate tool)
   - More mature, better docs
   - Train locally or on cloud
   - Import trained LoRA into ComfyUI

2. **EveryDream Trainer** (cloud-friendly)
   - Good for cloud training
   - Works well on RunPod

---

## Cost Comparison for Learning

| Approach | Session Cost | Best For |
|----------|--------------|----------|
| **Local (CPU)** | $0 | Learning LoRA usage only |
| **Local (GPU)** | $0 | Training if you have 16GB+ VRAM |
| **RunPod Pod (24GB)** | ~$0.29/hr | **Learning training** (recommended) |
| **RunPod Serverless** | ~$1.73/hr | Production/API after learning |

**Typical learning budget:**
- Week 1-2: ~$15-20 (experimenting, making mistakes)
- Week 3-4: ~$10-15 (getting better, fewer re-runs)
- Month 2+: ~$5-10/month (refining techniques)

---

## Quick Start: Training Your First LoRA on RunPod

1. **Launch pod** (RTX 3090, 24GB)
2. **Install ComfyUI** (or use template)
3. **Prepare dataset:**
   - 20-50 images in `input/` folder
   - Captions in `input/captions/` (one .txt per image)
4. **Build training workflow:**
   - Load base model
   - Load dataset images
   - Configure Train LoRA node
   - Save LoRA output
5. **Run training** (watch progress, adjust if needed)
6. **Test trained LoRA** in inference workflow
7. **Download LoRA** to local `models/lora/`

---

## Tips for Learning Efficiently

1. **Start small**: 10-20 images, rank 8, 500 steps
2. **Iterate quickly**: Don't perfect one LoRA, train many variations
3. **Use pause feature**: Pause pod between sessions
4. **Save experiments**: Name your LoRAs descriptively (rank8-lr0005-1000steps.safetensors)
5. **Document settings**: Keep notes on what worked/didn't work
6. **Join communities**: Discord/Reddit for tips and troubleshooting

---

## Your Current Setup

You're running locally on CPU (`--cpu` flag). For learning LoRA **usage**, this works but is slow.

**Next steps:**
1. ✅ Continue learning LoRA usage locally (slow but free)
2. 🚀 When ready for training: Get RunPod pod (24GB, pause between sessions)
3. 🎯 Once comfortable: Move to serverless for automation

Want help setting up a training workflow or RunPod pod?
