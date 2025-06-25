# 🚀 Deployment Checklist

Use this checklist to ensure successful deployment of your Enhanced RAG application.

## ✅ Pre-Deployment Setup

### Repository Setup

- [ ] Fork/clone repository to your GitHub account
- [ ] Ensure all files are committed and pushed to `main` branch
- [ ] Verify `streamlit_app.py` is in root directory
- [ ] Check `requirements.txt` contains all necessary dependencies

### API Keys & Secrets

- [ ] Obtain Google Gemini API key from [Google AI Studio](https://ai.google.dev/)
- [ ] Test API key locally before deployment
- [ ] Prepare any additional environment variables

## 🌐 Streamlit Community Cloud Deployment

### Account Setup

- [ ] Create account at [share.streamlit.io](https://share.streamlit.io/)
- [ ] Connect GitHub account to Streamlit Cloud
- [ ] Grant necessary repository permissions

### App Configuration

- [ ] Create new app in Streamlit Cloud
- [ ] Select correct repository: `your-username/enhanced-rag`
- [ ] Set main file path: `streamlit_app.py`
- [ ] Choose deployment branch: `main`
- [ ] Set app name (e.g., `enhanced-rag`)

### Secrets Configuration

- [ ] Navigate to app settings → Secrets
- [ ] Add required secrets in TOML format:
  ```toml
  GEMINI_API_KEY = "your_actual_api_key_here"
  API_BASE_URL = "http://localhost:8000"  # Optional
  ```
- [ ] Save secrets configuration

### Deployment

- [ ] Click "Deploy" button
- [ ] Monitor deployment logs for errors
- [ ] Test deployed app functionality
- [ ] Verify app URL: `https://your-app-name.streamlit.app`

## 🔧 GitHub Actions Setup

### Repository Secrets

- [ ] Go to repository `Settings > Secrets and variables > Actions`
- [ ] Add required secrets:
  - [ ] `GEMINI_API_KEY` - Your Google Gemini API key
  - [ ] `DISCORD_WEBHOOK` - Discord webhook URL (optional)
  - [ ] `SLACK_WEBHOOK_URL` - Slack webhook URL (optional)
  - [ ] `EMAIL_USERNAME` - Email for notifications (optional)
  - [ ] `EMAIL_PASSWORD` - Email password (optional)
  - [ ] `NOTIFICATION_EMAIL` - Email for alerts (optional)

### Workflow Configuration

- [ ] Verify `.github/workflows/` directory exists
- [ ] Check all workflow files are present:
  - [ ] `ci-cd.yml` - Main CI/CD pipeline
  - [ ] `streamlit-deploy.yml` - Streamlit deployment
  - [ ] `docker-publish.yml` - Docker image publishing
  - [ ] `dependency-update.yml` - Dependency updates
- [ ] Update workflow files with your app name/URL
- [ ] Test workflows by making a small commit

## 🐳 Docker Deployment (Optional)

### Local Testing

- [ ] Install Docker and Docker Compose
- [ ] Create `.env` file with your API key:
  ```env
  GEMINI_API_KEY=your_api_key_here
  ```
- [ ] Test Docker build: `docker-compose up --build`
- [ ] Verify both services start correctly (API: 8000, Streamlit: 8501)

### Production Docker

- [ ] Use production configuration: `docker-compose.production.yml`
- [ ] Configure environment variables securely
- [ ] Set up reverse proxy (nginx) if needed
- [ ] Configure SSL/TLS certificates
- [ ] Set up monitoring and logging

## 🧪 Post-Deployment Testing

### Functional Testing

- [ ] Visit deployed Streamlit app URL
- [ ] Test prompt enhancement functionality
- [ ] Verify search capabilities work
- [ ] Check visualization components
- [ ] Test different prompt techniques

### Performance Testing

- [ ] Test app with various prompt lengths
- [ ] Verify response times are acceptable
- [ ] Check memory usage and stability
- [ ] Test concurrent user scenarios

### API Testing (if applicable)

- [ ] Test API endpoints directly
- [ ] Verify API documentation accessibility
- [ ] Check authentication and rate limiting
- [ ] Test error handling

## 📊 Monitoring & Maintenance

### Setup Monitoring

- [ ] Configure Streamlit Cloud app monitoring
- [ ] Set up GitHub Actions notifications
- [ ] Monitor app performance and usage
- [ ] Set up log aggregation if needed

### Regular Maintenance

- [ ] Monitor dependency updates (automated weekly)
- [ ] Review security scan results
- [ ] Update API keys before expiration
- [ ] Monitor app usage and performance metrics

## 🆘 Troubleshooting

### Common Issues

- [ ] **App won't start**: Check Streamlit Cloud logs for errors
- [ ] **API key errors**: Verify secrets are set correctly
- [ ] **Import errors**: Ensure all dependencies in `requirements.txt`
- [ ] **Performance issues**: Check resource usage and optimize

### Debugging Steps

- [ ] Check Streamlit Cloud deployment logs
- [ ] Test app locally with same configuration
- [ ] Review GitHub Actions workflow logs
- [ ] Verify all secrets and environment variables

## 🎉 Success Criteria

### Deployment Success

- [ ] ✅ App accessible via public URL
- [ ] ✅ All features working correctly
- [ ] ✅ No errors in logs
- [ ] ✅ Good performance and responsiveness

### CI/CD Success

- [ ] ✅ All workflows passing
- [ ] ✅ Automatic deployment on push to main
- [ ] ✅ Docker images building successfully
- [ ] ✅ Security scans passing

### Documentation

- [ ] ✅ Update README with your app URL
- [ ] ✅ Document any custom configuration
- [ ] ✅ Share app with users/team
- [ ] ✅ Set up feedback collection

## 📞 Support

If you encounter issues:

1. **Check the logs** - Streamlit Cloud logs, GitHub Actions logs
2. **Review documentation** - This guide and setup documentation
3. **Test locally** - Reproduce issues in local environment
4. **Search issues** - Check GitHub issues for similar problems
5. **Create issue** - Report bugs with detailed information

---

🎊 **Congratulations!** Your Enhanced RAG application is now deployed and ready for users!
