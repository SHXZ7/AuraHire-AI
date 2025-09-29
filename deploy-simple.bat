@echo off
REM Simple Google Cloud Run deployment using source-based deployment (no Docker)
REM This uses buildpacks automatically

setlocal enabledelayedexpansion

set PROJECT_ID=distributed-inn-473215-u3
set SERVICE_NAME=aurahire-ai
set REGION=europe-west1

echo 🚀 Deploying AuraHire AI to Cloud Run (using buildpacks, no Docker)
echo 📋 Project: %PROJECT_ID%
echo 🌍 Region: %REGION%
echo.

REM Check if gcloud is installed
gcloud --version >nul 2>&1
if errorlevel 1 (
    echo ❌ gcloud CLI is not installed
    exit /b 1
)

REM Set project
gcloud config set project %PROJECT_ID%

REM Enable APIs
echo 🔧 Enabling required APIs...
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

REM Deploy directly from source (uses buildpacks automatically)
echo 🚀 Deploying from source code...
gcloud run deploy %SERVICE_NAME% ^
    --source=. ^
    --region=%REGION% ^
    --platform=managed ^
    --allow-unauthenticated ^
    --memory=2Gi ^
    --cpu=2 ^
    --timeout=300 ^
    --concurrency=100 ^
    --min-instances=0 ^
    --max-instances=10 ^
    --set-env-vars="MONGODB_URL=mongodb+srv://shaaz:Shaaz123@cluster0.hp19dzy.mongodb.net/resume_matcher,MONGODB_MIN_CONNECTIONS=5,MONGODB_MAX_CONNECTIONS=20,MONGODB_SERVER_SELECTION_TIMEOUT_MS=5000,MONGODB_CONNECT_TIMEOUT_MS=10000,MONGODB_SOCKET_TIMEOUT_MS=20000,LOG_LEVEL=INFO,DEBUG=False,MAX_FILE_SIZE_MB=10,ALLOWED_FILE_TYPES=pdf,doc,docx,txt"

if errorlevel 1 (
    echo ❌ Deployment failed!
    echo 💡 Check the logs above for details
    pause
    exit /b 1
)

REM Get service URL
for /f "tokens=*" %%i in ('gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="value(status.url)"') do set SERVICE_URL=%%i

echo.
echo ✅ Deployment successful!
echo 🌐 Service URL: %SERVICE_URL%
echo 🩺 Health: %SERVICE_URL%/health
echo 📊 Docs: %SERVICE_URL%/docs

echo.
echo 🧪 Testing...
timeout /t 5 /nobreak >nul
curl -s "%SERVICE_URL%/test"

pause