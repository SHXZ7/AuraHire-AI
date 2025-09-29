#!/usr/bin/env python3
"""
Cloud Run startup script for AuraHire AI
Handles environment variables and starts the FastAPI server
"""

import os
import sys
import uvicorn

def main():
    """Start the FastAPI application with Cloud Run configuratio"""
    
    # Get port from environment (Cloud Run sets this automatically)
    port = int(os.environ.get("PORT", 8080))
    
    # Get host (should be 0.0.0.0 for Cloud Run)
    host = os.environ.get("HOST", "0.0.0.0")
    
    # Logging configuration
    log_level = os.environ.get("LOG_LEVEL", "info").lower()
    
    print(f"🚀 Starting AuraHire AI server on {host}:{port}")
    print(f"📝 Log level: {log_level}")
    print(f"🗄️  MongoDB URL: {os.environ.get('MONGODB_URL', 'Not set')[:50]}...")
    
    # Start the server
    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        log_level=log_level,
        access_log=True,
        # Disable reload in production
        reload=False,
        # Optimize for production
        loop="auto",
        http="auto"
    )

if __name__ == "__main__":
    main()