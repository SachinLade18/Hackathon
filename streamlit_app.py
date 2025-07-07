import streamlit as st
import requests
from datetime import date
import json

# Page configuration
st.set_page_config(
    page_title="GitLab Issues AI Summarizer",
    page_icon="🔍",
    layout="wide"
)

st.title('🔍 GitLab Issues AI Summarizer')
st.markdown('*Fetch and analyze GitLab issues with AI-powered insights*')

backend_url = 'http://localhost:8000'

# Check backend status and available providers
@st.cache_data(ttl=30)  # Cache for 30 seconds
def check_backend_status():
    try:
        response = requests.get(f'{backend_url}/', timeout=5)
        if response.status_code == 200:
            providers_resp = requests.get(f'{backend_url}/providers', timeout=5)
            if providers_resp.status_code == 200:
                return True, providers_resp.json().get('providers', {})
            return True, {}
        return False, {}
    except Exception:
        return False, {}

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Backend status
    backend_online, providers = check_backend_status()
    if backend_online:
        st.success("✅ Backend Online")
    else:
        st.error("❌ Backend Offline")
        st.stop()
    
    # AI Provider status
    if providers:
        st.subheader("🤖 AI Providers")
        for provider, info in providers.items():
            if info.get('available'):
                icon = "✅" if provider == 'groq' else "🤖"
                cost = "🆓 Free" if info.get('cost') == 'free' else "💰 Paid"
                st.write(f"{icon} **{provider.title()}** - {cost}")
            else:
                st.write(f"❌ **{provider.title()}** - {info.get('error', 'Not available')}")

# Main form
with st.form('gitlab_form'):
    col1, col2 = st.columns(2)
    
    with col1:
        project_url = st.text_input(
            'GitLab Project URL or ID', 
            value='71150749',
            help='Full URL (https://gitlab.com/user/project) or Project ID (recommended for private repos)'
        )
        username = st.text_input(
            'GitLab Username', 
            'sachin.lade',
            help='Username to fetch issues for (assigned to or created by)'
        )
    
    with col2:
        # Filter options
        filter_option = st.selectbox(
            'Issue Filter',
            ['Both (Assigned + Created)', 'Assigned Only', 'Created Only'],
            help='Filter issues by relationship to user'
        )
        
        # AI options
        enable_ai = st.checkbox('Enable AI Summarization', value=True)
        
        if enable_ai and providers.get('groq', {}).get('available'):
            ai_provider = st.selectbox(
                'AI Provider',
                ['groq', 'openai'] if providers.get('openai', {}).get('available') else ['groq']
            )
        else:
            ai_provider = 'groq'
    
    # Query input
    query = st.text_area(
        'Your Query (Optional)', 
        value='What are the main themes and current status of these issues?',
        help='Ask specific questions about the issues for targeted AI analysis'
    )
    
    # Submit button
    submitted = st.form_submit_button('🔍 Analyze Issues', type='primary')

