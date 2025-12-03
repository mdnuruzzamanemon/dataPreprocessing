# Data Preprocessing Platform

A comprehensive data preprocessing platform that automatically detects and fixes common data quality issues in CSV and Excel files.

## 🚀 Features

### Data Issue Detection
- ✅ Missing values
- ✅ Duplicate rows
- ✅ Outliers detection
- ✅ Imbalanced data
- ✅ Inconsistent data types
- ✅ Categorical inconsistencies
- ✅ Invalid ranges
- ✅ Data skewness
- ✅ High cardinality features
- ✅ Constant-value features
- ✅ Correlated features
- ✅ Wrong date formats
- ✅ Encoding issues
- ✅ Mixed units
- ✅ Noisy text

### Preprocessing Options
- **Missing Values**: Mean/Median/Mode fill, Forward/Backward fill, Drop rows
- **Outliers**: Remove, Cap using IQR, Log transform
- **Duplicates**: Remove duplicate rows
- **Categorical**: Label/OneHot encoding, Normalize naming
- **Dates**: Format conversion, Feature extraction (year, month, day)
- **Scaling**: MinMax, Standard, Robust scalers
- **Text Cleaning**: Lowercase, Remove punctuation, Remove stopwords

## 🏗️ Architecture

```
├── backend/          # Python FastAPI backend
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── core/     # Core configurations
│   │   ├── models/   # Data models
│   │   ├── services/ # Business logic
│   │   └── utils/    # Helper functions
│   └── tests/        # Backend tests
│
└── frontend/         # Next.js React frontend
    ├── src/
    │   ├── app/      # Next.js app directory
    │   ├── components/ # React components
    │   ├── services/ # API services
    │   ├── types/    # TypeScript types
    │   └── utils/    # Helper functions
    └── public/       # Static assets
```

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.9+)
- **Data Processing**: Pandas, NumPy, SciPy
- **Machine Learning**: Scikit-learn
- **File Handling**: openpyxl, xlrd

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **State Management**: React Hooks
- **HTTP Client**: Axios

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- Node.js 18 or higher
- npm or yarn

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 🎯 Usage

1. **Upload Dataset**: Upload your CSV or Excel file through the web interface
2. **Detect Issues**: The system automatically analyzes and detects all data quality issues
3. **Review Issues**: Browse through detected issues with detailed statistics
4. **Apply Fixes**: 
   - Use "Fix All" to automatically apply recommended fixes to all issues
   - Or select specific fixes for individual issues
5. **Download**: Download the cleaned dataset

## 📡 API Endpoints

### POST `/api/upload`
Upload a CSV or Excel file for analysis

**Request**: `multipart/form-data`
```json
{
  "file": "<file>"
}
```

**Response**:
```json
{
  "file_id": "uuid",
  "filename": "data.csv",
  "rows": 1000,
  "columns": 25
}
```

### GET `/api/analyze/{file_id}`
Analyze uploaded file for data quality issues

**Response**:
```json
{
  "file_id": "uuid",
  "issues": [
    {
      "type": "missing_values",
      "severity": "high",
      "affected_columns": ["age", "salary"],
      "details": {...}
    }
  ]
}
```

### POST `/api/preprocess/{file_id}`
Apply preprocessing actions to the dataset

**Request**:
```json
{
  "actions": [
    {
      "issue_type": "missing_values",
      "columns": ["age"],
      "method": "mean"
    }
  ]
}
```

### GET `/api/download/{file_id}`
Download the processed dataset

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🔧 Configuration

### Backend Configuration
Edit `backend/app/core/config.py`:
- `MAX_UPLOAD_SIZE`: Maximum file size (default: 100MB)
- `ALLOWED_EXTENSIONS`: Allowed file types
- `TEMP_UPLOAD_DIR`: Temporary upload directory

### Frontend Configuration
Edit `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📝 Development

### Code Style
- **Backend**: Follow PEP 8 guidelines, use Black for formatting
- **Frontend**: ESLint + Prettier configuration included

### Git Workflow
1. Create feature branch from `main`
2. Make changes with clear commit messages
3. Submit pull request with description

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- FastAPI for the amazing web framework
- Next.js team for the React framework
- Pandas community for data processing capabilities
