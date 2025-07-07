# 🔐 Secrets and Environment Setup Guide

This document explains how to configure secrets and environment variables for the Enhanced RAG application.

## 🚀 Quick Setup

### For Local Development

1. Copy the environment template:
   ```bash
   cp .env.template .env
   ```

2. Edit `.env` with your actual values:
   ```bash
   # Required
   GEMINI_API_KEY=your_actual_api_key_here
   
   # Optional
   API_BASE_URL=http://localhost:8000
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   streamlit run streamlit_app.py
   ```

### For Streamlit Cloud Deployment

1. Go to [Streamlit Cloud](https://share.streamlit.io/)
2. Select your app
3. Go to Settings → Secrets
4. Add the following secrets:

```toml
# Required secrets for Streamlit Cloud
GEMINI_API_KEY = "your_gemini_api_key_here"

# Optional secrets
API_BASE_URL = "your_api_base_url_here"
```

## 📋 Required Secrets

### GEMINI_API_KEY
- **Purpose**: Google Gemini API access for AI features
- **How to get**: 
  1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
  2. Create a new API key
  3. Copy the key value
- **Format**: String (e.g., `AIzaSy...`)

## 🔧 Optional Configuration

### API_BASE_URL
- **Purpose**: Base URL for API endpoints (if using external API)
- **Default**: `http://localhost:8000`
- **Format**: URL (e.g., `https://your-api.com`)

## 🛡️ Security Best Practices

1. **Never commit secrets** to version control
2. **Use different keys** for development and production
3. **Rotate keys regularly** (at least every 90 days)
4. **Monitor API usage** for unusual activity
5. **Use environment variables** in production

## 🔍 Troubleshooting

### Common Issues

#### "Invalid API key" errors
- Verify your `GEMINI_API_KEY` is correct
- Check if the key has necessary permissions
- Ensure the key hasn't expired

#### Streamlit Cloud deployment issues
- Verify secrets are properly set in Streamlit Cloud dashboard
- Check that secret names match exactly (case-sensitive)
- Ensure no extra spaces in secret values

#### Local development issues
- Make sure `.env` file is in the project root
- Verify `.env` file is not committed to git
- Check that all required variables are set

## 📊 Environment Validation

Run the environment validation workflow to check your setup:

```bash
# Via GitHub Actions
gh workflow run "Environment & Secrets Management" --ref main
```

Or check locally:

```python
import os

# Check required variables
required_vars = ["GEMINI_API_KEY"]

for var in required_vars:
    if os.getenv(var):
        print(f"✅ {var}: Set")
    else:
        print(f"❌ {var}: Missing")
```

## 📞 Support

If you need help with setup:

1. Check the [GitHub Issues](../../issues)
2. Review the [README](../../README.md)
3. Check workflow logs for validation errors

---

**Last Updated**: $(date -u '+%Y-%m-%d %H:%M:%S UTC')
**Validation Status**: ✅ Automated checks passing
