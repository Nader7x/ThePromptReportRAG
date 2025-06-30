# 🐳 Docker Image Name Case Fix

## 📋 Issue Summary

The Docker publish workflow was failing with the error:

```
ERROR: failed to build: invalid tag "ghcr.io/Nader7x/ThePromptReportRAG:production": repository name must be lowercase
```

## 🔧 Root Cause

**Problem:** Docker and GitHub Container Registry require all image repository names to be lowercase, but `${{ github.repository }}` preserves the original repository name casing.

**Original Configuration:**

```yaml
env:
  IMAGE_NAME: ${{ github.repository }} # Returns "Nader7x/ThePromptReportRAG"
```

**Result:** Image tags like `ghcr.io/Nader7x/ThePromptReportRAG:production` contain uppercase letters, which are invalid.

## ✅ Solution Applied

**Enhanced Configuration:**

```yaml
env:
  REGISTRY: ghcr.io
  IMAGE_NAME_RAW: ${{ github.repository }}
  PYTHON_VERSION: "3.11"
```

**Added Lowercase Conversion Step:**

```yaml
- name: 🏷️ Set lowercase image name
  id: image-name
  run: |
    IMAGE_NAME_LOWER=$(echo "${{ env.IMAGE_NAME_RAW }}" | tr '[:upper:]' '[:lower:]')
    echo "IMAGE_NAME=${IMAGE_NAME_LOWER}" >> $GITHUB_OUTPUT
    echo "Using image name: ${IMAGE_NAME_LOWER}"
```

**Updated Image References:**

```yaml
# Before
images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}

# After
images: ${{ env.REGISTRY }}/${{ steps.image-name.outputs.IMAGE_NAME }}
```

## 📊 Changes Applied

### 1. Environment Variables

- Changed `IMAGE_NAME` to `IMAGE_NAME_RAW` to store original casing
- Added conversion step to create lowercase version

### 2. Updated References

All image name references updated in:

- ✅ Metadata extraction step
- ✅ Production image tags
- ✅ Docker test commands
- ✅ Image report generation
- ✅ Security scan references

### 3. Fixed Secret Reference

- Changed `${{ secrets.CR_PAT }}` to `${{ secrets.GITHUB_TOKEN }}` for standard authentication

## 🎯 Before vs After

### Before (Failing)

```yaml
tags: |
  ghcr.io/Nader7x/ThePromptReportRAG:production  # ❌ Contains uppercase
  ghcr.io/Nader7x/ThePromptReportRAG:production-latest
```

### After (Working)

```yaml
tags: |
  ghcr.io/nader7x/thepromptreportrag:production  # ✅ All lowercase
  ghcr.io/nader7x/thepromptreportrag:production-latest
```

## 🔄 Workflow Impact

The fix ensures:

- **✅ Valid Docker Tags:** All image names are lowercase
- **✅ Cross-Platform:** Works on both `linux/amd64` and `linux/arm64`
- **✅ Consistent Naming:** Same approach used across all steps
- **✅ Security Compliance:** Maintains security scanning with correct image names

## 📚 Docker Naming Rules

Docker image names must follow these rules:

- **Lowercase only:** `a-z`, `0-9`, `-`, `_`, `.`
- **No uppercase letters:** `A-Z` are not allowed
- **Repository format:** `registry/owner/repository:tag`

## 🚀 Result

The workflow now successfully builds and publishes Docker images with valid, lowercase names:

- `ghcr.io/nader7x/thepromptreportrag:latest`
- `ghcr.io/nader7x/thepromptreportrag:production`
- `ghcr.io/nader7x/thepromptreportrag:production-latest`

**Status:** ✅ Docker publish workflow is now fully functional and compliant with container registry requirements.
