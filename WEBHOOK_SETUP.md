# VAPI Webhook Setup Guide

## 🎯 Overview
This guide shows how to configure VAPI webhooks for real-time call status updates instead of polling.

## ✅ What's Implemented

### Webhook Endpoint
- **URL**: `http://localhost:8000/api/webhook/vapi/`
- **Method**: POST
- **Authentication**: None required (VAPI webhooks are validated by signature)

### Supported Events
- `call.started` - When call begins
- `call.ended` - When call completes with full transcript processing
- `call.failed` - When call fails
- `transcript.updated` - Real-time transcript updates
- `recording.ready` - When recording is available

### Security Features
- ✅ Webhook signature validation (optional)
- ✅ Request body validation
- ✅ Comprehensive error handling
- ✅ Detailed logging

## 🔧 Configuration Steps

### 1. Environment Variables (Optional)
Add to your `.env` file for webhook signature validation:
```bash
VAPI_WEBHOOK_SECRET=your_webhook_secret_from_vapi
```

### 2. Public URL Setup
For production, you need a publicly accessible URL:

**Development (using ngrok):**
```bash
# Install ngrok if not already installed
npm install -g ngrok

# Expose your local server
ngrok http 8000

# Use the https URL provided by ngrok
# Example: https://abc123.ngrok.io/api/webhook/vapi/
```

**Production:**
Use your domain: `https://yourdomain.com/api/webhook/vapi/`

### 3. VAPI Assistant Configuration
Update your assistant creation to include webhook URL:

```python
# In your assistant creation code (CreateAssistantView)
assistant_config = {
    "name": assistant_name,
    "firstMessage": first_message,
    "model": {
        "provider": "openai",
        "model": "gpt-4",
        "messages": [{"role": "system", "content": system_prompt}]
    },
    "voice": {
        "provider": voice_provider,
        "voiceId": voice_id
    },
    # Add webhook configuration
    "serverUrl": "https://your-domain.com/api/webhook/vapi/",  # Your webhook URL
    "serverUrlSecret": "your_webhook_secret_here"  # Optional but recommended
}
```

### 4. Alternative: VAPI Dashboard Configuration
1. Log in to VAPI Dashboard
2. Go to your Assistant settings
3. Add webhook URL in "Server URL" field
4. Set webhook secret (optional but recommended)

## 🚀 Benefits

### Before (Polling):
```
Your App ──GET /call/{id}──> VAPI API
    ↑                           │
    └─── Manual refresh ────────┘
```

### After (Webhooks):
```
VAPI ──webhook──> Your App
              ↓
        Real-time updates
        Automatic processing
```

### Advantages:
- ✅ **Real-time updates** - Instant status changes
- ✅ **Reduced API calls** - No more polling
- ✅ **Better UX** - Live transcript updates
- ✅ **Automatic processing** - Transcript processing on call end
- ✅ **Resource efficient** - Less server load

## 🧪 Testing

Run the test script:
```bash
python test_vapi_webhook.py
```

Expected output: 404 errors (normal - test data doesn't exist in DB)

## 📝 Webhook Payload Examples

### call.started
```json
{
  "type": "call.started",
  "call": {
    "id": "call_123",
    "status": "in-progress",
    "startedAt": "2024-01-20T14:30:05Z",
    "assistantId": "assistant_123"
  }
}
```

### call.ended
```json
{
  "type": "call.ended", 
  "call": {
    "id": "call_123",
    "status": "ended",
    "endedAt": "2024-01-20T14:32:15Z",
    "transcript": [...],
    "recordingUrl": "https://..."
  }
}
```

## 🔍 Monitoring

Check Django logs for webhook activity:
```bash
tail -f backend/server.log | grep "VAPI webhook"
```

## 🛠 Troubleshooting

### Webhook not receiving events?
1. Verify webhook URL is publicly accessible
2. Check VAPI assistant configuration
3. Ensure Django server is running
4. Check firewall/security group settings

### Signature validation failing?
1. Verify `VAPI_WEBHOOK_SECRET` matches VAPI dashboard
2. Check webhook secret in assistant configuration
3. Temporarily disable validation for testing

### Database errors?
1. Ensure call exists in database before webhook
2. Check `vapi_call_id` matches exactly
3. Verify user permissions

## 🎉 Success!
Your application now receives real-time updates from VAPI instead of polling for status changes!