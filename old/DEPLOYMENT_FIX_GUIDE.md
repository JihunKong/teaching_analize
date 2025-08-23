# AIBOA Frontend-Backend Communication Fix - Deployment Guide

## Critical Issue Resolved

**Problem**: Frontend could not communicate with backend services due to outdated server IP addresses in configuration files.

**Root Cause**: All configuration files were using the old server IP `3.38.107.23` instead of the new server IP `43.203.128.246`.

## Files Updated

### 1. Frontend Configuration
- **File**: `/frontend/next.config.js`
- **Changes**: Updated all API URLs to use new server IP (43.203.128.246)
- **Impact**: Fixed API proxy routing for transcription, analysis, auth, and workflow services

### 2. API Client Configuration
- **File**: `/frontend/src/lib/api.ts`  
- **Changes**: Updated default API endpoints to new server IP
- **Impact**: Fixed frontend API communication

### 3. Docker Compose Configuration
- **Files**: `/docker-compose.yml`, `/docker-compose.optimized.yml`
- **Changes**: 
  - Added missing transcription service
  - Updated service networking to use Docker service names
  - Updated CORS origins to include new server IP
  - Optimized inter-service communication

### 4. Environment Configuration
- **Files**: `.env.production`, deployment scripts
- **Changes**: Created production environment with proper service URLs

### 5. Test Configuration
- **File**: `/frontend/tests/global-setup.ts`
- **Changes**: Updated test base URL to new server IP

### 6. Deployment Scripts
- **Files**: `deploy.sh`, `/frontend/deploy-to-lightsail.sh`
- **Changes**: Updated server host IP addresses

## Deployment Steps

### Option 1: Quick Fix (Recommended)
```bash
# 1. Stop existing containers
docker-compose down

# 2. Use the optimized configuration
cp docker-compose.optimized.yml docker-compose.yml

# 3. Build and start with new configuration
docker-compose up --build -d

# 4. Verify all services are running
docker-compose ps
docker-compose logs -f
```

### Option 2: Environment-Based Deployment
```bash
# 1. Copy production environment
cp .env.production .env

# 2. Set your actual API keys
nano .env
# Update OPENAI_API_KEY, SOLAR_API_KEY, UPSTAGE_API_KEY

# 3. Deploy with environment file
docker-compose --env-file .env up --build -d
```

### Option 3: Manual Environment Variables
```bash
# Export required environment variables
export OPENAI_API_KEY="your_key_here"
export SOLAR_API_KEY="your_key_here" 
export UPSTAGE_API_KEY="your_key_here"

# Deploy
docker-compose up --build -d
```

## Service Communication Architecture

### Internal Communication (Docker Network)
- **Frontend → Transcription**: `http://transcription-service:8000`
- **Frontend → Analysis**: `http://analysis-service:8001`
- **Frontend → Auth**: `http://auth-service:8002`
- **Workflow → Services**: Uses Docker service names

### External Communication (Client-Side)
- **Browser → Transcription**: `http://43.203.128.246:8000`
- **Browser → Analysis**: `http://43.203.128.246:8001`
- **Browser → Auth**: `http://43.203.128.246:8002`

## Verification Steps

### 1. Container Health Check
```bash
# Check all containers are running
docker-compose ps

# Check container logs
docker-compose logs transcription-service
docker-compose logs analysis-service
docker-compose logs auth-service
docker-compose logs workflow-service
```

### 2. API Connectivity Test
```bash
# Test transcription service
curl http://43.203.128.246:8000/health

# Test analysis service  
curl http://43.203.128.246:8001/health

# Test auth service
curl http://43.203.128.246:8002/health

# Test workflow service
curl http://43.203.128.246:8003/health
```

### 3. Frontend Connectivity Test
```bash
# Test frontend is accessible
curl http://43.203.128.246:3000

# Check frontend API proxy
curl http://43.203.128.246:3000/api/health
```

### 4. Full Integration Test
```bash
cd frontend
npm run test:e2e:quick
```

## Network Configuration Details

### Docker Network: `aiboa_default`
- **Type**: Bridge network
- **Services**: All AIBOA services connected
- **Benefits**: 
  - Service discovery by name
  - Internal DNS resolution
  - Isolated network security

### Port Mappings
- **Frontend**: 3000 → 3000
- **Transcription**: 8000 → 8000
- **Analysis**: 8001 → 8001
- **Auth**: 8002 → 8002
- **Workflow**: 8003 → 8003
- **PostgreSQL**: 5432 → 5432
- **Redis**: 6379 → 6379

## CORS Configuration

All services now include the new server IP in CORS origins:
```
CORS_ORIGINS=http://localhost:3000,http://43.203.128.246,http://43.203.128.246:80,*
```

## Monitoring and Troubleshooting

### Common Issues
1. **Port conflicts**: Ensure ports 3000, 8000-8003, 5432, 6379 are available
2. **API key errors**: Set proper environment variables for external APIs
3. **Network connectivity**: Verify Docker network configuration

### Debug Commands
```bash
# Check Docker network
docker network ls
docker network inspect aiboa_default

# Check service discovery
docker exec aiboa_frontend ping transcription-service
docker exec aiboa_frontend ping analysis-service

# View service logs
docker-compose logs -f --tail=100
```

## Security Considerations

1. **API Keys**: Store in environment variables, not in code
2. **Network Security**: Services communicate over Docker bridge network
3. **CORS**: Configured to allow frontend domain access
4. **Health Checks**: All services have health monitoring enabled

## Performance Optimizations

1. **Service Networking**: Direct container-to-container communication
2. **Health Checks**: Automated service monitoring
3. **Resource Limits**: Can be added to docker-compose if needed
4. **Load Balancing**: Can be implemented with nginx reverse proxy

## Success Criteria

✅ All containers start successfully  
✅ All health checks pass  
✅ Frontend can proxy API requests  
✅ Inter-service communication works  
✅ External API access functional  
✅ CORS errors resolved  
✅ E2E tests pass  

The AIBOA platform should now have 100% functional frontend-backend communication with the new server infrastructure.