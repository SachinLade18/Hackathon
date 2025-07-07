from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from datetime import datetime
import json

# Import our enhanced GitLab issues functionality
from fetch_gitlab_issues import (
    fetch_issues_by_username, 
    setup_llm_client, 
    summarize_issue_with_llm, 
    summarize_issues_collection_with_llm,
    get_default_model
)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Global variables for caching LLM client
_llm_client = None
_llm_provider = None

def get_llm_client():
    """Get or initialize LLM client."""
    global _llm_client, _llm_provider
    
    if _llm_client is None:
        # Try Groq first, then OpenAI
        groq_key = os.getenv('GROQ_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        
        if groq_key:
            _llm_client, _llm_provider = setup_llm_client("groq", groq_key)
        elif openai_key:
            _llm_client, _llm_provider = setup_llm_client("openai", openai_key)
        else:
            return None, None
    
    return _llm_client, _llm_provider

@app.route('/')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'message': 'GitLab Issues API with AI Summarization',
        'endpoints': {
            'health': '/',
            'fetch_issues': '/fetch_issues [POST]',
            'summarize': '/summarize [POST]',
            'fetch_and_summarize': '/fetch_and_summarize [POST]',
            'demo_issues': '/demo_issues [GET]'
        }
    })

def fetch_issues_logic(data):
    """Core logic for fetching issues, returns (dict, status_code)"""
    # Required parameters
    project_url = data.get('project_url')
    username = data.get('username') or data.get('user')  # Support both field names
    if not project_url or not username:
        return {'error': 'Missing required fields: project_url and username', 'success': False}, 400
    # Optional parameters
    access_token = data.get('access_token') or os.getenv('GITLAB_ACCESS_TOKEN')
    assignee_only = data.get('assignee_only', False)
    author_only = data.get('author_only', False)
    # Determine what to fetch
    fetch_assignee = not author_only
    fetch_author = not assignee_only
    # Fetch issues using our enhanced function
    issues = fetch_issues_by_username(
        project_url=project_url,
        username=username,
        access_token=access_token,
        assignee=fetch_assignee,
        author=fetch_author
    )
    # Convert GitLab issue objects to JSON-serializable format
    issues_data = []
    for issue in issues:
        issue_data = {
            'iid': issue.iid,
            'id': issue.id,
            'title': issue.title,
            'state': issue.state,
            'created_at': issue.created_at,
            'updated_at': issue.updated_at,
            'closed_at': getattr(issue, 'closed_at', None),
            'author': {
                'username': issue.author['username'],
                'name': issue.author['name']
            },
            'assignee': {
                'username': issue.assignee['username'],
                'name': issue.assignee['name']
            } if issue.assignee else None,
            'web_url': issue.web_url,
            'description': issue.description
        }
        issues_data.append(issue_data)
    return {
        'success': True,
        'issues': issues_data,
        'count': len(issues_data),
        'project_url': project_url,
        'username': username
    }, 200

@app.route('/fetch_issues', methods=['POST'])
def fetch_issues():
    """Fetch GitLab issues by username."""
    try:
        data = request.json
        if not isinstance(data, dict):
            return jsonify({'error': 'Invalid or missing JSON body'}), 400
        result, status = fetch_issues_logic(data)
        return jsonify(result), status
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

def summarize_logic(data):
    """Core logic for summarizing issues, returns (dict, status_code)"""
    issues_data = data.get('issues', [])
    query = data.get('query', '')
    summary_type = data.get('type', 'collection')  # 'collection' or 'individual'
    provider = data.get('provider', 'groq')
    model = data.get('model')
    if not issues_data:
        return {'error': 'No issues provided for summarization', 'success': False}, 400
    # Get LLM client
    llm_client, current_provider = get_llm_client()
    if not llm_client:
        return {'error': 'No AI provider available. Set GROQ_API_KEY or OPENAI_API_KEY', 'success': False}, 400
    # Use requested provider if different from current
    if provider != current_provider:
        api_key = os.getenv('GROQ_API_KEY') if provider == 'groq' else os.getenv('OPENAI_API_KEY')
        if api_key:
            llm_client, current_provider = setup_llm_client(provider, api_key)
    # Get model (use default if not specified)
    if not model:
        model = get_default_model(current_provider)
    # Create mock issue objects for our summarization functions
    class MockIssue:
        def __init__(self, issue_data):
            self.iid = issue_data.get('iid', issue_data.get('id'))
            self.title = issue_data.get('title', '')
            self.state = issue_data.get('state', '')
            self.created_at = issue_data.get('created_at', '')
            self.description = issue_data.get('description', '')
            self.author = issue_data.get('author', {'username': 'unknown', 'name': 'Unknown'})
    mock_issues = [MockIssue(issue) for issue in issues_data]
    results = {
        'success': True,
        'provider': current_provider,
        'model': model,
        'query': query
    }
    if summary_type == 'individual':
        # Generate individual summaries
        individual_summaries = []
        for i, issue in enumerate(mock_issues):
            summary = summarize_issue_with_llm(issue, llm_client, current_provider, model)
            individual_summaries.append({
                'issue_id': issue.iid,
                'title': issue.title,
                'summary': summary
            })
        results['individual_summaries'] = individual_summaries
    # Generate collection summary
    if query:
        # Custom query-based summary
        issues_overview = f"User Query: {query}\n\nIssues Summary:\n"
        for issue in mock_issues[:10]:  # Limit for context
            issues_overview += f"- Issue #{issue.iid}: {issue.title} ({issue.state})\n"
        prompt = f"""
        Based on the user's query: "{query}"
        Please analyze these GitLab issues and provide a relevant response:
        {issues_overview}
        Focus on answering the user's specific question while providing insights from the issues.
        """
    else:
        # Standard collection summary
        prompt = None
    if prompt:
        # Custom prompt for query-based summary
        try:
            response = llm_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes GitLab issues and answers user questions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            collection_summary = response.choices[0].message.content.strip()
        except Exception as e:
            collection_summary = f"Error generating custom summary: {e}"
    else:
        # Standard collection summary
        collection_summary = summarize_issues_collection_with_llm(mock_issues, llm_client, current_provider, model)
    results['collection_summary'] = collection_summary
    return results, 200

