#!/usr/bin/env python3
"""
Database initialization script for Budipaste.
Run this script to create the database tables and an initial admin user.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.models import User
from app.core.security import get_password_hash

def create_admin_user():
    db = SessionLocal()
    try:
        # Check if admin user already exists
        admin = db.query(User).filter(User.email == "admin@budipaste.com").first()
        if admin:
            print("Admin user already exists.")
            return

        # Create admin user
        admin_user = User(
            email="admin@budipaste.com",
            hashed_password=get_password_hash("admin123"),
            full_name="System Administrator",
            role="admin",
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        print("Admin user created successfully!")
        print("Email: admin@budipaste.com")
        print("Password: admin123")
        print("Please change the password after first login.")

    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")

    print("Creating admin user...")
    create_admin_user()

    print("Setup complete!")