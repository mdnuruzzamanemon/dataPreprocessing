# Frontend Setup Guide

## Prerequisites
- Node.js 18 or higher
- npm or yarn

## Installation Steps

### 1. Navigate to Frontend Directory
```bash
cd frontend
```

### 2. Install Dependencies
```bash
npm install
# or
yarn install
```

### 3. Configure Environment
Create a `.env.local` file (already created):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Run Development Server
```bash
npm run dev
# or
yarn dev
```

The frontend will be available at http://localhost:3000

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Home page
│   │   └── globals.css      # Global styles
│   ├── components/
│   │   ├── FileUpload.tsx   # File upload component
│   │   ├── DataSummary.tsx  # Dataset summary cards
│   │   ├── IssueList.tsx    # Issues display & actions
│   │   └── ui/              # Reusable UI components
│   │       ├── Button.tsx
│   │       ├── Card.tsx
│   │       └── Badge.tsx
│   ├── services/
│   │   ├── api.ts           # Axios configuration
│   │   └── dataService.ts   # API calls
│   ├── types/
│   │   └── index.ts         # TypeScript interfaces
│   └── utils/
│       └── helpers.ts       # Helper functions
├── public/                  # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── next.config.js
```

## Features

### File Upload
- Drag & drop interface
- CSV, XLS, XLSX support
- Max 100MB file size
- File validation

### Data Analysis
- Automatic issue detection
- 15+ issue types
- Severity classification
- Detailed statistics

### Preprocessing
- Individual action selection
- "Fix All" automatic mode
- Real-time progress
- Download cleaned data

## Building for Production

```bash
# Build the application
npm run build

# Start production server
npm start
```

## Customization

### Styling
- Uses Tailwind CSS
- Edit `tailwind.config.js` for theme
- Modify `src/app/globals.css` for custom styles

### API Configuration
- Edit `.env.local` to change API URL
- Default: http://localhost:8000

### Components
All components are in `src/components/`
- Modular and reusable
- TypeScript interfaces defined
- Tailwind CSS styling

## Troubleshooting

### Port Already in Use
```bash
# Run on different port
PORT=3001 npm run dev
```

### API Connection Issues
1. Check backend is running on port 8000
2. Verify CORS settings in backend
3. Check `.env.local` file

### TypeScript Errors
```bash
# Clear cache and reinstall
rm -rf node_modules .next
npm install
```

### Build Errors
```bash
# Check TypeScript errors
npm run build

# Fix with type checking
npx tsc --noEmit
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint
