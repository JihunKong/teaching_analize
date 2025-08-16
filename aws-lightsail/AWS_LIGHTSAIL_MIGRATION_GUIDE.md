# AWS Lightsail Migration Guide for AIBOA

## Overview

This guide provides step-by-step instructions for migrating AIBOA from Railway to AWS Lightsail to resolve YouTube access restrictions and improve platform capabilities.

## Prerequisites

### Required Accounts & Tools
- [ ] AWS Account with billing set up
- [ ] Docker Desktop installed
- [ ] AWS CLI installed and configured
- [ ] Domain registrar access (if using custom domain)

### Required API Keys
- [ ] OpenAI API Key (for Whisper transcription)
- [ ] Solar/Upstage API Key (for Korean LLM analysis)
- [ ] YouTube Data API v3 Key (optional, for enhanced YouTube access)

## Phase 1: Local Environment Setup

### Step 1: Docker Environment Preparation

1. **Create Docker Compose Configuration**
   ```bash
   cd /Users/jihunkong/teaching_analize
   ```

2. **Create `docker-compose.yml`**:
   ```yaml
   version: '3.8'
   
   services:
     transcription:
       build: 
         context: ./services/transcription
         dockerfile: Dockerfile
       ports:
         - "8000:8000"
       environment:
         - OPENAI_API_KEY=${OPENAI_API_KEY}
         - DATABASE_URL=postgresql://postgres:password@postgres:5432/aiboa
         - REDIS_URL=redis://redis:6379
       depends_on:
         - postgres
         - redis
   
     analysis:
       build:
         context: ./services/analysis
         dockerfile: Dockerfile
       ports:
         - "8001:8001"  
       environment:
         - SOLAR_API_KEY=${SOLAR_API_KEY}
         - DATABASE_URL=postgresql://postgres:password@postgres:5432/aiboa
         - REDIS_URL=redis://redis:6379
       depends_on:
         - postgres
         - redis
   
     frontend:
       build:
         context: ./frontend
         dockerfile: Dockerfile
       ports:
         - "8501:8501"
       environment:
         - TRANSCRIPTION_API_URL=http://transcription:8000
         - ANALYSIS_API_URL=http://analysis:8001
       depends_on:
         - transcription
         - analysis
   
     postgres:
       image: postgres:15
       environment:
         - POSTGRES_DB=aiboa
         - POSTGRES_USER=postgres
         - POSTGRES_PASSWORD=password
       volumes:
         - postgres_data:/var/lib/postgresql/data
         - ./migrations:/docker-entrypoint-initdb.d
       ports:
         - "5432:5432"
   
     redis:
       image: redis:7-alpine
       ports:
         - "6379:6379"
   
   volumes:
     postgres_data:
   ```

3. **Update Service Dockerfiles**

   **Transcription Service Dockerfile** (`services/transcription/Dockerfile`):
   ```dockerfile
   FROM python:3.11-slim
   
   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       ffmpeg \
       && rm -rf /var/lib/apt/lists/*
   
   WORKDIR /app
   
   # Copy requirements and install Python dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   # Copy application code
   COPY . .
   
   # Create uploads directory
   RUN mkdir -p /app/uploads
   
   EXPOSE 8000
   
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

   **Analysis Service Dockerfile** (`services/analysis/Dockerfile`):
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   # Copy requirements and install dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   # Copy application code
   COPY . .
   
   EXPOSE 8001
   
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
   ```

   **Frontend Dockerfile** (`frontend/Dockerfile`):
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   # Copy requirements and install dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   # Copy application code
   COPY . .
   
   EXPOSE 8501
   
   HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
   
   CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

### Step 2: Local Testing

1. **Create Environment File** (`.env`):
   ```bash
   # API Keys
   OPENAI_API_KEY=your_openai_key_here
   SOLAR_API_KEY=your_solar_key_here
   UPSTAGE_API_KEY=your_upstage_key_here
   
   # Database
   DATABASE_URL=postgresql://postgres:password@postgres:5432/aiboa
   REDIS_URL=redis://redis:6379
   
   # Security
   API_SECRET_KEY=your_secret_key_here
   ```

2. **Start Local Environment**:
   ```bash
   docker-compose up --build
   ```

