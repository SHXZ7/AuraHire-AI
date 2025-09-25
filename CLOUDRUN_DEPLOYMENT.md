# Google Cloud Run Deployment Guide for AuraHire AI

## Prerequisites

1. **Google Cloud Account**: Create a free account at [cloud.google.com](https://cloud.google.com)
2. **Google Cloud Project**: Create a new project or use an existing one
3. **gcloud CLI**: Install from [cloud.google.com/sdk](https://cloud.google.com/sdk)
4. **Docker**: Install Docker Desktop for building images

## Setup Steps

### 1. Install and Configure gcloud CLI

```bash
# Install gcloud CLI (follow platform-specific instructions)
# Windows: Download installer from https://cloud.google.com/sdk/docs/install

# Authenticate with Google Cloud
gcloud auth login

# Set your project ID (replace with your actual project ID)
gcloud config set project YOUR-PROJECT-ID

# Enable Docker credential helper
gcloud auth configure-docker
```

### 2. Configure Your Project

1. **Update Project ID** in deployment scripts:
   - Edit `deploy-cloudrun.sh` (Linux/Mac) or `deploy-cloudrun.bat` (Windows)
   - Replace `your-project-id` with your actual Google Cloud project ID

2. **Update MongoDB URL** (if needed):
   - The scripts use your existing MongoDB connection string
   - Environment variables are set automatically during deployment

### 3. Deploy to Cloud Run

#### Option A: Using the deployment script (Recommended)

**Windows:**
```cmd
deploy-cloudrun.bat
```

**Linux/Mac:**
```bash
chmod +x deploy-cloudrun.sh
./deploy-cloudrun.sh
```

#### Option B: Manual deployment

```bash
# Build and tag the image
docker build -t gcr.io/YOUR-PROJECT-ID/aurahire-ai:latest .

# Push to Google Container Registry
docker push gcr.io/YOUR-PROJECT-ID/aurahire-ai:latest

# Deploy to Cloud Run
gcloud run deploy aurahire-ai \
    --image gcr.io/YOUR-PROJECT-ID/aurahire-ai:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --set-env-vars="MONGODB_URL=your-mongodb-connection-string"
```

## Configuration Options

### Environment Variables

The following environment variables are automatically set during deployment:

```bash
MONGODB_URL=mongodb+srv://shaaz:Shaaz123@cluster0.hp19dzy.mongodb.net/resume_matcher
MONGODB_MIN_CONNECTIONS=5
MONGODB_MAX_CONNECTIONS=20
MONGODB_SERVER_SELECTION_TIMEOUT_MS=5000
LOG_LEVEL=INFO
DEBUG=False
MAX_FILE_SIZE_MB=10
PORT=8080  # Set automatically by Cloud Run
```

### Resource Limits

Current configuration:
- **Memory**: 2GB
- **CPU**: 2 vCPU
- **Timeout**: 300 seconds
- **Concurrency**: 100 requests per container
- **Min instances**: 0 (scales to zero)
- **Max instances**: 10

### Scaling Configuration

Cloud Run automatically scales based on traffic:
- **Cold starts**: ~5-10 seconds for first request
- **Scale to zero**: Saves costs when no traffic
- **Auto-scaling**: Handles traffic spikes automatically

## Post-Deployment

### 1. Test Your Deployment

```bash
# Get your service URL
gcloud run services describe aurahire-ai --region=us-central1 --format="value(status.url)"

# Test endpoints
curl https://YOUR-SERVICE-URL/test
curl https://YOUR-SERVICE-URL/health
curl https://YOUR-SERVICE-URL/docs  # API documentation
```

### 2. Monitor Your Service

```bash
# View logs
gcloud run logs read --service=aurahire-ai --region=us-central1

# View service details
gcloud run services describe aurahire-ai --region=us-central1
```

### 3. Update Your Frontend

Update your Streamlit app's API base URL to point to your Cloud Run service:

```python
# In your frontend/app.py
API_BASE_URL = "https://YOUR-SERVICE-URL"  # Replace with actual URL
```

## Cost Optimization

### Pricing Model
Cloud Run charges for:
- **CPU and Memory**: Only when processing requests
- **Requests**: $0.40 per million requests
- **Compute**: ~$0.048 per vCPU-hour, ~$0.0048 per GB-hour

### Cost-Saving Tips
1. **Set appropriate resource limits**: Don't over-provision
2. **Use minimum instances**: Set to 0 to scale to zero
3. **Optimize cold starts**: Use smaller base images
4. **Monitor usage**: Use Cloud Monitoring to track costs

## Troubleshooting

### Common Issues

1. **Authentication errors**:
   ```bash
   gcloud auth login
   gcloud auth configure-docker
   ```

2. **Build failures**:
   - Check Docker is running
   - Verify Dockerfile syntax
   - Check for large files in .dockerignore

3. **Deployment timeouts**:
   - Increase timeout in deployment command
   - Check MongoDB connection string
   - Verify network connectivity

4. **502 errors**:
   - Check service logs: `gcloud run logs read --service=aurahire-ai`
   - Verify MongoDB Atlas IP whitelist includes `0.0.0.0/0`
   - Test health endpoint: `/health`

### Debugging Commands

```bash
# View recent logs
gcloud run logs read --service=aurahire-ai --region=us-central1 --limit=50

# Stream live logs
gcloud run logs tail --service=aurahire-ai --region=us-central1

# Get service status
gcloud run services describe aurahire-ai --region=us-central1
```

## Security Considerations

1. **Environment Variables**: Store sensitive data in Google Secret Manager
2. **Authentication**: Consider adding authentication for production use
3. **CORS**: Restrict origins in production
4. **Rate Limiting**: Implement rate limiting for API endpoints
5. **SSL**: Cloud Run provides HTTPS automatically

## Next Steps

1. **Custom Domain**: Map your own domain name
2. **CI/CD**: Set up automated deployments with GitHub Actions
3. **Monitoring**: Configure alerting and monitoring
4. **Load Testing**: Test with expected traffic loads
5. **Backup Strategy**: Ensure MongoDB data is backed up

## Support

- **Google Cloud Run Docs**: [cloud.google.com/run/docs](https://cloud.google.com/run/docs)
- **Pricing Calculator**: [cloud.google.com/products/calculator](https://cloud.google.com/products/calculator)
- **Support**: [cloud.google.com/support](https://cloud.google.com/support)