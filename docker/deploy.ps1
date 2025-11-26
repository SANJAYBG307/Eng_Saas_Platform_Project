# Docker Deployment Script for SaaS Platform (Windows)
# Run with: .\docker\deploy.ps1

$ErrorActionPreference = "Stop"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "SaaS Platform - Docker Deployment Script" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Check if .env file exists
if (-not (Test-Path .env)) {
    Write-Host "Warning: .env file not found!" -ForegroundColor Yellow
    Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "Please update .env file with your configuration before continuing!" -ForegroundColor Red
    exit 1
}

# Check if Docker is running
try {
    docker ps | Out-Null
} catch {
    Write-Host "Error: Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Generate SSL certificates if not exists (Windows OpenSSL or use pre-generated)
if (-not (Test-Path docker/nginx/ssl/cert.pem)) {
    Write-Host "Note: SSL certificates not found." -ForegroundColor Yellow
    Write-Host "For development, you can generate them with OpenSSL or use provided certificates." -ForegroundColor Yellow
    Write-Host "Continuing without SSL setup..." -ForegroundColor Yellow
}

# Build and start containers
Write-Host "Building Docker images..." -ForegroundColor Green
docker-compose build --no-cache

Write-Host "Starting containers..." -ForegroundColor Green
docker-compose up -d

# Wait for database to be ready
Write-Host "Waiting for database to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Run migrations
Write-Host "Running database migrations..." -ForegroundColor Green
docker-compose exec -T web python manage.py migrate

# Collect static files
Write-Host "Collecting static files..." -ForegroundColor Green
docker-compose exec -T web python manage.py collectstatic --noinput

# Create superuser prompt
Write-Host "Do you want to create a superuser? (y/n): " -ForegroundColor Yellow -NoNewline
$createSuperuser = Read-Host
if ($createSuperuser -eq "y") {
    docker-compose exec web python manage.py createsuperuser
}

Write-Host "================================================" -ForegroundColor Green
Write-Host "Deployment completed successfully!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Application URLs:"
Write-Host "  - HTTP:  http://localhost"
Write-Host "  - HTTPS: https://localhost"
Write-Host "  - Admin: https://localhost/django-admin/"
Write-Host ""
Write-Host "Useful commands:"
Write-Host "  - View logs:        docker-compose logs -f"
Write-Host "  - Stop containers:  docker-compose down"
Write-Host "  - Restart:          docker-compose restart"
Write-Host "  - Shell access:     docker-compose exec web bash"
Write-Host ""
