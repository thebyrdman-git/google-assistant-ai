# Quick Start Guide

Get your Google Assistant AI integration running in minutes.

---

## ✅ What We've Built

**Flask Webhook Service** - Production-ready voice AI assistant

### Features Implemented
- ✅ **Flask app** with webhook endpoint for Google Assistant
- ✅ **LiteLLM integration** - Connects to your Granite 3.2 models
- ✅ **Conversation management** - Maintains context across sessions
- ✅ **Voice optimization** - Responses formatted for speech output
- ✅ **Health monitoring** - `/health` and `/metrics` endpoints
- ✅ **Structured logging** - JSON logs for production monitoring
- ✅ **Error handling** - Graceful failures with friendly messages

---

## 🚀 Local Development

### 1. Install Dependencies

```bash
cd /home/jbyrd/ai-dev-workspace/personal-projects/google-assistant-ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Start the Service

```bash
# Make sure LiteLLM is running on localhost:4000
systemctl --user status pai-litellm

# Start the webhook service
python3 app/main.py
```

Output:
```
{"message": "Starting Google Assistant AI Webhook Service on port 5001"}
 * Running on http://0.0.0.0:5001
```

### 3. Test Locally

```bash
# Health check
curl http://localhost:5001/health

# Test webhook with sample request
curl -X POST http://localhost:5001/webhook \
  -H "Content-Type: application/json" \
  -d @tests/sample_request.json
```

---

## 📊 Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/webhook` | POST | Main Google Assistant webhook |
| `/health` | GET | Health check for monitoring |
| `/metrics` | GET | Prometheus metrics |
| `/` | GET | Service information |

---

## 🔧 Configuration

Environment variables (use `config.env.example` as template):

```bash
# Flask
PORT=5001
FLASK_DEBUG=false

# LiteLLM
LITELLM_BASE_URL=http://localhost:4000/v1
LITELLM_API_KEY=***REMOVED***
LITELLM_MODEL=granite-3.2-8b-instruct

# Conversation
MAX_CONVERSATION_HISTORY=10
SESSION_TIMEOUT_MINUTES=30
```

---

## 📝 Example Request/Response

### Request (from Google Assistant)
```json
{
  "queryResult": {
    "queryText": "What is Kubernetes?",
    "intent": {
      "displayName": "Ask AI"
    }
  },
  "session": "projects/my-project/agent/sessions/abc123"
}
```

### Response (to Google Assistant)
```json
{
  "fulfillmentText": "Kubernetes is a container orchestration platform that automates deployment, scaling, and management of containerized applications..."
}
```

---

## 🎯 Next Steps

1. **Google Actions Console Setup** - Configure Dialogflow project
2. **Deploy to MiracleMax** - Containerize and deploy with Traefik
3. **External Access** - Set up `assistant.jbyrd.org` domain
4. **Testing** - Use Actions Console simulator
5. **Production** - Enable monitoring and alerts

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Check what's using port 5001
sudo lsof -i :5001

# Or use different port
PORT=5002 python3 app/main.py
```

### LiteLLM Connection Failed
```bash
# Verify LiteLLM is running
curl http://localhost:4000/v1/models \
  -H "Authorization: Bearer ***REMOVED***"

# Check LiteLLM logs
journalctl --user -u pai-litellm -f
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 📚 Project Structure

```
google-assistant-ai/
├── app/
│   ├── main.py              # Flask application entry point
│   ├── webhook.py           # Google Assistant request handler
│   ├── litellm_client.py    # LiteLLM integration
│   ├── conversation.py      # Session management
│   └── utils.py             # Helper functions
├── tests/
│   └── sample_request.json  # Test data
├── requirements.txt         # Python dependencies
└── config.env.example       # Configuration template
```

---

## ✅ Status

**Phase 1: Flask Webhook Service** - ✅ **COMPLETE**

- [x] Flask app with production patterns
- [x] LiteLLM client integration
- [x] Conversation state management
- [x] Voice-optimized responses
- [x] Health and metrics endpoints
- [x] Structured logging
- [x] Error handling
- [x] Local testing validated

**Ready for**: Google Actions configuration and deployment

---

**Repository**: https://github.com/thebyrdman-git/google-assistant-ai  
**Local Path**: `/home/jbyrd/ai-dev-workspace/personal-projects/google-assistant-ai`

