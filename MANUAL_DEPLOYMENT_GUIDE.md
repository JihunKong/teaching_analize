# Manual Deployment Guide for AWS Lightsail

## Current Infrastructure Status ✅

**All Docker services are running and healthy:**
- Web Server (port 80): ✅ nginx serving HTML
- Auth Service (port 8002): ✅ FastAPI with PostgreSQL (2 users in DB)
- Transcription Service (port 8000): ✅ Working
- Analysis Service (port 8001): ✅ Working

**Issue:** SSH port 22 timeout - requires manual deployment via Lightsail console

## 🚀 Quick Deployment Steps

### Step 1: Access AWS Lightsail Console

1. Go to: https://lightsail.aws.amazon.com/
2. Sign in to your AWS account
3. Select your instance (should show "Running" status)
4. Click **"Connect using SSH"** button (browser-based terminal)

### Step 2: Deploy Updated HTML File

In the Lightsail SSH terminal, run:

```bash
# Check current web content
sudo ls -la /usr/share/nginx/html/

# Check Docker containers
docker ps

# Identify web server container (likely nginx)
docker exec -it [nginx_container_name] ls -la /usr/share/nginx/html/
```

**Method A: Direct File Update (if accessible)**
```bash
# If you can access the file system directly:
sudo nano /usr/share/nginx/html/index.html
# Copy the content from authenticated-dashboard.html and paste it
```

**Method B: Container Update (recommended)**
```bash
# Find the web server container
docker ps | grep nginx

# Copy updated HTML content into container
docker exec -it [container_name] sh -c "cat > /usr/share/nginx/html/index.html << 'EOF'
[paste content from authenticated-dashboard.html here]
EOF"

# Or use docker cp if file exists on server
docker cp index.html [container_name]:/usr/share/nginx/html/index.html
```

### Step 3: Deploy Workflow Service

```bash
# Check if workflow service is running
curl -s http://localhost:8003/health || echo "Workflow service not running"

# If needed, create and run workflow container
cd /opt/aiboa  # or wherever your project is located

# Build workflow service image
docker build -t aiboa/workflow:latest services/workflow/

# Run workflow container
docker run -d \
  --name aiboa_workflow \
  --network bridge \
  -p 8003:8003 \
  -e TRANSCRIPTION_SERVICE_URL="http://127.0.0.1:8000" \
  -e ANALYSIS_SERVICE_URL="http://127.0.0.1:8001" \
  -e AUTH_SERVICE_URL="http://127.0.0.1:8002" \
  --restart unless-stopped \
  aiboa/workflow:latest

# Verify it's running
docker ps | grep workflow
curl http://localhost:8003/health
```

### Step 4: Update Nginx Configuration

```bash
# Backup current nginx config
sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup

# Add workflow service routing to nginx
sudo tee -a /etc/nginx/sites-available/default > /dev/null << 'EOF'

    # Workflow service proxy
    location /api/workflow/ {
        proxy_pass http://127.0.0.1:8003/api/workflow/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # WebSocket endpoint for real-time progress
    location /ws/ {
        proxy_pass http://127.0.0.1:8003;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
EOF

# Test nginx configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx
```

### Step 5: Verify Deployment

```bash
# Test all services
echo "Testing services..."
curl -s -o /dev/null -w "Web Server (80): %{http_code}\n" http://localhost/
curl -s -o /dev/null -w "Auth Service (8002): %{http_code}\n" http://localhost:8002/health
curl -s -o /dev/null -w "Transcription (8000): %{http_code}\n" http://localhost:8000/health
curl -s -o /dev/null -w "Analysis (8001): %{http_code}\n" http://localhost:8001/health
curl -s -o /dev/null -w "Workflow (8003): %{http_code}\n" http://localhost:8003/health

# Check if updated HTML is deployed (should contain favicon and workflow-form)
curl -s http://localhost/ | grep -c "favicon\|workflow-form" && echo "✅ HTML updated" || echo "❌ HTML not updated"

# Test workflow API endpoint
curl -s http://localhost/api/workflow/ | head -20
```

## 📋 Files to Deploy

### 1. Updated HTML File
**Source:** `/Users/jihunkong/teaching_analize/authenticated-dashboard.html`
**Target:** `/usr/share/nginx/html/index.html` (in container or host)

**Key features added:**
- Favicon to fix 404 errors
- Enhanced workflow form handler
- Real-time progress monitoring
- Improved security (removed hardcoded credentials)

