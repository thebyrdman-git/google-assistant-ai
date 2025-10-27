# Google Dialogflow Setup Guide

Complete guide to connecting your Google Assistant to the AI webhook on MiracleMax.

---

## 🎯 Overview

We'll set up:
1. **Google Cloud Project** - Enable required APIs
2. **Dialogflow Agent** - Handle conversation flow
3. **Webhook Integration** - Connect to `https://assistant.jbyrd.org/webhook`
4. **Intents** - Define what questions trigger AI responses
5. **Testing** - Test in simulator and on real devices

---

## 📋 Prerequisites

- ✅ Google account (personal Gmail works fine)
- ✅ Webhook running at `https://assistant.jbyrd.org/webhook`
- ✅ SSL certificate valid (Traefik + Cloudflare)
- ✅ Webhook accessible from internet (test from phone)

---

## 🚀 Step 1: Create Google Cloud Project

### 1.1 Go to Google Cloud Console
- Visit: https://console.cloud.google.com/
- Sign in with your Google account

### 1.2 Create New Project
1. Click **"Select a project"** dropdown (top bar)
2. Click **"New Project"**
3. **Project Name:** `Personal AI Assistant`
4. **Location:** No organization (or select if you have one)
5. Click **"Create"**
6. Wait ~30 seconds for project creation

### 1.3 Enable Required APIs
1. Go to **APIs & Services** → **Library**
2. Search for and enable:
   - **Dialogflow API** ✅
   - **Actions API** (optional, for advanced features) ✅

---

## 🤖 Step 2: Create Dialogflow Agent

### 2.1 Open Dialogflow Console
- Visit: https://dialogflow.cloud.google.com/
- Select your project: `Personal AI Assistant`
- Accept Terms of Service if prompted

### 2.2 Create Agent
1. Click **"Create Agent"**
2. **Agent name:** `Personal AI Assistant`
3. **Default language:** English
4. **Default time zone:** `America/New_York` (or your timezone)
5. **Google project:** Select `Personal AI Assistant`
6. Click **"Create"**

---

## 🔗 Step 3: Configure Webhook