@app.route('/summarize', methods=['POST'])
def summarize():
    """Summarize issues using AI."""
    try:
        data = request.json
        if not isinstance(data, dict):
            return jsonify({'error': 'Invalid or missing JSON body'}), 400
        result, status = summarize_logic(data)
        return jsonify(result), status
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/fetch_and_summarize', methods=['POST'])
def fetch_and_summarize():
    """Fetch issues and summarize them in one call."""
    try:
        data = request.json
        if not isinstance(data, dict):
            return jsonify({'error': 'Invalid or missing JSON body'}), 400
        # First fetch issues
        fetch_data, fetch_status = fetch_issues_logic(data)
        if fetch_status != 200 or not fetch_data.get('success'):
            return jsonify(fetch_data), fetch_status
        issues = fetch_data['issues']
        # Then summarize if AI is requested
        if data.get('summarize', False) and issues:
            summarize_data = {
                'issues': issues,
                'query': data.get('query', ''),
                'type': data.get('summary_type', 'collection'),
                'provider': data.get('provider', 'groq'),
                'model': data.get('model')
            }
            try:
                summary_data, summary_status = summarize_logic(summarize_data)
                if summary_status == 200:
                    fetch_data.update(summary_data)
            except Exception as e:
                fetch_data['summary_error'] = str(e)
        return jsonify(fetch_data)
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/demo_issues', methods=['GET'])
def demo_issues():
    """Demo endpoint with predefined parameters."""
    try:
        # Demo parameters
        demo_data = {
            'project_url': 'https://gitlab.com/sachin.lade-group/sachin.lade-project',
            'username': 'sachin.lade',  # Change this to an actual username
            'summarize': True,
            'query': 'What are the main themes and status of these issues?'
        }
        
        # Temporarily set request data
        original_json = getattr(request, 'json', None)
        request.json = demo_data
        
        try:
            response = fetch_and_summarize()
            request.json = original_json  # Restore original
            return response
        except Exception as e:
            request.json = original_json  # Restore original
            raise e
            
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/providers', methods=['GET'])
def get_providers():
    """Get available AI providers and their status."""
    try:
        providers = {}
        
        # Check Groq
        groq_key = os.getenv('GROQ_API_KEY')
        if groq_key:
            try:
                client, _ = setup_llm_client("groq", groq_key)
                providers['groq'] = {
                    'available': client is not None,
                    'models': ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant', 'llama-3.2-11b-text-preview'],
                    'cost': 'free'
                }
            except:
                providers['groq'] = {'available': False, 'error': 'Setup failed'}
        else:
            providers['groq'] = {'available': False, 'error': 'No API key'}
        
        # Check OpenAI
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            try:
                client, _ = setup_llm_client("openai", openai_key)
                providers['openai'] = {
                    'available': client is not None,
                    'models': ['gpt-3.5-turbo', 'gpt-4', 'gpt-4o', 'gpt-4-turbo'],
                    'cost': 'paid'
                }
            except:
                providers['openai'] = {'available': False, 'error': 'Setup failed'}
        else:
            providers['openai'] = {'available': False, 'error': 'No API key'}
        
        return jsonify({
            'success': True,
            'providers': providers
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

if __name__ == '__main__':
    print("🚀 Starting GitLab Issues API with AI Summarization...")
    print("📍 Available endpoints:")
    print("   - GET  /           - Health check and API info")
    print("   - POST /fetch_issues - Fetch GitLab issues by username")
    print("   - POST /summarize   - Summarize issues with AI")
    print("   - POST /fetch_and_summarize - Fetch and summarize in one call")
    print("   - GET  /demo_issues - Demo with predefined parameters")
    print("   - GET  /providers   - Check available AI providers")
    print("\n🔑 Environment variables needed:")
    print("   - GITLAB_ACCESS_TOKEN (optional for public repos)")
    print("   - GROQ_API_KEY (recommended - free AI)")
    print("   - OPENAI_API_KEY (alternative - paid AI)")
    print("\n🌐 Server starting on http://localhost:8000")
    app.run(debug=True, host='0.0.0.0', port=8000) 