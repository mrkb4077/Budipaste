#!/usr/bin/env python
"""
Create a test user for Budibase testing
"""
from app.db.session import SessionLocal
from app.models import models
from app.core import security
from datetime import datetime

db = SessionLocal()

# Create user directly
user = models.User(
    email="admin@example.com",
    hashed_password=security.get_password_hash("TestPass123!"),
    full_name="Admin User",
    role="admin",
    is_active=True,
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow()
)

try:
    db.add(user)
    db.commit()
    print("✅ Test user created successfully!")
    print(f"Email: admin@example.com")
    print(f"Password: TestPass123!")
    print(f"Role: admin")
except Exception as e:
    db.rollback()
    print(f"❌ Error: {e}")
finally:
    db.close()