# Process form submission
if submitted:
    if not project_url or not username:
        st.error('Please provide both a GitLab project URL and username.')
    else:
        # Determine filter parameters
        assignee_only = filter_option == 'Assigned Only'
        author_only = filter_option == 'Created Only'
        
        # Prepare API request
        api_data = {
            'project_url': project_url,
            'username': username,
            'assignee_only': assignee_only,
            'author_only': author_only
        }
        
        # Add AI parameters if enabled
        if enable_ai:
            api_data.update({
                'summarize': True,
                'query': query.strip() if query.strip() else None,
                'provider': ai_provider,
                'summary_type': 'collection'
            })
        
        # Make API request
        with st.spinner('🔄 Fetching and analyzing GitLab issues...'):
            try:
                if enable_ai:
                    # Use the combined endpoint for fetching and summarizing
                    response = requests.post(
                        f'{backend_url}/fetch_and_summarize', 
                        json=api_data,
                        timeout=60
                    )
                else:
                    # Just fetch issues
                    response = requests.post(
                        f'{backend_url}/fetch_issues', 
                        json=api_data,
                        timeout=30
                    )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('success'):
                        issues = data.get('issues', [])
                        
                        # Display results summary
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("📊 Total Issues", len(issues))
                        with col2:
                            open_count = sum(1 for issue in issues if issue.get('state') == 'opened')
                            st.metric("📈 Open Issues", open_count)
                        with col3:
                            closed_count = len(issues) - open_count
                            st.metric("✅ Closed Issues", closed_count)
                        
                        if issues:
                            # AI Summary Section
                            if enable_ai and data.get('collection_summary'):
                                st.subheader(f'🤖 AI Analysis ({ai_provider.title()})')
                                
                                # Display the AI summary in a nice container
                                with st.container():
                                    st.markdown(f"""
                                    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #1f77b4;">
                                        <h4>📝 Summary</h4>
                                        <p>{data.get('collection_summary', '')}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                # Show AI metadata
                                with st.expander("🔧 AI Details"):
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.write(f"**Provider:** {data.get('provider', 'Unknown')}")
                                        st.write(f"**Model:** {data.get('model', 'Unknown')}")
                                    with col2:
                                        if data.get('query'):
                                            st.write(f"**Query:** {data.get('query')}")
                            
                            # Issues List Section
                            st.subheader('📋 Issues List')
                            
                            # Add filters for the issues display
                            col1, col2 = st.columns(2)
                            with col1:
                                state_filter = st.selectbox(
                                    'Filter by State:', 
                                    ['All', 'Open', 'Closed']
                                )
                            with col2:
                                show_descriptions = st.checkbox('Show Descriptions', value=False)
                            
                            # Filter issues based on state
                            filtered_issues = issues
                            if state_filter == 'Open':
                                filtered_issues = [issue for issue in issues if issue.get('state') == 'opened']
                            elif state_filter == 'Closed':
                                filtered_issues = [issue for issue in issues if issue.get('state') == 'closed']
                            
                            # Display issues
                            for i, issue in enumerate(filtered_issues, 1):
                                with st.expander(f"#{issue.get('iid', issue.get('id'))} - {issue.get('title', 'No Title')}", expanded=False):
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.write(f"**State:** {issue.get('state', 'Unknown')}")
                                        st.write(f"**Created:** {issue.get('created_at', 'Unknown')}")
                                        if issue.get('author'):
                                            author = issue['author']
                                            st.write(f"**Author:** {author.get('name', author.get('username', 'Unknown'))}")
                                    
                                    with col2:
                                        if issue.get('assignee'):
                                            assignee = issue['assignee']
                                            st.write(f"**Assignee:** {assignee.get('name', assignee.get('username', 'Unknown'))}")
                                        else:
                                            st.write("**Assignee:** Unassigned")
                                        
                                        if issue.get('web_url'):
                                            st.markdown(f"[🔗 View on GitLab]({issue['web_url']})")
                                    
                                    if show_descriptions and issue.get('description'):
                                        st.markdown("**Description:**")
                                        st.write(issue['description'][:300] + "..." if len(issue.get('description', '')) > 300 else issue.get('description'))

                                    # --- Show comments and their summaries ---
                                    comments = issue.get('comments', [])
                                    if comments:
                                        st.markdown("**💬 Comments:**")
                                        for comment in comments:
                                            st.markdown(f"- **{comment.get('author', 'unknown')}** at {comment.get('created_at', '')}:")
                                            st.write(comment.get('body', ''))
                                            if 'llm_summary' in comment:
                                                st.info(f"🤖 Summary: {comment['llm_summary']}")
                            
                            # Download option
                            st.subheader('💾 Export Data')
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # JSON download
                                json_data = json.dumps(data, indent=2, default=str)
                                st.download_button(
                                    label="📄 Download as JSON",
                                    data=json_data,
                                    file_name=f"gitlab_issues_{username}_{date.today().isoformat()}.json",
                                    mime="application/json"
                                )
                            
                            with col2:
                                # CSV-like text download
                                csv_lines = ["Title,State,Author,Assignee,Created,URL"]
                                for issue in issues:
                                    author = issue.get('author', {}).get('username', 'Unknown')
                                    assignee = issue.get('assignee', {}).get('username', 'Unassigned') if issue.get('assignee') else 'Unassigned'
                                    csv_lines.append(f'"{issue.get("title", "")}",{issue.get("state", "")},{author},{assignee},{issue.get("created_at", "")},{issue.get("web_url", "")}')
                                
                                csv_data = "\n".join(csv_lines)
                                st.download_button(
                                    label="📊 Download as CSV",
                                    data=csv_data,
                                    file_name=f"gitlab_issues_{username}_{date.today().isoformat()}.csv",
                                    mime="text/csv"
                                )
                        
                        else:
                            st.info(f"No issues found for username '{username}' in this project.")
                            st.markdown("""
                            **Possible reasons:**
                            - The username doesn't have any issues in this project
                            - The username might be incorrect
                            - The project might be private and requires authentication
                            """)
                    
                    else:
                        st.error(f"❌ API Error: {data.get('error', 'Unknown error')}")
                
                else:
                    try:
                        error_data = response.json()
                        st.error(f"❌ Error {response.status_code}: {error_data.get('error', response.text)}")
                    except:
                        st.error(f"❌ Error {response.status_code}: {response.text}")
            
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. The server might be busy or the repository might be large.")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Cannot connect to the backend server. Make sure it's running on http://localhost:8000")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8em;">
    🚀 Powered by Groq AI • Built with Streamlit • GitLab API Integration
</div>
""", unsafe_allow_html=True) 