# System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                 │
│                     (Web Browser)                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP/HTTPS
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   FRONTEND (Port 3000)                       │
│                  Next.js 14 + React                          │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ FileUpload   │  │ DataSummary  │  │  IssueList   │     │
│  │ Component    │  │  Component   │  │  Component   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         API Service (Axios)                        │    │
│  │  - uploadFile()                                    │    │
│  │  - analyzeFile()                                   │    │
│  │  - preprocessFile()                                │    │
│  │  - downloadFile()                                  │    │
│  └────────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ REST API
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   BACKEND (Port 8000)                        │
│                      FastAPI                                 │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              API ROUTES                            │    │
│  │  POST   /api/upload                                │    │
│  │  GET    /api/analyze/{file_id}                     │    │
│  │  GET    /api/analyze/{file_id}/preview             │    │
│  │  POST   /api/preprocess/{file_id}                  │    │
│  │  POST   /api/preprocess/{file_id}/fix-all          │    │
│  │  GET    /api/download/{file_id}                    │    │
│  │  DELETE /api/upload/{file_id}                      │    │
│  └────────────────────────────────────────────────────┘    │
│                         │                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │              SERVICES LAYER                        │    │
│  │                                                     │    │
│  │  ┌──────────────────┐  ┌──────────────────┐      │    │
│  │  │  FileHandler     │  │  DataAnalyzer    │      │    │
│  │  │  - save()        │  │  - analyze()     │      │    │
│  │  │  - load()        │  │  - check_*()     │      │    │
│  │  │  - delete()      │  │  - detect()      │      │    │
│  │  └──────────────────┘  └──────────────────┘      │    │
│  │                                                     │    │
│  │  ┌──────────────────────────────────────┐         │    │
│  │  │     DataPreprocessor                 │         │    │
│  │  │  - preprocess()                      │         │    │
│  │  │  - handle_missing()                  │         │    │
│  │  │  - handle_outliers()                 │         │    │
│  │  │  - handle_categorical()              │         │    │
│  │  │  - fix_all()                         │         │    │
│  │  └──────────────────────────────────────┘         │    │
│  └────────────────────────────────────────────────────┘    │
│                         │                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │              DATA PROCESSING                       │    │
│  │          (Pandas, NumPy, Scikit-learn)             │    │
│  └────────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ File I/O
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   FILE STORAGE                               │
│                                                              │
│  ┌──────────────┐            ┌──────────────┐             │
│  │   uploads/   │            │    temp/     │             │
│  │  (Original)  │            │ (Processed)  │             │
│  └──────────────┘            └──────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌─────────┐
│  START  │
└────┬────┘
     │
     ▼
┌─────────────────────┐
│ User Uploads File   │
│ (CSV/Excel)         │
└────┬────────────────┘
     │
     ▼
┌──────────────────────────────┐
│ POST /api/upload             │
│ - Validate file type & size  │
│ - Generate unique file_id    │
│ - Save to uploads/           │
│ - Load with Pandas           │
│ - Return FileInfo            │
└────┬─────────────────────────┘
     │
     ▼
┌──────────────────────────────┐
│ GET /api/analyze/{file_id}   │
│                              │
│ DataAnalyzer.analyze()       │
│ ├─ Check missing values      │
│ ├─ Check duplicates          │
│ ├─ Check outliers            │
│ ├─ Check data types          │
│ ├─ Check categorical         │
│ ├─ Check skewness            │
│ ├─ Check correlations        │
│ ├─ Check dates               │
│ ├─ Check text noise          │
│ └─ Check imbalance           │
│                              │
│ Return AnalysisResponse      │
└────┬─────────────────────────┘
     │
     ▼
┌──────────────────────────────┐
│ Display Issues to User       │
│ - Show severity badges       │
│ - List affected columns      │
│ - Show statistics            │
│ - Provide action buttons     │
└────┬─────────────────────────┘
     │
     ├──────────┬───────────────┐
     │          │               │
     ▼          ▼               ▼
  ┌────┐   ┌─────┐   ┌──────────────┐
  │Fix │   │Apply│   │ Individual   │
  │All │   │Multi│   │   Actions    │
  └─┬──┘   └──┬──┘   └──────┬───────┘
    │         │              │
    └─────────┴──────────────┘
              │
              ▼
