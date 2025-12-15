# EC2 Deployment Guide

This document outlines the deployment process for the Pixel Perfect Renderer API on AWS EC2.

---

## EC2 Instance Details

- **Instance Name:** `pdf-renderer-service`
- **Account:** Client AWS Account
- **Git Branch:** `feature-html-to-pdf`

---

## Deployment Process

### 1. Environment Setup

The EC2 instance has a `.env` file configured with all necessary environment variables including:
- API keys
- Azure Document Intelligence credentials
- Azure Blob Storage configuration
- Rate limiting settings

### 2. Build Docker Image

To build the Docker image with the latest code from the `feature-html-to-pdf` branch:

```bash
docker build -t pixel-perfect-renderer:latest .
```

This command:
- Builds a new Docker image from the Dockerfile
- Tags it as `pixel-perfect-renderer:latest`
- Includes all dependencies and configurations

### 3. Run the Container

Once the image is built, run the container to expose the API:

```bash
docker run -p 8000:8000 --env-file .env pixel-perfect-renderer
```

This command:
- Runs the Docker container
- Maps port 8000 on the host to port 8000 in the container
- Loads environment variables from the `.env` file
- Makes the API accessible at `http://<EC2-PUBLIC-IP>:8000`

---

## Updating the Service

When code changes are pushed to the `feature-html-to-pdf` branch:

1. **Pull the latest changes:**
   ```bash
   git pull origin feature-html-to-pdf
   ```

2. **Rebuild the Docker image:**
   ```bash
   docker build -t pixel-perfect-renderer:latest .
   ```

3. **Stop the running container:**
   ```bash
   docker stop $(docker ps -q --filter ancestor=pixel-perfect-renderer)
   ```

4. **Re-run with the updated image:**
   ```bash
   docker run -p 8000:8000 --env-file .env pixel-perfect-renderer
   ```

---

## Verification

After deployment, verify the service is running:

```bash
curl http://<EC2-PUBLIC-IP>:8000/health
```

Expected response:
```json
{
  "status": true,
  "message": "Service is healthy.",
  "data": null
}
```

---

## Notes

- The `.env` file is pre-configured on the EC2 instance and contains sensitive credentials
- Ensure the security group allows inbound traffic on port 8000
- For production deployments, consider using Docker Compose or container orchestration tools
