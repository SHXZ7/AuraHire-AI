#!/usr/bin/env python3
"""
Minimal test for Cloud Run deployment
"""

import os
from datetime import datetime

def main():
    """Start minimal FastAPI server"""
    
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"🚀 Starting minimal server on {host}:{port}")
    
    from fastapi import FastAPI
    import uvicorn
    
    app = FastAPI(title="AuraHire AI Minimal", version="1.0.0")
    
    @app.get("/")
    async def root():
        return {
            "message": "Hello from AuraHire AI!",
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
    
    # Start server
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    main()