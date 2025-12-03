#!/bin/bash

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Starting Data Preprocessing Platform...${NC}"

# Start backend in background
echo -e "${CYAN}Starting Backend Server...${NC}"
cd backend || exit
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 2

# Start frontend in background
echo -e "${CYAN}Starting Frontend Server...${NC}"
cd frontend || exit
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo -e "${GREEN}Servers are running!${NC}"
echo -e "${CYAN}Backend: http://localhost:8000${NC}"
echo -e "${CYAN}Frontend: http://localhost:3000${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
