@echo off
REM Google Cloud Run Deployment Script for AuraHire AI (Windows)
REM Make sure you have gcloud CLI installed and authenticated

setlocal enabledelayedexpansion

REM Configuration - CHANGE THESE VALUES
set PROJECT_ID=your-project-id
set SERVICE_NAME=aurahire-ai
set REGION=us-central1
set IMAGE_NAME=gcr.io/%PROJECT_ID%/%SERVICE_NAME%

echo 🚀 Starting Google Cloud Run deployment for AuraHire AI...

REM Check if gcloud is installed
gcloud --version >nul 2>&1
if errorlevel 1 (
    echo ❌ gcloud CLI is not installed. Please install it first:
    echo https://cloud.google.com/sdk/docs/install
    exit /b 1
)

REM Set the project
echo 📋 Setting project to: %PROJECT_ID%
gcloud config set project %PROJECT_ID%

REM Enable required APIs
echo 🔧 Enabling required APIs...
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

REM Build and push Docker image
echo 🔨 Building Docker image...
docker build -t %IMAGE_NAME%:latest .

echo 📤 Pushing image to Google Container Registry...
docker push %IMAGE_NAME%:latest

REM Deploy to Cloud Run
echo 🚀 Deploying to Cloud Run...
gcloud run deploy %SERVICE_NAME% ^
    --image %IMAGE_NAME%:latest ^
    --platform managed ^
    --region %REGION% ^
    --allow-unauthenticated ^
    --memory 2Gi ^
    --cpu 2 ^
    --timeout 300 ^
    --concurrency 100 ^
    --min-instances 0 ^
    --max-instances 10 ^
    --set-env-vars="MONGODB_URL=mongodb+srv://shaaz:Shaaz123@cluster0.hp19dzy.mongodb.net/resume_matcher,MONGODB_MIN_CONNECTIONS=5,MONGODB_MAX_CONNECTIONS=20,LOG_LEVEL=INFO,DEBUG=False,MAX_FILE_SIZE_MB=10"

REM Get the service URL
for /f "tokens=*" %%i in ('gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="value(status.url)"') do set SERVICE_URL=%%i

echo ✅ Deployment completed successfully!
echo 🌐 Service URL: %SERVICE_URL%
echo 🩺 Health check: %SERVICE_URL%/health
echo 📊 API docs: %SERVICE_URL%/docs

echo 🎉 Deployment complete! Your AuraHire AI API is now running on Google Cloud Run.
pause