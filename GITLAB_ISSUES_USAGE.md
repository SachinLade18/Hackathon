# GitLab Issues Fetcher with AI Summarization (Groq & OpenAI)

This tool allows you to fetch GitLab issues based on username from your repository and provides AI-powered summarization using **Groq** (recommended - fast & free) or OpenAI APIs.

## Features

✅ **Fetch issues by username** - Both issues assigned to and created by the user  
✅ **Flexible filtering** - Can filter by assignee only or author only  
✅ **Multiple output formats** - Console display or JSON  
✅ **Works with public repos** - No token needed for public repositories  
✅ **Supports private repos** - With GitLab access token  
✅ **🚀 Groq AI Summarization** - Fast, FREE AI-powered summaries with Llama models  
✅ **🤖 OpenAI Support** - Alternative premium AI summarization  
✅ **Detailed information** - Shows title, state, dates, assignee, author, and URL  

## Setup

1. **Activate your virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Set up GitLab Access Token (Optional but recommended):**
   
   For private repositories or to avoid rate limits, create a personal access token:
   - Go to https://gitlab.com/-/profile/personal_access_tokens
   - Create a new token with `read_api` scope
   - Set it as an environment variable:
   ```bash
   export GITLAB_ACCESS_TOKEN="your-token-here"
   ```

3. **Set up AI API Key (Required for AI summarization):**
   
   ### 🚀 Groq (Recommended - Fast & Free!)
   ```bash
   # Get a FREE API key from https://console.groq.com/keys
   export GROQ_API_KEY="your-groq-api-key-here"
   ```
   
   ### 🤖 OpenAI (Alternative - Paid)
   ```bash
   # Get an API key from https://platform.openai.com/account/api-keys
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

## Usage Options

### Option 1: Command Line Interface

#### Basic Usage (without AI)
```bash
# Basic usage - fetch all issues for a user
python fetch_gitlab_issues.py --project-url "https://gitlab.com/sachin.lade-group/sachin.lade-project" --username "your-username"

# Only issues assigned to the user
python fetch_gitlab_issues.py --project-url "https://gitlab.com/sachin.lade-group/sachin.lade-project" --username "your-username" --assignee-only

# Only issues created by the user
python fetch_gitlab_issues.py --project-url "https://gitlab.com/sachin.lade-group/sachin.lade-project" --username "your-username" --author-only
```

#### 🚀 Groq AI-Powered Summarization (Fast & Free!)
```bash
# Get Groq AI summary for each individual issue
python fetch_gitlab_issues.py --project-url "https://gitlab.com/sachin.lade-group/sachin.lade-project" --username "your-username" --summarize-individual

# Get Groq AI summary of the entire collection of issues
python fetch_gitlab_issues.py --project-url "https://gitlab.com/sachin.lade-group/sachin.lade-project" --username "your-username" --summarize-collection

# Get both individual and collection summaries with Groq
python fetch_gitlab_issues.py --project-url "https://gitlab.com/sachin.lade-group/sachin.lade-project" --username "your-username" --summarize-individual --summarize-collection

# Use a specific Groq model
python fetch_gitlab_issues.py --project-url "https://gitlab.com/sachin.lade-group/sachin.lade-project" --username "your-username" --summarize-individual --llm-model "llama-3.1-8b-instant"

# Provide Groq API key directly
python fetch_gitlab_issues.py --project-url "https://gitlab.com/sachin.lade-group/sachin.lade-project" --username "your-username" --summarize-individual --api-key "your-groq-key"
```

#### 🤖 OpenAI Alternative (Paid)
```bash
# Use OpenAI instead of Groq
python fetch_gitlab_issues.py --project-url "https://gitlab.com/sachin.lade-group/sachin.lade-project" --username "your-username" --summarize-individual --provider openai

# Use GPT-4 with OpenAI
python fetch_gitlab_issues.py --project-url "https://gitlab.com/sachin.lade-group/sachin.lade-project" --username "your-username" --summarize-individual --provider openai --llm-model "gpt-4"
```

#### JSON Output with AI Summaries
```bash
# Output as JSON with Groq individual summaries
python fetch_gitlab_issues.py --project-url "https://gitlab.com/sachin.lade-group/sachin.lade-project" --username "your-username" --output json --summarize-individual

# Save JSON with both Groq summaries to file
python fetch_gitlab_issues.py --project-url "https://gitlab.com/sachin.lade-group/sachin.lade-project" --username "your-username" --output json --summarize-individual --summarize-collection > issues_with_summaries.json
```

### Option 2: Using the Example Scripts

#### Basic Example
1. Edit `example_usage.py` and replace `"your-username"` with the actual username
2. Run: `python example_usage.py`

#### Enhanced Groq AI Example
1. Edit `example_usage_with_llm.py` and replace `"your-username"` with the actual username
2. Run: `python example_usage_with_llm.py`

### Option 3: Import as a Module

```python
from fetch_gitlab_issues import fetch_issues_by_username, display_issues, setup_llm_client

# Fetch issues
issues = fetch_issues_by_username(
    project_url="https://gitlab.com/sachin.lade-group/sachin.lade-project",
    username="your-username",
    access_token="your-token",  # optional
    assignee=True,  # include assigned issues
    author=True     # include authored issues
)

# Setup Groq client for summarization
llm_client, provider = setup_llm_client("groq", "your-groq-key")

