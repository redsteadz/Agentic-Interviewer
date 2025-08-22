# 📁 Webhook Event Logging

## 🎯 Overview
All VAPI webhook events are now automatically saved to JSON files for debugging, auditing, and development purposes.

## 📂 Log File Structure

### **Storage Location:**
```
backend/webhook_logs/
├── call_started_test-call-123_20250822_042140.json
├── call_ended_test-call-123_20250822_042140.json
├── call_failed_test-call-123_20250822_042140.json
├── transcript_updated_test-call-123_20250822_042140.json
└── recording_ready_test-call-123_20250822_042140.json
```

### **File Naming Convention:**
```
{event_type}_{event_id}_{timestamp}.json

Examples:
- call_started_abc123_20250822_143025.json
- call_ended_abc123_20250822_143055.json  
- transcript_updated_abc123_20250822_143045.json
```

## 🔧 Implementation Details

### **Configuration:**
```python
# Location: backend/api/views.py
WEBHOOK_LOG_FOLDER = os.path.join(settings.BASE_DIR, 'webhook_logs')
```

### **Logging Function:**
```python
def save_webhook_event(event_type, event):
    """Save webhook event data to JSON file for debugging and auditing"""
    
    # Create unique filename
    event_name = event_type.replace('.', '_')
    event_id = event.get('id', 'no_event_id')
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    filename = f"{event_name}_{event_id}_{timestamp}.json"
    
    # Save to file
    with open(filepath, 'w') as f:
        json.dump(event, f, indent=4)
```

### **Integration:**
```python
# In VapiWebhookView.post() method:
webhook_data = request.data
event_type = webhook_data.get('type')

# Save webhook event to file for debugging and auditing
save_webhook_event(event_type or 'unknown_event', webhook_data)
```

## 📋 Logged Event Types

### **1. call.started**
```json
{
    "type": "call.started",
    "call": {
        "id": "test-call-123",
        "status": "in-progress", 
        "startedAt": "2025-08-22T09:21:40.106319Z",
        "assistantId": "test-assistant-123",
        "phoneNumberId": "test-phone-123",
        "customer": {"number": "+1234567890"}
    }
}
```

### **2. call.ended** 
```json
{
    "type": "call.ended",
    "call": {
        "id": "test-call-123",
        "status": "ended",
        "startedAt": "2025-08-22T09:21:40.106329Z",
        "endedAt": "2025-08-22T09:21:40.106331Z",
        "duration": 120,
        "cost": 0.05,
        "transcript": [
            {
                "timestamp": "2024-01-20T14:30:05Z",
                "role": "assistant",
                "message": "Hello! How can I help you today?"
            }
        ],
        "recordingUrl": "https://example.com/recording.wav"
    }
}
```

### **3. call.failed**
```json
{
    "type": "call.failed",
    "call": {
        "id": "test-call-123",
        "status": "failed",
        "endReason": "no-answer",
        "endedAt": "2025-08-22T09:21:40.106331Z"
    }
}
```

### **4. transcript.updated**
```json
{
    "type": "transcript.updated", 
    "call": {
        "id": "test-call-123",
        "transcript": [
            {
                "timestamp": "2024-01-20T14:30:05Z",
                "role": "assistant",
                "message": "Hello! How can I help you today?"
            },
            {
                "timestamp": "2024-01-20T14:30:25Z",
                "role": "user", 
                "message": "I'd like to discuss AI applications in healthcare."
            }
        ]
    }
}
```

### **5. recording.ready**
```json
{
    "type": "recording.ready",
    "call": {
        "id": "test-call-123",
        "recordingUrl": "https://example.com/recording.wav"
    }
}
```

## 🛠 Usage & Benefits

### **Debugging:**
- **Inspect raw webhook data** from VAPI
- **Verify webhook payload structure**
- **Debug processing issues**
- **Validate security implementations**

### **Auditing:**
- **Track all webhook events** with timestamps
- **Monitor call lifecycle** progression
- **Analyze webhook patterns**
- **Compliance and logging requirements**

### **Development:**
- **Test webhook handlers** with real data
- **Understand VAPI payload formats**
- **Replay webhook events** for testing
- **Analyze integration issues**

## 📊 Log Management

### **Log File Commands:**
```bash
# View recent webhook events
ls -la backend/webhook_logs/

# Check latest call.ended events  
ls backend/webhook_logs/call_ended_* | tail -5

# View specific event content
cat backend/webhook_logs/call_ended_abc123_20250822_143055.json

# Count events by type
ls backend/webhook_logs/ | cut -d'_' -f1-2 | sort | uniq -c
```

### **Log Rotation (Optional):**
```python
# Add to save_webhook_event() function for production:
def cleanup_old_logs():
    """Remove webhook logs older than 30 days"""
    cutoff = time.time() - (30 * 24 * 60 * 60)  # 30 days
    for filename in os.listdir(WEBHOOK_LOG_FOLDER):
        filepath = os.path.join(WEBHOOK_LOG_FOLDER, filename)
        if os.path.getctime(filepath) < cutoff:
            os.remove(filepath)
```

## 🔍 Monitoring & Analysis

### **Error Analysis:**
```bash
# Find failed webhooks
grep -l "call.failed" backend/webhook_logs/*.json

# Check for missing call IDs
grep -l "no_event_id" backend/webhook_logs/*.json
```

### **Performance Monitoring:**
```bash
# Count webhook events per hour
ls backend/webhook_logs/*.json | grep $(date +%Y%m%d_%H) | wc -l

# Analyze transcript update frequency
ls backend/webhook_logs/transcript_updated_* | wc -l
```

## ⚠️ Production Considerations

### **Storage Management:**
- Webhook logs can accumulate quickly in high-volume environments
- Consider implementing log rotation or archival
- Monitor disk space usage

### **Security:**
- Webhook logs may contain sensitive call data
- Ensure proper file permissions (600)
- Consider encrypting sensitive log files

### **Performance:**
- File I/O is asynchronous and shouldn't impact webhook response time
- Monitor for potential storage bottlenecks

## 🎉 Benefits Summary

✅ **Complete webhook audit trail**
✅ **Easy debugging and troubleshooting**  
✅ **Development and testing support**
✅ **Compliance and monitoring capabilities**
✅ **Real VAPI payload examples**
✅ **Integration validation**

**All webhook events are now preserved for analysis and debugging!** 📁