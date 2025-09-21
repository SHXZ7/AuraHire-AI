# AuraHire AI Deployment Guide

## 🚀 Backend Deployment on Render

### 1. Prepare Your Repository
- Push your code to GitHub: `SHXZ7/AuraHire-AI`
- Ensure all deployment files are committed

### 2. Create Render Account
- Go to [render.com](https://render.com)
- Sign up/login with your GitHub account

### 3. Deploy Backend
1. **Create New Web Service**
   - Connect your GitHub repository: `SHXZ7/AuraHire-AI`
   - Branch: `main`
   - Root Directory: Leave empty (uses root)

2. **Configure Build & Deploy**
   - Build Command: `pip install -r requirements.txt && alembic upgrade head`
   - Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - Environment: `Python 3.11`

3. **Add Environment Variables**
   ```
   DATABASE_URL=postgresql://user:password@host:port/database
   PYTHON_VERSION=3.11
   ```

### 4. Create PostgreSQL Database
1. **Add PostgreSQL Service**
   - Create new PostgreSQL database on Render
   - Note the connection details

2. **Update Environment Variables**
   - Copy the DATABASE_URL from your PostgreSQL service
   - Add it to your web service environment variables

### 5. Deploy
- Click "Create Web Service"
- Wait for deployment (5-10 minutes)
- Your API will be available at: `https://your-app-name.onrender.com`

## 📱 Frontend Deployment on Streamlit Cloud

### 1. Prepare Frontend
- Ensure `frontend/requirements.txt` exists
- Logo file should be in `frontend/` directory

### 2. Deploy on Streamlit Cloud
1. **Go to Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Login with GitHub account

2. **Create New App**
   - Repository: `SHXZ7/AuraHire-AI`
   - Branch: `main`
   - Main file path: `frontend/app.py`

3. **Advanced Settings**
   - Add environment variable:
     ```
     API_BASE_URL=https://your-render-app.onrender.com
     ```

4. **Deploy**
   - Click "Deploy!"
   - Your app will be available at: `https://your-app-name.streamlit.app`

## 🔧 Post-Deployment

### Update CORS Settings
After frontend deployment, update backend CORS:

```python
# In backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-streamlit-app.streamlit.app",
        "http://localhost:8501"  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Test Your Deployment
1. **Backend Health Check**
   - Visit: `https://your-render-app.onrender.com/`
   - Should show API information

2. **Frontend Test**
   - Visit your Streamlit app
   - Check API status in sidebar
   - Test file upload and matching

## 🛠️ Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify DATABASE_URL format
   - Check PostgreSQL service status
   - Ensure migrations are applied

2. **CORS Errors**
   - Update allowed origins in backend
   - Check API_BASE_URL in frontend

3. **File Upload Issues**
   - Check file size limits (200MB max)
   - Verify CORS configuration

4. **Cold Start Delays**
   - Render free tier has cold starts (~30s)
   - First request may be slow

### Environment Variables

**Backend (Render):**
```
DATABASE_URL=postgresql://user:password@host:port/database
PYTHON_VERSION=3.11
```

**Frontend (Streamlit Cloud):**
```
API_BASE_URL=https://your-render-app.onrender.com
```

## 📊 Monitoring

### Backend Logs
- Check Render dashboard for logs
- Monitor database connections
- Watch for memory/CPU usage

### Frontend Performance
- Monitor Streamlit Cloud dashboard
- Check user sessions and usage
- Review error logs

## 🔄 Updates

### Code Updates
1. Push changes to GitHub
2. Render auto-deploys from main branch
3. Streamlit Cloud auto-deploys frontend changes

### Database Schema Updates
1. Create new Alembic migration:
   ```bash
   alembic revision --autogenerate -m "description"
   ```
2. Commit migration file
3. Push to GitHub
4. Render will run `alembic upgrade head` on deploy

## 🎯 Success Checklist

- [ ] Backend deployed on Render
- [ ] PostgreSQL database created and connected
- [ ] Frontend deployed on Streamlit Cloud
- [ ] API_BASE_URL configured correctly
- [ ] CORS settings updated
- [ ] File upload working
- [ ] Database operations functional
- [ ] All endpoints responding

Your AuraHire AI application should now be fully deployed and accessible worldwide! 🚀