#!/usr/bin/env python3
"""
Quick setup script to prepare for cloud deployment.
Run this to generate necessary files and check prerequisites.
"""

import os
import sys
import secrets
import json

def generate_secret_key():
    """Generate a cryptographically secure secret key."""
    return secrets.token_urlsafe(32)

def check_files():
    """Check if necessary files exist."""
    required_files = [
        'app/main.py',
        'app/core/config.py',
        'requirements.txt',
        'Procfile',
        '.gitignore',
    ]
    
    print("✓ Checking required files...")
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - MISSING")
    print()

def generate_env_template():
    """Generate Railway environment variables template."""
    secret_key = generate_secret_key()
    
    env_template = {
        "SECRET_KEY": secret_key,
        "BACKEND_CORS_ORIGINS": '["https://bjz5m74f.budibase.app"]',
        "DATABASE_URL": "sqlite:///./budipaste_cloud.db",
        "ENVIRONMENT": "production",
        "DEBUG": "False"
    }
    
    print("✓ Generated Railway ENV Variables:")
    print("  Copy these to Railway dashboard → Variables tab:\n")
    for key, value in env_template.items():
        print(f"  {key} = {value}")
    print()
    
    return env_template

def git_setup():
    """Print git setup instructions."""
    print("✓ Git Setup Instructions:")
    print("""
  1. Create repository on GitHub:
     https://github.com/new
     Repository name: Budipaste
     Make it PUBLIC
     
  2. Add to your local repository:
     git init
     git add .
     git commit -m "Initial Budipaste FastAPI deployment"
     git branch -M main
     git remote add origin https://github.com/YOUR_USERNAME/Budipaste.git
     git push -u origin main
     
  3. Connect to Railway:
     Go to https://railway.app
     New Project → Deploy from GitHub
     Select your Budipaste repository
     Click Deploy
""")

def main():
    print("=" * 60)
    print("  📦 BUDIPASTE CLOUD DEPLOYMENT SETUP")
    print("=" * 60)
    print()
    
    check_files()
    env_vars = generate_env_template()
    git_setup()
    
    print("=" * 60)
    print("  ✅ SETUP CHECKLIST")
    print("=" * 60)
    print("""
  □ Create GitHub account and repository
  □ Push code to GitHub
  □ Create Railway.app account
  □ Connect GitHub to Railway
  □ Add environment variables to Railway
  □ Wait for deployment to complete
  □ Copy Railway domain URL
  □ Add CORS origin to config.py (if not already done)
  □ Update Bearer token in Budibase
  □ Test endpoints from Budibase
  
  Full guide: See CLOUD_DEPLOYMENT_GUIDE.md
""")
    print("=" * 60)

if __name__ == "__main__":
    main()
