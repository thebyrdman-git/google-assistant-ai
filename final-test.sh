#!/bin/bash
# Final Integration Test

echo "🎯 Final Integration Test"
echo "========================="
echo ""

# Wait for container to be ready
echo "⏳ Waiting for container to be fully ready..."
sleep 10

# Test 1: Health endpoint
echo "1️⃣ Testing health endpoint..."
HEALTH=$(curl -s http://localhost:5001/health)
echo "$HEALTH" | python3 -m json.tool 2>/dev/null || echo "$HEALTH"

# Test 2: Root endpoint
echo ""
echo "2️⃣ Testing root endpoint..."
curl -s http://localhost:5001/ | python3 -m json.tool

# Test 3: Complete Google Assistant flow
echo ""
echo "3️⃣ Testing complete Google Assistant webhook flow..."
echo "   Question: What is Kubernetes?"
echo ""

RESPONSE=$(curl -s -X POST http://localhost:5001/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "responseId": "test-response-123",
    "queryResult": {
      "queryText": "What is Kubernetes?",
      "languageCode": "en",
      "intent": {
        "name": "projects/test-project/agent/intents/ask-ai-intent",
        "displayName": "Ask AI"
      },
      "intentDetectionConfidence": 0.95,
      "parameters": {}
    },
    "originalDetectIntentRequest": {
      "source": "google"
    },
    "session": "projects/test-project/agent/sessions/test-session-123"
  }')

if echo "$RESPONSE" | grep -q "fulfillmentText"; then
    echo "   ✅ Webhook responded successfully!"
    echo ""
    echo "   📝 Full Response:"
    echo "$RESPONSE" | python3 -m json.tool
    echo ""
    echo "   🎤 Voice Response:"
    VOICE_RESPONSE=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('fulfillmentText', 'No response'))" 2>/dev/null)
    echo "   \"$VOICE_RESPONSE\""
else
    echo "   ❌ Error in webhook response:"
    echo "$RESPONSE" | python3 -m json.tool
fi

# Test 4: Check container logs for errors
echo ""
echo "4️⃣ Recent container activity:"
podman logs google-assistant-ai 2>&1 | tail -20

echo ""
echo "========================="
echo "🎉 Testing Complete!"
echo ""
echo "📊 System Ready:"
echo "  • Ollama: localhost:11434 (mistral-7b-instruct)"
echo "  • LiteLLM: localhost:4000"
echo "  • Google Assistant AI: localhost:5001"
echo "  • External: https://assistant.jbyrd.org"
echo ""


