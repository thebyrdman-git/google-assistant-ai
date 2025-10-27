#!/bin/bash
# Commit all Ollama integration changes

cd /home/jbyrd/ai-dev-workspace/personal-projects/google-assistant-ai

echo "📝 Committing changes..."
git add -A

git commit -m "feat: Ollama integration with local models

- Add Ollama local model support via LiteLLM
- Configure mistral-7b-instruct as default model
- Update docker-compose to use local Ollama models
- Add httpx version pinning for OpenAI compatibility
- Improve health check to be non-blocking
- Add comprehensive setup and testing scripts
- Update Docker to use Flask directly (simpler than gunicorn)
- Add Traefik integration for assistant.jbyrd.org

Ollama models available:
- mistral-7b-instruct (default, 8192 token context)
- phi3-mini (lightweight)
- llama3.2-3b (balanced)

System now runs completely locally with no external API dependencies.
Self-healing with automatic restart on failure."

echo ""
echo "🚀 Pushing to GitHub..."
git push origin master

echo ""
echo "✅ Done!"
git log --oneline -5


