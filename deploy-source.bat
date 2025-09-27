@echo off
REM Google Cloud Run Source-based Deployment (No Docker)
REM This script deploys directly from source code using Buildpacks

setlocal enabledelayedexpansion

REM Configuration
set PROJECT_ID=distributed-inn-473215-u3
set SERVICE_NAME=aurahire-ai
set REGION=asia-south1

echo 🚀 Deploying AuraHire AI to Cloud Run (Source-based)
echo ================================================
echo 📋 Project: %PROJECT_ID%
echo 🌍 Region: %REGION%
echo 🔧 Service: %SERVICE_NAME%
echo.

REM Check if gcloud is installed
gcloud --version >nul 2>&1
if errorlevel 1 (
    echo ❌ gcloud CLI is not installed. Please install it first.
    exit /b 1
)

REM Set project
echo 📋 Setting project...
gcloud config set project %PROJECT_ID%

REM Enable required APIs
echo 🔧 Enabling required APIs...
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

REM Deploy from source
echo 🏗️  Deploying from source code...
gcloud run deploy %SERVICE_NAME% ^
    --source . ^
    --region %REGION% ^
    --allow-unauthenticated ^
    --memory 2Gi ^
    --cpu 2 ^
    --timeout 300 ^
    --concurrency 80 ^
    --min-instances 0 ^
    --max-instances 10 ^
    --port 8080 ^
    --set-env-vars="MONGODB_URL=mongodb+srv://shaaz:Shaaz123@cluster0.hp19dzy.mongodb.net/resume_matcher,MONGODB_MIN_CONNECTIONS=5,MONGODB_MAX_CONNECTIONS=20,MONGODB_SERVER_SELECTION_TIMEOUT_MS=10000,MONGODB_CONNECT_TIMEOUT_MS=15000,MONGODB_SOCKET_TIMEOUT_MS=30000,LOG_LEVEL=INFO,DEBUG=False,MAX_FILE_SIZE_MB=10,ALLOWED_FILE_TYPES=pdf,doc,docx,txt"

if errorlevel 1 (
    echo.
    echo ❌ Deployment failed!
    echo 💡 Troubleshooting tips:
    echo    1. Check the build logs in Cloud Console
    echo    2. Verify all required files are present ^(Procfile, requirements.txt^)
    echo    3. Test the application locally first
    echo    4. Check for any import errors in your code
    echo.
    echo 📝 View logs: gcloud run logs read --service=%SERVICE_NAME% --region=%REGION%
    pause
    exit /b 1
)

REM Get service URL
echo.
echo 🔍 Getting service URL...
for /f "tokens=*" %%i in ('gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="value(status.url)"') do set SERVICE_URL=%%i

echo.
echo ✅ Deployment completed successfully!
echo 🌐 Service URL: %SERVICE_URL%
echo 🩺 Health check: %SERVICE_URL%/health
echo 📊 API docs: %SERVICE_URL%/docs
echo 🧪 Test endpoint: %SERVICE_URL%/test

echo.
echo 🧪 Testing deployment in 15 seconds...
timeout /t 15 /nobreak >nul

curl -f "%SERVICE_URL%/test" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Test failed. Service might still be starting.
    echo 📝 Check logs: gcloud run logs read --service=%SERVICE_NAME% --region=%REGION%
) else (
    echo ✅ Service is responding correctly!
)

echo.
echo 🎉 AuraHire AI is now running on Cloud Run!
echo 📱 Update your frontend to use: %SERVICE_URL%

pause