#!/bin/bash

# Google Cloud Run Deployment Script for AuraHire AI
# Make sure you have gcloud CLI installed and authenticated

set -e

# Configuration
PROJECT_ID="your-project-id"  # Replace with your actual project ID
SERVICE_NAME="aurahire-ai"
REGION="us-central1"  # Change to your preferred region
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 Starting Google Cloud Run deployment for AuraHire AI..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first:"
    echo "https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated with gcloud. Please run: gcloud auth login"
    exit 1
fi

# Set the project
echo "📋 Setting project to: ${PROJECT_ID}"
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and push Docker image
echo "🔨 Building Docker image..."
docker build -t ${IMAGE_NAME}:latest .

echo "📤 Pushing image to Google Container Registry..."
docker push ${IMAGE_NAME}:latest

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME}:latest \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --concurrency 100 \
    --min-instances 0 \
    --max-instances 10 \
    --set-env-vars="MONGODB_URL=mongodb+srv://shaaz:Shaaz123@cluster0.hp19dzy.mongodb.net/resume_matcher,MONGODB_MIN_CONNECTIONS=5,MONGODB_MAX_CONNECTIONS=20,LOG_LEVEL=INFO,DEBUG=False,MAX_FILE_SIZE_MB=10"

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format="value(status.url)")

echo "✅ Deployment completed successfully!"
echo "🌐 Service URL: ${SERVICE_URL}"
echo "🩺 Health check: ${SERVICE_URL}/health"
echo "📊 API docs: ${SERVICE_URL}/docs"

# Test the deployment
echo "🧪 Testing deployment..."
if curl -f "${SERVICE_URL}/test" > /dev/null 2>&1; then
    echo "✅ Basic connectivity test passed!"
else
    echo "⚠️  Basic connectivity test failed. Check the logs:"
    echo "gcloud run logs read --service=${SERVICE_NAME} --region=${REGION}"
fi

echo "🎉 Deployment complete! Your AuraHire AI API is now running on Google Cloud Run."