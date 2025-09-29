#!/usr/bin/env python3
"""
Simple test for Cloud Run deployment
"""

import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Start a simple test server"""
    
    # Get port from environment (Cloud Run sets this automatically)
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"🚀 Starting simple test server on {host}:{port}")
    print(f"📝 Python version: {sys.version}")
    print(f"🗄️  MongoDB URL: {os.environ.get('MONGODB_URL', 'Not set')[:50]}...")
    
    try:
        import uvicorn
        from fastapi import FastAPI
        
        app = FastAPI(title="AuraHire AI Test", version="1.0.0")
        
        @app.get("/")
        async def root():
            return {
                "message": "AuraHire AI is running!",
                "status": "ok",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        @app.get("/health")
        async def health():
            return {
                "status": "healthy",
                "message": "Simple test endpoint working",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        @app.get("/test")
        async def test():
            return {
                "status": "ok",
                "message": "Test endpoint working",
                "python_version": sys.version,
                "environment": {
                    "PORT": port,
                    "HOST": host,
                    "MONGODB_URL": "***" if os.environ.get('MONGODB_URL') else "Not set"
                }
            }
        
        # Start the server
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            reload=False
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        # Fallback to a simple HTTP server
        import http.server
        import socketserver
        
        class MyHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = '{"message": "AuraHire AI fallback server", "status": "ok"}'
                self.wfile.write(response.encode())
        
        with socketserver.TCPServer((host, port), MyHandler) as httpd:
            print(f"Serving fallback HTTP server at {host}:{port}")
            httpd.serve_forever()
    
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()