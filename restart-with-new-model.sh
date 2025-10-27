#!/bin/bash
# Restart container with Ollama model

echo "🔄 Restarting Google Assistant AI with Ollama model..."

cd /home/jbyrd/ai-dev-workspace/personal-projects/google-assistant-ai

# Stop container
podman-compose down

# Start with new environment
podman-compose up -d

echo ""
echo "⏳ Waiting for container to start..."
sleep 8

echo ""
echo "📊 Container status:"
podman ps | grep google-assistant-ai

echo ""
echo "📝 Recent logs:"
podman logs google-assistant-ai 2>&1 | tail -15

echo ""
echo "🧪 Testing health endpoint..."
curl -s http://localhost:5001/health | python3 -m json.tool

echo ""
echo "✅ Done! Container should now be using mistral-7b-instruct"


