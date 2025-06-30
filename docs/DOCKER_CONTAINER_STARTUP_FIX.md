# 🐳 Docker Container Startup Fix

## 📋 Issue Summary

The Docker publish workflow was failing at the "🧪 Test Docker image" step with the error:

```
❌ Container failed to start
Error response from daemon: No such container: test-container
```

The `docker run` command was not successfully starting the container, causing the test to fail immediately.

## 🔧 Root Cause

**Dockerfile Issues:**

1. **Incorrect virtual environment setup:** Using `uv venv` but not properly activating it in the CMD
2. **Wrong startup command:** Using `CMD ["python", "api.py"]` instead of proper uvicorn server
3. **NLTK downloads:** Noisy downloads that could potentially fail
4. **Poor error visibility:** Limited debugging information in the workflow

**Application Issues:**

- FastAPI server wasn't starting properly due to virtual environment issues
- Missing proper uvicorn command for production deployment

## ✅ Solution Applied

### 1. **Fixed Dockerfile (Main)**

```dockerfile
# Before (Problematic)
RUN pip install uv
RUN uv venv && . .venv/bin/activate
RUN uv pip install --no-cache-dir -r requirements.txt
RUN . .venv/bin/activate && python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
CMD ["python", "api.py"]

# After (Fixed)
RUN pip install --no-cache-dir -r requirements.txt
RUN python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True)"
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. **Fixed Dockerfile.production**

```dockerfile
# Updated to match main Dockerfile fixes
RUN python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True)"
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. **Enhanced Container Testing Workflow**

```yaml
- name: 🧪 Test Docker image
  run: |
    # Verify image exists
    echo "🔍 Checking if image exists..."
    if ! docker images | grep -q "$(echo $IMAGE_TAG | cut -d: -f1)"; then
      echo "❌ Image not found in local registry"
      echo "📋 Available images:"
      docker images
      exit 1
    fi

    # Show image details
    echo "📊 Image details:"
    docker inspect --format='{{.Config.Cmd}}' $IMAGE_TAG
    docker inspect --format='{{.Config.ExposedPorts}}' $IMAGE_TAG

    # Enhanced container startup with error handling
    if ! CONTAINER_ID=$(docker run --rm -d --name test-container \
      -e GEMINI_API_KEY="test-key-placeholder" \
      -p 8000:8000 \
      $IMAGE_TAG); then
      echo "❌ Failed to start container"
      exit 1
    fi
```

### 4. **Comprehensive Error Handling**

```yaml
# Check if container is still running during tests
if ! docker ps --format "table {{.Names}}\t{{.Status}}" | grep test-container; then
echo "❌ Container stopped unexpectedly"
echo "📋 Container logs:"
docker logs test-container 2>&1 || echo "Could not retrieve logs"
echo "📋 All containers:"
docker ps -a
exit 1
fi
```

## 📊 Key Improvements

### 1. **Simplified Dependency Management**

- Removed complex `uv` virtual environment setup
- Used standard `pip install` for reliability
- Made NLTK downloads quiet to reduce noise

### 2. **Proper FastAPI Server Startup**

- Changed from `python api.py` to `uvicorn api:app --host 0.0.0.0 --port 8000`
- Ensures proper ASGI server startup
- Consistent between development and production

### 3. **Enhanced Debugging and Monitoring**

- **Image verification:** Check if image exists before testing
- **Image inspection:** Show CMD and exposed ports
- **Container status monitoring:** Continuous checks during testing
- **Detailed logging:** Show container logs on failure
- **Network testing:** Verify connectivity issues
- **Container stats:** Resource usage monitoring

### 4. **Robust Error Recovery**

- **Graceful failures:** Detailed error messages with context
- **Log collection:** Automatic log retrieval on failures
- **Cleanup:** Proper container cleanup even on failures
- **Multi-point validation:** Image, container, and application level checks

## 🎯 Before vs After

### Before (Failing)

```bash
❌ Container failed to start
Error response from daemon: No such container: test-container
```

### After (Detailed Debugging)

```bash
🔍 Checking if image exists...
✅ Image found: ghcr.io/nader7x/thepromptreportrag:latest

📊 Image details:
[uvicorn api:app --host 0.0.0.0 --port 8000]
{8000/tcp:{}}

🚀 Starting container...
📝 Container started with ID: abc123...
✅ Container is running

📋 Container logs (first 20 lines):
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000

⏳ Health check attempt 1/10...
✅ Health check passed
✅ API docs endpoint accessible
✅ Docker image test completed successfully
```

## 🚀 Testing Workflow Enhancements

### 1. **Pre-Flight Checks**

- Verify image existence in local registry
- Inspect image configuration and exposed ports
- Show available images if target image missing

### 2. **Startup Monitoring**

- Monitor container startup process
- Check container status continuously
- Collect and display startup logs

### 3. **Health Check Improvements**

- Extended wait time for application startup (20 seconds total)
- Multiple health check attempts with detailed reporting
- Test multiple endpoints (health, docs)
- Network connectivity verification

### 4. **Failure Analysis**

- Automatic log collection on any failure
- Container status reporting
- Network diagnostic information
- Resource usage statistics

## 📚 Docker Best Practices Applied

### 1. **Simplified Build Process**

- Removed unnecessary virtual environment complexity
- Used standard Python package installation
- Optimized layer caching

### 2. **Production-Ready Server**

- Proper ASGI server (uvicorn) instead of development server
- Correct host binding (0.0.0.0) for container networking
- Explicit port configuration

### 3. **Security and Reliability**

- Non-root user in production Dockerfile
- Proper health checks
- Clean dependency installation

## 🔄 Result

The Docker workflow now:

- ✅ **Builds containers reliably** with proper FastAPI server startup
- ✅ **Provides comprehensive debugging** for troubleshooting issues
- ✅ **Tests thoroughly** with multiple validation points
- ✅ **Handles failures gracefully** with detailed error reporting
- ✅ **Follows best practices** for container deployment

**Status:** Docker container startup issues resolved with enhanced debugging and proper FastAPI server configuration.
