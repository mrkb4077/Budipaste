#!/usr/bin/env python3
"""
Run script for Budipaste FastAPI application.
"""

import os
import uvicorn

# Change to the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8002,  # Use port 8002 to avoid conflicts
        reload=False,
        log_level="info"
    )