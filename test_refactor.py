#!/usr/bin/env python3
"""
Simple test script to verify PyGithub imports work correctly
"""

try:
    from github import Github
    from github.GithubException import GithubException
    print("✓ PyGithub imports successful")
    
    # Test basic functionality (without token)
    try:
        g = Github()  # Anonymous access
        print("✓ PyGithub initialization successful")
    except Exception as e:
        print(f"✗ PyGithub initialization failed: {e}")
        
except ImportError as e:
    print(f"✗ PyGithub import failed: {e}")
    print("Please install PyGithub with: pip install PyGithub")
