#!/usr/bin/env python3
"""
Simple test script to debug the OAuth backend repositories endpoint
"""

import requests
import json
import sys
import time

def test_repositories_endpoint():
    """Test the repositories endpoint with various debugging"""
    
    base_url = "http://localhost:5000"
    
    print("Testing OAuth Backend Repository Endpoint")
    print("=" * 50)
    
    # Test health endpoint first
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        print(f"   Health status: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"   Health check failed: {e}")
        return
    
    # Test config endpoint
    print("\n2. Testing config endpoint...")
    try:
        response = requests.get(f"{base_url}/api/config", timeout=5)
        print(f"   Config status: {response.status_code}")
        print(f"   Config: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   Config check failed: {e}")
    
    # Test rate limit endpoint (requires auth)
    print("\n3. Testing rate limit endpoint...")
    try:
        session = requests.Session()
        response = session.get(f"{base_url}/api/debug/rate-limit", timeout=10)
        if response.status_code == 401:
            print("   Rate limit check requires authentication (expected)")
        else:
            print(f"   Rate limit status: {response.status_code}")
            print(f"   Rate limit: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   Rate limit check failed: {e}")
    
    # Test simple repos endpoint (requires auth)
    print("\n4. Testing simple repos endpoint...")
    try:
        session = requests.Session()
        response = session.get(f"{base_url}/api/debug/simple-repos", timeout=15)
        if response.status_code == 401:
            print("   Simple repos check requires authentication (expected)")
        else:
            print(f"   Simple repos status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Found {data.get('count', 0)} repositories in {data.get('processing_time', 0):.2f}s")
            else:
                print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Simple repos check failed: {e}")
    
    # Test full repositories endpoint (requires auth)
    print("\n5. Testing full repositories endpoint...")
    try:
        session = requests.Session()
        start_time = time.time()
        response = session.get(f"{base_url}/api/repositories?per_page=5", timeout=30)
        end_time = time.time()
        
        if response.status_code == 401:
            print("   Full repos check requires authentication (expected)")
        else:
            print(f"   Full repos status: {response.status_code}")
            print(f"   Request took {end_time - start_time:.2f} seconds")
            if response.status_code == 200:
                data = response.json()
                print(f"   Found {data.get('total_count', 0)} repositories")
                if 'debug_info' in data:
                    print(f"   Processing time: {data['debug_info'].get('processing_time', 0):.2f}s")
            else:
                print(f"   Error: {response.text[:200]}...")
    except requests.exceptions.Timeout:
        print("   Full repos request timed out after 30 seconds")
    except Exception as e:
        print(f"   Full repos check failed: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_repositories_endpoint()
