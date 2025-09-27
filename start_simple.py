#!/usr/bin/env python3
"""
Simple Cloud Run startup script for AuraHire AI
Optimized for fast startup and Cloud Run compatibility
"""

import os
import sys

def main():
    """Start the FastAPI application with minimal overhead"""
    
    # Set environment variables
    os.environ['PYTHONPATH'] = '/app'
    port = int(os.environ.get("PORT", 8080))
    
    print(f"🚀 Starting AuraHire AI on port {port}")
    print(f"🐍 Python version: {sys.version}")
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Quick import test
    try:
        import uvicorn
        print("✅ uvicorn imported")
    except ImportError as e:
        print(f"❌ Failed to import uvicorn: {e}")
        sys.exit(1)
    
    # Start with minimal configuration for fastest startup
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        # Minimal settings for fast startup
        access_log=False,  # Disable access logs for faster startup
        reload=False,
        workers=1,
        # Cloud Run optimizations
        timeout_keep_alive=10,
        timeout_graceful_shutdown=10
    )

if __name__ == "__main__":
    main()