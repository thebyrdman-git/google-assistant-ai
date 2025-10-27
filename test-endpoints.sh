#!/bin/bash
# Test all Flask endpoints directly

echo "🧪 Testing Flask Endpoints"
echo "=========================="
echo ""

echo "1️⃣ Test root endpoint (/):"
curl -s http://localhost:5001/ 2>&1 | head -10

echo ""
echo "2️⃣ Test health endpoint (/health):"
curl -s http://localhost:5001/health 2>&1 | head -10

echo ""
echo "3️⃣ Test webhook endpoint (/webhook) - POST:"
curl -s -X POST http://localhost:5001/webhook \
  -H "Content-Type: application/json" \
  -d '{"queryResult":{"queryText":"test"},"session":"test"}' 2>&1 | head -10

echo ""
echo "4️⃣ Test metrics endpoint (/metrics):"
curl -s http://localhost:5001/metrics 2>&1 | head -10

echo ""
echo "5️⃣ Check what's actually running in container:"
podman exec google-assistant-ai ps aux

echo ""
echo "6️⃣ Check if Flask is listening:"
podman exec google-assistant-ai ss -tlnp | grep 5001 || echo "Nothing on port 5001"

echo ""
echo "7️⃣ Test from inside container:"
podman exec google-assistant-ai curl -s http://localhost:5001/ | head -5

echo ""
echo "8️⃣ Full container logs:"
podman logs google-assistant-ai 2>&1 | tail -30

echo ""
echo "Done!"


