#!/usr/bin/env python3
"""
Main entry point for AuraHire AI - Google Cloud Run deployment
This file is required by Google Cloud Buildpacks
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the startup script
from start import main

if __name__ == "__main__":
    main()