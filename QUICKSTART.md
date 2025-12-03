# Quick Start Guide

This guide will help you get the Data Preprocessing Platform up and running quickly.

## Prerequisites

- **Python 3.9+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **Git** (optional, for version control)

## Step 1: Setup Backend (Python/FastAPI)

### Windows

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### macOS/Linux

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Backend running at: http://localhost:8000

## Step 2: Setup Frontend (Next.js)

Open a **new terminal window** and:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

✅ Frontend running at: http://localhost:3000

## Step 3: Use the Application

1. **Open your browser** to http://localhost:3000
2. **Upload a dataset** (CSV or Excel file)
3. **Review detected issues** automatically
4. **Fix issues** individually or use "Fix All"
5. **Download** your cleaned dataset

## Quick Test

Want to test immediately? Use any CSV file with common issues like:
- Missing values
- Duplicate rows
- Outliers

## Verification

### Backend Check
Visit http://localhost:8000/docs - You should see the API documentation

### Frontend Check
Visit http://localhost:3000 - You should see the upload interface

## Common Issues

### Backend won't start
- Ensure Python 3.9+ is installed: `python --version`
- Virtual environment activated? Look for `(venv)` in terminal
- Port 8000 in use? Try: `uvicorn app.main:app --reload --port 8001`

### Frontend won't start
- Ensure Node.js 18+ is installed: `node --version`
- Delete `node_modules` and run `npm install` again
- Port 3000 in use? Edit `.env.local`: `PORT=3001`

### Cannot connect frontend to backend
- Check backend is running on http://localhost:8000
- Verify `.env.local` in frontend has: `NEXT_PUBLIC_API_URL=http://localhost:8000`

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [backend/README.md](backend/README.md) for API details
- Check [frontend/README.md](frontend/README.md) for UI customization

## Stopping the Application

### Stop Backend
Press `Ctrl+C` in the backend terminal

### Stop Frontend
Press `Ctrl+C` in the frontend terminal

### Deactivate Python Virtual Environment
```bash
deactivate
```

## Development Workflow

1. Start backend: `cd backend && uvicorn app.main:app --reload`
2. Start frontend (new terminal): `cd frontend && npm run dev`
3. Make changes - both auto-reload on save
4. Test at http://localhost:3000
5. Stop with `Ctrl+C` when done

---

🎉 **You're all set!** Start preprocessing your data with confidence.