### 2. Workflow Service
**Source:** `/Users/jihunkong/teaching_analize/services/workflow/`
**Action:** Build and deploy as Docker container on port 8003

### 3. Nginx Configuration
**Source:** `/Users/jihunkong/teaching_analize/nginx-with-update-endpoint.conf`
**Target:** `/etc/nginx/sites-available/default`

## 🔧 Infrastructure Optimization

### Container Management
```bash
# View all containers
docker ps -a

# View container logs
docker logs [container_name] --tail 50

# Restart containers if needed
docker restart [container_name]

# View container resource usage
docker stats
```

### Health Monitoring
```bash
# Create a simple health check script
cat > /opt/health-check.sh << 'EOF'
#!/bin/bash
echo "AIBOA Health Check - $(date)"
echo "========================="

services=(
  "80:Web Server"
  "8000:Transcription"
  "8001:Analysis" 
  "8002:Auth"
  "8003:Workflow"
)

for service in "${services[@]}"; do
  port=$(echo $service | cut -d: -f1)
  name=$(echo $service | cut -d: -f2)
  
  status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port/health" 2>/dev/null || echo "000")
  if [ "$status" = "200" ]; then
    echo "✅ $name (port $port): Healthy"
  else
    echo "❌ $name (port $port): Unhealthy ($status)"
  fi
done
EOF

chmod +x /opt/health-check.sh

# Run health check
/opt/health-check.sh
```

### Backup Strategy
```bash
# Backup current web content
sudo tar -czf /opt/backup_web_$(date +%Y%m%d_%H%M%S).tar.gz /usr/share/nginx/html/

# Backup nginx configuration
sudo cp /etc/nginx/sites-available/default /opt/backup_nginx_$(date +%Y%m%d_%H%M%S).conf

# Backup database (if using SQLite files)
docker exec [postgres_container] pg_dump -U postgres aiboa > /opt/backup_db_$(date +%Y%m%d_%H%M%S).sql
```

## 🚨 Troubleshooting

### If Services Don't Start
```bash
# Check Docker status
sudo systemctl status docker

# Check container logs
docker logs [container_name]

# Restart Docker service
sudo systemctl restart docker

# Rebuild and restart containers
docker-compose down
docker-compose up -d
```

### If Nginx Fails
```bash
# Test nginx config
sudo nginx -t

# View nginx error logs
sudo tail -f /var/log/nginx/error.log

# Restart nginx
sudo systemctl restart nginx
```

### If Workflow Service Fails
```bash
# Check if port 8003 is in use
sudo netstat -tlnp | grep 8003

# Check workflow container logs
docker logs aiboa_workflow

# Manually test workflow service
docker run -it --rm -p 8003:8003 aiboa/workflow:latest
```

## 📊 Testing the Complete Workflow

1. **Open Browser:** http://3.38.107.23/
2. **Login:** Use existing test credentials
3. **Test Workflow:**
   - Enter YouTube URL
   - Select analysis options
   - Click "분석 시작"
   - Monitor real-time progress

## 🔐 Security Notes

- Updated HTML removes hardcoded admin credentials
- Nginx configuration includes security headers
- Rate limiting is configured for all endpoints
- Consider implementing proper SSL/TLS certificates

## 📞 Emergency Recovery

If deployment breaks the system:

```bash
# Restore HTML backup
sudo cp /opt/backup_web_[timestamp].tar.gz /tmp/
sudo tar -xzf /tmp/backup_web_[timestamp].tar.gz -C /

# Restore nginx config
sudo cp /opt/backup_nginx_[timestamp].conf /etc/nginx/sites-available/default
sudo nginx -t && sudo systemctl reload nginx

# Restart all containers
docker restart $(docker ps -aq)
```

## 🎯 Success Criteria

✅ **Deployment Complete When:**
- All 5 services return HTTP 200 on health endpoints
- Updated HTML contains favicon and workflow-form elements
- Workflow API responds at `/api/workflow/`
- Real-time progress monitoring works
- No error messages in nginx logs

**Expected URLs:**
- Main App: http://3.38.107.23/
- API Health: http://3.38.107.23:8002/health
- Workflow API: http://3.38.107.23/api/workflow/

This manual deployment approach ensures all security fixes and workflow integration are properly deployed to your AWS Lightsail infrastructure.