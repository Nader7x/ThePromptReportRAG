# Docker Configuration Guide

This guide explains how to use Docker and Docker Compose with the Enhanced RAG application.

## Quick Start

### 1. Set up environment variables

Copy the example environment file and configure your API key:

```bash
# Copy the example file
cp .env.example .env

# Edit the .env file and set your Gemini API key
# GEMINI_API_KEY=your_actual_api_key_here
```

### 2. Development Setup

For development with hot reload:

```bash
# Start both API and Streamlit services
docker-compose up --build

# Or start services individually
docker-compose up api         # API only
docker-compose up streamlit   # Streamlit only (requires API)
```

### 3. Production Setup

For production deployment:

```bash
# Use the production configuration
docker-compose -f docker-compose.production.yml up --build -d
```

## Services

### API Service

- **Port**: 8000
- **Health Check**: http://localhost:8000/api/health
- **Documentation**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### Streamlit Service

- **Port**: 8501
- **URL**: http://localhost:8501
- **Health Check**: http://localhost:8501/\_stcore/health

## Configuration Files

### Development

- `Dockerfile` - Standard development Dockerfile
- `docker-compose.yml` - Development configuration

### Production

- `Dockerfile.production` - Production-optimized Dockerfile with security features
- `docker-compose.production.yml` - Production configuration with additional services

## Environment Variables

| Variable         | Description            | Default | Required |
| ---------------- | ---------------------- | ------- | -------- |
| `GEMINI_API_KEY` | Google Gemini API key  | -       | Yes      |
| `API_PORT`       | API service port       | 8000    | No       |
| `STREAMLIT_PORT` | Streamlit service port | 8501    | No       |
| `LOG_LEVEL`      | Logging level          | INFO    | No       |

## Volumes

The application uses several volumes for persistent data:

- `./logs` - Application logs
- `./data` - Application data
- `./knowledge_base_vectors` - Vector database files
- `api_cache` - API caching (production only)

## Networking

Services communicate through the `rag_network` bridge network:

- API service accessible at `http://api:8000` from within containers
- External access via mapped ports

## Health Checks

Both services include health checks:

- **API**: Checks `/api/health` endpoint
- **Streamlit**: Checks Streamlit's internal health endpoint

Health checks include:

- 30s interval between checks
- 10s timeout per check
- 3 retries before marking unhealthy
- 40s startup grace period

## Commands

### Common Operations

```bash
# Build and start all services
docker-compose up --build

# Start services in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild specific service
docker-compose build api
docker-compose up api
```

### Production Operations

```bash
# Start production services
docker-compose -f docker-compose.production.yml up -d

# View production logs
docker-compose -f docker-compose.production.yml logs -f

# Scale services (if needed)
docker-compose -f docker-compose.production.yml up -d --scale api=2
```

### Debugging

```bash
# Execute commands in running container
docker-compose exec api bash
docker-compose exec streamlit bash

# View container status
docker-compose ps

# View resource usage
docker stats
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: Change ports in `.env` file
2. **API key not set**: Ensure `GEMINI_API_KEY` is properly set in `.env`
3. **Volume permissions**: Ensure Docker has access to mounted directories
4. **Health check failures**: Check logs for startup errors

### Logs

View logs for debugging:

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs api
docker-compose logs streamlit

# Follow logs
docker-compose logs -f
```

### Clean Up

```bash
# Stop and remove containers
docker-compose down

# Remove images
docker-compose down --rmi all

# Remove volumes (will delete data!)
docker-compose down -v
```

## Security Notes

### Development

- API key is passed via environment variable
- Services run as root (acceptable for development)
- CORS allows all origins

### Production

- Uses non-root user in containers
- Environment variables should be secured
- Consider using Docker secrets for sensitive data
- Implement proper CORS configuration
- Use HTTPS with reverse proxy (nginx configuration available)

## Next Steps

1. **Monitoring**: Add monitoring with Prometheus/Grafana
2. **Logging**: Centralized logging with ELK stack
3. **Load Balancing**: Scale services behind a load balancer
4. **SSL/TLS**: Configure HTTPS with Let's Encrypt
5. **CI/CD**: Automate builds and deployments
