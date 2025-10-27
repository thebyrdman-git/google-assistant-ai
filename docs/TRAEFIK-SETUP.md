# Traefik Integration Setup

Complete guide to deploying Google Assistant AI behind Traefik on MiracleMax.

---

## 🎯 Overview

This service will be accessible at:
- **External**: https://assistant.jbyrd.org
- **Internal**: http://google-assistant-ai:5001

---

## 📋 Prerequisites

### 1. Traefik Running on MiracleMax
```bash
# Check Traefik status
podman ps | grep traefik

# Verify traefik-net network exists
podman network ls | grep traefik-net
```

### 2. DNS Configuration
Ensure `assistant.jbyrd.org` points to your external IP:
```bash
# Check current DNS
dig +short assistant.jbyrd.org

# Should return your public IP (managed by Cloudflare)
```

### 3. Cloudflare SSL Certificate Resolver
Verify Traefik is configured with Cloudflare cert resolver:
```bash
# Check Traefik config
cat /home/jbyrd/pai/miraclemax-infrastructure/config/traefik/traefik.yml | grep cloudflare
```

---

## 🚀 Deployment Steps

### 1. Build Container Image

```bash
cd /home/jbyrd/ai-dev-workspace/personal-projects/google-assistant-ai

# Build the image
podman build -t google-assistant-ai:latest .

# Verify build
podman images | grep google-assistant-ai
```

### 2. Deploy with Docker Compose

```bash
# Ensure traefik-net exists (create if needed)
podman network ls | grep traefik-net || \
  podman network create traefik-net

# Start the service
podman-compose up -d

# Check status
podman-compose ps
```

### 3. Verify Container Health

```bash
# Check container status
podman ps | grep google-assistant-ai

# Check logs
podman logs google-assistant-ai --tail 50

# Test health endpoint (internal)
podman exec google-assistant-ai curl -f http://localhost:5001/health
```

### 4. Test Traefik Routing

```bash
# Test from MiracleMax (internal)
curl -k https://assistant.jbyrd.org/health

# Test from laptop (external - requires router port forwarding)
curl https://assistant.jbyrd.org/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "google-assistant-ai",
  "litellm": "connected"
}
```

---

## 🔧 Traefik Configuration Details

### Labels Applied to Container

```yaml
# Enable Traefik
traefik.enable=true

# HTTP Router
traefik.http.routers.assistant.rule=Host(`assistant.jbyrd.org`)
traefik.http.routers.assistant.entrypoints=websecure
traefik.http.routers.assistant.tls=true
traefik.http.routers.assistant.tls.certresolver=cloudflare

# Service
traefik.http.services.assistant.loadbalancer.server.port=5001
traefik.http.services.assistant.loadbalancer.healthcheck.path=/health
traefik.http.services.assistant.loadbalancer.healthcheck.interval=30s
```

### What This Does

1. **Host-based routing**: Requests to `assistant.jbyrd.org` → this service
2. **Automatic SSL**: Cloudflare cert resolver handles certificates
3. **Health checks**: Traefik monitors `/health` endpoint
4. **Load balancing**: Ready for multiple replicas if needed

---

## 🔐 Security Features

### 1. Non-Root Container
- Runs as user `assistant` (UID 1000)
- Limited permissions inside container

### 2. Resource Limits
- CPU: 1 core max, 0.5 core reserved
- Memory: 512MB max, 256MB reserved

### 3. Security Headers
```yaml
X-Robots-Tag: noindex,nofollow  # Don't index in search engines
SSL-Redirect: true              # Force HTTPS
STS: 31536000                   # HTTP Strict Transport Security
```

### 4. Network Isolation
- Only accessible via Traefik network
- No direct external access
- LiteLLM communication via host network

---

## 📊 Monitoring

### View Logs
```bash
# Real-time logs
podman logs -f google-assistant-ai

# Last 100 lines
podman logs google-assistant-ai --tail 100

# Logs from last hour
podman logs google-assistant-ai --since 1h
```

### Check Metrics
```bash
# Prometheus metrics
curl -s http://192.168.1.34:5001/metrics | grep assistant

# Health status
watch -n 5 'curl -s http://192.168.1.34:5001/health | jq'
```

### Traefik Dashboard
Access Traefik dashboard to see routing:
```
http://miraclemax.local:8080/dashboard/
```

---

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs
podman logs google-assistant-ai

# Verify image built correctly
podman images | grep google-assistant-ai

# Test build manually
podman run --rm -it google-assistant-ai:latest /bin/bash
```

### Can't Reach via Traefik

```bash
# Verify container is on traefik-net
podman inspect google-assistant-ai | grep traefik-net

# Check Traefik can reach service
podman exec traefik ping google-assistant-ai

# Verify Traefik sees the service
curl http://localhost:8080/api/http/services | jq | grep assistant
```

### SSL Certificate Issues

```bash
# Check cert resolver in Traefik config
cat /home/jbyrd/pai/miraclemax-infrastructure/config/traefik/traefik.yml

# Verify Cloudflare DNS
dig assistant.jbyrd.org

# Check certificate
openssl s_client -connect assistant.jbyrd.org:443 -servername assistant.jbyrd.org
```

### LiteLLM Connection Failed

```bash
# Verify LiteLLM is accessible from container
podman exec google-assistant-ai curl http://192.168.1.34:4000/v1/models \
  -H "Authorization: Bearer ***REMOVED***"

# Check if LiteLLM service is running
systemctl --user status pai-litellm
```

---

## 🔄 Updates and Maintenance

### Update Container

```bash
cd /home/jbyrd/ai-dev-workspace/personal-projects/google-assistant-ai

# Pull latest code
git pull

# Rebuild image
podman build -t google-assistant-ai:latest .

# Restart service
podman-compose down
podman-compose up -d
```

### View Container Stats

```bash
# Resource usage
podman stats google-assistant-ai

# Container info
podman inspect google-assistant-ai
```

---

## ✅ Verification Checklist

Before considering deployment complete:

- [ ] Container builds successfully
- [ ] Container starts and stays healthy
- [ ] Health endpoint returns 200 OK
- [ ] Service accessible at `https://assistant.jbyrd.org/health`
- [ ] SSL certificate is valid
- [ ] Logs show no errors
- [ ] LiteLLM connection working
- [ ] Metrics endpoint accessible
- [ ] Service auto-restarts on failure

---

## 📁 File Locations

| File | Location |
|------|----------|
| Docker Compose | `/home/jbyrd/ai-dev-workspace/personal-projects/google-assistant-ai/docker-compose.yml` |
| Dockerfile | `/home/jbyrd/ai-dev-workspace/personal-projects/google-assistant-ai/Dockerfile` |
| Traefik Config | `/home/jbyrd/pai/miraclemax-infrastructure/config/traefik/traefik.yml` |
| Container Logs | `podman logs google-assistant-ai` |

---

## 🎯 Next Steps

After Traefik integration is working:

1. **Test externally** - Access from phone/laptop outside network
2. **Google Actions setup** - Configure Dialogflow webhook URL
3. **Monitoring integration** - Add to Grafana dashboards
4. **Alerting** - Set up failure notifications
5. **Production testing** - Test with real Google Assistant

---

**Status**: Ready for deployment  
**External URL**: https://assistant.jbyrd.org  
**Self-Healing**: ✅ Automatic restart on failure


