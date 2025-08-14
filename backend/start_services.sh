#!/bin/bash

# Start Agentic Interviewer Services
echo "🚀 Starting Agentic Interviewer Services..."

# Kill any existing processes
pkill -f "run_scheduler.py"
pkill -f "manage.py runserver"

# Start Django server
echo "📡 Starting Django backend server..."
cd /Users/apple/Desktop/David2/Agentic-Interviewer/backend
python3 manage.py runserver localhost:8000 > server.log 2>&1 &
SERVER_PID=$!

# Start scheduler
echo "⏰ Starting call scheduler..."
python3 run_scheduler.py > scheduler.log 2>&1 &
SCHEDULER_PID=$!

# Start frontend (if needed)
echo "🌐 Starting frontend..."
cd /Users/apple/Desktop/David2/Agentic-Interviewer/frontend
npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!

echo "✅ All services started!"
echo "📡 Backend: http://localhost:8000 (PID: $SERVER_PID)"
echo "🌐 Frontend: http://localhost:5174 (PID: $FRONTEND_PID)"
echo "⏰ Scheduler: Running (PID: $SCHEDULER_PID)"
echo ""
echo "📋 To stop all services:"
echo "   kill $SERVER_PID $SCHEDULER_PID $FRONTEND_PID"
echo ""
echo "📊 To check scheduler logs:"
echo "   tail -f /Users/apple/Desktop/David2/Agentic-Interviewer/backend/scheduler.log"