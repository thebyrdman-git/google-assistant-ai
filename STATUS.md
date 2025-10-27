# AI Chat Gateway - Current Status

**Date:** 2025-10-27  
**Service:** AI Chat Gateway (Gemini + Local Models)

## ✅ What's Working

1. **Container Running**: Successfully built and deployed with Gunicorn
2. **Local Access**: Service accessible at `http://localhost:5002`
3. **Local Models (Mistral 7B)**: Working perfectly via LiteLLM/Ollama
4. **Endpoints Working Locally**:
   - `/health` - ✅ Returns service status
   - `/chat` - ✅ Returns AI responses from Mistral
   - `/metrics` - ✅ Prometheus metrics
   - `/webhook` - ✅ For future Google Assistant integration

## ⚠️ Known Issues

1. **Traefik Health Checks**: Intermittent timeouts causing "no available server" errors
   - Health checks work manually but fail in Traefik
   - Gunicorn workers occasionally timeout (need to investigate why)
   - Service marked as unhealthy by Docker healthcheck

2. **Public Access**: Inconsistent due to health check failures
   - `https://assistant.jbyrd.org/health` - Works sometimes
   - `https://assistant.jbyrd.org/chat` - Returns 503 when health check fails

## 🔧 Temporary Workaround

**Use localhost access for now:**

```bash
# Test health
curl http://localhost:5002/health

# Chat with Mistral (local model)
curl -X POST http://localhost:5002/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "mistral-7b-instruct",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 50
  }'
```

## 📝 Next Steps

### 1. Add Gemini API Key

To enable Google Gemini models:

1. Get API key from: https://aistudio.google.com/app/apikey
2. Add to environment:
   ```bash
   cd /home/jbyrd/ai-dev-workspace/personal-projects/google-assistant-ai
   
   # Create .env file
   echo "GEMINI_API_KEY=your-key-here" > .env
   
   # Restart container
   podman-compose down
   podman-compose up -d
   ```

3. Test Gemini:
   ```bash
   curl -X POST http://localhost:5002/chat \
     -H 'Content-Type: application/json' \
     -d '{
       "model": "gemini-1.5-flash",
       "messages": [{"role": "user", "content": "Hello from Gemini!"}],
       "max_tokens": 100
     }'
   ```

### 2. Fix Traefik Health Checks

Need to investigate:
- Why Gunicorn workers are timing out
- Increase health check timeout in Traefik config
- Consider disabling health checks temporarily

### 3. Production Hardening

- Add authentication middleware
- Set up proper logging aggregation
- Configure Prometheus alerting
- Add rate limiting

## 🏗️ Architecture

```
Internet → Cloudflare → Traefik (host:80/443) → localhost:5002 → Container (port 5001)
                                                                        ↓
                                                      ┌─────────────────┴──────────────────┐
                                                      │                                     │
                                                   Gemini API                        LiteLLM Proxy
                                                (Google Cloud)                    (localhost:4000)
                                                                                        ↓
                                                                                    Ollama
                                                                              (mistral, phi3, llama)
```

## 📊 Available Models

### Local Models (via LiteLLM/Ollama)
- `mistral-7b-instruct` - Fast, good quality
- `phi-3-mini` - Very fast, compact
- `llama3.2-3b` - Latest Llama, efficient

### Cloud Models (via Gemini API) - Requires API Key
- `gemini-1.5-flash` - Fast, cost-effective
- `gemini-1.5-pro` - Best quality, slower

## 🔐 Configuration Files

- **Service Config**: `docker-compose.yml`
- **Traefik Route**: `/home/jbyrd/miraclemax-infrastructure/config/traefik/dynamic/routes.yml`
- **Environment**: `.env` (create this with your GEMINI_API_KEY)
- **Requirements**: `requirements.txt`

## 📖 API Documentation

### Chat Endpoint

```bash
POST /chat
Content-Type: application/json

{
  "model": "gemini-1.5-flash" | "mistral-7b-instruct" | etc,
  "messages": [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.7,
  "max_tokens": 2048
}
```

**Response:**
```json
{
  "id": "chat-abc123",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "gemini-1.5-flash",
  "backend": "gemini",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Hello! How can I help you?"
    },
    "finish_reason": "stop"
  }]
}
```

## 💡 Usage Examples

### Python
```python
import requests

response = requests.post('http://localhost:5002/chat', json={
    'model': 'gemini-1.5-flash',
    'messages': [{'role': 'user', 'content': 'Explain quantum computing'}],
    'max_tokens': 200
})

print(response.json()['choices'][0]['message']['content'])
```

### cURL
```bash
# Local model
curl -X POST http://localhost:5002/chat \
  -H 'Content-Type: application/json' \
  -d '{"model":"mistral-7b-instruct","messages":[{"role":"user","content":"Hi"}]}'

# Gemini (after adding API key)
curl -X POST http://localhost:5002/chat \
  -H 'Content-Type: application/json' \
  -d '{"model":"gemini-1.5-flash","messages":[{"role":"user","content":"Hi"}]}'
```

---

**Service is functional locally. Public access pending Traefik health check fix.**

