#!/usr/bin/env python3
"""
Enhanced example usage of the GitLab issues fetcher script with LLM summarization.
Updated to use Groq API by default for fast, free AI inference.
"""

from fetch_gitlab_issues import fetch_issues_by_username, display_issues, setup_llm_client
import os

def main():
    # Your GitLab repository URL
    project_url = "https://gitlab.com/sachin.lade-group/sachin.lade-project"
    
    # Username to search for (replace with the actual username you want to search for)
    username = "your-username"  # Replace this with the actual username
    
    # Get access tokens from environment variables
    gitlab_token = os.getenv('GITLAB_ACCESS_TOKEN')
    groq_key = os.getenv('GROQ_API_KEY')
    
    print("🔍 GitLab Issues Fetcher with Groq AI Summarization")
    print("=" * 60)
    
    # Check for GitLab token
    if not gitlab_token:
        print("⚠️  No GITLAB_ACCESS_TOKEN environment variable found.")
        print("   For private repositories, you'll need to set this.")
        print("   You can create a personal access token at: https://gitlab.com/-/profile/personal_access_tokens")
        print()
    
    # Check for Groq key
    if not groq_key:
        print("⚠️  No GROQ_API_KEY environment variable found.")
        print("   AI summarization will be disabled.")
        print("   Get a FREE API key from: https://console.groq.com/keys")
        print("   Set it with: export GROQ_API_KEY='your-key-here'")
        print("   Note: Groq offers fast, free inference!")
        print()
    
    print(f"📊 Fetching issues for username '{username}' from:")
    print(f"   {project_url}")
    print()
    
    # Fetch issues (both assigned to and created by the user)
    print("🔄 Fetching issues...")
    issues = fetch_issues_by_username(
        project_url=project_url,
        username=username,
        access_token=gitlab_token,
        assignee=True,
        author=True
    )
    
    if not issues:
        print("❌ No issues found for this username.")
        print("   Make sure:")
        print("   - The username is correct")
        print("   - The user has issues in this repository")
        print("   - You have access to the repository")
        return
    
    print(f"✅ Found {len(issues)} issues!")
    print()
    
    # Setup Groq LLM client if possible
    llm_client = None
    provider = "groq"
    if groq_key:
        print("🤖 Setting up Groq AI summarization...")
        llm_client, provider = setup_llm_client("groq", groq_key)
        if llm_client:
            print("✅ Groq AI summarization ready! (Fast & Free)")
        else:
            print("❌ Failed to setup Groq AI summarization")
        print()
    
    # Display results with different levels of AI enhancement
    if llm_client:
        print("🎯 OPTION 1: Basic view (no AI)")
        print("-" * 40)
        display_issues(issues)
        
        print("\n" + "=" * 60)
        print("🤖 OPTION 2: With Groq AI Collection Summary")
        print("-" * 40)
        display_issues(
            issues, 
            llm_client=llm_client,
            provider=provider,
            model="llama-3.3-70b-versatile",
            summarize_individual=False,
            summarize_collection=True
        )
        
        print("\n" + "=" * 60)
        print("🚀 OPTION 3: Full Groq AI Enhancement (Collection + Individual Summaries)")
        print("-" * 40)
        print("⚡ Note: Groq is fast and free, so this won't take long!")
        
        # Groq is fast and free, so we can be more generous with individual summaries
        if len(issues) <= 10:
            display_issues(
                issues, 
                llm_client=llm_client,
                provider=provider,
                model="llama-3.3-70b-versatile",
                summarize_individual=True,
                summarize_collection=True
            )
        else:
            print(f"   Note: {len(issues)} issues found. Showing collection summary only.")
            print("   Run with --summarize-individual flag on command line for individual summaries.")
            print("   Good news: Groq is free, so no cost concerns!")
    else:
        print("📋 Issues found (no AI summarization available):")
        print("-" * 50)
        display_issues(issues)
    
    print("\n" + "=" * 60)
    print("💡 Pro Tips for Groq:")
    print("   • Groq is FREE and incredibly fast")
    print("   • Use --summarize-collection for quick insights")
    print("   • Use --summarize-individual for detailed analysis (also free!)")
    print("   • Available models: llama-3.3-70b-versatile (default), llama-3.1-8b-instant")
    print("   • Export to JSON: --output json > report.json")
    print("   • Get your free API key: https://console.groq.com/keys")

if __name__ == "__main__":
    main() 