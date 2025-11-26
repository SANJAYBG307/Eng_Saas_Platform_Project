#!/bin/bash
# Docker deployment script for SaaS Platform

set -e

echo "================================================"
echo "SaaS Platform - Docker Deployment Script"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found!${NC}"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo -e "${RED}Please update .env file with your configuration before continuing!${NC}"
    exit 1
fi

# Generate SSL certificates if not exists
if [ ! -f docker/nginx/ssl/cert.pem ]; then
    echo -e "${YELLOW}Generating self-signed SSL certificates...${NC}"
    bash docker/nginx/ssl/generate_cert.sh
fi

# Build and start containers
echo -e "${GREEN}Building Docker images...${NC}"
docker-compose build --no-cache

echo -e "${GREEN}Starting containers...${NC}"
docker-compose up -d

# Wait for database to be ready
echo -e "${YELLOW}Waiting for database to be ready...${NC}"
sleep 10

# Run migrations
echo -e "${GREEN}Running database migrations...${NC}"
docker-compose exec web python manage.py migrate

# Collect static files
echo -e "${GREEN}Collecting static files...${NC}"
docker-compose exec web python manage.py collectstatic --noinput

# Create superuser if needed
echo -e "${YELLOW}Do you want to create a superuser? (y/n)${NC}"
read -r create_superuser
if [ "$create_superuser" = "y" ]; then
    docker-compose exec web python manage.py createsuperuser
fi

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "Application URLs:"
echo "  - HTTP:  http://localhost"
echo "  - HTTPS: https://localhost"
echo "  - Admin: https://localhost/django-admin/"
echo ""
echo "Useful commands:"
echo "  - View logs:        docker-compose logs -f"
echo "  - Stop containers:  docker-compose down"
echo "  - Restart:          docker-compose restart"
echo "  - Shell access:     docker-compose exec web bash"
echo ""