3. **Test Services**:
   ```bash
   # Test transcription service
   curl http://localhost:8000/health
   
   # Test analysis service  
   curl http://localhost:8001/health
   
   # Test frontend
   open http://localhost:8501
   ```

4. **Test YouTube Access**:
   ```bash
   # Test YouTube transcription
   curl -X POST http://localhost:8000/api/transcribe/youtube \
     -H "X-API-Key: test-api-key" \
     -H "Content-Type: application/json" \
     -d '{"youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "language": "en"}'
   ```

## Phase 2: AWS Lightsail Setup

### Step 1: Create Lightsail Container Service

1. **Login to AWS Lightsail Console**
   - Navigate to https://lightsail.aws.amazon.com
   - Create container service

2. **Container Service Configuration**:
   - **Service name**: `aiboa-production`
   - **Power**: Small (1 GB RAM, 0.25 vCPUs) - can scale up later
   - **Scale**: 1 node initially
   - **Region**: Choose based on your target audience location

### Step 2: Create Database

1. **Create Lightsail Database**:
   - **Database engine**: PostgreSQL
   - **Blueprint**: PostgreSQL 15
   - **Instance plan**: $15/month (1 GB RAM, 1 vCPU, 40 GB SSD)
   - **Database name**: `aiboa-db`
   - **Master username**: `aiboa`
   - **Master password**: Generate secure password

2. **Database Configuration**:
   ```sql
   -- Connect to database and create application database
   CREATE DATABASE aiboa;
   CREATE USER aiboa_app WITH PASSWORD 'secure_app_password';
   GRANT ALL PRIVILEGES ON DATABASE aiboa TO aiboa_app;
   ```

### Step 3: Create Redis Instance

1. **Launch Redis Instance**:
   - Use AWS ElastiCache or Lightsail-compatible Redis
   - **Instance type**: cache.t3.micro (for testing)
   - **Node type**: Single node
   - **Port**: 6379

### Step 4: Prepare Container Deployments

1. **Build and Push Images** (using AWS Lightsail container service):

   Create deployment configuration file (`lightsail-deployment.json`):
   ```json
   {
     "serviceName": "aiboa-production",
     "containers": {
       "transcription": {
         "image": "transcription:latest",
         "ports": {
           "8000": "HTTP"
         },
         "environment": {
           "OPENAI_API_KEY": "{{OPENAI_API_KEY}}",
           "DATABASE_URL": "{{DATABASE_URL}}",
           "REDIS_URL": "{{REDIS_URL}}",
           "API_SECRET_KEY": "{{API_SECRET_KEY}}"
         },
         "healthcheck": {
           "path": "/health",
           "intervalSeconds": 30,
           "timeoutSeconds": 10,
           "unhealthyThresholdCount": 3,
           "successCodes": "200"
         }
       },
       "analysis": {
         "image": "analysis:latest", 
         "ports": {
           "8001": "HTTP"
         },
         "environment": {
           "SOLAR_API_KEY": "{{SOLAR_API_KEY}}",
           "DATABASE_URL": "{{DATABASE_URL}}",
           "REDIS_URL": "{{REDIS_URL}}",
           "API_SECRET_KEY": "{{API_SECRET_KEY}}"
         },
         "healthcheck": {
           "path": "/health",
           "intervalSeconds": 30,
           "timeoutSeconds": 10,
           "unhealthyThresholdCount": 3,
           "successCodes": "200"
         }
       },
       "frontend": {
         "image": "frontend:latest",
         "ports": {
           "8501": "HTTP"
         },
         "environment": {
           "TRANSCRIPTION_API_URL": "https://aiboa-production.amazonaws.com",
           "ANALYSIS_API_URL": "https://aiboa-production.amazonaws.com",
           "API_SECRET_KEY": "{{API_SECRET_KEY}}"
         },
         "healthcheck": {
           "path": "/_stcore/health",
           "intervalSeconds": 30,
           "timeoutSeconds": 10,
           "unhealthyThresholdCount": 3,
           "successCodes": "200"
         }
       }
     },
     "publicEndpoint": {
       "containerName": "frontend",
       "containerPort": 8501,
       "healthcheck": {
         "path": "/",
         "intervalSeconds": 30,
         "timeoutSeconds": 10,
         "unhealthyThresholdCount": 3,
         "successCodes": "200"
       }
     }
   }
   ```

## Phase 3: Deployment Process

