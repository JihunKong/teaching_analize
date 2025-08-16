# Railway Deployment Troubleshooting Guide

## Common Issues and Solutions

### 1. Nixpacks Build Failure

**Error**: "Nixpacks was unable to generate a build plan for this app"

**Cause**: Railway is trying to build from the wrong directory or can't detect the project type.

**Solution**:
1. Ensure the root directory is set correctly in Railway settings
2. For each service, set:
   - Transcription: `/services/transcription`
   - Analysis: `/services/analysis`
3. Make sure Dockerfile exists in each service directory
4. If Nixpacks still fails, explicitly set builder to DOCKERFILE in railway.toml

### 2. Service Not Starting

**Symptoms**: Build succeeds but service crashes immediately

**Check**:
```bash
railway logs --service [service-name] --tail 100
```

**Common Causes**:
- Missing environment variables
- Port mismatch (check PORT env var matches Dockerfile)
- Database connection failure

**Solutions**:
1. Verify all required environment variables are set
2. Check DATABASE_URL and REDIS_URL are correct
3. Ensure port binding uses $PORT variable

### 3. Database Connection Issues

**Error**: "could not connect to database"

**Solutions**:
1. Verify PostgreSQL service is running:
   ```bash
   railway logs --service postgres
   ```

2. Test connection:
   ```bash
   railway run psql $DATABASE_URL -c "SELECT 1"
   ```

3. Check connection string format:
   ```
   postgresql://user:password@host:port/database
   ```

### 4. Environment Variables Not Loading

**Symptoms**: Services can't find API keys or configuration

**Solutions**:
1. List all variables:
   ```bash
   railway variables --service [service-name]
   ```

2. Set missing variables:
   ```bash
   railway variables set KEY=value --service [service-name]
   ```

3. Restart service after setting variables:
   ```bash
   railway restart --service [service-name]
   ```

### 5. Build Takes Too Long or Times Out

**Solutions**:
1. Optimize Dockerfile with better layer caching
2. Use .dockerignore to exclude unnecessary files
3. Consider using smaller base images

### 6. Monorepo Not Detected

**Symptoms**: Railway builds from root instead of service directories

**Solutions**:
1. Use railway.json at root level
2. Set root directory manually in Railway dashboard
3. Create separate Railway services for each microservice

### 7. Port Binding Issues

**Error**: "bind: address already in use" or service not accessible

**Solutions**:
1. Use environment variable for port:
   ```python
   port = int(os.environ.get("PORT", 8000))
   ```

2. Ensure Dockerfile CMD uses 0.0.0.0:
   ```dockerfile
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

### 8. Memory or Resource Limits

**Symptoms**: Service crashes with OOM (Out of Memory)

**Solutions**:
1. Scale service resources:
   ```bash
   railway scale --service [service-name] --memory 1024
   ```

2. Optimize application memory usage
3. Consider using worker processes for heavy tasks

### 9. Deployment Rollback

**When needed**: After a failed deployment

**Steps**:
```bash
# List recent deployments
railway deployments --service [service-name]

# Rollback to specific deployment
railway rollback --service [service-name] --deployment [deployment-id]
```

### 10. SSL/HTTPS Issues

**Note**: Railway provides HTTPS automatically

**If issues occur**:
1. Don't configure SSL in your application
2. Use Railway's provided domain
3. For custom domains, follow Railway's DNS setup

## Quick Diagnostic Commands

```bash
# Check service status
railway status --service [service-name]

# View recent logs
railway logs --service [service-name] --tail 50

# List all services
railway list

# Check environment variables
railway variables --service [service-name]

# Restart service
railway restart --service [service-name]

# Run command in service context
railway run --service [service-name] [command]
```

## Getting Help

1. Check Railway documentation: https://docs.railway.app
2. Railway Discord: https://discord.gg/railway
3. GitHub Issues: https://github.com/JihunKong/teaching_analize/issues
4. Railway Status Page: https://status.railway.app