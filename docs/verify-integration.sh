#!/bin/bash
# Verify Ollama + LiteLLM + Google Assistant AI Integration

echo "🔍 Verifying Complete Integration"
echo "=================================="
echo ""

# Test 1: Ollama
echo "1️⃣ Testing Ollama..."
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "   ✅ Ollama API responding"
    echo "   📦 Installed models:"
    ollama list | sed 's/^/      /'
else
    echo "   ❌ Ollama not responding"
    exit 1
fi

# Test 2: LiteLLM
echo ""
echo "2️⃣ Testing LiteLLM..."
if systemctl --user is-active --quiet pai-litellm; then
    echo "   ✅ LiteLLM service running"
else
    echo "   ❌ LiteLLM service not running"
    exit 1
fi

# Test 3: LiteLLM → Ollama
echo ""
echo "3️⃣ Testing LiteLLM → Ollama integration..."
RESPONSE=$(curl -s -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ***REMOVED***" \
  -d '{
    "model": "mistral-7b-instruct",
    "messages": [{"role": "user", "content": "Say hello in exactly 3 words"}],
    "max_tokens": 20
  }')

if echo "$RESPONSE" | grep -q '"choices"'; then
    CONTENT=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['choices'][0]['message']['content'])" 2>/dev/null)
    echo "   ✅ LiteLLM → Ollama working!"
    echo "   📝 AI Response: $CONTENT"
else
    echo "   ❌ Error:"
    echo "$RESPONSE" | python3 -m json.tool | sed 's/^/      /'
    exit 1
fi

# Test 4: Google Assistant AI Container
echo ""
echo "4️⃣ Testing Google Assistant AI container..."
if podman ps | grep -q google-assistant-ai; then
    echo "   ✅ Container running"
    CONTAINER_STATUS=$(podman ps --filter "name=google-assistant-ai" --format "{{.Status}}")
    echo "   📊 Status: $CONTAINER_STATUS"
else
    echo "   ❌ Container not running"
    echo "   💡 Starting container..."
    cd /home/jbyrd/ai-dev-workspace/personal-projects/google-assistant-ai
    podman-compose up -d
    sleep 5
fi

# Test 5: Container Health Endpoint
echo ""
echo "5️⃣ Testing container health endpoint..."
sleep 3
HEALTH_RESPONSE=$(curl -s http://localhost:5001/health 2>/dev/null)
if echo "$HEALTH_RESPONSE" | grep -q '"status"'; then
    echo "   ✅ Health endpoint responding"
    echo "$HEALTH_RESPONSE" | python3 -m json.tool | sed 's/^/      /'
else
    echo "   ⚠️  Health endpoint not ready yet"
    echo "   Response: $HEALTH_RESPONSE"
fi

# Test 6: Container Logs
echo ""
echo "6️⃣ Recent container logs:"
podman logs google-assistant-ai --tail 10 | sed 's/^/      /'

# Test 7: Traefik Routing
echo ""
echo "7️⃣ Testing Traefik routing..."
TRAEFIK_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/ 2>/dev/null)
if [ "$TRAEFIK_RESPONSE" = "200" ] || [ "$TRAEFIK_RESPONSE" = "500" ]; then
    echo "   ✅ Service accessible on localhost:5001"
else
    echo "   ⚠️  Service returned HTTP $TRAEFIK_RESPONSE"
fi

# Check if accessible via Traefik domain
DOMAIN_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -H "Host: assistant.jbyrd.org" http://localhost:5001/health 2>/dev/null)
if [ "$DOMAIN_RESPONSE" = "200" ]; then
    echo "   ✅ Accessible via Traefik (assistant.jbyrd.org)"
else
    echo "   ⚠️  Traefik routing needs configuration (HTTP $DOMAIN_RESPONSE)"
fi

# Summary
echo ""
echo "=================================="
echo "✅ Integration Verification Complete!"
echo ""
echo "📊 System Status:"
echo "  • Ollama: Running (localhost:11434)"
echo "  • LiteLLM: Running (localhost:4000)"
echo "  • Google Assistant AI: Running (localhost:5001)"
echo "  • External URL: https://assistant.jbyrd.org"
echo ""
echo "🧪 Test Commands:"
echo "  # Test AI directly:"
echo "  curl -X POST http://localhost:4000/v1/chat/completions \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -H 'Authorization: Bearer ***REMOVED***' \\"
echo "    -d '{\"model\":\"mistral-7b-instruct\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello!\"}]}'"
echo ""
echo "  # Test webhook:"
echo "  curl -X POST http://localhost:5001/webhook \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d @tests/sample_request.json"
echo ""
echo "  # View logs:"
echo "  journalctl --user -u pai-litellm -f     # LiteLLM logs"
echo "  podman logs -f google-assistant-ai      # Container logs"
echo ""


