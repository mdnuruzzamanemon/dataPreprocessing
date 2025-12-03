# 🎯 Getting Started Checklist

Use this checklist to ensure your Data Preprocessing Platform is set up correctly.

## 📋 Pre-Setup Checklist

- [ ] **Python 3.9+ installed**
  - Check: `python --version` (Windows) or `python3 --version` (macOS/Linux)
  - Download: https://www.python.org/downloads/

- [ ] **Node.js 18+ installed**
  - Check: `node --version`
  - Download: https://nodejs.org/

- [ ] **Git installed** (optional, for version control)
  - Check: `git --version`
  - Download: https://git-scm.com/

## 🚀 Setup Checklist

### Automated Setup (Recommended)

**Windows:**
- [ ] Open PowerShell in project directory
- [ ] Run: `.\setup.ps1`
- [ ] Verify no errors in output
- [ ] See "Setup Complete!" message

**macOS/Linux:**
- [ ] Open Terminal in project directory
- [ ] Run: `chmod +x setup.sh` (first time only)
- [ ] Run: `./setup.sh`
- [ ] Verify no errors in output
- [ ] See "Setup Complete!" message

### Manual Setup (Alternative)

#### Backend Setup
- [ ] Navigate to `backend` directory
- [ ] Create virtual environment: `python -m venv venv`
- [ ] Activate virtual environment:
  - Windows: `venv\Scripts\Activate.ps1`
  - macOS/Linux: `source venv/bin/activate`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Verify installation: No error messages
- [ ] Create `.env` file (optional, copy from `.env.example`)

#### Frontend Setup
- [ ] Navigate to `frontend` directory
- [ ] Install dependencies: `npm install`
- [ ] Verify installation: No error messages
- [ ] Check `.env.local` exists with correct API URL

## 🏃 Running the Application

### Start Backend
- [ ] Open Terminal/PowerShell in `backend` directory
- [ ] Activate virtual environment
- [ ] Run: `uvicorn app.main:app --reload`
- [ ] Verify output shows:
  - `INFO:     Uvicorn running on http://0.0.0.0:8000`
  - `INFO:     Application startup complete`
- [ ] Test: Open http://localhost:8000 in browser
- [ ] Should see: `{"message": "Data Preprocessing Platform API", ...}`
- [ ] Test: Open http://localhost:8000/docs
- [ ] Should see: Interactive API documentation

### Start Frontend
- [ ] Open NEW Terminal/PowerShell in `frontend` directory
- [ ] Run: `npm run dev`
- [ ] Verify output shows:
  - `ready - started server on 0.0.0.0:3000`
  - `compiled successfully`
- [ ] Test: Open http://localhost:3000 in browser
- [ ] Should see: Data Preprocessing Platform homepage with upload area

## ✅ Verification Checklist

### Backend Verification
- [ ] Backend running on port 8000
- [ ] No error messages in terminal
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Health check works: http://localhost:8000/health
- [ ] `uploads/` directory created automatically
- [ ] `temp/` directory created automatically

### Frontend Verification
- [ ] Frontend running on port 3000
- [ ] No error messages in terminal
- [ ] Homepage loads correctly
- [ ] Upload area is visible
- [ ] No console errors in browser (F12 → Console tab)
- [ ] Styling looks correct (Tailwind CSS working)

### Integration Verification
- [ ] Upload a CSV file
- [ ] File uploads successfully
- [ ] Analysis runs automatically
- [ ] Issues are displayed (if any)
- [ ] Summary cards show file info
- [ ] "Fix All" button appears (if issues exist)
- [ ] Can download processed file

## 🧪 Test with Sample Data

Create a simple test CSV file:

```csv
name,age,salary,department
John,25,50000,IT
Jane,30,60000,HR
Bob,,55000,IT
John,25,50000,IT
Alice,35,200000,Finance
```

This file has:
- Missing value (Bob's age)
- Duplicate row (John)
- Potential outlier (Alice's salary)

**Test Steps:**
- [ ] Upload the test CSV
- [ ] Verify it detects missing values
- [ ] Verify it detects duplicates
- [ ] Verify it detects outliers
- [ ] Click "Fix All"
- [ ] Download cleaned file
- [ ] Open cleaned file and verify fixes applied

## 🐛 Troubleshooting Checklist

### Backend Issues
- [ ] Virtual environment activated? (Look for `(venv)` in prompt)
- [ ] All dependencies installed? Run `pip install -r requirements.txt` again
- [ ] Port 8000 available? Try different port: `--port 8001`
- [ ] Python version correct? Must be 3.9+
- [ ] Check error messages for missing packages

### Frontend Issues
- [ ] Dependencies installed? Run `npm install` again
- [ ] Node version correct? Must be 18+
- [ ] Port 3000 available? Set `PORT=3001` in environment
- [ ] `.env.local` file exists with correct API URL
- [ ] Try deleting `node_modules` and `.next`, then `npm install`

### Connection Issues
- [ ] Backend running before starting frontend?
- [ ] API URL correct in `.env.local`? Should be `http://localhost:8000`
- [ ] CORS configured? Check `backend/app/core/config.py`
- [ ] Firewall blocking? Check firewall settings
- [ ] Both on same network/localhost?

## 📱 Browser Compatibility
- [ ] Chrome/Edge (Recommended)
- [ ] Firefox
- [ ] Safari
- [ ] JavaScript enabled
- [ ] Cookies enabled

## 🎓 Next Steps After Setup

- [ ] Read through README.md
- [ ] Explore API documentation at /docs
- [ ] Try different file types (CSV, XLS, XLSX)
- [ ] Test with your own datasets
- [ ] Review ARCHITECTURE.md for technical details
- [ ] Check CONTRIBUTING.md if planning to modify
- [ ] Star the project on GitHub (if applicable)

## 📞 Getting Help

If you're stuck:

1. **Check Documentation:**
   - README.md
   - QUICKSTART.md
   - backend/README.md
   - frontend/README.md

2. **Check Console Output:**
   - Backend terminal for Python errors
   - Frontend terminal for Node errors
   - Browser console (F12) for JavaScript errors

3. **Common Solutions:**
   - Restart both servers
   - Clear browser cache
   - Reinstall dependencies
   - Check file permissions
   - Verify Python/Node versions

4. **Still Stuck?**
   - Create an issue with:
     - Error messages
     - Steps to reproduce
     - System information
     - Screenshots

## ✨ You're Ready!

Once all checks are complete, you're ready to start preprocessing data!

**Reminder:**
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

Happy preprocessing! 🎉
