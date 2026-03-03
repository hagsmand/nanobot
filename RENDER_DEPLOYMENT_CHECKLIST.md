# Render.com Deployment Checklist

Your repository is now ready for deployment! Follow these steps:

## ✅ Repository Setup (COMPLETED)

- [x] Forked nanobot repository
- [x] Created `.nanobot/config.json` with environment variable placeholders
- [x] Created `.nanobot/workspace/HEARTBEAT.md` for periodic tasks
- [x] Created `init-config.sh` initialization script
- [x] Modified `Dockerfile` for Render.com deployment
- [x] Committed and pushed all changes to GitHub

## 🚀 Next Steps: Deploy to Render.com

### Step 1: Create Web Service

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Click "Build and deploy from a Git repository"
4. Connect your GitHub account (if not already connected)
5. Select repository: `hagsmand/nanobot`

### Step 2: Configure Service

Fill in these settings:

**Basic Settings:**
```
Name: nanobot-gateway
Region: [Choose closest to you - e.g., Oregon (US West)]
Branch: main
Root Directory: [leave empty]
```

**Build Settings:**
```
Runtime: Docker
Dockerfile Path: ./Dockerfile
Docker Command: gateway
```

**Instance Type:**
```
Plan: Free
```

### Step 3: Add Environment Variables

Click "Add Environment Variable" and add:

**Required:**
```
Key: OPENROUTER_API_KEY
Value: [Your OpenRouter API key - get from https://openrouter.ai/keys]
Secret: ✓ (toggle on)
```

**Optional (for Telegram bot):**
```
Key: TELEGRAM_BOT_TOKEN
Value: [Get from @BotFather on Telegram]
Secret: ✓

Key: TELEGRAM_USER_ID
Value: [Get from @userinfobot on Telegram]
Secret: ✗
```

To enable Telegram:
1. Get bot token from @BotFather
2. Get your user ID from @userinfobot
3. Add both environment variables above
4. The config will automatically enable Telegram

### Step 4: Deploy

1. Click "Create Web Service"
2. Wait 5-10 minutes for build to complete
3. Monitor the build logs

### Step 5: Verify Deployment

**Check Logs:**

In Render dashboard, go to "Logs" tab. You should see:

```
==========================================
Nanobot Configuration Initialization
==========================================
Found config file: /root/.nanobot/config.json
Created backup: /root/.nanobot/config.json.backup
Substituting environment variables...
✓ Substituted OPENROUTER_API_KEY
==========================================
Configuration initialized successfully!
==========================================
Starting nanobot...
==========================================
```

**Test the Bot:**

If using Telegram:
1. Find your bot on Telegram
2. Send: "Hello!"
3. Wait 30 seconds (first request wakes up the service)
4. Bot should respond

## 🔧 Configuration Files Created

Your repository now contains:

```
nanobot/
├── .nanobot/
│   ├── config.json              # Configuration with env var placeholders
│   └── workspace/
│       └── HEARTBEAT.md         # Periodic tasks
├── init-config.sh               # Initialization script
├── Dockerfile                   # Modified for Render deployment
└── ... (other original files)
```

## 📝 Important Notes

### Free Plan Limitations

- **Service sleeps after 15 minutes** of inactivity
  - First request after sleep takes ~30 seconds to wake up
  - Subsequent requests are fast
  
- **750 hours/month limit**
  - With sleep: can last full month
  - Without sleep: ~31 days

- **No shell access**
  - Configuration is pre-baked into Docker image
  - To change config: edit files on GitHub and redeploy

### Keeping Service Awake (Optional)

Use UptimeRobot to ping your service every 10 minutes:

1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Create free account
3. Add HTTP(s) monitor
4. URL: Your Render service URL (from Render dashboard)
5. Interval: 10 minutes

This keeps your service awake during active hours.

## 🔄 Making Changes

To update configuration:

1. **Edit files on GitHub**
   - Go to https://github.com/hagsmand/nanobot
   - Navigate to `.nanobot/config.json`
   - Click pencil icon to edit
   - Make changes
   - Commit

2. **Trigger Redeploy**
   - Go to Render dashboard
   - Click "Manual Deploy" → "Deploy latest commit"
   - Wait for rebuild

3. **Verify**
   - Check logs for "Configuration initialized successfully!"
   - Test functionality

## 🆘 Troubleshooting

### Build Fails

**Check:**
- Dockerfile syntax is correct
- All files are committed to GitHub
- Build logs for specific errors

**Solution:**
- Review build logs in Render dashboard
- Try "Clear build cache & deploy"

### Service Crashes

**Check:**
- Environment variables are set correctly
- API key is valid
- Logs for error messages

**Solution:**
```bash
# Test your API key at:
https://openrouter.ai/keys
```

### Bot Doesn't Respond

**Check:**
- Service is awake (check Render dashboard)
- Bot token is correct
- Your user ID is in allowFrom list

**Solution:**
- Send another message (wakes up service)
- Wait 30 seconds for first response
- Check logs for errors

### Configuration Not Applied

**Check:**
- Environment variables are set in Render
- Logs show "Configuration initialized successfully!"

**Solution:**
- Verify environment variable names match placeholders
- Check for typos in variable names
- Redeploy with "Clear build cache & deploy"

## 💰 Cost Estimate

### Free Plan
- **Hosting**: $0/month
- **API Usage**: $2-20/month (depending on usage)
- **Total**: $2-20/month

### Upgrade to Starter Plan ($7/month)
Benefits:
- No sleep (24/7 uptime)
- Shell access for easier configuration
- Better performance
- Guaranteed persistent disk

## 📚 Additional Resources

- **Full Documentation**: See parent directory for complete guides
- **Nanobot GitHub**: [github.com/HKUDS/nanobot](https://github.com/HKUDS/nanobot)
- **Render Docs**: [render.com/docs](https://render.com/docs)
- **OpenRouter**: [openrouter.ai](https://openrouter.ai)

## ✅ Success Checklist

- [ ] Created Render service
- [ ] Set environment variables
- [ ] Deployed successfully
- [ ] Verified in logs
- [ ] Tested bot functionality
- [ ] (Optional) Set up UptimeRobot

---

**Your repository is ready!** Go to [dashboard.render.com](https://dashboard.render.com) and follow the steps above to deploy! 🚀