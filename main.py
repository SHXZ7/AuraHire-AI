#!/usr/bin/env python3
"""
Main entry point for AuraHire AI - Google App Engine
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the FastAPI app directly for App Engine
from backend.main import app

# App Engine will automatically serve this app object