### Step 1: Deploy Services to AWS Lightsail

1. **Push Container Images**:
   ```bash
   # Build images locally
   docker build -t transcription services/transcription/
   docker build -t analysis services/analysis/
   docker build -t frontend frontend/
   
   # Tag for Lightsail
   aws lightsail push-container-image --service-name aiboa-production --label transcription --image transcription
   aws lightsail push-container-image --service-name aiboa-production --label analysis --image analysis  
   aws lightsail push-container-image --service-name aiboa-production --label frontend --image frontend
   ```

2. **Deploy Container Service**:
   ```bash
   aws lightsail create-container-service-deployment \
     --service-name aiboa-production \
     --cli-input-json file://lightsail-deployment.json
   ```

### Step 2: Database Migration

1. **Export Data from Railway**:
   ```bash
   # Export from SQLite (if using SQLite)
   sqlite3 production.db .dump > railway_data_export.sql
   
   # Or from PostgreSQL (if Railway uses PostgreSQL)
   pg_dump $RAILWAY_DATABASE_URL > railway_data_export.sql
   ```

2. **Import to Lightsail Database**:
   ```bash
   # Connect to Lightsail PostgreSQL
   psql -h your-lightsail-db-endpoint -U aiboa -d aiboa -f railway_data_export.sql
   ```

3. **Run Migrations**:
   ```bash
   # Run any pending migrations
   python migrate.py
   ```

### Step 3: Configuration and Testing

1. **Set Environment Variables**:
   ```bash
   # Set in Lightsail container service environment
   OPENAI_API_KEY=sk-...
   SOLAR_API_KEY=...
   DATABASE_URL=postgresql://aiboa_app:password@lightsail-db:5432/aiboa
   REDIS_URL=redis://lightsail-redis:6379
   API_SECRET_KEY=your-secure-secret
   ```

2. **Test Deployment**:
   ```bash
   # Health checks
   curl https://your-lightsail-url/health
   
   # API functionality
   curl -X POST https://your-lightsail-url/api/transcribe/youtube \
     -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"youtube_url": "https://www.youtube.com/watch?v=test", "language": "ko"}'
   ```

3. **YouTube Access Validation**:
   ```bash
   # Test YouTube caption extraction specifically
   curl -X POST https://your-lightsail-url/api/transcribe/youtube \
     -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "language": "en"}' \
     -v
   ```

## Phase 4: Production Migration

### Step 1: Domain and SSL Setup

1. **Configure Custom Domain** (Optional):
   ```bash
   # Create a custom domain in Lightsail
   aws lightsail create-domain --domain-name yourdomain.com
   
   # Create SSL certificate
   aws lightsail create-certificate --certificate-name aiboa-ssl --domain-name yourdomain.com
   ```

2. **Update DNS Records**:
   - Point your domain to Lightsail container service
   - Set up CNAME for www subdomain

### Step 2: Load Balancer Configuration

1. **Configure Load Balancer**:
   - Enable HTTPS/SSL termination
   - Set up health checks for all services
   - Configure routing rules:
     - `/api/transcribe/*` → Transcription service (port 8000)
     - `/api/analyze/*` → Analysis service (port 8001)  
     - `/*` → Frontend service (port 8501)

### Step 3: Monitoring and Alerting

1. **Set Up CloudWatch Integration**:
   ```bash
   # Enable container metrics
   aws lightsail put-container-log --service-name aiboa-production --enable
   ```

2. **Create Monitoring Dashboard**:
   - CPU and memory usage
   - Request counts and error rates
   - Response times
   - Database connection health
   - Redis queue metrics

3. **Set Up Alerts**:
   - High error rate (>5%)
   - High response time (>5 seconds)
   - Service unavailability
   - Database connection failures

## Phase 5: Validation and Optimization

### Step 1: Comprehensive Testing

1. **Functional Testing Checklist**:
   - [ ] File upload transcription
   - [ ] YouTube URL transcription  
   - [ ] Text analysis with CBIL classification
   - [ ] Statistics dashboard
   - [ ] API authentication
   - [ ] Error handling

