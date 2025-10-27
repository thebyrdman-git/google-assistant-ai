# Google Assistant AI Integration

**Talk to your LiteLLM models via Google Assistant**

---

## 🎯 What This Does

Enables voice interaction with your Red Hat Granite AI models through Google Assistant:

- **"Hey Google, talk to My AI Assistant"** → Connects to your LiteLLM instance
- **Ask any question** → Granite 3.2 8B Instruct responds
- **Privacy-first** → All processing on your own infrastructure
- **Enterprise-grade** → Self-healing, monitored, secure

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User's Phone/Speaker                    │
│                   "Hey Google, ask my AI..."                 │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              Google Dialogflow / Actions Console             │
│                    (Conversation Management)                 │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTPS Webhook POST
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                   assistant.jbyrd.org                        │
│              (Traefik Reverse Proxy + SSL)                   │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│           Google Assistant Webhook Service (Flask)           │
│  • Request validation                                        │
│  • Conversation state management                             │
│  • LiteLLM integration                                       │
│  • Response formatting for voice                             │
└─────────────────┬───────────────────────────────────────────┘
                  │ OpenAI-compatible API
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    LiteLLM (localhost:4000)                  │
│                      Model Gateway                           │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              Red Hat Granite 3.2 8B Instruct                 │
│                  (Your AI Brain)                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Google Actions Console project
- Domain with SSL (assistant.jbyrd.org)
- LiteLLM running on MiracleMax

### Deploy

```bash
cd /home/jbyrd/ai-dev-workspace/personal-projects/google-assistant-ai

# Deploy with Ansible (production)
ansible-playbook ansible/deploy-assistant.yml

# Or manual development
python3 app/main.py
```

---

## 📋 Features

### Voice Interactions
- ✅ **Natural conversation** with AI models
- ✅ **Context retention** across conversation turns
- ✅ **Voice-optimized responses** (concise, clear)
- ✅ **Error handling** with friendly fallbacks

### Security
- ✅ **Request verification** (Google JWT validation)
- ✅ **Rate limiting** (prevent abuse)
- ✅ **API key protection** (secrets management)
- ✅ **Audit logging** (track all requests)

### Enterprise Features
- ✅ **Self-healing** (automatic restart on failure)
- ✅ **Health monitoring** (Prometheus metrics)
- ✅ **Alerting** (email notifications)
- ✅ **Resource limits** (CPU, memory)

---

## 🔧 Configuration

### Google Actions Console Setup
1. Create new Actions project
2. Configure webhook URL: `https://assistant.jbyrd.org/webhook`
3. Set up intents and conversation flow
4. Enable account linking (optional)

### MiracleMax Configuration
- **Service Port**: 5001
- **External URL**: https://assistant.jbyrd.org
- **LiteLLM Backend**: http://localhost:4000
- **Model**: granite-3.2-8b-instruct

---

## 📊 Monitoring

```bash
# Check service status
systemctl --user status google-assistant-ai

# View logs
journalctl --user -u google-assistant-ai -f

# Check metrics
curl http://localhost:5001/metrics
```

---

## 🎤 Example Conversations

**User**: "Hey Google, talk to My AI Assistant"  
**Assistant**: "Hi! I'm your personal AI powered by Granite. How can I help you today?"

**User**: "What's the weather like for coding today?"  
**Assistant**: "Great question! While I don't have real-time weather data, I can help you with coding questions, system administration, or technical discussions. What would you like to know?"

**User**: "Explain Kubernetes in simple terms"  
**Assistant**: "Kubernetes is like a smart manager for containerized applications..."

---

## 🛠️ Development

### Local Testing
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python3 app/main.py

# Test webhook locally
curl -X POST http://localhost:5001/webhook \
  -H "Content-Type: application/json" \
  -d @tests/sample_request.json
```

### Testing with Google Actions
Use Actions Console simulator for end-to-end testing before deploying to production.

---

## 📁 Project Structure

```
google-assistant-ai/
├── app/
│   ├── main.py              # Flask application
│   ├── webhook.py           # Google Actions webhook handler
│   ├── litellm_client.py    # LiteLLM integration
│   ├── conversation.py      # Conversation state management
│   └── utils.py             # Helper functions
├── config/
│   ├── assistant-config.yaml # Service configuration
│   └── intents.json         # Dialogflow intents (export)
├── ansible/
│   ├── deploy-assistant.yml # Ansible deployment
│   └── inventory.ini        # Inventory file
├── tests/
│   ├── sample_request.json  # Example webhook request
│   └── test_webhook.py      # Unit tests
├── docs/
│   ├── SETUP.md             # Detailed setup guide
│   ├── GOOGLE-ACTIONS-CONFIG.md
│   └── TROUBLESHOOTING.md
├── docker-compose.yml       # Container definition
├── Dockerfile               # Container image
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

---

## 🎯 Roadmap

### Phase 1: Basic Integration (MVP)
- [x] Project structure
- [ ] Flask webhook service
- [ ] LiteLLM integration
- [ ] Google Actions configuration
- [ ] Basic conversation flow

### Phase 2: Enhanced Features
- [ ] Context retention across sessions
- [ ] Multi-user support
- [ ] Custom intents (home automation, calendar, etc.)
- [ ] Voice response optimization

### Phase 3: Advanced Capabilities
- [ ] Integration with Home Assistant
- [ ] n8n workflow triggers
- [ ] Actual Budget voice queries
- [ ] Grocery list management

---

## 🔐 Security Considerations

- **No data sent to Google Cloud AI** - All AI processing on your infrastructure
- **Request verification** - Validates requests from Google
- **Secrets in GPG-encrypted storage** - Never hardcoded
- **Rate limiting** - Prevents abuse
- **Audit logging** - Full request tracking

---

## 💡 Use Cases

- **Home Control**: "Turn on living room lights"
- **Information Queries**: "What's on my calendar today?"
- **AI Conversations**: "Help me debug this Python code"
- **Budget Checks**: "How much did I spend on groceries this month?"
- **System Status**: "Is my server healthy?"

---

**Status**: 🚧 Phase 1 - Initial Setup  
**Next Step**: Build Flask webhook service  
**Target**: Functional voice AI assistant in <4 hours

