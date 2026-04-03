# Budipaste - Youth Program Attendance Tracker

A FastAPI-based application for tracking attendance and activities in the Yili Youth Program.

## Features
- User authentication with role-based permissions
- Participant management
- Attendance tracking
- Activity logging with time tracking
- Notes and observations
- Automatic API documentation

## Tech Stack
- **Backend**: FastAPI (Python)
- **Database**: SQLAlchemy with SQLite/PostgreSQL
- **Authentication**: JWT tokens
- **Documentation**: Auto-generated OpenAPI/Swagger

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Initialize the database:
   ```bash
   python init_db.py
   ```

3. Run the application:
   ```bash
   python run.py
   ```

4. Open http://localhost:8000/docs for API documentation

## Default Admin Account
- Email: admin@budipaste.com
- Password: admin123
- **Please change this password after first login!**

## API Endpoints
- `POST /api/v1/auth/access-token` - Login
- `GET /api/v1/participants/` - List participants
- `POST /api/v1/participants/` - Create participant
- `GET /api/v1/attendance/` - List attendance records
- `POST /api/v1/attendance/` - Create attendance record
- `GET /api/v1/activities/` - List activity records
- `POST /api/v1/activities/` - Create activity record