#!/usr/bin/env python3
"""
Cloud Run startup script for AuraHire AI
Handles environment variables and starts the FastAPI server
"""

import os
import sys
import uvicorn
import asyncio
import signal
from contextlib import asynccontextmanager

def setup_environment():
    """Setup environment variables and validate configuration"""
    
    # Ensure Python path is set correctly
    if '/app' not in sys.path:
        sys.path.insert(0, '/app')
    
    # Set Python path environment variable
    os.environ['PYTHONPATH'] = '/app'
    
    # Get port from environment (Cloud Run sets this automatically)
    port = int(os.environ.get("PORT", 8080))
    
    # Get host (should be 0.0.0.0 for Cloud Run)
    host = os.environ.get("HOST", "0.0.0.0")
    
    # Logging configuration
    log_level = os.environ.get("LOG_LEVEL", "info").lower()
    
    # Validate MongoDB URL
    mongodb_url = os.environ.get('MONGODB_URL', '')
    if not mongodb_url:
        print("⚠️  WARNING: MONGODB_URL not set! Database operations will fail.")
    
    print(f"🚀 Starting AuraHire AI server on {host}:{port}")
    print(f"📝 Log level: {log_level}")
    print(f"� Python path: {sys.path[0]}")
    print(f"�🗄️  MongoDB URL: {mongodb_url[:50]}..." if mongodb_url else "🗄️  MongoDB URL: Not set")
    
    return host, port, log_level

def main():
    """Start the FastAPI application with Cloud Run configuration"""
    
    try:
        host, port, log_level = setup_environment()
        
        print("🔄 Importing FastAPI application...")
        
        # Import the FastAPI app to check for import errors
        try:
            from backend.main import app
            print("✅ FastAPI application imported successfully!")
        except Exception as e:
            print(f"❌ Failed to import FastAPI application: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        
        print("🔄 Starting uvicorn server...")
        
        # Start the server with Cloud Run optimized settings
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
            http="auto",
            # Add timeout settings for Cloud Run
            timeout_keep_alive=30,
            timeout_graceful_shutdown=30
        )
        
    except Exception as e:
        print(f"❌ Failed to start server: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()