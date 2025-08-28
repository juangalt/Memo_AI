#!/bin/bash

# Production Deployment Script for Memo AI Coach
# This script handles proper file permissions and container deployment

set -e  # Exit on any error

echo "=== Memo AI Coach Production Deployment ==="
echo "Starting deployment at $(date)"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy env.example to .env and configure your environment variables."
    echo "cp env.example .env"
    exit 1
fi

# Load environment variables
source .env

echo "1. Checking environment configuration..."
if [ -z "$DOMAIN" ] || [ "$DOMAIN" = "your-subdomain.com" ]; then
    echo "ERROR: Please configure DOMAIN in .env file"
    exit 1
fi

if [ -z "$LLM_API_KEY" ] || [ "$LLM_API_KEY" = "your-anthropic-api-key-here" ]; then
    echo "ERROR: Please configure LLM_API_KEY in .env file"
    exit 1
fi

if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "your-secret-key-here-generate-a-secure-random-string" ]; then
    echo "ERROR: Please configure SECRET_KEY in .env file"
    exit 1
fi

echo "2. Setting up directory permissions for containers..."

# Ensure proper ownership for mounted volumes
# Host user should own the directories that will be mounted
sudo chown -R $USER:$USER ./config ./data ./logs ./letsencrypt

# Set proper permissions for config files (readable by container user)
chmod -R 644 ./config/*.yaml
chmod 755 ./config

# Set proper permissions for data directory (writable by container user)
chmod 755 ./data
chmod 644 ./data/*.db 2>/dev/null || true  # Ignore if no db files exist yet

# Set proper permissions for logs directory (writable by container user)
chmod 755 ./logs
chmod 644 ./logs/*.log 2>/dev/null || true  # Ignore if no log files exist yet

# Set proper permissions for letsencrypt directory
chmod 755 ./letsencrypt
chmod 600 ./letsencrypt/acme.json 2>/dev/null || true  # Ignore if file doesn't exist

echo "3. Validating configuration files..."
cd backend
python3 validate_config.py
if [ $? -ne 0 ]; then
    echo "ERROR: Configuration validation failed!"
    exit 1
fi
cd ..

echo "4. Building Docker images..."
docker compose build --no-cache

echo "5. Stopping existing containers..."
docker compose down

echo "6. Starting production containers..."
docker compose up -d

echo "7. Waiting for services to start..."
sleep 30

echo "8. Checking container health..."
docker compose ps

echo "9. Testing configuration paths inside containers..."
echo "Testing backend configuration access..."
docker compose exec backend ls -la /app/config/ || echo "Backend config check failed"
docker compose exec backend python -c "import yaml; print('Backend config loaded:', bool(yaml.safe_load(open('/app/config/rubric.yaml'))))" || echo "Backend config loading failed"

echo "Testing frontend configuration access..."
docker compose exec frontend ls -la /app/config/ || echo "Frontend config check failed"
docker compose exec frontend python -c "import yaml; print('Frontend config loaded:', bool(yaml.safe_load(open('/app/config/prompt.yaml'))))" || echo "Frontend config loading failed"

echo "10. Testing user permissions..."
echo "Backend container user:"
docker compose exec backend whoami || echo "Backend user check failed"
docker compose exec backend id || echo "Backend id check failed"

echo "Frontend container user:"
docker compose exec frontend whoami || echo "Frontend user check failed"
docker compose exec frontend id || echo "Frontend id check failed"

echo "11. Testing health endpoints..."
echo "Testing backend health..."
curl -f http://localhost:8000/health || echo "Backend health check failed"

echo "Testing frontend health..."
curl -f http://localhost:8501/_stcore/health || echo "Frontend health check failed"

echo "12. Deployment summary:"
echo "- Domain: $DOMAIN"
echo "- Backend URL: http://localhost:8000"
echo "- Frontend URL: http://localhost:8501"
echo "- Traefik Dashboard: http://localhost:8080"
echo "- HTTPS URL: https://$DOMAIN"

echo ""
echo "=== Deployment Complete ==="
echo "Next steps:"
echo "1. Configure your DNS to point $DOMAIN to this server"
echo "2. Ensure ports 80, 443, and 8080 are accessible from the internet"
echo "3. Wait for Let's Encrypt SSL certificate generation"
echo "4. Test the application at https://$DOMAIN"
echo ""
echo "To monitor logs: docker compose logs -f"
echo "To stop services: docker compose down"
echo "To restart services: docker compose restart"
