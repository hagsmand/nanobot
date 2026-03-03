# Fix: "No open ports detected" Error on Render.com

## The Problem

You're seeing this error:
```
No open ports detected, continuing to scan...
```

This happens because:
- Render.com's **Web Service** (free plan) requires an HTTP port to be open
- Nanobot's `gateway` command doesn't expose an HTTP server by default
- Render needs to detect a port binding to consider the service healthy

## The Solution: HTTP Wrapper Script

I've added a wrapper script (`gateway_with_http.py`) that:
1. Starts a simple HTTP health endpoint on port 10000
2. Runs the nanobot gateway alongside it
3. Satisfies Render's port requirement

This is already configured in your repository!

## How to Deploy

### Option 1: Use render.yaml (Easiest - Recommended)

1. **Go to Render Dashboard**: [dashboard.render.com](https://dashboard.render.com)
2. **Click "New +" → "Blueprint"**
3. **Connect your repository**: `hagsmand/nanobot`
4. **Render will detect** the `render.yaml` file automatically
5. **Set environment variables** when prompted:
   - `OPENROUTER_API_KEY` = your key (required)
   - `CEREBRAS_API_KEY` = your key (optional)
   - `TELEGRAM_BOT_TOKEN` = your token (optional)
   - `TELEGRAM_USER_ID` = your user ID (optional)
6. **Click "Apply"**

### Option 2: Manual Setup

If you prefer manual setup or already created a service:

1. **Create/Update Web Service**:
   - Go to Render dashboard
   - Click "New +" → "Web Service" (or edit existing)
   - Connect repository: `hagsmand/nanobot`

2. **Configure**:
   ```
   Name: nanobot-gateway
   Runtime: Docker
   Dockerfile Path: ./Dockerfile
   Docker Command: python /app/gateway_with_http.py
   Plan: Free
   ```

3. **Add Environment Variables**:
   ```
   PORT = 10000
   OPENROUTER_API_KEY = [your key]
   ```
   
   Optional:
   ```
   CEREBRAS_API_KEY = [your key]
   TELEGRAM_BOT_TOKEN = [your token]
   TELEGRAM_USER_ID = [your user id]
   ```

4. **Add Disk** (optional but recommended):
   ```
   Name: nanobot-config
   Mount Path: /root/.nanobot
   Size: 1 GB
   ```

5. **Deploy**: Click "Create Web Service" or "Manual Deploy"

## What Changed

The repository now includes:

1. **`gateway_with_http.py`** - Wrapper script that adds HTTP endpoint
2. **Updated `Dockerfile`** - Installs aiohttp and uses the wrapper
3. **`render.yaml`** - Blueprint for one-click deployment

## How It Works

```
┌─────────────────────────────────────┐
│   Docker Container                   │
│                                      │
│  ┌────────────────────────────────┐ │
│  │  HTTP Server (port 10000)      │ │  ← Render detects this
│  │  GET / → "OK"                  │ │
│  │  GET /health → "OK"            │ │
│  └────────────────────────────────┘ │
│                                      │
│  ┌────────────────────────────────┐ │
│  │  Nanobot Gateway               │ │
│  │  - Telegram bot                │ │
│  │  - Discord bot                 │ │
│  │  - Other channels              │ │
│  └────────────────────────────────┘ │
└─────────────────────────────────────┘
```

## Verification

After deploying, check the logs in Render dashboard. You should see:

```
==========================================
Nanobot Configuration Initialization
==========================================
Found config file: /root/.nanobot/config.json
✓ Substituted OPENROUTER_API_KEY
==========================================
Configuration initialized successfully!
==========================================
✓ HTTP health endpoint running on port 10000
🐈 Starting nanobot gateway...
✓ Channels enabled: telegram
✓ Heartbeat: every 1800s
✓ Gateway ready!
```

Then Render will show:
```
==> Your service is live 🎉
```

## Testing

1. **Health Check**: Visit your Render service URL (e.g., `https://nanobot-gateway-xxx.onrender.com`)
   - You should see: `OK`

2. **Bot Functionality**: 
   - If Telegram is configured, send a message to your bot
   - First message may take 30 seconds (service waking up)
   - Subsequent messages should be fast

## Free Plan Limitations

- **Service sleeps after 15 minutes** of inactivity
  - First request after sleep takes ~30 seconds to wake up
  - HTTP health checks don't prevent sleep
  
- **750 hours/month limit**
  - With sleep: can last full month
  - Monitor usage in Render dashboard

- **No persistent disk guarantee**
  - Configuration is baked into Docker image
  - Disk may not survive service restarts

## Troubleshooting

### Still seeing "No open ports detected"?

1. **Check Docker Command**: Should be `python /app/gateway_with_http.py`
2. **Check PORT env var**: Should be set to `10000`
3. **Check logs**: Look for "HTTP health endpoint running on port 10000"
4. **Rebuild**: Try "Clear build cache & deploy"

### Service crashes immediately?

1. **Check API key**: Verify `OPENROUTER_API_KEY` is set correctly
2. **Check logs**: Look for error messages
3. **Test API key**: Visit [openrouter.ai](https://openrouter.ai) and verify your key works

### Bot doesn't respond?

1. **Service sleeping**: Send another message, wait 30 seconds
2. **Check configuration**: Verify bot token and user ID are correct
3. **Check logs**: Look for connection errors

## Summary

✅ **Solution**: HTTP wrapper script provides the required port  
✅ **Already configured**: Just deploy and set environment variables  
✅ **Free plan compatible**: Works with Render's free Web Service  
✅ **No code changes needed**: Everything is ready in your repository  

Your repository is now properly configured for Render.com free plan deployment!