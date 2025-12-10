# Authentication System Setup Guide

## Prerequisites

1. **PostgreSQL Installation**
   - Download PostgreSQL from: https://www.postgresql.org/download/windows/
   - Install with default settings
   - Remember the password you set for the `postgres` user

## Setup Steps

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Create PostgreSQL Database

Open PowerShell or Command Prompt and run:

```bash
# Connect to PostgreSQL (enter password when prompted)
psql -U postgres

# Create database
CREATE DATABASE dml_db;

# Exit psql
\q
```

### 3. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```bash
cp .env.example .env
```

Edit `.env` and update:
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/dml_db
SECRET_KEY=generate-a-random-secret-key-here
```

To generate a secure secret key, run in Python:
```python
import secrets
print(secrets.token_hex(32))
```

### 4. Initialize Database

```bash
cd backend
python init_db.py
```

You should see: `✓ Database tables created successfully!`

### 5. Start Backend Server

```bash
uvicorn app.main:app --reload
```

### 6. Test Authentication

Open browser to: http://localhost:8000/docs

Test the endpoints:
- `POST /api/auth/signup` - Create account
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user (requires login)

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login (sets HTTP-only cookies)
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout (clears cookies)
- `GET /api/auth/me` - Get current user info

### Notes
- Tokens are stored in HTTP-only cookies for security
- Access token expires in 15 minutes
- Refresh token expires in 7 days
- All file upload/analyze/preprocess endpoints will require authentication (to be implemented next)

## Troubleshooting

**Database connection error:**
- Verify PostgreSQL is running
- Check DATABASE_URL in .env
- Ensure database `dml_db` exists

**Import errors:**
- Run `pip install -r requirements.txt` again
- Ensure virtual environment is activated

**Token errors:**
- Clear browser cookies
- Generate new SECRET_KEY in .env
