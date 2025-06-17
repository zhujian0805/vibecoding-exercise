#!/bin/bash

# Vibecoding Exercise Launcher with Cache Support

echo "🚀 Starting Vibecoding Exercise with Cache..."
echo "============================================"

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

# Check if Redis is available and start if needed
echo "🔧 Setting up Redis cache..."
if command -v redis-server &> /dev/null; then
    # Check if Redis is already running
    if ! redis-cli ping &> /dev/null; then
        echo "📦 Starting Redis server..."
        redis-server --daemonize yes --port 6379 --bind 127.0.0.1
        sleep 2
        
        if redis-cli ping &> /dev/null; then
            echo "✅ Redis started successfully"
            export CACHE_TYPE=redis
            export REDIS_HOST=localhost
            export REDIS_PORT=6379
            export REDIS_DB=0
            # No password for local Redis
        else
            echo "⚠️  Redis failed to start, falling back to simple cache"
            export CACHE_TYPE=simple
        fi
    else
        echo "✅ Redis already running"
        export CACHE_TYPE=redis
        export REDIS_HOST=localhost
        export REDIS_PORT=6379
        export REDIS_DB=0
    fi
else
    echo "⚠️  Redis not found, using simple in-memory cache"
    echo "   Install Redis for better performance: sudo apt install redis-server"
    export CACHE_TYPE=simple
fi

# Set cache configuration
export CACHE_DEFAULT_TIMEOUT=300

# Set maximum repositories to fetch (0 = unlimited, but we set a reasonable default)
export MAX_REPOS_FETCH=2000

echo "🔧 Cache configuration:"
echo "   Type: $CACHE_TYPE"
echo "   Max repos fetch: $MAX_REPOS_FETCH"
if [ "$CACHE_TYPE" = "redis" ]; then
    echo "   Redis: $REDIS_HOST:$REDIS_PORT (DB: $REDIS_DB)"
fi

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
sudo npm start &
FRONTEND_PID=$!

echo ""
echo "🎉 Demo is starting up!"
echo "==============================="
echo "Backend:  http://localhost:5000"
echo "Frontend: http://localhost (port 80)"
echo "Cache:    $CACHE_TYPE"
echo ""
echo "📊 Cache endpoints available:"
echo "   http://localhost:5000/api/cache/status"
echo "   http://localhost:5000/api/cache/clear (POST)"
echo ""
echo "Press Ctrl+C to stop all servers"

# Function to clean up processes
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    
    # Stop Redis if we started it
    if [ "$CACHE_TYPE" = "redis" ] && command -v redis-cli &> /dev/null; then
        echo "🛑 Stopping Redis..."
        redis-cli shutdown 2>/dev/null || true
    fi
    
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for user to interrupt
wait
