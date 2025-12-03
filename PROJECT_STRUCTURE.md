# Data Preprocessing Platform - Project Structure

```
F:\project\DML\
│
├── README.md                          # Main project documentation
├── QUICKSTART.md                      # Quick start guide
├── .gitignore                         # Git ignore rules
│
├── backend/                           # Python FastAPI Backend
│   ├── README.md                      # Backend documentation
│   ├── requirements.txt               # Python dependencies
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app entry point
│   │   │
│   │   ├── core/                      # Core configurations
│   │   │   ├── __init__.py
│   │   │   └── config.py              # Settings & environment variables
│   │   │
│   │   ├── models/                    # Data models
│   │   │   ├── __init__.py
│   │   │   └── schemas.py             # Pydantic schemas
│   │   │
│   │   ├── api/                       # API layer
│   │   │   ├── __init__.py
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── upload.py          # POST /api/upload
│   │   │       ├── analyze.py         # GET /api/analyze/{file_id}
│   │   │       └── preprocess.py      # POST /api/preprocess/{file_id}
│   │   │
│   │   ├── services/                  # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── file_handler.py        # File operations
│   │   │   ├── data_analyzer.py       # Issue detection (15+ checks)
│   │   │   └── data_preprocessor.py   # Data transformation
│   │   │
│   │   └── utils/                     # Helper functions
│   │       └── __init__.py
│   │
│   ├── uploads/                       # Uploaded files (auto-created)
│   ├── temp/                          # Processed files (auto-created)
│   └── tests/                         # Unit tests
│
└── frontend/                          # Next.js React Frontend
    ├── README.md                      # Frontend documentation
    ├── package.json                   # Node dependencies
    ├── tsconfig.json                  # TypeScript configuration
    ├── next.config.js                 # Next.js configuration
    ├── tailwind.config.js             # Tailwind CSS configuration
    ├── postcss.config.js              # PostCSS configuration
    ├── .eslintrc.json                 # ESLint rules
    ├── .env.local                     # Environment variables
    │
    ├── public/                        # Static assets
    │
    └── src/
        ├── app/
        │   ├── layout.tsx             # Root layout
        │   ├── page.tsx               # Home page (main UI)
        │   └── globals.css            # Global styles
        │
        ├── components/
        │   ├── FileUpload.tsx         # Drag & drop upload component
        │   ├── DataSummary.tsx        # Dataset statistics cards
        │   ├── IssueList.tsx          # Issues list with actions
        │   │
        │   └── ui/                    # Reusable UI components
        │       ├── Button.tsx
        │       ├── Card.tsx
        │       └── Badge.tsx
        │
        ├── services/
        │   ├── api.ts                 # Axios HTTP client
        │   └── dataService.ts         # API endpoint functions
        │
        ├── types/
        │   └── index.ts               # TypeScript interfaces & types
        │
        └── utils/
            └── helpers.ts             # Utility functions
```

## Key Components

### Backend Services

#### `file_handler.py`
- Upload file handling
- DataFrame loading (CSV/Excel)
- File storage & retrieval
- Processed file management

#### `data_analyzer.py`
- ✅ Missing values detection
- ✅ Duplicate rows detection
- ✅ Outliers detection (IQR method)
- ✅ Data type inconsistencies
- ✅ Categorical inconsistencies
- ✅ Constant features detection
- ✅ Correlated features detection
- ✅ Skewness analysis
- ✅ High cardinality detection
- ✅ Date format issues
- ✅ Text noise detection
- ✅ Imbalanced data detection

#### `data_preprocessor.py`
- Missing value imputation (mean/median/mode/ffill/bfill/drop)
- Duplicate removal
- Outlier handling (remove/cap/transform)
- Categorical encoding (label/one-hot/normalize)
- Date conversion & extraction
- Text cleaning (lowercase/punctuation/stopwords)
- Scaling (MinMax/Standard/Robust)
- Skewness transformation (log/sqrt/box-cox)

### Frontend Components

#### `FileUpload.tsx`
- Drag & drop interface
- File validation
- Progress indication
- Error handling

#### `DataSummary.tsx`
- File information display
- Row/column statistics
- Issue count summary
- Severity badges

#### `IssueList.tsx`
- Collapsible issue cards
- Severity indicators
- Affected columns display
- Action selection buttons
- Details expansion

#### `page.tsx` (Main Page)
- Orchestrates entire workflow
- State management
- API integration
- User interaction handling

## Data Flow

```
1. User uploads file (FileUpload)
   ↓
2. POST /api/upload → file_handler.save_uploaded_file()
   ↓
3. GET /api/analyze/{id} → data_analyzer.analyze_dataset()
   ↓
4. Display issues (IssueList) + summary (DataSummary)
   ↓
5. User selects actions or "Fix All"
   ↓
6. POST /api/preprocess/{id} → data_preprocessor.preprocess_dataset()
   ↓
7. GET /api/download/{id} → Download cleaned file
```

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Pandas** - Data manipulation
- **NumPy** - Numerical operations
- **Scikit-learn** - ML preprocessing tools
- **SciPy** - Statistical functions
- **Pydantic** - Data validation

### Frontend
- **Next.js 14** - React framework (App Router)
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **react-dropzone** - File upload
- **lucide-react** - Icons
- **recharts** - Charts (optional)

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload CSV/Excel file |
| GET | `/api/analyze/{file_id}` | Analyze for issues |
| GET | `/api/analyze/{file_id}/preview` | Preview data |
| POST | `/api/preprocess/{file_id}` | Apply actions |
| POST | `/api/preprocess/{file_id}/fix-all` | Auto-fix all |
| GET | `/api/download/{file_id}` | Download result |
| DELETE | `/api/upload/{file_id}` | Delete file |

## Configuration Files

- **backend/app/core/config.py** - Backend settings
- **frontend/.env.local** - Frontend environment variables
- **frontend/tailwind.config.js** - UI theme
- **backend/requirements.txt** - Python packages
- **frontend/package.json** - Node packages
