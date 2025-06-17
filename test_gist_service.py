#!/usr/bin/env python3
"""
Test script for the updated gist service using PyGithub
"""
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.gist_service import GistRepository, GistService
from github import Github

def test_gist_service():
    """Test the gist service with a sample token"""
    # This is just a test structure - you would use a real token
    test_token = "your_real_github_token_here"
    
    print("Testing Gist Service with PyGithub...")
    
    try:
        # Test GitHub client initialization
        github_client = Github(test_token)
        print("✓ GitHub client initialized successfully")
        
        # Test repository initialization
        gist_repo = GistRepository(test_token)
        print("✓ GistRepository initialized successfully")
        
        # Test service initialization
        gist_service = GistService(gist_repo)
        print("✓ GistService initialized successfully")
        
        print("\nStructure test passed! The service is ready to use with a real GitHub token.")
        print("\nTo use this service:")
        print("1. Replace 'your_real_github_token_here' with your actual GitHub OAuth token")
        print("2. Call gist_service.get_all_gists(user_id) to fetch gists")
        print("3. The service will use PyGithub to fetch gists instead of direct API calls")
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("Make sure PyGithub is installed: pip install PyGithub")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_gist_service()
