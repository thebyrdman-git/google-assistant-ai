#!/bin/bash
# Diagnose Google Assistant AI Container Issues

echo "🔍 Diagnosing Container Issues"
echo "=============================="
echo ""

echo "1️⃣ Container Status:"
podman ps -a | grep google-assistant-ai

echo ""
echo "2️⃣ Container Logs (last 50 lines):"
podman logs google-assistant-ai 2>&1 | tail -50

echo ""
echo "3️⃣ Processes inside container:"
podman exec google-assistant-ai ps aux 2>/dev/null || echo "   ⚠️  Can't exec into container (might be crashed)"

echo ""
echo "4️⃣ Testing endpoints:"
echo "   Root endpoint:"
curl -s http://localhost:5001/ 2>&1 | head -5

echo ""
echo "   Health endpoint:"
curl -s http://localhost:5001/health 2>&1

echo ""
echo "   Webhook endpoint:"
curl -s http://localhost:5001/webhook 2>&1 | head -5

echo ""
echo "5️⃣ Container environment:"
podman exec google-assistant-ai env 2>/dev/null | grep -E "LITELLM|PORT|FLASK"

echo ""
echo "6️⃣ Check if Flask is listening:"
podman exec google-assistant-ai ss -tlnp 2>/dev/null | grep 5001 || echo "   ⚠️  Nothing listening on port 5001"

echo ""
echo "7️⃣ Restart container and watch startup:"
echo "   Restarting..."
podman restart google-assistant-ai
sleep 5
echo "   Logs after restart:"
podman logs google-assistant-ai 2>&1 | tail -20

echo ""
echo "Done!"