2. **Performance Testing**:
   ```bash
   # Load testing with curl or ab
   ab -n 1000 -c 10 https://your-lightsail-url/api/health
   
   # YouTube access testing
   for i in {1..10}; do
     curl -X POST https://your-lightsail-url/api/transcribe/youtube \
       -H "X-API-Key: your-api-key" \
       -H "Content-Type: application/json" \
       -d '{"youtube_url": "https://www.youtube.com/watch?v=test", "language": "ko"}'
   done
   ```

### Step 2: Performance Optimization

1. **Container Optimization**:
   - Adjust container resources based on monitoring data
   - Optimize database queries and connections
   - Implement connection pooling

2. **Caching Strategy**:
   - Redis caching for frequent queries
   - CDN for static assets (if applicable)
   - Database query optimization

### Step 3: Backup and Recovery

1. **Database Backups**:
   ```bash
   # Automated daily backups
   aws lightsail create-relational-database-snapshot \
     --relational-database-name aiboa-db \
     --relational-database-snapshot-name aiboa-backup-$(date +%Y%m%d)
   ```

2. **Application State Backup**:
   - Container service configuration backup
   - Environment variables backup
   - SSL certificates backup

## Success Criteria & Validation

### Pre-Migration Validation
- [ ] All services running locally with Docker Compose
- [ ] Database migration scripts tested
- [ ] YouTube access working in test environment
- [ ] All API endpoints responding correctly

### Post-Migration Validation  
- [ ] All Railway functionality preserved
- [ ] YouTube caption extraction working (>95% success rate)
- [ ] API response times ≤ 2 seconds
- [ ] Frontend loading times ≤ 3 seconds
- [ ] No data loss during migration
- [ ] SSL certificates working
- [ ] Monitoring and alerting active

### Performance Benchmarks
- **Transcription**: ≤ 30 seconds for 5-minute audio file
- **Analysis**: ≤ 10 seconds for 1000-word text
- **YouTube Access**: ≤ 15 seconds for caption extraction
- **Database Queries**: ≤ 100ms average response time

## Troubleshooting Guide

### Common Issues and Solutions

1. **YouTube Access Still Blocked**:
   - Verify AWS Lightsail region (try different regions)
   - Implement proxy rotation if needed
   - Use YouTube Data API v3 as fallback

2. **Database Connection Issues**:
   - Check security group settings
   - Verify database endpoint and credentials
   - Test database connectivity from containers

3. **Container Startup Failures**:
   - Check container logs: `aws lightsail get-container-log`
   - Verify environment variables
   - Check resource allocation (CPU/memory)

4. **SSL/Domain Issues**:
   - Verify DNS propagation
   - Check SSL certificate status
   - Validate domain routing configuration

### Rollback Plan

If critical issues arise:

1. **Immediate Rollback**:
   - Keep Railway services running during migration
   - Switch DNS back to Railway endpoints
   - Communicate status to users

2. **Data Recovery**:
   - Restore from latest database backup
   - Re-import any data created during migration
   - Validate data integrity

## Cost Analysis

### AWS Lightsail Estimated Monthly Costs

- **Container Service**: $10-40/month (depending on scale)
- **PostgreSQL Database**: $15/month  
- **Redis Instance**: $10/month
- **Data Transfer**: $5-15/month
- **SSL Certificate**: Free with Lightsail

**Total Estimated**: $40-80/month vs Railway costs

### Cost Optimization Strategies

- Start with smaller instances and scale as needed
- Use spot instances for non-critical workloads
- Implement efficient caching to reduce API calls
- Monitor and optimize data transfer costs

## Support and Maintenance

### Documentation
- [ ] Updated API documentation
- [ ] Deployment runbooks
- [ ] Monitoring and alerting guides
- [ ] Backup and recovery procedures

### Knowledge Transfer
- [ ] Technical architecture overview
- [ ] Operational procedures
- [ ] Troubleshooting guides
- [ ] Cost optimization strategies

---

## Next Steps

1. **Immediate (This Week)**:
   - Set up local Docker development environment
   - Create AWS Lightsail account and test YouTube access

2. **Short-term (Next 2 Weeks)**:
   - Deploy services to AWS Lightsail
   - Migrate database and test functionality
   - Validate YouTube access restoration

3. **Medium-term (Next Month)**:
   - Complete production migration
   - Set up monitoring and optimization
   - Create documentation and training materials

**This migration will unlock AIBOA's full potential by solving the YouTube access limitation while maintaining all existing functionality and improving platform capabilities.**