# Data Preprocessing Platform - Quick Start Guide

## Prerequisites

Before running the setup scripts, ensure you have:

1. **Python 3.9+** installed
2. **Node.js 18+** installed
3. **PostgreSQL** installed and running

## Quick Setup (Automated)

### Step 1: Create PostgreSQL Database

```bash
# Open PostgreSQL command line (psql)
psql -U postgres

# Create database
CREATE DATABASE data_preprocessing;

# Exit
\q
```

### Step 2: Configure Environment

1. Copy the example environment file:
   ```bash
   cd backend
   copy .env.example .env
   ```

2. Edit `backend/.env` and update:
   ```env
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/data_preprocessing
   SECRET_KEY=your-generated-secret-key-here
   ```

   To generate a secure secret key, run in Python:
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```

### Step 3: Run Setup Script

**Windows (PowerShell):**
```powershell
.\setup.ps1
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

This will:
- ✅ Check Python and Node.js installations
- ✅ Create Python virtual environment
- ✅ Install all backend dependencies
- ✅ **Initialize database tables automatically**
- ✅ Install all frontend dependencies

### Step 4: Start the Application

**Windows (PowerShell):**
```powershell
.\start.ps1
```

**Linux/Mac:**
```bash
./start.sh
```

This will start both servers in separate windows.

### Step 5: Access the Application

Open your browser and go to:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs

## What the Setup Script Does

The `setup.ps1` script automatically:

1. ✅ Verifies Python and Node.js are installed
2. ✅ Creates a Python virtual environment
3. ✅ Installs all Python dependencies from `requirements.txt`
4. ✅ **Runs `init_db.py` to create database tables**
5. ✅ Installs all Node.js dependencies

### Database Initialization

The setup script automatically runs `python init_db.py` which creates:
- `users` table (for authentication)
- `files` table (for file tracking)

If database initialization fails, the script will:
- Show a warning (not an error)
- Continue with the rest of the setup
- Provide instructions to manually run `python init_db.py` later

## Manual Setup (If Needed)

If the automated setup fails or you prefer manual setup:

### Backend Setup
```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac
pip install -r requirements.txt
python init_db.py
```

### Frontend Setup
```bash
cd frontend
npm install
```

### Start Servers Manually

**Backend:**
```bash
cd backend
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm run dev
```

## Troubleshooting

### Database Connection Error

If you see database connection errors:

1. **Check PostgreSQL is running:**
   ```bash
   # Windows
   Get-Service postgresql*
   
   # Linux/Mac
   sudo systemctl status postgresql
   ```

2. **Verify database exists:**
   ```bash
   psql -U postgres -l
   ```

3. **Check DATABASE_URL in `.env`:**
   - Correct format: `postgresql://username:password@host:port/database`
   - Example: `postgresql://postgres:mypassword@localhost:5432/data_preprocessing`

4. **Manually initialize database:**
   ```bash
   cd backend
   .\venv\Scripts\Activate.ps1
   python init_db.py
   ```

### Import Errors

If you see Python import errors:
```bash
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Port Already in Use

If port 8000 or 3000 is already in use:
- **Backend**: Change port with `uvicorn app.main:app --reload --port 8001`
- **Frontend**: Change port in `package.json` or use `npm run dev -- -p 3001`

## First Time Usage

1. **Navigate to** http://localhost:3000
2. **Click "Sign up"** to create an account
3. **Login** with your credentials
4. **Upload a CSV/Excel file** to start preprocessing

## Features

✅ User authentication with JWT (HTTP-only cookies)
✅ Automatic data quality issue detection
✅ One-click fix for all issues
✅ Selective issue fixing
✅ User-specific file management
✅ Secure file storage

## Support

For detailed documentation, see:
- `SETUP_AUTH.md` - Authentication system setup
- `PROJECT_COMPLETE.md` - Complete project documentation
