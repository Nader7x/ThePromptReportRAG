# 🚀 GitHub Actions & Streamlit Cloud Deployment Guide

This guide explains how to set up GitHub Actions workflows and deploy to Streamlit Community Cloud.

## 📋 Overview

Your project now includes comprehensive CI/CD workflows:

1. **🧪 CI/CD Pipeline** (`ci-cd.yml`) - Main testing and validation
2. **🚀 Streamlit Deploy** (`streamlit-deploy.yml`) - Streamlit Cloud deployment
3. **🐳 Docker Publish** (`docker-publish.yml`) - Docker image building and publishing
4. **🔄 Dependency Updates** (`dependency-update.yml`) - Automated dependency management

## 🔐 Required Secrets

### GitHub Repository Secrets

Add these secrets in your GitHub repository settings (`Settings > Secrets and variables > Actions`):

| Secret Name | Description | Required For |
|-------------|-------------|--------------|
| `GEMINI_API_KEY` | Google Gemini API key | All workflows |
| `DISCORD_WEBHOOK` | Discord webhook URL for notifications | Optional |
| `SLACK_WEBHOOK_URL` | Slack webhook URL for notifications | Optional |
| `EMAIL_USERNAME` | Gmail username for email notifications | Optional |
| `EMAIL_PASSWORD` | Gmail app password for email notifications | Optional |
| `NOTIFICATION_EMAIL` | Email address for failure notifications | Optional |

### How to Add Secrets

1. Go to your GitHub repository
2. Navigate to `Settings > Secrets and variables > Actions`
3. Click "New repository secret"
4. Add the secret name and value
5. Click "Add secret"

## 🌐 Streamlit Community Cloud Setup

### Step 1: Prepare Your Repository

Ensure your repository has:
- ✅ `streamlit_app.py` (main Streamlit file)
- ✅ `requirements.txt` (dependencies)
- ✅ `.streamlit/config.toml` (configuration)

### Step 2: Deploy to Streamlit Cloud

1. **Visit Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io/)
   - Sign in with your GitHub account

2. **Create New App**
   - Click "New app"
   - Select your repository: `your-username/enhanced-rag`
   - Set main file path: `streamlit_app.py`
   - Choose branch: `main`

3. **Configure App Settings**
   - App name: `enhanced-rag` (or your preferred name)
   - App URL: `https://your-app-name.streamlit.app`

4. **Add Secrets**
   - In app settings, go to "Secrets"
   - Add your secrets in TOML format:
   ```toml
   GEMINI_API_KEY = "your_actual_api_key_here"
   API_BASE_URL = "your_api_endpoint_if_needed"
   ```

5. **Deploy**
   - Click "Deploy!"
   - Streamlit will automatically build and deploy your app

### Step 3: Automatic Deployment

Once configured, your app will automatically redeploy when you:
- Push changes to the `main` branch
- Modify `streamlit_app.py`, `requirements.txt`, or other Python files

## 🔄 Workflow Triggers

### CI/CD Pipeline
- **Triggers:** Push to `main`/`develop`, Pull requests to `main`
- **Actions:** Testing, linting, security scans, Docker builds
- **On Success:** Creates releases (if commit contains `[release]`)

### Streamlit Deployment
- **Triggers:** Push to `main`, manual trigger
- **Actions:** Validates app, triggers Streamlit Cloud deployment
- **Files Watched:** `streamlit_app.py`, `requirements.txt`, `*.py`

### Docker Publishing
- **Triggers:** Push to `main`, tags, manual trigger
- **Actions:** Builds multi-platform Docker images, security scans
- **Outputs:** Images published to GitHub Container Registry

### Dependency Updates
- **Triggers:** Weekly schedule (Mondays 9 AM UTC), manual trigger
- **Actions:** Updates requirements files, creates PR with changes

## 📊 Monitoring & Notifications

### GitHub Actions Dashboard
- View workflow runs in the "Actions" tab of your repository
- Monitor build status, logs, and artifacts
- Set up branch protection rules based on workflow status

### Deployment Status
- Check deployment status at: `https://your-app-name.streamlit.app`
- View deployment logs in Streamlit Cloud dashboard
- Monitor app health via built-in health checks

### Notifications (Optional)
Configure notifications for:
- **Discord:** App deployment status
- **Email:** Failure notifications
- **GitHub:** PR comments and status checks

## 🛠️ Customization

### Update App Name
Replace `your-app-name` in workflow files with your actual Streamlit app name:

```yaml
# In .github/workflows/streamlit-deploy.yml
environment_url: 'https://your-actual-app-name.streamlit.app'
```

### Modify Triggers
Customize when workflows run by editing the `on:` sections:

```yaml
on:
  push:
    branches: [ main, develop ]  # Add/remove branches
    paths:                       # Only run on specific file changes
      - 'streamlit_app.py'
      - 'requirements.txt'
```

### Add Environment Variables
Add environment variables in workflow files:

```yaml
env:
  CUSTOM_VAR: "value"
  ANOTHER_VAR: ${{ secrets.SECRET_NAME }}
```

## 🚀 Deployment Commands

### Manual Deployment
Trigger deployments manually from GitHub Actions:

1. Go to `Actions > Streamlit Deploy`
2. Click "Run workflow"
3. Select branch and options
4. Click "Run workflow"

### Local Testing
Test your Streamlit app locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run streamlit_app.py

# Test with Docker
docker-compose up --build
```

## 📝 Best Practices

### Branch Strategy
- **`main`** - Production branch (auto-deploys to Streamlit)
- **`develop`** - Development branch (runs tests only)
- **Feature branches** - Create PRs to `main`

### Commit Messages
- Use conventional commits for better automation
- Add `[release]` to commit messages to trigger releases
- Examples:
  ```
  feat: add new RAG functionality
  fix: resolve API connection issue
  docs: update deployment guide [release]
  ```

### Security
- Never commit API keys or secrets
- Use environment variables and GitHub secrets
- Regularly update dependencies
- Monitor security scan results

### Performance
- Use caching in workflows (`cache: 'pip'`)
- Optimize Docker images with multi-stage builds
- Monitor app performance in Streamlit Cloud

## 🆘 Troubleshooting

### Common Issues

**1. Workflow Fails**
- Check workflow logs in GitHub Actions
- Verify all required secrets are set
- Ensure requirements.txt is valid

**2. Streamlit Deployment Fails**
- Verify `streamlit_app.py` runs locally
- Check Streamlit Cloud logs
- Ensure all dependencies are in requirements.txt

**3. Docker Build Fails**
- Test Docker build locally
- Check Dockerfile syntax
- Verify base image availability

**4. App Won't Start**
- Check Streamlit Cloud app logs
- Verify secrets are set correctly
- Test app locally with same environment

### Getting Help

1. **GitHub Issues** - Report bugs and request features
2. **Streamlit Community** - [discuss.streamlit.io](https://discuss.streamlit.io/)
3. **Documentation** - Check workflow comments and this guide
4. **Logs** - Always check workflow and app logs first

## 🎉 Next Steps

1. **Set up repository secrets** with your API keys
2. **Deploy to Streamlit Cloud** following the steps above
3. **Test the workflows** by making a small commit
4. **Monitor deployments** and set up notifications
5. **Customize workflows** as needed for your project

Your Enhanced RAG application is now ready for automated deployment! 🚀
