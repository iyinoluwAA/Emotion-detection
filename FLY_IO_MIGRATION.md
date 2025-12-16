# Quick Migration to Fly.io (Free, Better Memory)

## Why Fly.io?
- ✅ **Free tier**: 3 shared-cpu VMs, 256MB each (can request more)
- ✅ **Better memory management**: Can handle ViT model
- ✅ **Global edge deployment**: Fast worldwide
- ✅ **Easy migration**: Just a few commands

## Quick Setup (5 minutes)

### 1. Install Fly CLI
```bash
curl -L https://fly.io/install.sh | sh
```

### 2. Login to Fly.io
```bash
flyctl auth login
```

### 3. Create Fly.io App
```bash
cd /home/iyino/projects/Emotion-detection
flyctl launch --name emotion-detection-backend
```

When prompted:
- **App name**: `emotion-detection-backend` (or your choice)
- **Region**: Choose closest to you
- **Postgres/Redis**: No (we use SQLite)
- **Dockerfile**: `backend/Dockerfile`
- **Deploy now**: Yes

### 4. Configure Memory (Important!)
Create `fly.toml` in project root (or edit the one created):

```toml
app = "emotion-detection-backend"
primary_region = "iad"  # Change to your region

[build]
  dockerfile = "backend/Dockerfile"

[http_service]
  internal_port = 5000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
  processes = ["app"]

[[vm]]
  memory_mb = 1024  # 1GB - enough for ViT model!
  cpu_kind = "shared"
  cpus = 1
```

### 5. Set Environment Variables
```bash
flyctl secrets set PORT=5000
```

### 6. Deploy!
```bash
flyctl deploy
```

### 7. Get Your URL
```bash
flyctl status
# Your app will be at: https://emotion-detection-backend.fly.dev
```

## Update Frontend

Update `frontend/src/api/config.ts`:
```typescript
// Production default: Fly.io backend
return "https://emotion-detection-backend.fly.dev";
```

## Verify ViT Model is Loading

Check logs:
```bash
flyctl logs
```

You should see:
```
[MODEL] Loading Vision Transformer: HardlyHumans/Facial-expression-detection
[MODEL] ✅ ViT model loaded successfully!
[APP] Model loaded: type=vit, version=hardlyhumans-vit-92.2%, labels=8
```

## Cost
- **Free tier**: 3 shared-cpu VMs, 256MB each
- **Upgrade**: $1.94/month per 1GB VM (if needed)
- **First month**: Usually free credits

## Troubleshooting

### If deployment fails:
```bash
flyctl logs
flyctl status
```

### If model still doesn't load:
Check memory usage:
```bash
flyctl scale memory 2048  # Upgrade to 2GB if needed
```

### If you need more help:
```bash
flyctl help
flyctl docs
```

## Next Steps

1. Deploy to Fly.io (follow steps above)
2. Update frontend API URL
3. Test with your surprise image
4. Should now correctly classify as "surprise"! 🎉


