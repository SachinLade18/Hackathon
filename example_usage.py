#!/usr/bin/env python3
"""
Example usage of the GitLab issues fetcher script.
"""

from fetch_gitlab_issues import fetch_issues_by_username, display_issues
import os

def main():
    # Your GitLab repository URL
    project_url = "https://gitlab.com/sachin.lade-group/sachin.lade-project"
    
    # Username to search for (replace with the actual username you want to search for)
    username = "your-username"  # Replace this with the actual username
    
    # Get access token from environment variable (optional for public repos)
    access_token = os.getenv('GITLAB_ACCESS_TOKEN')
    
    if not access_token:
        print("Note: No GITLAB_ACCESS_TOKEN environment variable found.")
        print("For private repositories, you'll need to set this.")
        print("You can create a personal access token at: https://gitlab.com/-/profile/personal_access_tokens")
        print("\nContinuing with public access...\n")
    
    print(f"Fetching issues for username '{username}' from:")
    print(f"{project_url}\n")
    
    # Fetch issues (both assigned to and created by the user)
    issues = fetch_issues_by_username(
        project_url=project_url,
        username=username,
        access_token=access_token,
        assignee=True,
        author=True
    )
    
    # Display the results
    display_issues(issues)

if __name__ == "__main__":
    main() 