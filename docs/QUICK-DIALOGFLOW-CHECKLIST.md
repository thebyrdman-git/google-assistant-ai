# Quick Dialogflow Setup Checklist

**Time Required:** ~20-30 minutes

---

## ✅ Pre-Setup Verification

Before starting Dialogflow setup:

```bash
# 1. Verify webhook is accessible
curl https://assistant.jbyrd.org/health

# 2. Test webhook endpoint
curl -X POST https://assistant.jbyrd.org/webhook \
  -H "Content-Type: application/json" \
  -d '{"queryResult":{"queryText":"test"},"session":"test"}'

# 3. Check container is healthy
podman ps | grep google-assistant-ai
```

**Expected:** All commands return successful responses

---

## 📝 Dialogflow Setup (20 minutes)

### Step 1: Google Cloud Project (5 min)
- [ ] Go to https://console.cloud.google.com/
- [ ] Create project: **"Personal AI Assistant"**
- [ ] Enable **Dialogflow API**

### Step 2: Create Agent (2 min)
- [ ] Go to https://dialogflow.cloud.google.com/
- [ ] Create agent: **"Personal AI Assistant"**
- [ ] Language: English
- [ ] Timezone: America/New_York

### Step 3: Configure Webhook (2 min)
- [ ] Click **Fulfillment** in sidebar
- [ ] Enable **Webhook**
- [ ] URL: `https://assistant.jbyrd.org/webhook`
- [ ] Click **Save**
- [ ] Verify ✅ green checkmark appears

### Step 4: Enable Webhook for Intents (5 min)

**Default Welcome Intent:**
- [ ] Click **Intents** → **Default Welcome Intent**
- [ ] Scroll to **Fulfillment** section
- [ ] Enable **"Enable webhook call for this intent"**
- [ ] Click **Save**

**Default Fallback Intent:**
- [ ] Click **Default Fallback Intent**
- [ ] Enable webhook in **Fulfillment**
- [ ] Click **Save**

**Create "Ask AI" Intent:**
- [ ] Click **Create Intent**
- [ ] Name: `Ask AI`
- [ ] Add training phrases:
  ```
  What is Kubernetes?
  Explain Docker
  Tell me about AI
  How does Python work?
  What are microservices?
  ```
- [ ] Enable webhook in **Fulfillment**
- [ ] Click **Save**

### Step 5: Test in Simulator (5 min)
- [ ] Click **"Try it now"** (right panel)
- [ ] Type: `What is Kubernetes?`
- [ ] Verify AI response appears
- [ ] Check **Diagnostic Info** tab shows webhook call
- [ ] Try 2-3 more questions

---

## 🎤 Test on Device (5 minutes)

### Enable Device Testing
- [ ] Click **Integrations** → **Google Assistant**
- [ ] Click **Test** button
- [ ] In Actions Console, go to **Test** tab
- [ ] Enable **On device** testing

### Try It Out
On your phone/Google Home:

```
You: "Hey Google, talk to my test app"
Google: Opens your agent
You: "What is Kubernetes?"
AI: [Response from Mistral 7B]
```

---

## 🐛 If Something Doesn't Work

### Webhook Not Connecting
```bash
# Check external accessibility
curl https://assistant.jbyrd.org/health

# From phone (mobile data, not WiFi):
# Visit https://assistant.jbyrd.org/health in browser
```

### AI Not Responding
```bash
# Check container logs
podman logs google-assistant-ai --tail 30

# Verify LiteLLM is working
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer ***REMOVED***" \
  -H "Content-Type: application/json" \
  -d '{"model":"mistral-7b-instruct","messages":[{"role":"user","content":"hi"}]}'
```

### Slow Responses (> 10 seconds)
```bash
# Pre-warm Ollama model
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer ***REMOVED***" \
  -H "Content-Type: application/json" \
  -d '{"model":"mistral-7b-instruct","messages":[{"role":"user","content":"hi"}],"max_tokens":5}'
```

---

## ✅ Success Criteria

You're done when:

- ✅ Can talk to AI via Google Assistant
- ✅ AI responds with relevant answers
- ✅ Response time < 10 seconds
- ✅ Follow-up questions work (context maintained)
- ✅ Works on phone and/or Google Home

---

## 🎉 You're Live!

Once everything works, try these:

```
"What is machine learning?"
"Explain microservices"
"Tell me about Docker containers"
"How does Kubernetes work?"
"What are the benefits of cloud computing?"
```

---

**Questions? Issues?** Check the full guide: [DIALOGFLOW-SETUP.md](DIALOGFLOW-SETUP.md)