┌──────────────────────────────────────┐
│ POST /api/preprocess/{file_id}       │
│                                      │
│ DataPreprocessor.preprocess()        │
│ For each action:                     │
│ ├─ Handle missing values             │
│ │  └─ mean/median/mode/drop          │
│ ├─ Handle outliers                   │
│ │  └─ remove/cap/transform           │
│ ├─ Handle duplicates                 │
│ │  └─ remove                         │
│ ├─ Handle categorical                │
│ │  └─ encode/normalize               │
│ ├─ Handle dates                      │
│ │  └─ convert/extract                │
│ └─ Handle text                       │
│    └─ clean/lowercase                │
│                                      │
│ Save to temp/{file_id}_processed.csv │
│ Return PreprocessResponse            │
└────┬─────────────────────────────────┘
     │
     ▼
┌──────────────────────────────┐
│ Display Success Message      │
│ - Show applied actions       │
│ - Show statistics            │
│ - Provide download button    │
└────┬─────────────────────────┘
     │
     ▼
┌──────────────────────────────┐
│ GET /api/download/{file_id}  │
│ - Return processed CSV       │
│ - User downloads file        │
└────┬─────────────────────────┘
     │
     ▼
┌─────────┐
│   END   │
└─────────┘
```

## Component Interaction

```
Frontend Components:
┌────────────────────────────────────────────────────────┐
│                     page.tsx (Main)                    │
│  - Orchestrates entire workflow                        │
│  - Manages state (fileInfo, analysis, actions)         │
│  - Handles user interactions                           │
└────┬──────────────────┬──────────────────┬────────────┘
     │                  │                  │
     ▼                  ▼                  ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ FileUpload  │  │ DataSummary │  │  IssueList  │
│             │  │             │  │             │
│ - Dropzone  │  │ - Cards     │  │ - Issues    │
│ - Validate  │  │ - Stats     │  │ - Actions   │
│ - Upload    │  │ - Badges    │  │ - Expand    │
└─────────────┘  └─────────────┘  └─────────────┘
```

## Issue Detection Flow

```
DataFrame Input
      │
      ▼
┌─────────────────┐
│ Check Missing   │──► Count nulls per column
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│ Check Duplicates│──► Count duplicate rows
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│ Check Outliers  │──► IQR method on numeric cols
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│ Check Types     │──► Mixed types detection
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│Check Categorical│──► Inconsistent naming
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│ Check Constant  │──► Single unique value
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│Check Correlation│──► High correlation pairs
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│ Check Skewness  │──► Distribution skew > threshold
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│Check Cardinality│──► Too many unique values
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│  Check Dates    │──► Invalid/inconsistent formats
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│  Check Text     │──► Special character ratio
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│Check Imbalance  │──► Class distribution ratio
└────┬────────────┘
     │
     ▼
  List of Issues
```

## Deployment Architecture (Production)

```
┌────────────────────────────────────────────────┐
│                 Cloud Provider                  │
│            (Azure/AWS/GCP/Heroku)              │
│                                                 │
│  ┌──────────────────────────────────────┐     │
│  │         Frontend Container            │     │
│  │         Next.js (Node.js)             │     │
│  │         Port 3000                      │     │
│  └────────────┬─────────────────────────┘     │
│               │                                 │
│               │ REST API                        │
│               │                                 │
│  ┌────────────▼─────────────────────────┐     │
│  │         Backend Container             │     │
│  │         FastAPI (Python)              │     │
│  │         Port 8000                      │     │
│  └────────────┬─────────────────────────┘     │
│               │                                 │
│               │ File I/O                        │
│               │                                 │
│  ┌────────────▼─────────────────────────┐     │
│  │       Object Storage / Volume         │     │
│  │       (for uploaded files)            │     │
│  └───────────────────────────────────────┘     │
│                                                 │
│  ┌──────────────────────────────────────┐     │
│  │         Load Balancer                 │     │
│  └──────────────────────────────────────┘     │
└────────────────────────────────────────────────┘
```
