# Docker Local Testing Guide for QuickQ

This guide will help you test your Docker container locally to ensure it works properly before deploying to Google Cloud Platform (GCP).

## Prerequisites

- Docker Desktop installed and running
- Your project files in the current directory
- MongoDB Atlas connection configured
- GCP credentials configured (for Vertex AI)

## Step 1: Build the Docker Image

```bash
docker build -t quickq-local:latest .
```

**Expected Output:**
- Build should complete successfully without errors
- You should see all layers being processed
- Final message: "Successfully tagged quickq-local:latest"

## Step 2: Run the Container

```bash
docker run -d --name quickq-test -p 8080:8080 quickq-local:latest
```

**What this does:**
- `-d`: Runs container in detached mode (background)
- `--name quickq-test`: Names the container for easy reference
- `-p 8080:8080`: Maps host port 8080 to container port 8080
- `quickq-local:latest`: Uses the image we just built

## Step 3: Verify Container is Running

```bash
docker ps
```

**Expected Output:**
You should see your container listed with STATUS "Up" and PORTS showing "0.0.0.0:8080->8080/tcp"

## Step 4: Check Container Logs

```bash
docker logs quickq-test
```

**Expected Output:**
- Gunicorn starting messages
- Flask application startup messages
- MongoDB connection success
- Vertex AI initialization success
- No error messages

## Step 5: Test the Health Endpoint

```bash
curl -f http://localhost:8080/health
```

**Expected Response:**
```json
{
  "mongodb": "connected",
  "project_id": "quickq-462214",
  "region": "us-central1",
  "status": "healthy",
  "vertex_ai": "connected"
}
```

## Step 6: Test the Main API Endpoints

### Test Jobs Search
```bash
curl -X POST http://localhost:8080/jobs \
  -H "Content-Type: application/json" \
  -d '{"query": "python developer", "tech_skills": ["Python", "Flask"], "job_level": "senior"}'
```

### Test Questions Generation
```bash
curl -X POST http://localhost:8080/questions \
  -H "Content-Type: application/json" \
  -d '{
    "job": {
      "title": "Senior Python Developer",
      "description": "Looking for an experienced Python developer",
      "skills": ["Python", "Django", "AWS"]
    }
  }'
```

### Test Feedback Generation
```bash
curl -X POST http://localhost:8080/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "job": {
      "title": "Senior Python Developer",
      "description": "Looking for an experienced Python developer",
      "skills": ["Python", "Django", "AWS"]
    },
    "questions": [
      {
        "question": "What is your experience with Python?",
        "answer": "I have 5 years of experience with Python development."
      }
    ]
  }'
```

## Step 7: Performance Testing

### Test Container Resource Usage
```bash
docker stats quickq-test --no-stream
```

### Test Multiple Concurrent Requests
```bash
# Install Apache Bench if not available
# brew install httpd (on macOS)

# Test with 10 concurrent requests, 100 total
ab -n 100 -c 10 -H "Content-Type: application/json" \
  -p test_payload.json http://localhost:8080/jobs
```

Create `test_payload.json`:
```json
{"query": "python developer", "tech_skills": ["Python"], "job_level": "senior"}
```

## Step 8: Test Container Restart and Recovery

```bash
# Stop the container
docker stop quickq-test

# Start it again
docker start quickq-test

# Verify it's working
curl -f http://localhost:8080/health
```

## Step 9: Test with Environment Variables (GCP Simulation)

```bash
# Run with environment variables similar to GCP
docker run -d --name quickq-test-env \
  -p 8081:8080 \
  -e PORT=8080 \
  -e GOOGLE_CLOUD_PROJECT=quickq-462214 \
  quickq-local:latest

# Test the new instance
curl -f http://localhost:8081/health
```

## Step 10: Clean Up

```bash
# Stop and remove containers
docker stop quickq-test quickq-test-env
docker rm quickq-test quickq-test-env

# Optional: Remove the image
docker rmi quickq-local:latest
```

## Troubleshooting

### Container Won't Start
1. Check logs: `docker logs quickq-test`
2. Look for syntax errors in Python files
3. Verify all dependencies are in requirements.txt
4. Check if ports are already in use: `lsof -i :8080`

### API Returns Errors
1. Check container logs for detailed error messages
2. Verify MongoDB Atlas connection string
3. Ensure GCP credentials are properly configured
4. Test individual endpoints one by one

### Performance Issues
1. Monitor resource usage: `docker stats quickq-test`
2. Check if container has enough memory allocated
3. Review application logs for slow queries
4. Test with smaller payloads first

## GCP Deployment Readiness Checklist

✅ **Container builds successfully**
✅ **Container starts without errors**
✅ **Health endpoint responds correctly**
✅ **All API endpoints work as expected**
✅ **Container handles multiple requests**
✅ **Container recovers from restarts**
✅ **Resource usage is reasonable**
✅ **No syntax errors in code**
✅ **All dependencies are included**
✅ **Environment variables work correctly**

## Next Steps for GCP Deployment

Once all tests pass locally, your container is ready for GCP deployment:

1. **Cloud Build**: Your container will build the same way in GCP
2. **Cloud Run**: Will use the same container image and configuration
3. **Environment**: GCP will provide similar environment variables
4. **Scaling**: Cloud Run will handle multiple instances automatically
5. **Monitoring**: GCP provides built-in logging and monitoring

## Additional Testing Commands

### View Container Details
```bash
docker inspect quickq-test
```

### Execute Commands Inside Container
```bash
docker exec -it quickq-test /bin/bash
```

### Copy Files from Container
```bash
docker cp quickq-test:/app/logs ./local-logs
```

### Test with Different Resource Limits
```bash
docker run -d --name quickq-test-limited \
  --memory=512m --cpus=0.5 \
  -p 8082:8080 quickq-local:latest
```

This comprehensive testing approach ensures your Docker container will work reliably when deployed to GCP Cloud Run. 