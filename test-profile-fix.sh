#!/bin/bash

echo "🧪 Testing User Profile Statistics Fix"
echo "======================================="

echo "✅ Changes made:"
echo "  1. Development frontend now runs on port 80"
echo "  2. Backend OAuth callback now stores complete user profile data"
echo "  3. Frontend checkAuthStatus() now handles incomplete session data"
echo "  4. Added debug logging to track profile data flow"
echo ""

echo "🔍 Verifying configuration files..."

# Check if start-dev.sh uses port 80
if grep -q "PORT=80" /home/jzhu/projects/repos/learn-oauth-flow/start-dev.sh; then
    echo "✅ start-dev.sh configured for port 80"
else
    echo "❌ start-dev.sh not configured for port 80"
fi

# Check if package.json has port 80
if grep -q "PORT=80" /home/jzhu/projects/repos/learn-oauth-flow/frontend/package.json; then
    echo "✅ package.json configured for port 80"
else
    echo "❌ package.json not configured for port 80"
fi

# Check CORS configuration
if grep -q "http://localhost:80" /home/jzhu/projects/repos/learn-oauth-flow/backend/oauth_backend.py; then
    echo "✅ Backend CORS configured for port 80"
else
    echo "❌ Backend CORS not configured for port 80"
fi

echo ""
echo "🚀 To test the fix:"
echo "  1. Make sure your GitHub OAuth app callback URL is: http://localhost:5000/api/callback"
echo "  2. Set your environment variables: GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET"
echo "  3. Run: ./start-dev.sh"
echo "  4. Open: http://localhost (or http://localhost:80)"
echo "  5. Login and check if the User Profile page shows correct statistics"
echo ""
echo "🐛 Debug info will be available in:"
echo "  - Browser console (F12) - frontend debug logs"
echo "  - Backend terminal - server debug logs"
