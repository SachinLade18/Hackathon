#!/usr/bin/env python3
"""
Script to fetch GitLab issues based on username.
This script uses the python-gitlab library to interact with GitLab API.
Enhanced with LLM summarization capabilities (Groq and OpenAI support).
"""

import gitlab
import argparse
import sys
from datetime import datetime
import os
import json

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, continue without it

# LLM integration - supporting both Groq and OpenAI
try:
    import groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

def setup_llm_client(provider="groq", api_key=None):
    """Setup LLM client with API key (Groq or OpenAI)."""
    
    if provider.lower() == "groq":
        if not GROQ_AVAILABLE:
            print("Error: groq package not installed. Install with: pip install groq")
            return None, provider
        
        api_key = api_key or os.getenv('GROQ_API_KEY')
        if not api_key:
            print("Error: Groq API key not found. Set GROQ_API_KEY environment variable or use --api-key")
            print("Get your free Groq API key at: https://console.groq.com/keys")
            return None, provider
        
        try:
            client = groq.Groq(api_key=api_key)
            return client, "groq"
        except Exception as e:
            print(f"Error setting up Groq client: {e}")
            return None, provider
    
    elif provider.lower() == "openai":
        if not OPENAI_AVAILABLE:
            print("Error: openai package not installed. Install with: pip install openai")
            return None, provider
        
        api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("Error: OpenAI API key not found. Set OPENAI_API_KEY environment variable or use --api-key")
            return None, provider
        
        try:
            client = openai.OpenAI(api_key=api_key)
            return client, "openai"
        except Exception as e:
            print(f"Error setting up OpenAI client: {e}")
            return None, provider
    
    else:
        print(f"Error: Unsupported provider '{provider}'. Use 'groq' or 'openai'")
        return None, provider

def get_default_model(provider):
    """Get default model for the provider."""
    if provider == "groq":
        return "llama-3.3-70b-versatile"  # Fast and capable Groq model
    elif provider == "openai":
        return "gpt-3.5-turbo"
    else:
        return "llama-3.3-70b-versatile"

def summarize_issue_with_llm(issue, client, provider, model=None):
    """Summarize a single issue using LLM, including all comments."""
    if not client:
        return "LLM summarization not available"
    if not model:
        model = get_default_model(provider)
    # Prepare comments text
    comments_text = ""
    if hasattr(issue, 'comments') and issue.comments:
        comments_text = "\n".join([
            f"{c.get('author', 'unknown')}: {c.get('body', '')}" for c in issue.comments if c.get('body')
        ])
    # Prepare issue content for summarization
    issue_content = f"""
    Issue #{issue.iid}: {issue.title}
    State: {issue.state}
    Author: {issue.author['name']} (@{issue.author['username']})
    Created: {issue.created_at}
    Description:
    {issue.description or 'No description provided'}
    Comments:
    {comments_text or 'No comments'}
    """
    prompt = f"""
    Please provide a concise summary (2-3 sentences) of this GitLab issue, including the latest updates and discussions from the comments:
    {issue_content}
    Focus on:
    - What the issue is about
    - Current status/state
    - Key actionable points or recent discussions from the comments
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes software development issues clearly and concisely, including the latest comments."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating summary: {e}"

def summarize_issues_collection_with_llm(issues, client, provider, model=None):
    """Summarize a collection of issues using LLM."""
    if not client or not issues:
        return "No issues to summarize or LLM not available"
    
    if not model:
        model = get_default_model(provider)
    
    # Prepare overview of all issues
    issues_overview = f"Total issues: {len(issues)}\n\n"
    
    for issue in issues[:10]:  # Limit to first 10 issues for context
        issues_overview += f"- Issue #{issue.iid}: {issue.title} ({issue.state})\n"
        if issue.description:
            desc_preview = issue.description[:100] + "..." if len(issue.description) > 100 else issue.description
            issues_overview += f"  Description: {desc_preview}\n"
        issues_overview += "\n"
    
    if len(issues) > 10:
        issues_overview += f"... and {len(issues) - 10} more issues\n"
    
    prompt = f"""
    Please provide a high-level summary of this collection of GitLab issues:
    
    {issues_overview}
    
    Include:
    - Overall themes or patterns
    - Distribution of issue states (open/closed)
    - Key areas of focus or concern
    - Any notable trends
    
    Keep it concise (3-4 sentences).
    """
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes and summarizes software development issues to provide insights."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"Error generating collection summary: {e}"

def summarize_comment_with_llm(comment, client, provider, model=None):
    """Summarize a single comment using LLM."""
    if not client:
        return "LLM summarization not available"
    if not model:
        model = get_default_model(provider)
    comment_content = f"""
    Comment by {comment['author']} at {comment['created_at']}:
    {comment['body']}
    """
    prompt = f"""
    Please provide a concise summary (1-2 sentences) of this GitLab comment:
    {comment_content}
    Focus on the main point or update in the comment.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes software development comments clearly and concisely."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=80,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating comment summary: {e}"

