#!/bin/bash

# Test script to verify cache and pagination improvements

echo "🧪 Testing Cache and Pagination Improvements"
echo "==========================================="

# Test Redis setup
echo "📦 Testing Redis setup..."
if command -v redis-server &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo "✅ Redis is running and accessible"
    else
        echo "❌ Redis is not responding"
    fi
else
    echo "⚠️  Redis not installed - will use simple cache"
fi

# Test backend endpoints (requires backend to be running)
echo ""
echo "🔧 Testing backend endpoints..."

# Test health endpoint
if curl -s "http://localhost:5000/api/health" &> /dev/null; then
    echo "✅ Backend is running"
    
    # Test cache status
    echo "📊 Cache status:"
    curl -s "http://localhost:5000/api/cache/status" | grep -o '"cache_type":"[^"]*"' || echo "   (requires authentication)"
    
    # Test config endpoint
    echo "🔧 Backend config:"
    curl -s "http://localhost:5000/api/config" | grep -o '"cache_type":"[^"]*"' || echo "   Cache type: unknown"
    
else
    echo "❌ Backend is not running"
    echo "   Start with: ./start-demo.sh"
fi

echo ""
echo "✅ Test completed!"
echo ""
echo "To test pagination:"
echo "1. Start the demo: ./start-demo.sh"
echo "2. Login via http://localhost"
echo "3. Go to repositories page"
echo "4. Check browser console for debug logs"
echo "5. Try clicking Next/Previous buttons"
echo ""
echo "Expected improvements:"
echo "• All repositories loaded (not limited to 50)"
echo "• Pagination works correctly"
echo "• Cache speeds up subsequent requests"
echo "• Debug logs show cache hits/misses"
