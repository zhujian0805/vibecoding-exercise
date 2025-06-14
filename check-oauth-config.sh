#!/bin/bash

# GitHub OAuth Configuration Checker

echo "🔍 GitHub OAuth Configuration Checker"
echo "====================================="

# Check environment variables
if [ -z "$GITHUB_CLIENT_ID" ]; then
    echo "❌ GITHUB_CLIENT_ID is not set"
    MISSING_ENV=1
else
    echo "✅ GITHUB_CLIENT_ID is set: ${GITHUB_CLIENT_ID:0:8}..."
fi

if [ -z "$GITHUB_CLIENT_SECRET" ]; then
    echo "❌ GITHUB_CLIENT_SECRET is not set"
    MISSING_ENV=1
else
    echo "✅ GITHUB_CLIENT_SECRET is set: ${GITHUB_CLIENT_SECRET:0:8}..."
fi

if [ "$MISSING_ENV" = "1" ]; then
    echo ""
    echo "🚨 Missing environment variables. Set them with:"
    echo "export GITHUB_CLIENT_ID=your_github_client_id"
    echo "export GITHUB_CLIENT_SECRET=your_github_client_secret"
    exit 1
fi

echo ""
echo "📋 Configuration Summary:"
echo "========================"
echo "Expected callback URL: http://localhost:5000/api/callback"
echo "Frontend URL (demo):   http://localhost (port 80)"
echo "Frontend URL (dev):    http://localhost:3000"
echo "Backend URL:           http://localhost:5000"

echo ""
echo "🔧 GitHub OAuth App Setup:"
echo "=========================="
echo "1. Go to: https://github.com/settings/developers"
echo "2. Click 'OAuth Apps' -> 'New OAuth App'"
echo "3. Fill in the form:"
echo "   - Application name: Your app name"
echo "   - Homepage URL: http://localhost"
echo "   - Authorization callback URL: http://localhost:5000/api/callback"
echo "4. Click 'Register application'"
echo "5. Copy the Client ID and Client Secret"

echo ""
echo "⚠️  CRITICAL: The 'Authorization callback URL' in your GitHub OAuth app"
echo "    MUST exactly match: http://localhost:5000/api/callback"
echo ""
echo "If you're getting 'redirect_uri is not associated with this application':"
echo "1. Check your GitHub OAuth app settings"
echo "2. Make sure the callback URL is exactly: http://localhost:5000/api/callback"
echo "3. No trailing slashes, no extra characters"
echo "4. Use lowercase 'localhost' (not 127.0.0.1)"

echo ""
echo "🧪 To test your configuration:"
echo "1. Run: ./start-dev.sh or ./start-demo.sh"
echo "2. Visit: http://localhost:5000/api/config"
echo "3. Check that callback_url shows: http://localhost:5000/api/callback"
