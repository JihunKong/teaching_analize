# AIBOA Frontend Deployment Guide

## Quick Start - Deploy in 5 Minutes

This guide will help you deploy the AIBOA frontend to Railway immediately.

## Prerequisites
- Railway account (https://railway.app)
- Railway CLI installed (`npm install -g @railway/cli`)
- Git installed on your machine

## Step 1: Prepare the Frontend

The frontend is already created in the `frontend/` directory with:
- ✅ Streamlit multi-page application
- ✅ API integration with backend services
- ✅ CBIL analysis visualization
- ✅ File upload and YouTube transcription
- ✅ Real-time job tracking

## Step 2: Deploy to Railway

### Option A: Deploy via Railway Dashboard (Easiest)

1. **Login to Railway Dashboard**
   ```
   https://railway.app/dashboard
   ```

2. **Create New Service**
   - Click "New Project" or go to your existing project
   - Click "New Service" → "GitHub Repo"
   - Select your repository: `teaching_analize`

3. **Configure Service Settings**
   - Service Name: `aiboa-frontend`
   - Root Directory: `/frontend`
   - Branch: `main`

4. **Set Environment Variables**
   ```
   TRANSCRIPTION_API_URL=https://teachinganalize-production.up.railway.app
   ANALYSIS_API_URL=https://amusedfriendship-production.up.railway.app
   API_KEY=test-api-key
   ```

5. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes for build to complete

### Option B: Deploy via CLI

1. **Navigate to frontend directory**
   ```bash
   cd /Users/jihunkong/teaching_analize/frontend
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Link to your project**
   ```bash
   railway link
   # Select your existing project
   ```

4. **Create new service**
   ```bash
   railway service create aiboa-frontend
   ```

5. **Deploy**
   ```bash
   railway up --service aiboa-frontend
   ```

## Step 3: Access Your Frontend

After deployment, Railway will provide a URL like:
```
https://aiboa-frontend-production.up.railway.app
```

Visit this URL to access your AIBOA platform with full UI!

## Step 4: Test the Application

### Test Transcription
1. Click "📝 Transcription" in sidebar
2. Upload a sample audio file or enter YouTube URL
3. Wait for processing
4. View and download transcript

### Test Analysis
1. Click "🔍 Analysis" in sidebar
2. Paste teaching content or use transcript
3. View CBIL classification results
4. Check recommendations

### Test Statistics
1. Click "📊 Statistics" in sidebar
2. View platform metrics
3. Check service health status

## Local Development (Optional)

If you want to test locally before deploying:

```bash
# Navigate to frontend directory
cd /Users/jihunkong/teaching_analize/frontend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TRANSCRIPTION_API_URL=https://teachinganalize-production.up.railway.app
export ANALYSIS_API_URL=https://amusedfriendship-production.up.railway.app
export API_KEY=test-api-key

# Run locally
streamlit run app.py
```

Visit http://localhost:8501 to see the app locally.

## Troubleshooting

### Issue: Service not starting
**Solution**: Check Railway logs
```bash
railway logs --service aiboa-frontend
```

### Issue: API connection errors
**Solution**: Verify environment variables in Railway dashboard

### Issue: File upload not working
**Solution**: Check file size limits (max 200MB) and formats

### Issue: Slow loading
**Solution**: Railway free tier may have cold starts. Upgrade for better performance.

## Next Steps

### Immediate Actions (Day 1)
- [x] Deploy frontend to Railway
- [ ] Test all features with real data
- [ ] Share URL with team for feedback
- [ ] Monitor Railway logs for errors

### Week 1 Improvements
- [ ] Add user authentication
- [ ] Implement PDF report generation
- [ ] Add batch file processing
- [ ] Improve mobile responsiveness

### Future Enhancements
- [ ] Integrate PostgreSQL for data persistence
- [ ] Add Redis for caching
- [ ] Implement real-time updates with WebSockets
- [ ] Add multi-language UI support

## Support & Monitoring

### Monitor Application
```bash
# View logs
railway logs --service aiboa-frontend --tail

# Check deployment status
railway status

# View metrics
railway metrics
```

### Update Application
```bash
# Make changes to code
# Commit to git
git add .
git commit -m "Update frontend"
git push

# Railway will auto-deploy on push
```

## Production Checklist

Before going to production:
- [ ] Change API_KEY from test value
- [ ] Enable HTTPS only
- [ ] Set up error monitoring (Sentry)
- [ ] Configure custom domain
- [ ] Set up backup strategy
- [ ] Create user documentation
- [ ] Load test the application

## Cost Estimation

Railway Pricing (as of 2025):
- **Hobby Plan**: $5/month
  - Includes $5 usage credit
  - Good for MVP and testing
  
- **Pro Plan**: $20/month
  - Includes $20 usage credit
  - Better performance
  - Priority support

Estimated monthly cost for AIBOA frontend:
- CPU: ~$3-5
- Memory: ~$2-3
- Network: ~$1-2
- **Total**: ~$6-10/month

## Success Metrics

After deployment, monitor:
1. **Page Load Time**: Should be < 2 seconds
2. **API Response Time**: Should be < 1 second
3. **Upload Success Rate**: Should be > 95%
4. **User Session Duration**: Target > 5 minutes
5. **Error Rate**: Should be < 1%

## Conclusion

Your AIBOA frontend is now ready for deployment! The Streamlit-based interface provides:
- ✅ User-friendly interface for transcription and analysis
- ✅ Real-time job tracking and status updates
- ✅ Beautiful visualizations of CBIL analysis
- ✅ Easy deployment and maintenance
- ✅ Scalable architecture

Deploy now and start providing value to your users immediately!

---

**Need Help?**
- Railway Documentation: https://docs.railway.app
- Streamlit Documentation: https://docs.streamlit.io
- Project Repository: https://github.com/[your-username]/teaching_analize