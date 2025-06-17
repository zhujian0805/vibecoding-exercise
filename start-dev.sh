#!/bin/bash

# Vibecoding Exercise Launcher (Development Mode - Port 80)

echo "🚀 Starting Vibecoding Exercise (Development Mode)..."
echo "=================================================="

# Check if environment variables are set
if [ -z "$GITHUB_CLIENT_ID" ] || [ -z "$GITHUB_CLIENT_SECRET" ]; then
    echo "❌ Error: GitHub OAuth environment variables not set!"
    echo ""
    echo "Please set the following environment variables:"
    echo "export GITHUB_CLIENT_ID=your_github_client_id"
    echo "export GITHUB_CLIENT_SECRET=your_github_client_secret"
    echo ""
    echo "To get these values:"
    echo "1. Go to https://github.com/settings/developers"
    echo "2. Click 'New OAuth App'"
    echo "3. Set Authorization callback URL to: http://localhost:5000/api/callback"
    echo "4. Copy the Client ID and Client Secret"
    echo ""
    echo "⚠️  IMPORTANT: Make sure the callback URL in your GitHub OAuth app"
    echo "    exactly matches: http://localhost:5000/api/callback"
    exit 1
fi

echo "✅ Environment variables configured"

# Start backend in background
echo "🐍 Starting Flask backend on port 5000..."
cd /home/jzhu/projects/repos/learn-oauth-flow/backend
python oauth_backend.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "⚛️  Starting React frontend on port 80..."
cd /home/jzhu/projects/repos/learn-oauth-flow/frontend

# Check if we need to install dependencies
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Start frontend (will run on port 80)
PORT=80 npm start &
FRONTEND_PID=$!

echo ""
echo "🎉 Demo is starting up!"
echo "==============================="
echo "Backend:  http://localhost:5000"
echo "Frontend: http://localhost:80"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to clean up processes
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for user to interrupt
wait
