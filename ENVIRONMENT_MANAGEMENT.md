# Environment Variable Management Guide

## Overview
This guide explains how to properly manage environment variables in the AIBOA platform to prevent API key deletion/overwriting issues.

## Root Cause of API Key Issues

The Upstage API key deletion/overwriting was caused by:

1. **Multiple conflicting environment files** with different API key values
2. **Inconsistent environment variable loading** by Docker Compose
3. **Missing required environment variables** causing Docker Compose warnings

## Solution Implemented

### 1. Consolidated Environment Configuration

**Primary Environment File: `.env`**
- Contains all required API keys including `UPSTAGE_API_KEY=up_kcU1IMWm9wcC1rqplsIFMsEeqlUXN`
- Includes all Docker Compose required variables
- Automatically loaded by Docker Compose

### 2. Environment Files Structure

```
.env                    # Main environment file (used by Docker Compose)
.env.local             # Local development overrides (optional)
.env.production        # Production-specific settings (for reference)
.env.template          # Template for new deployments
.env.example           # Example configuration
```

**Priority Order:**
1. `.env` (primary, always loaded by Docker Compose)
2. `.env.local` (local overrides, if needed)
3. System environment variables (highest priority)

### 3. Required Environment Variables

```bash
# API Keys (Critical)
UPSTAGE_API_KEY=up_kcU1IMWm9wcC1rqplsIFMsEeqlUXN
SOLAR_API_KEY=up_kcU1IMWm9wcC1rqplsIFMsEeqlUXN
OPENAI_API_KEY=sk-proj-...
YOUTUBE_API_KEY=

# Service Configuration
TRANSCRIPTION_API_KEY=transcription-api-key-2025
ANALYSIS_API_KEY=analysis-api-key-2025

# Database
POSTGRES_PASSWORD=aiboa_secure_2025!
```

## Deployment Best Practices

### Use the Enhanced Deployment Script

```bash
# Deploy with environment validation
./deploy-with-env.sh
```

The deployment script:
- ✅ Validates environment variables before deployment
- ✅ Ensures proper API key format
- ✅ Loads environment variables correctly
- ✅ Provides detailed logging
- ✅ Verifies container environment setup

### Manual Deployment

If using manual docker-compose commands:

```bash
# 1. Always source environment first
source .env

# 2. Verify variables are loaded
echo "UPSTAGE_API_KEY: ${UPSTAGE_API_KEY:0:10}..."

# 3. Run docker-compose with explicit environment
docker-compose -f docker-compose.fixed.yml up -d
```

## Troubleshooting

### Check Environment Loading
```bash
# Test environment file loading
source .env && echo "UPSTAGE_API_KEY: ${UPSTAGE_API_KEY}"

# Check Docker Compose configuration
docker-compose -f docker-compose.fixed.yml config | grep UPSTAGE_API_KEY

# Verify in running containers
docker-compose -f docker-compose.fixed.yml exec analysis printenv | grep UPSTAGE
```

### Common Issues

**Issue: "variable is not set" warnings**
- **Solution**: Ensure all required variables are in `.env` file

**Issue: API key gets reset to empty or old value**
- **Solution**: Check for conflicting environment files (`.env.local`, `.env.production`)
- **Action**: Use primary `.env` file only for deployment

**Issue: Container can't access API key**
- **Solution**: Restart containers after updating `.env`
```bash
docker-compose -f docker-compose.fixed.yml down
docker-compose -f docker-compose.fixed.yml up -d
```

## Security Best Practices

1. **Never commit `.env` files to git** (already configured in `.gitignore`)
2. **Use different API keys for different environments**
3. **Rotate API keys periodically**
4. **Monitor API key usage** through provider dashboards
5. **Keep backup of working `.env` configuration**

## Verification Commands

```bash
# 1. Check git exclusion
git status  # Should not show .env files

# 2. Verify environment loading
docker-compose -f docker-compose.fixed.yml config --services  # Should show no warnings

# 3. Test API key in container
docker-compose -f docker-compose.fixed.yml exec analysis python -c "import os; print('UPSTAGE_API_KEY:', os.environ.get('UPSTAGE_API_KEY', 'NOT SET')[:15] + '...')"
```

## Current Configuration Status

✅ **Fixed Issues:**
- Multiple conflicting environment files consolidated
- Docker Compose environment variable warnings resolved  
- Upstage API key properly configured: `up_kcU1IMWm9wcC1rqplsIFMsEeqlUXN`
- Enhanced deployment script with validation created

✅ **Validated:**
- `.gitignore` properly excludes `.env` files
- Environment variables load correctly in Docker containers
- No more API key deletion/overwriting issues

## Next Steps

1. **Use `./deploy-with-env.sh` for all deployments**
2. **Monitor logs for any environment-related issues**
3. **Keep `.env` file backed up securely**
4. **Test API functionality after each deployment**