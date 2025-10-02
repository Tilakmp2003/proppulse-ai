# 🚂 Railway Deployment Guide

## Environment Variables Setup

### Frontend Service Variables
Add these to your **frontend** service in Railway:

```
NEXT_PUBLIC_SUPABASE_URL = [from your Supabase project settings]
NEXT_PUBLIC_SUPABASE_ANON_KEY = [from your Supabase project API settings]
NEXT_PUBLIC_API_URL = https://proppulse-ai-production.up.railway.app
NEXT_PUBLIC_APP_NAME = PropPulse AI
NEXT_PUBLIC_APP_DESCRIPTION = AI-Powered Commercial Real Estate Platform
```

### Backend Service Variables
Add these to your **backend** service in Railway:

```
TWILIO_ACCOUNT_SID = [from your Twilio Console]
TWILIO_AUTH_TOKEN = [from your Twilio Console]
TWILIO_VERIFY_SERVICE_SID = [from your Twilio Verify Service]
```

## Steps
1. Go to railway.app
2. Select your project
3. Click on each service
4. Go to Variables tab
5. Add the variables above
6. Railway will auto-redeploy

## Ready!
Your SMS OTP system will work after adding these variables.