def fetch_issues_by_username(project_url, username, access_token=None, assignee=True, author=True, llm_client=None, provider=None, model=None):
    """
    Fetch GitLab issues based on username, including all comments and their summaries.
    """
    # Extract project path from URL or use project ID directly
    if project_url.startswith('https://gitlab.com/'):
        project_path = project_url.replace('https://gitlab.com/', '')
        gitlab_url = 'https://gitlab.com'
    elif project_url.isdigit():
        # Project ID provided directly
        project_path = int(project_url)
        gitlab_url = 'https://gitlab.com'
    else:
        print("Error: Please provide either a GitLab URL or project ID")
        return []
    
    try:
        # Initialize GitLab connection
        if access_token:
            gl = gitlab.Gitlab(gitlab_url, private_token=access_token)
        else:
            gl = gitlab.Gitlab(gitlab_url)
        
        # Get the project
        project = gl.projects.get(project_path)
        
        issues = []
        
        # Fetch issues assigned to the user
        if assignee:
            print(f"Fetching issues assigned to {username}...")
            assigned_issues = project.issues.list(assignee_username=username, state='all', all=True)
            issues.extend(assigned_issues)
        
        # Fetch issues created by the user
        if author:
            print(f"Fetching issues created by {username}...")
            authored_issues = project.issues.list(author_username=username, state='all', all=True)
            # Avoid duplicates
            authored_issue_ids = {issue.iid for issue in issues}
            for issue in authored_issues:
                if issue.iid not in authored_issue_ids:
                    issues.append(issue)
        
        # For each issue, fetch all comments (notes) and summarize them if LLM is provided
        for issue in issues:
            comments = []
            try:
                notes = issue.notes.list(all=True, sort='asc')
                for note in notes:
                    comment = {
                        'id': note.id,
                        'author': note.author['username'],
                        'body': note.body,
                        'created_at': note.created_at
                    }
                    if llm_client and provider:
                        comment['llm_summary'] = summarize_comment_with_llm(comment, llm_client, provider, model)
                    comments.append(comment)
            except Exception as e:
                comments.append({'error': f'Failed to fetch or summarize comments: {e}'})
            issue.comments = comments
        
        return issues
        
    except gitlab.GitlabError as e:
        print(f"GitLab API Error: {e}")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def display_issues(issues, llm_client=None, provider="groq", model=None, summarize_individual=False, summarize_collection=False):
    """Display issues in a formatted way with optional LLM summaries."""
    if not issues:
        print("No issues found.")
        return
    
    # Collection summary first if requested
    if summarize_collection and llm_client:
        print("=" * 80)
        print(f"COLLECTION SUMMARY (Generated by {provider.upper()} AI)")
        print("=" * 80)
        collection_summary = summarize_issues_collection_with_llm(issues, llm_client, provider, model)
        print(collection_summary)
        print("=" * 80)
        print()
    
    print(f"\nFound {len(issues)} issue(s):\n")
    print("-" * 80)
    
    for issue in issues:
        created_at = datetime.fromisoformat(issue.created_at.replace('Z', '+00:00'))
        updated_at = datetime.fromisoformat(issue.updated_at.replace('Z', '+00:00'))
        
        print(f"Issue #{issue.iid}: {issue.title}")
        print(f"State: {issue.state}")
        print(f"Author: {issue.author['name']} (@{issue.author['username']})")
        if hasattr(issue, 'assignee') and issue.assignee:
            print(f"Assignee: {issue.assignee['name']} (@{issue.assignee['username']})")
        else:
            print("Assignee: Unassigned")
        print(f"Created: {created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Updated: {updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"URL: {issue.web_url}")
        
        if issue.description:
            # Show first 100 characters of description
            desc_preview = issue.description[:100] + "..." if len(issue.description) > 100 else issue.description
            print(f"Description: {desc_preview}")
        
        # Add LLM summary if requested
        if summarize_individual and llm_client:
            print(f"\n🤖 {provider.upper()} AI Summary:")
            summary = summarize_issue_with_llm(issue, llm_client, provider, model)
            print(f"   {summary}")
        
        print("-" * 80)

def main():
    parser = argparse.ArgumentParser(description='Fetch GitLab issues by username with optional LLM summarization (Groq/OpenAI)')
    parser.add_argument('--project-url', required=True, help='GitLab project URL')
    parser.add_argument('--username', required=True, help='Username to filter issues by')
    parser.add_argument('--token', help='GitLab access token (for private repos or higher rate limits)')
    parser.add_argument('--assignee-only', action='store_true', help='Only fetch issues assigned to the user')
    parser.add_argument('--author-only', action='store_true', help='Only fetch issues created by the user')
    parser.add_argument('--output', choices=['console', 'json'], default='console', help='Output format')
    
    # LLM options
    parser.add_argument('--summarize-individual', action='store_true', help='Generate LLM summary for each individual issue')
    parser.add_argument('--summarize-collection', action='store_true', help='Generate LLM summary for the entire collection of issues')
    parser.add_argument('--provider', choices=['groq', 'openai'], default='groq', help='LLM provider to use (default: groq)')
    parser.add_argument('--api-key', help='LLM API key (or set GROQ_API_KEY/OPENAI_API_KEY env var)')
    parser.add_argument('--llm-model', help='LLM model to use (defaults: groq=llama-3.3-70b-versatile, openai=gpt-3.5-turbo)')
    
    args = parser.parse_args()
    
    # Determine what to fetch
    fetch_assignee = not args.author_only
    fetch_author = not args.assignee_only
    
    # Get access token from environment if not provided
    access_token = args.token or os.getenv('GITLAB_ACCESS_TOKEN')
    
    if not access_token:
        print("Warning: No access token provided. Only public repositories will be accessible.")
        print("Set GITLAB_ACCESS_TOKEN environment variable or use --token for private repos.")
    
    # Setup LLM client if summarization is requested
    llm_client = None
    provider = args.provider
    if args.summarize_individual or args.summarize_collection:
        if provider == "groq" and not GROQ_AVAILABLE:
            print("Error: Groq package not installed. Install with: pip install groq")
            sys.exit(1)
        elif provider == "openai" and not OPENAI_AVAILABLE:
            print("Error: OpenAI package not installed. Install with: pip install openai")
            sys.exit(1)
        
        llm_client, provider = setup_llm_client(provider, args.api_key)
        if not llm_client:
            print("Warning: LLM summarization disabled due to setup issues.")
    
    # Get model (use default if not specified)
    model = args.llm_model or get_default_model(provider)
    
    # Fetch issues
    issues = fetch_issues_by_username(
        args.project_url, 
        args.username, 
        access_token, 
        assignee=fetch_assignee, 
        author=fetch_author,
        llm_client=llm_client,
        provider=provider,
        model=model
    )
    
    # Display results
    if args.output == 'json':
        issue_data = []
        for issue in issues:
            issue_info = {
                'iid': issue.iid,
                'title': issue.title,
                'state': issue.state,
                'author': issue.author['username'],
                'assignee': issue.assignee['username'] if issue.assignee else None,
                'created_at': issue.created_at,
                'updated_at': issue.updated_at,
                'web_url': issue.web_url,
                'description': issue.description
            }
            
            # Add LLM summaries to JSON output
            if args.summarize_individual and llm_client:
                issue_info['llm_summary'] = summarize_issue_with_llm(issue, llm_client, provider, model)
                issue_info['llm_provider'] = provider
                issue_info['llm_model'] = model
            
            issue_data.append(issue_info)
        
        # Add collection summary to JSON output
        output_data = {
            'issues': issue_data,
            'total_count': len(issues)
        }
        
        if args.summarize_collection and llm_client:
            output_data['collection_summary'] = summarize_issues_collection_with_llm(issues, llm_client, provider, model)
            output_data['llm_provider'] = provider
            output_data['llm_model'] = model
        
        print(json.dumps(output_data, indent=2))
    else:
        display_issues(
            issues, 
            llm_client=llm_client, 
            provider=provider,
            model=model,
            summarize_individual=args.summarize_individual,
            summarize_collection=args.summarize_collection
        )

if __name__ == "__main__":
    main() 