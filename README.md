# Agentic AI Framework

## Environment Setup

Create a `.env` file in the project root with the following content:

```
GITLAB_TOKEN=your_gitlab_token_here
GITLAB_URL=https://gitlab.com
GROQ_API_KEY=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
```

Replace `your_gitlab_token_here` with your actual GitLab personal access token.

## Running the Flask App

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Export environment variables (if not using a .env loader):
   ```bash
   export $(cat .env | xargs)
   ```
3. Start the Flask app:
   ```bash
   python app.py
   ``` 