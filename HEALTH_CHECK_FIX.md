# Health Check Fix - Intermittent "Offline" Issue

## Problem

Frontend sometimes shows "backend offline" even though Railway shows service as "active". This happens intermittently.

## Root Causes

1. **Railway Cold Starts** - Free tier services can sleep after inactivity, causing slow first response
2. **Network Latency** - Vercel → Railway can have variable latency
3. **Short Timeout** - 5 second timeout too aggressive for Railway free tier
4. **Single Failure = Offline** - One failed check immediately marks as offline
5. **Health Check Too Frequent** - Checking every 30 seconds is aggressive

## Fixes Applied

### Backend (`/health` endpoint)
- ✅ **Faster response** - Minimal checks, no expensive operations
- ✅ **Error handling** - Returns 200 even on minor errors (prevents false offline)
- ✅ **Lightweight** - Doesn't check model deeply (just config)

### Frontend (`useBackendHealth` hook)
- ✅ **Longer timeout** - 10 seconds (was 5) for Railway's slower responses
- ✅ **Less frequent checks** - 60 seconds (was 30) to reduce load
- ✅ **Resilient to failures** - Requires 2 consecutive failures before marking offline
- ✅ **No cache** - Prevents browser caching health check responses

## How It Works Now

1. **First failure** → Status stays "online" (might be temporary network issue)
2. **Second consecutive failure** → Status changes to "offline"
3. **Any success** → Resets failure counter, marks "online"

This prevents false "offline" from:
- Temporary network hiccups
- Railway cold starts (first request slow)
- Browser caching issues
- Brief Railway slowdowns

## Testing

After these changes:
- Health check should be more stable
- Less false "offline" status
- Better handling of Railway cold starts
- More resilient to network issues

If you still see issues, we can:
- Increase timeout further (15-20 seconds)
- Increase failure threshold (3 failures instead of 2)
- Add retry logic with exponential backoff


