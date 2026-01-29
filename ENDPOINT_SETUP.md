# Endpoint Setup & Testing Guide

## Your Endpoint Details

- **Endpoint ID**: `11bu8yupz6eou9`
- **API Key**: `$RUNPOD_API_KEY` (set in env or RunPod console)
- **Name**: `Ira_kim`
- **URL**: `https://api.runpod.ai/v2/11bu8yupz6eou9/run`

## Important: Worker Settings

If you see **"100% of max workers are busy"**:

1. **Go to Endpoint Settings**
2. **Set Max Workers = 1 or 2** (for testing)
3. This prevents workers from getting stuck

**Why?**
- Too many workers = all busy warming up
- Jobs queue while workers cold-start
- With 1-2 workers, you can test reliably

## Testing Steps

### Step 1: Quick Healthcheck

Test that endpoint responds:

```bash
python3 test_healthcheck.py
```

This uses minimal input to verify the endpoint is working.

### Step 2: Full Test

Once healthcheck passes, run full test:

```bash
python3 test_serverless.py
```

## Manual Test (cURL)

### Quick Test

```bash
curl -X POST \
  "https://api.runpod.ai/v2/11bu8yupz6eou9/run" \
  -H "Authorization: Bearer $RUNPOD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "positive_prompt": "test",
      "steps": 1,
      "width": 128,
      "height": 128,
      "length": 1
    }
  }'
```

### Check Status

```bash
# Replace JOB_ID with ID from above response
curl -X GET \
  "https://api.runpod.ai/v2/11bu8yupz6eou9/status/JOB_ID" \
  -H "Authorization: Bearer $RUNPOD_API_KEY"
```

## Troubleshooting "100% Workers Busy"

**Symptoms:**
- Banner shows "100% of max workers are busy"
- Jobs stuck in queue
- Long wait times

**Solutions:**

1. **Reduce Max Workers** (for testing):
   - Settings → Max Workers → Set to 1 or 2
   - This ensures workers aren't all warming up

2. **Check Worker Status**:
   - Dashboard → Endpoint → Workers tab
   - See if workers are stuck in "Warming" state

3. **Restart Workers** (if stuck):
   - Sometimes workers get stuck
   - Restart endpoint or scale workers to 0 then back up

4. **Increase Workers** (for production):
   - Once working, increase to 3-5 for better throughput
   - But start with 1-2 for testing

## Expected Behavior

**First Request (Cold Start):**
- 30-60 seconds: Container starting
- 10-30 seconds: ComfyUI loading
- 2-5 minutes: Video generation
- **Total: ~3-6 minutes**

**Subsequent Requests (Warm):**
- 2-5 minutes: Video generation only
- **Total: ~2-5 minutes**

## Production Settings

Once testing works:

1. **Max Workers**: 3-5 (for concurrent requests)
2. **Always Ready Workers**: 1-2 (to avoid cold starts)
3. **Timeout**: 600 seconds (10 minutes)

## Monitoring

Check logs in:
- RunPod Dashboard → Serverless → `Ira_kim` → Logs

Look for:
- ✅ "ComfyUI started successfully"
- ✅ "Prompt queued: ..."
- ❌ "Models not found" → Check network volume
- ❌ "Failed to start ComfyUI" → Check container disk size
