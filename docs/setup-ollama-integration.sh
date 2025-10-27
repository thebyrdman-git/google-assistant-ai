#!/bin/bash
# Setup Ollama Integration with LiteLLM and Google Assistant AI
# Run this script to complete the Ollama setup

set -e

echo "🎯 Setting up Ollama Integration..."
echo ""

# 1. Check Ollama is running
echo "1️⃣ Checking Ollama status..."
if systemctl is-active --quiet ollama; then
    echo "   ✅ Ollama is running"
else
    echo "   ❌ Ollama is not running"
    echo "   Starting Ollama..."
    sudo systemctl start ollama
    sleep 2
fi

# 2. List installed models
echo ""
echo "2️⃣ Installed Ollama models:"
ollama list

# 3. Test Ollama API
echo ""
echo "3️⃣ Testing Ollama API..."
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "   ✅ Ollama API is responding"
else
    echo "   ❌ Ollama API not responding"
    exit 1
fi

# 4. Backup existing LiteLLM config
echo ""
echo "4️⃣ Backing up LiteLLM config..."
cp ~/.config/litellm/config.yaml ~/.config/litellm/config.yaml.backup-$(date +%Y%m%d-%H%M%S)
echo "   ✅ Backup created"

# 5. Install new LiteLLM config
echo ""
echo "5️⃣ Installing new LiteLLM config with Ollama models..."
cp /home/jbyrd/ai-dev-workspace/personal-projects/google-assistant-ai/docs/OLLAMA-LITELLM-CONFIG.yaml \
   ~/.config/litellm/config.yaml
echo "   ✅ Config installed"

# 6. Restart LiteLLM service
echo ""
echo "6️⃣ Restarting LiteLLM service..."
systemctl --user restart pai-litellm
sleep 3

if systemctl --user is-active --quiet pai-litellm; then
    echo "   ✅ LiteLLM restarted successfully"
else
    echo "   ❌ LiteLLM failed to start"
    echo "   Checking logs..."
    journalctl --user -u pai-litellm -n 20 --no-pager
    exit 1
fi

# 7. Test LiteLLM with Ollama model
echo ""
echo "7️⃣ Testing LiteLLM → Ollama integration..."
RESPONSE=$(curl -s -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-pai-hatter-red-hat-ai-models-2025" \
  -d '{
    "model": "mistral-7b-instruct",
    "messages": [{"role": "user", "content": "Say hello in exactly 3 words"}],
    "max_tokens": 20
  }')

if echo "$RESPONSE" | grep -q "error"; then
    echo "   ❌ Error testing LiteLLM:"
    echo "$RESPONSE" | python3 -m json.tool
    exit 1
else
    echo "   ✅ LiteLLM → Ollama working!"
    echo "   Response: $(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['choices'][0]['message']['content'])")"
fi

# 8. Update Google Assistant AI container environment
echo ""
echo "8️⃣ Updating Google Assistant AI configuration..."
cd /home/jbyrd/ai-dev-workspace/personal-projects/google-assistant-ai

# Update docker-compose environment
sed -i 's/LITELLM_MODEL=.*/LITELLM_MODEL=mistral-7b-instruct/' docker-compose.yml
echo "   ✅ Updated docker-compose.yml to use mistral-7b-instruct"

# 9. Rebuild and restart container
echo ""
echo "9️⃣ Rebuilding and restarting Google Assistant AI container..."
podman-compose down
podman build -t google-assistant-ai:latest .
podman-compose up -d

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "📊 Summary:"
echo "  • Ollama: Running on localhost:11434"
echo "  • LiteLLM: Running on localhost:4000"
echo "  • Models: mistral-7b-instruct (default), phi3-mini, llama3.2-3b"
echo "  • Google Assistant AI: Running in container"
echo ""
echo "🧪 Test the integration:"
echo "  curl http://localhost:5001/health"
echo ""
echo "📝 View logs:"
echo "  journalctl --user -u pai-litellm -f     # LiteLLM"
echo "  podman logs -f google-assistant-ai      # Assistant"
echo ""


