# AWS Lightsail Docker Infrastructure Update Strategy

## Current Infrastructure Status ✅

- **Web Server (port 80)**: ✅ nginx serving HTML
- **Auth Service (port 8002)**: ✅ FastAPI with PostgreSQL
- **Transcription Service (port 8000)**: ✅ Working 
- **Analysis Service (port 8001)**: ✅ Working
- **Issue**: SSH port 22 timeout preventing direct file updates

## Deployment Solutions (No SSH Required)

### 1. **HTTP-Based File Deployment** (Recommended)

Create an update endpoint on the web server to receive new files:

```bash
# Test if the server has an update endpoint
curl -X POST http://3.38.107.23/admin/update-content \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: your-admin-key" \
  -d '{"file": "index.html", "content": "base64-encoded-content"}'
```

### 2. **Container Volume Update** (Advanced)

If using Docker volumes, create an update container:

```yaml
# Add to docker-compose.yml
services:
  file_updater:
    image: alpine/curl
    volumes:
      - web_content:/web_content
      - ./updates:/updates
    command: |
      sh -c "
        while true; do
          if [ -f /updates/index.html ]; then
            cp /updates/index.html /web_content/index.html
            echo 'Updated at $(date)'
            rm /updates/index.html
          fi
          sleep 30
        done
      "
```

### 3. **AWS Lightsail Console Deployment**

1. **Access Lightsail Console**: https://lightsail.aws.amazon.com/
2. **Connect via Browser Terminal**: Use the built-in browser SSH
3. **Container Management**: Access Docker containers directly

### 4. **Alternative SSH Ports**

Test if SSH is available on non-standard ports:

```bash
# Test common alternative SSH ports
for port in 2222 2200 22222; do
  echo "Testing port $port..."
  ssh -i teaching_analize.pem -p $port -o ConnectTimeout=5 ubuntu@3.38.107.23 "echo 'Connected on port $port'" 2>/dev/null && echo "SUCCESS: Port $port works" || echo "FAILED: Port $port"
done
```

## Immediate Deployment Steps

### Step 1: Deploy Updated HTML File

Create an update script that doesn't require SSH:

```bash
#!/bin/bash
# update-web-content.sh

LIGHTSAIL_IP="3.38.107.23"
HTML_FILE="authenticated-dashboard.html"

# Method 1: Try HTTP update endpoint
echo "Trying HTTP update..."
if curl -f -X POST "http://$LIGHTSAIL_IP/admin/update" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@$HTML_FILE" \
  -F "target=index.html"; then
  echo "✅ HTTP update successful"
  exit 0
fi

# Method 2: Try Docker exec if container is accessible
echo "Trying Docker container update..."
if docker -H "tcp://$LIGHTSAIL_IP:2376" exec nginx_container \
  sh -c "curl -o /usr/share/nginx/html/index.html http://host.docker.internal:8080/index.html"; then
  echo "✅ Docker update successful"
  exit 0
fi

# Method 3: Use AWS Lightsail API (requires AWS CLI)
echo "Trying AWS Lightsail API..."
aws lightsail put-instance-port-states \
  --instance-name your-instance-name \
  --port-infos fromPort=22,toPort=22,protocol=tcp,cidrListAliases=0.0.0.0/0

echo "❌ All update methods failed. Manual intervention required."
```

### Step 2: Implement Workflow API Integration

Update the HTML file's JavaScript to connect to the workflow service:

```javascript
// Update API endpoints in the HTML
const API_ENDPOINTS = {
    auth: `${API_BASE}:8002/auth`,
    workflow: `${API_BASE}:8003/api/workflow`,  // New workflow service
    transcribe: `${API_BASE}:8000/api/transcribe`,
    analyze: `${API_BASE}:8001/api/analyze`
};
```

### Step 3: Deploy Workflow Service Container

Create the workflow service Dockerfile:

```dockerfile
# services/workflow/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8003

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8003/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
```

## Monitoring and Health Checks

### Container Health Monitoring

```bash
# Check all service health
for port in 80 8000 8001 8002 8003; do
  echo "Checking port $port..."
  curl -s -o /dev/null -w "%{http_code}" "http://3.38.107.23:$port/health" || echo "FAILED"
done
```

### Real-time Log Monitoring

```bash
# If Docker remote API is enabled
docker -H "tcp://3.38.107.23:2376" logs -f container_name
```

## Security Considerations

### 1. **Secure Update Endpoint**

```python
# Add to nginx container or create update service
@app.post("/admin/update-content")
async def update_content(
    file: UploadFile,
    admin_key: str = Header(..., alias="X-Admin-Key")
):
    if admin_key != os.getenv("ADMIN_UPDATE_KEY"):
        raise HTTPException(401, "Invalid admin key")
    
    # Validate file type and content
    if file.filename != "index.html":
        raise HTTPException(400, "Only index.html updates allowed")
    
    # Update file safely
    content = await file.read()
    with open("/usr/share/nginx/html/index.html", "wb") as f:
        f.write(content)
    
    return {"status": "updated", "file": file.filename}
```

### 2. **Network Security Rules**

```bash
# AWS Lightsail firewall rules to check
aws lightsail get-instance-port-states --instance-name your-instance

# Add SSH port if needed
aws lightsail put-instance-port-states \
  --instance-name your-instance \
  --port-infos fromPort=22,toPort=22,protocol=tcp,accessDirection=inbound,accessType=restricted,accessFrom=yourip/32
```

## Infrastructure Optimization

### 1. **Resource Monitoring**

```bash
# Check resource usage via HTTP endpoints
curl "http://3.38.107.23:8002/admin/system-stats"
```

### 2. **Backup Strategy**

```yaml
# Add to docker-compose.yml
services:
  backup:
    image: alpine
    volumes:
      - web_content:/backup/web
      - postgres_data:/backup/db
    command: |
      sh -c "
        tar -czf /backup/web_$(date +%Y%m%d_%H%M%S).tar.gz /backup/web
        tar -czf /backup/db_$(date +%Y%m%d_%H%M%S).tar.gz /backup/db
      "
    restart: "no"
```

### 3. **Automated Health Checks**

```bash
#!/bin/bash
# health-monitor.sh - Run from local machine

SERVICES=(
  "80:/health"
  "8000:/health" 
  "8001:/health"
  "8002:/health"
  "8003:/health"
)

for service in "${SERVICES[@]}"; do
  port=$(echo $service | cut -d: -f1)
  endpoint=$(echo $service | cut -d: -f2)
  
  status=$(curl -s -o /dev/null -w "%{http_code}" "http://3.38.107.23:$port$endpoint")
  if [ "$status" = "200" ]; then
    echo "✅ Service on port $port is healthy"
  else
    echo "❌ Service on port $port is unhealthy (status: $status)"
  fi
done
```

## Next Steps

1. **Immediate**: Try AWS Lightsail browser console SSH access
2. **Short-term**: Implement HTTP-based update endpoint
3. **Long-term**: Set up proper CI/CD pipeline with container registry

## Emergency Recovery

If all services fail:

1. **Lightsail Snapshot**: Create snapshot before changes
2. **Container Restart**: Restart containers via Lightsail console
3. **Port Reset**: Reset firewall rules via AWS console
4. **Instance Reboot**: Reboot entire Lightsail instance

## Contact Points

- **Lightsail Console**: https://lightsail.aws.amazon.com/
- **Docker Hub**: For updating container images
- **Local Development**: Keep working backup of all services