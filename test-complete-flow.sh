#!/bin/bash
# Test Complete Google Assistant Flow

echo "🎤 Testing Complete Google Assistant Flow"
echo "=========================================="
echo ""

# Test with sample Google Assistant request
echo "📤 Sending Google Assistant webhook request..."
echo ""

RESPONSE=$(curl -s -X POST http://localhost:5001/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "responseId": "test-123",
    "queryResult": {
      "queryText": "What is Kubernetes?",
      "languageCode": "en",
      "intent": {
        "name": "projects/test/agent/intents/ask-ai",
        "displayName": "Ask AI"
      }
    },
    "session": "projects/test/agent/sessions/test-session-123"
  }')

echo "📥 Response:"
echo "$RESPONSE" | python3 -m json.tool

echo ""
echo "🎯 Extracted Answer:"
ANSWER=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('fulfillmentText', 'No response'))" 2>/dev/null)
echo "   $ANSWER"

echo ""
echo "✅ Test complete!"


