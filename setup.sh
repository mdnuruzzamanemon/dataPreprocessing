#!/bin/bash

echo "========================================"
echo "Data Preprocessing Platform Setup"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check Python installation
echo -e "${YELLOW}Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Python found: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python not found. Please install Python 3.9 or higher.${NC}"
    echo -e "${YELLOW}Download from: https://www.python.org/downloads/${NC}"
    exit 1
fi

# Check Node.js installation
echo -e "${YELLOW}Checking Node.js installation...${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js found: $NODE_VERSION${NC}"
else
    echo -e "${RED}✗ Node.js not found. Please install Node.js 18 or higher.${NC}"
    echo -e "${YELLOW}Download from: https://nodejs.org/${NC}"
    exit 1
fi

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}Setting up Backend${NC}"
echo -e "${CYAN}========================================${NC}"

# Setup Backend
cd backend || exit

echo -e "${YELLOW}Creating virtual environment...${NC}"
python3 -m venv venv

echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Python dependencies installed!${NC}"
else
    echo -e "${RED}✗ Failed to install Python dependencies!${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Initializing database...${NC}"
python3 init_db.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database initialized successfully!${NC}"
    echo -e "${GREEN}✓ Backend setup completed!${NC}"
else
    echo -e "${YELLOW}⚠ Database initialization failed!${NC}"
    echo -e "${YELLOW}  Please ensure:${NC}"
    echo -e "  1. PostgreSQL is installed and running"
    echo -e "  2. Database 'data_preprocessing' exists"
    echo -e "  3. DATABASE_URL in .env is correct"
    echo ""
    echo -e "  You can manually initialize later with: python3 init_db.py"
    echo ""
fi

cd ..

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}Setting up Frontend${NC}"
echo -e "${CYAN}========================================${NC}"

# Setup Frontend
cd frontend || exit

echo -e "${YELLOW}Installing Node.js dependencies...${NC}"
npm install

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend setup completed!${NC}"
else
    echo -e "${RED}✗ Frontend setup failed!${NC}"
    exit 1
fi

cd ..

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${CYAN}Before starting the servers:${NC}"
echo -e "1. Ensure PostgreSQL is installed and running"
echo -e "2. Create database: createdb data_preprocessing"
echo -e "3. Update backend/.env with your database credentials"
echo ""
echo -e "${CYAN}To start the application:${NC}"
echo -e "1. Start backend:  ${NC}cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo -e "2. Start frontend: ${NC}cd frontend && npm run dev"
echo ""
echo -e "${YELLOW}Then open http://localhost:3000 in your browser${NC}"
echo ""
