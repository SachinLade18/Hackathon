#!/usr/bin/env python3
"""
Test script for private GitLab project access.
This script helps verify that your GitLab access token and project ID work correctly.
"""

import os
import sys
import requests

def test_gitlab_project(project_id, username, gitlab_token):
    """Test access to GitLab project with authentication."""
    
    print(f"🔍 Testing GitLab Project Access")
    print(f"📊 Project ID: {project_id}")
    print(f"👤 Username: {username}")
    print(f"🔑 Token: {'✅ Provided' if gitlab_token else '❌ Missing'}")
    print("-" * 50)
    
    # Test 1: Direct API access
    print("Test 1: Direct GitLab API Access")
    try:
        headers = {"PRIVATE-TOKEN": gitlab_token} if gitlab_token else {}
        url = f"https://gitlab.com/api/v4/projects/{project_id}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            project_data = response.json()
            print(f"✅ Project found: {project_data.get('name', 'Unknown')}")
            print(f"   Namespace: {project_data.get('namespace', {}).get('full_path', 'Unknown')}")
            print(f"   Visibility: {project_data.get('visibility', 'Unknown')}")
        elif response.status_code == 404:
            print("❌ Project not found (404)")
            print("   Possible causes:")
            print("   - Project ID is incorrect")
            print("   - Project is private and token doesn't have access")
            print("   - Token is invalid")
            return False
        elif response.status_code == 401:
            print("❌ Unauthorized (401)")
            print("   Possible causes:")
            print("   - Token is missing or invalid")
            print("   - Token doesn't have 'read_api' scope")
            return False
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False
    
    print()
    
    # Test 2: Backend API access
    print("Test 2: Backend API Access")
    try:
        # Set environment variable temporarily
        if gitlab_token:
            os.environ['GITLAB_ACCESS_TOKEN'] = gitlab_token
        
        backend_url = "http://localhost:8000"
        payload = {
            "project_url": str(project_id),  # Use project ID as string
            "username": username
        }
        
        response = requests.post(
            f"{backend_url}/fetch_issues",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                issues = data.get('issues', [])
                print(f"✅ Backend API success: Found {len(issues)} issues")
                
                if issues:
                    print("   Sample issues:")
                    for issue in issues[:3]:  # Show first 3 issues
                        print(f"   - #{issue.get('iid')}: {issue.get('title', 'No title')[:60]}...")
                else:
                    print("   No issues found for this username")
                return True
            else:
                print(f"❌ Backend API error: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Backend API returned {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server")
        print("   Make sure the backend is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    """Main test function."""
    
    # Your project details
    PROJECT_ID = "71150749"
    USERNAME = "sachin.lade"  # Replace with actual username you want to test
    
    print("🔧 GitLab Private Project Access Test")
    print("=" * 50)
    print()
    
    # Get GitLab token from environment or prompt
    gitlab_token = os.getenv('GITLAB_ACCESS_TOKEN')
    
    if not gitlab_token:
        print("❌ GITLAB_ACCESS_TOKEN environment variable not set!")
        print()
        print("To fix this:")
        print("1. Get a token from: https://gitlab.com/-/profile/personal_access_tokens")
        print("2. Create token with 'read_api' scope")
        print("3. Set environment variable:")
        print("   export GITLAB_ACCESS_TOKEN='your-token-here'")
        print("4. Restart this script")
        print()
        
        # Optionally allow manual input for testing
        token_input = input("Or enter token manually for this test (will not be saved): ").strip()
        if token_input:
            gitlab_token = token_input
        else:
            print("❌ No token provided. Exiting.")
            sys.exit(1)
    
    # Run tests
    success = test_gitlab_project(PROJECT_ID, USERNAME, gitlab_token)
    
    print()
    print("=" * 50)
    if success:
        print("✅ All tests passed! Your setup is working correctly.")
        print()
        print("You can now use the Streamlit app with:")
        print(f"   Project URL: {PROJECT_ID}")
        print(f"   Username: {USERNAME}")
        print()
        print("Or try the API directly at: http://localhost:8000")
    else:
        print("❌ Tests failed. Please check the error messages above.")
        print()
        print("Common solutions:")
        print("1. Verify your GitLab token has 'read_api' scope")
        print("2. Check that the project ID is correct")
        print("3. Ensure the username exists and has issues in the project")
        print("4. Make sure the backend server is running")

if __name__ == "__main__":
    main() 