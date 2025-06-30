# 🔧 Troubleshooting Guide: GitHub Actions Issues

## 🐛 Issue 1: NLTK Module Not Found in Docker

### Problem

```
ModuleNotFoundError: No module named 'nltk'
```

### Root Cause

The NLTK module wasn't available in the Python environment when trying to download NLTK data during Docker build.

### ✅ Solution Applied

Fixed in both `Dockerfile` and `Dockerfile.production`:

**Dockerfile:**

- Ensured NLTK runs within the virtual environment: `. .venv/bin/activate && python -c "import nltk; ..."`

**Dockerfile.production:**

- NLTK is installed via requirements.txt and available in the global Python environment

## 🐛 Issue 2: CR_PAT Permissions Error

### Problem

```
HttpError: Resource not accessible by integration
```

### Root Cause

The Personal Access Token (CR_PAT) either:

1. Lacks sufficient permissions
2. Is not properly configured in repository secrets
3. Has expired

### ✅ Solutions Applied

#### 1. Docker Registry Authentication

- **Changed**: Docker publish workflow now uses `GITHUB_TOKEN` for GitHub Container Registry
- **Benefit**: More secure and doesn't require additional token management

#### 2. CR_PAT Configuration Requirements

For the dependency update workflow that still uses CR_PAT, ensure your token has these permissions:

### 📋 Required CR_PAT Permissions

#### Classic Personal Access Token

If using a classic PAT, ensure these scopes are enabled:

- ✅ **repo** (Full control of private repositories)
  - `repo:status` - Access commit status
  - `repo_deployment` - Access deployment status
  - `public_repo` - Access public repositories
- ✅ **workflow** (Update GitHub Action workflows)
- ✅ **write:packages** (Upload packages to GitHub Package Registry)
- ✅ **read:packages** (Download packages from GitHub Package Registry)

#### Fine-grained Personal Access Token (Recommended)

If using fine-grained PATs, ensure these permissions:

- ✅ **Contents**: Read and write
- ✅ **Pull requests**: Write
- ✅ **Issues**: Write
- ✅ **Metadata**: Read
- ✅ **Actions**: Write (if triggering workflows)

### 🔧 How to Check/Update Your CR_PAT

#### Step 1: Verify Token Exists

1. Go to GitHub.com → Settings → Developer settings → Personal access tokens
2. Find your token and check its permissions
3. Ensure it hasn't expired

#### Step 2: Update Repository Secret

1. Go to your repository → Settings → Secrets and variables → Actions
2. Find `CR_PAT` secret
3. Update with new token if needed

#### Step 3: Test Token Permissions

You can test your token manually:

```bash
# Test repo access
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/repos/YOUR_USERNAME/ThePromptReportRAG

# Test PR creation (this should return method not allowed, but not unauthorized)
curl -H "Authorization: token YOUR_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/YOUR_USERNAME/ThePromptReportRAG/pulls
```

### 🛠️ Alternative Solution: Use GITHUB_TOKEN

If you continue having issues with CR_PAT, you can switch to GITHUB_TOKEN for most operations:

```yaml
# In dependency-update.yml
- name: 📥 Checkout code
  uses: actions/checkout@v4
  with:
    token: ${{ secrets.GITHUB_TOKEN }} # Instead of CR_PAT
    fetch-depth: 0

- name: 📝 Create pull request
  uses: peter-evans/create-pull-request@v6
  with:
    token: ${{ secrets.GITHUB_TOKEN }} # Instead of CR_PAT
```

**Note**: GITHUB_TOKEN has some limitations:

- PRs created with GITHUB_TOKEN won't trigger workflow runs
- May have different permissions in private repos

### 🔍 Debugging Workflow Permissions

Add this debug step to any workflow to check token permissions:

```yaml
- name: 🔍 Debug token permissions
  env:
    GITHUB_TOKEN: ${{ secrets.CR_PAT }}
  run: |
    echo "Testing token permissions..."
    curl -H "Authorization: token $GITHUB_TOKEN" \
      -H "Accept: application/vnd.github.v3+json" \
      https://api.github.com/repos/${{ github.repository }} \
      | jq '.permissions'
```

## 🚀 Workflow Status After Fixes

### ✅ Fixed Workflows

- **Docker Publish**: Now uses GITHUB_TOKEN for registry authentication
- **Dockerfiles**: NLTK module availability fixed
- **Error Handling**: Improved error messages and debugging

### 🔄 Workflows Using CR_PAT

These workflows still require your CR_PAT to be properly configured:

- **Dependency Updates**: Creates PRs and needs repo write access
- **Environment Management**: May create/update files

### 📊 Testing Your Fixes

1. **Test Docker Build**:

   ```bash
   docker build -f Dockerfile -t test-image .
   ```

2. **Test Production Docker Build**:

   ```bash
   docker build -f Dockerfile.production -t test-prod-image .
   ```

3. **Trigger Dependency Update**:
   - Go to Actions → Dependency Updates → Run workflow
   - Watch for any permission errors

### 🆘 If Issues Persist

1. **Check GitHub Status**: https://www.githubstatus.com/
2. **Regenerate CR_PAT**: Create a new token with full permissions
3. **Contact Support**: File a ticket if GitHub API is having issues
4. **Use GITHUB_TOKEN**: Switch workflows to use built-in token

## 📞 Quick Reference

### Working Tokens by Use Case

| Use Case          | Recommended Token | Required Permissions |
| ----------------- | ----------------- | -------------------- |
| Docker Registry   | `GITHUB_TOKEN`    | Automatic            |
| Create PRs        | `CR_PAT`          | repo, workflow       |
| Read Repository   | `GITHUB_TOKEN`    | Automatic            |
| Trigger Workflows | `CR_PAT`          | repo, workflow       |

### Workflow Files Modified

- ✅ `Dockerfile` - Fixed NLTK import
- ✅ `Dockerfile.production` - Fixed NLTK import
- ✅ `docker-publish.yml` - Switched to GITHUB_TOKEN
- ℹ️ `dependency-update.yml` - Still uses CR_PAT (verify permissions)

---

**Last Updated**: $(date -u '+%Y-%m-%d %H:%M:%S UTC')
**Status**: Ready for testing
