# Keeping ComfyUI Running

## Why It Disconnects

ComfyUI may disconnect if:
1. The terminal window closes (if started in foreground)
2. The process crashes due to an error
3. System resources are low
4. The process is killed manually

## Solution: Use the Startup Script

I've created a startup script that uses `nohup` to keep ComfyUI running even if the terminal closes:

```bash
cd /Volumes/Misha/ComfyUI
./START_COMFYUI.sh
```

This will:
- Kill any existing ComfyUI processes
- Start ComfyUI in the background with `nohup`
- Keep it running even if you close the terminal
- Show you the process ID

## Manual Start (Background)

```bash
cd /Volumes/Misha/ComfyUI
nohup /usr/local/opt/python@3.11/bin/python3.11 main.py --listen 127.0.0.1 --port 8188 --cpu > /tmp/comfyui_misha.log 2>&1 &
```

## Check if Running

```bash
ps aux | grep "[p]ython.*main.py"
```

## View Logs

```bash
tail -f /tmp/comfyui_misha.log
```

## Stop ComfyUI

```bash
pkill -f "python.*main.py"
```

Or find the PID and kill it:
```bash
ps aux | grep "[p]ython.*main.py"
kill [PID]
```

## Auto-Start on System Boot (Optional)

If you want ComfyUI to start automatically when your Mac boots, you can create a LaunchAgent. Let me know if you want help setting that up.
