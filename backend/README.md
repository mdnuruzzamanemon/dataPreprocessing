# Backend Setup Guide

## Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

## Installation Steps

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv

# macOS/Linux
python3 -m venv venv
```

### 3. Activate Virtual Environment
```bash
# Windows PowerShell
venv\Scripts\Activate.ps1

# Windows CMD
venv\Scripts\activate.bat

# macOS/Linux
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at:
- API: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── core/
│   │   └── config.py        # Configuration settings
│   ├── models/
│   │   └── schemas.py       # Pydantic models for request/response
│   ├── api/
│   │   └── routes/          # API endpoints
│   │       ├── upload.py    # File upload endpoints
│   │       ├── analyze.py   # Data analysis endpoints
│   │       └── preprocess.py # Preprocessing endpoints
│   ├── services/            # Business logic
│   │   ├── file_handler.py  # File operations
│   │   ├── data_analyzer.py # Issue detection logic
│   │   └── data_preprocessor.py # Preprocessing logic
│   └── utils/               # Helper functions
├── uploads/                 # Uploaded files (auto-created)
├── temp/                    # Processed files (auto-created)
└── requirements.txt         # Python dependencies
```

## API Endpoints

### Upload File
**POST** `/api/upload`
- Upload CSV or Excel file
- Returns file metadata

### Analyze File
**GET** `/api/analyze/{file_id}`
- Analyze dataset for issues
- Returns list of detected issues

### Preview Data
**GET** `/api/analyze/{file_id}/preview?rows=10`
- Get preview of dataset
- Returns first N rows

### Preprocess File
**POST** `/api/preprocess/{file_id}`
- Apply preprocessing actions
- Body: `{ "actions": [...] }`

### Fix All Issues
**POST** `/api/preprocess/{file_id}/fix-all`
- Automatically fix all detected issues

### Download File
**GET** `/api/download/{file_id}`
- Download processed file

## Configuration

Edit `app/core/config.py` to customize:
- Maximum upload size
- Allowed file extensions
- Analysis thresholds
- Directory paths

## Troubleshooting

### Port Already in Use
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
```

### Module Not Found
```bash
# Make sure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

### CORS Issues
The backend is configured to allow requests from:
- http://localhost:3000
- http://127.0.0.1:3000

Edit `app/core/config.py` to add more origins.