### 3.1 Enable Fulfillment
1. In Dialogflow console, click **"Fulfillment"** (left sidebar)
2. Toggle **"Webhook"** to **ENABLED**
3. **URL:** `https://assistant.jbyrd.org/webhook`
4. **Basic Auth:** Leave empty (we're using API key in LiteLLM, not webhook auth)
5. **Headers:** (Optional - add if you want extra security)
   ```
   X-API-Key: your-secret-key-here
   ```
6. Click **"Save"** (bottom of page)

### 3.2 Test Webhook Connectivity
Dialogflow will automatically test the webhook URL. You should see:
- ✅ Green checkmark if successful
- ❌ Red error if webhook unreachable

**If you get an error:**
```bash
# Test webhook from MiracleMax
curl https://assistant.jbyrd.org/webhook

# Test from external network
curl https://assistant.jbyrd.org/health

# Check container logs
podman logs google-assistant-ai --tail 50
```

---

## 💬 Step 4: Create Intents

Intents define what the user can say and how your AI responds.

### 4.1 Default Welcome Intent (Already Exists)

1. Click **"Intents"** in left sidebar
2. Click **"Default Welcome Intent"**
3. Scroll down to **"Fulfillment"**
4. Enable **"Enable webhook call for this intent"**
5. Click **"Save"**

**What this does:** When user starts conversation, sends request to your AI.

### 4.2 Default Fallback Intent (Already Exists)

1. Click **"Default Fallback Intent"**
2. Scroll to **"Fulfillment"**
3. Enable **"Enable webhook call for this intent"**
4. Click **"Save"**

**What this does:** When user says something unexpected, AI handles it.

### 4.3 Create "Ask AI" Intent (NEW)

This is the main intent for asking questions to your AI.

1. Click **"Intents"** → **"Create Intent"** (top right)
2. **Intent name:** `Ask AI`

3. **Training Phrases** (add these examples):
   ```
   What is Kubernetes?
   Tell me about artificial intelligence
   How does machine learning work?
   Explain quantum computing
   What are microservices?
   Who is the president?
   What's the weather like?
   Tell me a joke
   Help me understand Docker
   Explain Red Hat OpenShift
   ```

4. **Action and parameters:** (skip for now)

5. **Responses:** (delete default text responses)

6. **Fulfillment:**
   - ✅ Enable **"Enable webhook call for this intent"**

7. Click **"Save"**

**What this does:** Any question-like phrase triggers your AI webhook.

---

## 🧪 Step 5: Test in Dialogflow Simulator

### 5.1 Open Test Console
- Click **"Try it now"** (right side panel)
- Or press `Ctrl+Shift+D` / `Cmd+Shift+D`

### 5.2 Test Queries

Try these in the test console:

```
User: "What is Kubernetes?"
Expected: AI-powered response from Mistral 7B

User: "Explain Docker containers"
Expected: Detailed explanation

User: "Tell me about Red Hat"
Expected: Information about Red Hat
```

### 5.3 Inspect Webhook Calls

1. After each test, click **"DIAGNOSTIC INFO"** tab
2. Look for:
   - **Fulfillment Status:** Should show webhook call
   - **Fulfillment Response:** Your AI's response
   - **Webhook Latency:** Should be 2-6 seconds

### 5.4 Check Container Logs

```bash
# Watch live logs during testing
podman logs -f google-assistant-ai
```

You should see:
```json
{"message": "Webhook request received", "intent": "Ask AI"}
{"message": "LiteLLM endpoint: http://192.168.1.34:4000/v1"}
{"message": "Webhook response sent", "intent": "Ask AI"}
```

---

## 🎤 Step 6: Test on Google Assistant Device

### 6.1 Enable Testing

1. In Dialogflow, click **"Integrations"** (left sidebar)
2. Click **"Google Assistant"** card
3. Click **"Test"** button
4. This opens **Actions Console**

### 6.2 Actions Console Setup

1. In Actions Console, go to **"Test"** tab (left sidebar)
2. Select **"On device"** testing
3. Enable testing on your devices

### 6.3 Test on Phone/Speaker

**On your phone or Google Home:**

```
You: "Hey Google, talk to my test app"
Google: Opens your agent
You: "What is Kubernetes?"
AI: [Mistral 7B response about Kubernetes]
```

**Note:** While in test mode, you'll need to say **"talk to my test app"** instead of the actual invocation name.

---

## 🌐 Step 7: Deploy to Production (Optional)

### 7.1 Set Invocation Name

1. In Actions Console, go to **"Deploy"** → **"Directory Information"**
2. **Display name:** `Personal AI Assistant`
3. **Pronunciation:** (optional)
4. **Voice:** Choose male/female voice

### 7.2 Add Description & Images

1. **Short description:** "Talk to AI models running on your personal infrastructure"
2. **Full description:** Add detailed description
3. **Sample invocations:**
   ```
   Hey Google, talk to Personal AI Assistant
   Ask Personal AI Assistant about Kubernetes
   ```
4. Upload icons (512x512px)

### 7.3 Privacy & Consent

1. **Category:** Productivity / Education
2. **Privacy Policy URL:** (create simple page or skip for personal use)
3. **Terms of Service:** (optional for personal use)

### 7.4 Submit for Review

**For Public Release:**
- Click **"Submit for Production"**
- Google reviews (1-2 weeks)
- Requires compliance with policies

**For Personal Use Only:**
- Stay in test mode (works indefinitely)
- No review needed
- Works on devices signed in to your account

---

## 🔧 Troubleshooting

### Webhook Not Responding

```bash
# Test webhook directly
curl -X POST https://assistant.jbyrd.org/webhook \
  -H "Content-Type: application/json" \
  -d '{"queryResult": {"queryText": "test"}}'

# Check if container is healthy
podman ps | grep google-assistant-ai

# View logs
podman logs google-assistant-ai --tail 50

# Test from outside network
# (Use phone's mobile data, not WiFi)
curl https://assistant.jbyrd.org/health
```

### SSL Certificate Issues

```bash
# Test SSL
openssl s_client -connect assistant.jbyrd.org:443 -servername assistant.jbyrd.org

# Check Cloudflare DNS
dig assistant.jbyrd.org

# Verify Traefik routing
curl -H "Host: assistant.jbyrd.org" http://192.168.1.34:5001/health
```

### AI Responses Too Slow

Current setup: **2-6 seconds response time**

To improve:
1. **Use smaller model:** Switch to `phi3-mini` (faster, less detailed)
2. **Reduce max_tokens:** Edit `app/webhook.py`, set `max_tokens=100`
3. **Pre-load model:** Ollama keeps model in memory after first use

```bash
# Pre-warm the model
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer ***REMOVED***" \
  -H "Content-Type: application/json" \
  -d '{"model":"mistral-7b-instruct","messages":[{"role":"user","content":"hi"}]}'
```

### Conversation Context Not Working

Check session management:
```bash
# Verify conversation history is being saved
podman exec google-assistant-ai ps aux | grep python
```

Session timeout is **30 minutes** by default. After that, context is lost.

---

## 📊 Monitoring

### View Request Logs

```bash
# Real-time webhook logs
podman logs -f google-assistant-ai | grep -E "Webhook|fulfillmentText"

# LiteLLM logs
journalctl --user -u pai-litellm -f | grep -E "POST|completion"

# Ollama logs
journalctl -u ollama -f
```

### Check Metrics

```bash
# Prometheus metrics
curl http://localhost:5001/metrics

# Request count
curl -s http://localhost:5001/metrics | grep assistant_requests_total

# Response time
curl -s http://localhost:5001/metrics | grep assistant_request_duration
```

---

## 🎯 Success Checklist

Before considering Dialogflow setup complete:

- [ ] Dialogflow agent created
- [ ] Webhook URL configured and verified
- [ ] Default Welcome Intent uses webhook
- [ ] Default Fallback Intent uses webhook
- [ ] "Ask AI" intent created with training phrases
- [ ] Tested successfully in Dialogflow simulator
- [ ] Tested on real Google Assistant device
- [ ] Response time acceptable (< 10 seconds)
- [ ] Conversation context works (follow-up questions)
- [ ] Error handling works (try invalid requests)

---

## 🎤 Example Conversations

### Basic Question

```
You: "Hey Google, talk to my test app"
Google: "Hi! I'm your personal AI assistant powered by Granite. What would you like to know?"
You: "What is Kubernetes?"
AI: "Kubernetes is an open-source container orchestration platform..."
```

### Follow-up Questions (Context Maintained)

```
You: "Tell me about Docker"
AI: "Docker is a platform for developing, shipping, and running applications in containers..."
You: "How does it compare to virtual machines?"
AI: "Docker containers are lighter than VMs because they share the host OS kernel..."
```

### Complex Query

```
You: "Explain how microservices architecture works"
AI: "Microservices architecture is a design pattern where applications are structured as a collection of loosely coupled services..."
```

---

## 🚀 Next Steps After Setup

1. **Customize System Prompt** - Edit `app/litellm_client.py` to change AI personality
2. **Add More Intents** - Create specific intents for common queries
3. **Improve Voice Optimization** - Fine-tune response formatting in `app/webhook.py`
4. **Add Context Management** - Enhance conversation memory
5. **Monitor Usage** - Set up Grafana dashboards
6. **Production Deployment** - Submit for public release (optional)

---

## 📚 Resources

- **Dialogflow Documentation:** https://cloud.google.com/dialogflow/docs
- **Actions Console:** https://console.actions.google.com/
- **Webhook Format:** https://cloud.google.com/dialogflow/es/docs/fulfillment-webhook
- **Voice Design Best Practices:** https://developers.google.com/assistant/conversational/design

---

**Ready to talk to your AI?** Follow the steps above and you'll be having conversations in ~30 minutes! 🎉