# Display them with Groq AI summaries
display_issues(
    issues, 
    llm_client=llm_client,
    provider=provider,
    model="llama-3.3-70b-versatile",
    summarize_individual=True,
    summarize_collection=True
)
```

## Command Line Arguments

### Core Arguments
- `--project-url`: Your GitLab project URL (required)
- `--username`: Username to filter issues by (required)
- `--token`: GitLab access token (optional)
- `--assignee-only`: Only fetch issues assigned to the user
- `--author-only`: Only fetch issues created by the user
- `--output`: Output format (`console` or `json`)

### 🤖 AI Arguments
- `--summarize-individual`: Generate AI summary for each individual issue
- `--summarize-collection`: Generate AI summary for the entire collection of issues
- `--provider`: AI provider (`groq` [default] or `openai`)
- `--api-key`: AI API key (or set `GROQ_API_KEY`/`OPENAI_API_KEY` env var)
- `--llm-model`: Specific model to use (see available models below)

## Output Information

### Standard Output
For each issue, the script displays:
- Issue number and title
- State (open/closed)
- Author information
- Assignee information
- Creation and update dates
- Direct URL to the issue
- Description preview (first 100 characters)

### 🤖 AI Enhanced Output
When AI summarization is enabled:
- **Individual Summaries**: 2-3 sentence AI-generated summary for each issue
- **Collection Summary**: High-level analysis of all issues including themes, patterns, and trends
- **JSON Output**: Structured data with embedded AI summaries
- **Provider Info**: Shows which AI provider and model was used

## Available AI Models

### 🚀 Groq Models (Free & Fast)
- **`llama-3.3-70b-versatile`** (default): Balanced performance, great for most tasks
- **`llama-3.1-8b-instant`**: Ultra-fast, good for quick summaries
- **`llama-3.2-11b-text-preview`**: Good balance of speed and quality

### 🤖 OpenAI Models (Paid)
- **`gpt-3.5-turbo`** (default): Fast and cost-effective
- **`gpt-4`**: Higher quality but slower and more expensive  
- **`gpt-4o`**: Latest optimized model
- **`gpt-4-turbo`**: Good balance of quality and speed

## Examples

### Basic Examples
```bash
# Get all issues for user "john.doe"
python fetch_gitlab_issues.py --project-url "https://gitlab.com/sachin.lade-group/sachin.lade-project" --username "john.doe"

# Get only assigned issues as JSON
python fetch_gitlab_issues.py --project-url "https://gitlab.com/sachin.lade-group/sachin.lade-project" --username "john.doe" --assignee-only --output json
```

### 🚀 Groq AI-Powered Examples (Recommended)
```bash
# Get Groq AI-powered insights on all issues (FREE!)
python fetch_gitlab_issues.py --project-url "https://gitlab.com/sachin.lade-group/sachin.lade-project" --username "john.doe" --summarize-collection

# Comprehensive analysis with individual summaries (FREE!)
python fetch_gitlab_issues.py --project-url "https://gitlab.com/sachin.lade-group/sachin.lade-project" --username "john.doe" --summarize-individual --summarize-collection

# Use ultra-fast Groq model
python fetch_gitlab_issues.py --project-url "https://gitlab.com/sachin.lade-group/sachin.lade-project" --username "john.doe" --summarize-individual --llm-model "llama-3.1-8b-instant"

# Generate comprehensive report as JSON
python fetch_gitlab_issues.py --project-url "https://gitlab.com/sachin.lade-group/sachin.lade-project" --username "john.doe" --summarize-individual --summarize-collection --output json > comprehensive_report.json
```

### 🤖 OpenAI Examples (Alternative)
```bash
# Use OpenAI GPT-4 for premium quality
python fetch_gitlab_issues.py --project-url "https://gitlab.com/sachin.lade-group/sachin.lade-project" --username "john.doe" --summarize-individual --provider openai --llm-model "gpt-4"
```

## Troubleshooting

### GitLab Issues
- **"GitLab API Error"**: Check if the repository URL is correct and if you have access to it
- **"No issues found"**: The user might not have any issues, or they might be in a different repository
- **Rate limiting**: Use an access token to increase rate limits
- **Private repository access**: An access token is required for private repositories

### 🚀 Groq Issues
- **"groq package not installed"**: Run `pip install groq`
- **"Groq API key not found"**: Set the `GROQ_API_KEY` environment variable or use `--api-key`
- **"Error generating summary"**: Check your Groq API key at https://console.groq.com/keys
- **Rate limits**: Groq has generous free limits; if exceeded, wait a moment and retry

### 🤖 OpenAI Issues  
- **"openai package not installed"**: Run `pip install openai`
- **"OpenAI API key not found"**: Set the `OPENAI_API_KEY` environment variable or use `--api-key`
- **"Error generating summary"**: Check your OpenAI API key and ensure you have credits/quota
- **Rate limits**: OpenAI has rate limits; consider using Groq for free alternative
- **Cost control**: Switch to Groq to eliminate costs entirely

## Cost Comparison

### 🚀 Groq (Recommended)
- **Collection Summary**: **FREE** 
- **Individual Summaries**: **FREE**
- **Rate Limits**: Very generous free tier
- **Speed**: Extremely fast inference
- **Models**: State-of-the-art Llama models

### 🤖 OpenAI
- **Collection Summary**: ~$0.001-0.005 per run 
- **Individual Summaries**: ~$0.001-0.002 per issue (GPT-3.5-turbo)
- **GPT-4**: ~$0.01-0.03 per issue summary
- **Rate Limits**: Based on payment tier

## Why Choose Groq?

✅ **Completely FREE** - No usage costs  
✅ **Lightning Fast** - Sub-second response times  
✅ **High Quality** - State-of-the-art Llama models  
✅ **Easy Setup** - Just get a free API key  
✅ **Generous Limits** - High rate limits on free tier  

**Get started with Groq**: https://console.groq.com/keys 