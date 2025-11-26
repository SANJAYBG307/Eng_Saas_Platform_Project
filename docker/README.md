# Docker Configuration for SaaS Platform

This directory contains Docker configuration files for deploying the SaaS Platform in production.

## Directory Structure

```
docker/
├── nginx/
│   ├── conf.d/          # Nginx server configurations
│   ├── ssl/             # SSL certificates
│   └── nginx.conf       # Main Nginx configuration
├── mysql/
│   └── init.sql         # Database initialization script
├── deploy.sh            # Linux/Mac deployment script
├── deploy.ps1           # Windows deployment script
└── README.md            # This file
```

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum (8GB recommended)
- 20GB disk space

## Quick Start

### 1. Environment Setup

Copy the example environment file and configure:

```bash
cp .env.example .env
```

Edit `.env` and update:
- `SECRET_KEY`: Generate a secure key (50+ characters)
- `DB_PASSWORD`: Strong database password
- `DB_ROOT_PASSWORD`: Strong root password
- `REDIS_PASSWORD`: Strong Redis password
- `STRIPE_SECRET_KEY`: Your Stripe API keys
- `EMAIL_HOST_PASSWORD`: Your email service credentials
- `ALLOWED_HOSTS`: Your domain names

### 2. SSL Certificates

#### Development (Self-signed):
```bash
cd docker/nginx/ssl
bash generate_cert.sh
```

#### Production (Let's Encrypt):
Use Certbot or your certificate provider and place:
- Certificate: `docker/nginx/ssl/cert.pem`
- Private Key: `docker/nginx/ssl/key.pem`

### 3. Deploy

#### Linux/Mac:
```bash
bash docker/deploy.sh
```

#### Windows PowerShell:
```powershell
.\docker\deploy.ps1
```

## Docker Services

### Web Application (Django)
- **Port**: 8000
- **Container**: `saas_web`
- **Command**: Gunicorn with 4 workers

### MySQL Database
- **Port**: 3306
- **Container**: `saas_mysql`
- **Volume**: `mysql_data`

### Redis Cache
- **Port**: 6379
- **Container**: `saas_redis`
- **Volume**: `redis_data`

### Celery Worker
- **Container**: `saas_celery_worker`
- **Concurrency**: 4 workers

### Celery Beat
- **Container**: `saas_celery_beat`
- **Function**: Task scheduler

### Nginx Reverse Proxy
- **Ports**: 80 (HTTP), 443 (HTTPS)
- **Container**: `saas_nginx`

## Management Commands

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f celery_worker
```

### Access Container Shell
```bash
docker-compose exec web bash
docker-compose exec db mysql -u root -p
```

### Run Django Commands
```bash
# Migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic

# Django shell
docker-compose exec web python manage.py shell
```

### Database Backup
```bash
# Backup
docker-compose exec db mysqldump -u root -p saas_platform > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
docker-compose exec -T db mysql -u root -p saas_platform < backup.sql
```

### Restart Services
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart web
docker-compose restart nginx
```

### Scale Celery Workers
```bash
docker-compose up -d --scale celery_worker=4
```

## Monitoring

### Health Checks
- Application: `https://your-domain.com/health/`
- Readiness: `https://your-domain.com/readiness/`
- Liveness: `https://your-domain.com/liveness/`

### Container Stats
```bash
docker stats
```

### Check Service Health
```bash
docker-compose ps
```

## Production Deployment

### 1. Update Environment
- Set `DEBUG=False`
- Configure production domains in `ALLOWED_HOSTS`
- Use strong passwords for all services
- Configure email service
- Set up Stripe production keys
- Configure S3 for media files (optional)

### 2. SSL/TLS Configuration
- Obtain valid SSL certificate
- Update Nginx configuration if needed
- Enable HSTS headers (already configured)

### 3. Performance Tuning
- Adjust Gunicorn workers: `GUNICORN_WORKERS=4` (2 * CPU cores + 1)
- Configure MySQL buffer pool size in `docker-compose.yml`
- Adjust Redis memory limit based on usage
- Scale Celery workers based on task load

### 4. Security Checklist
- [ ] Change all default passwords
- [ ] Enable SSL/TLS
- [ ] Configure firewall rules
- [ ] Set up regular backups
- [ ] Configure Sentry for error tracking
- [ ] Enable rate limiting in Nginx
- [ ] Review Django security settings
- [ ] Set up monitoring and alerts

### 5. Backup Strategy
- Database: Daily automated backups
- Media files: Sync to S3 or backup storage
- Configuration: Version control `.env` template

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs web

# Check container status
docker-compose ps

# Rebuild
docker-compose build --no-cache web
```

### Database Connection Issues
```bash
# Check MySQL is running
docker-compose ps db

# Test connection
docker-compose exec web python manage.py dbshell
```

### Static Files Not Loading
```bash
# Recollect static files
docker-compose exec web python manage.py collectstatic --clear --noinput

# Check Nginx volume
docker-compose exec nginx ls -la /app/staticfiles/
```

### Permission Issues
```bash
# Fix ownership
docker-compose exec web chown -R appuser:appuser /app/mediafiles
```

## Development vs Production

### Development Mode
- Use `docker-compose.yml` as is
- Self-signed SSL certificates
- Debug mode enabled
- Local volumes mounted

### Production Mode
- Set `DEBUG=False` in `.env`
- Valid SSL certificates
- Separate database server (optional)
- S3 for static/media files (recommended)
- Configure monitoring (Sentry)
- Set up log aggregation

## Useful Links

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review health checks: `/health/` endpoint
- Contact: support@your-domain.com
