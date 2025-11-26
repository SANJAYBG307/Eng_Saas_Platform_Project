# Docker Deployment Guide

## Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 20GB free disk space

### Deploy in 3 Steps

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your settings

# 2. Generate SSL certificates (development)
cd docker/nginx/ssl
bash generate_cert.sh
cd ../../..

# 3. Deploy
bash docker/deploy.sh
```

Your application will be available at:
- HTTP: http://localhost
- HTTPS: https://localhost
- Admin: https://localhost/django-admin/

## Environment Configuration

### Required Variables

Edit `.env` file:

```env
# Security - CHANGE THESE!
SECRET_KEY=generate-a-very-long-secret-key-minimum-50-characters
DB_PASSWORD=your-strong-database-password
DB_ROOT_PASSWORD=your-strong-root-password
REDIS_PASSWORD=your-strong-redis-password

# Application
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Stripe
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_PUBLIC_KEY=pk_live_your_stripe_public_key

# Email
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
```

### Generate Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Services

### Architecture

```
┌─────────────────────────────────────────────┐
│              Nginx (Port 80, 443)           │
│         (Reverse Proxy + SSL)               │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│           Django Web App (Port 8000)        │
│              (Gunicorn)                     │
└────────┬───────────────────────┬────────────┘
         │                       │
┌────────▼────────┐    ┌────────▼────────┐
│   MySQL (3306)  │    │  Redis (6379)   │
│   (Database)    │    │   (Cache)       │
└─────────────────┘    └─────────────────┘
         │                       │
┌────────▼───────────────────────▼────────┐
│         Celery Worker + Beat            │
│        (Background Tasks)               │
└─────────────────────────────────────────┘
```

### Service Details

**1. web** - Django Application
- Image: Custom (built from Dockerfile)
- Port: 8000
- Workers: 4 Gunicorn workers
- Auto-restart: Yes

**2. db** - MySQL Database
- Image: mysql:8.0
- Port: 3306
- Volume: mysql_data (persistent)
- Health check: mysqladmin ping

**3. redis** - Redis Cache
- Image: redis:7-alpine
- Port: 6379
- Volume: redis_data (persistent)
- Max memory: 256MB

**4. celery_worker** - Task Worker
- Image: Custom (same as web)
- Concurrency: 4 workers
- Tasks: Email, reports, cleanup

**5. celery_beat** - Task Scheduler
- Image: Custom (same as web)
- Function: Periodic tasks

**6. nginx** - Web Server
- Image: nginx:1.25-alpine
- Ports: 80 (HTTP), 443 (HTTPS)
- SSL: Configured

## Docker Commands

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
docker-compose logs -f nginx
docker-compose logs -f celery_worker
```

### Restart Services

```bash
# All services
docker-compose restart

# Specific service
docker-compose restart web
```

### Check Status

```bash
docker-compose ps
```

### Execute Commands

```bash
# Django shell
docker-compose exec web python manage.py shell

# Database migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic
```

### Access Container Shell

```bash
# Web container
docker-compose exec web bash

# Database container
docker-compose exec db bash
docker-compose exec db mysql -u root -p
```

## SSL Configuration

### Development (Self-signed)

Generate certificates:

```bash
cd docker/nginx/ssl
bash generate_cert.sh
```

Browser will show "Not Secure" warning - this is normal for self-signed certificates.

### Production (Let's Encrypt)

1. Install Certbot:
```bash
# Ubuntu/Debian
sudo apt install certbot python3-certbot-nginx
```

2. Generate certificates:
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

3. Copy certificates:
```bash
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem docker/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem docker/nginx/ssl/key.pem
```

4. Auto-renewal:
```bash
sudo certbot renew --dry-run
```

## Database Management

### Backup Database

```bash
# Create backup
docker-compose exec db mysqldump -u root -p saas_platform > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore Database

```bash
# Restore from backup
docker-compose exec -T db mysql -u root -p saas_platform < backup.sql
```

### Access MySQL

```bash
docker-compose exec db mysql -u root -p
```

```sql
USE saas_platform;
SHOW TABLES;
SELECT COUNT(*) FROM core_useraccount;
```

## Scaling

### Scale Celery Workers

```bash
docker-compose up -d --scale celery_worker=4
```

### Scale Web Servers

For multiple web servers, you need:
1. Load balancer (Nginx upstream)
2. Shared session storage (Redis)
3. Shared media files (S3/NFS)

```yaml
# docker-compose.yml
services:
  web:
    replicas: 3
```

## Monitoring

### Health Checks

- Application: https://yourdomain.com/health/
- Readiness: https://yourdomain.com/readiness/
- Liveness: https://yourdomain.com/liveness/

### Container Stats

```bash
docker stats
```

### Disk Usage

```bash
# Check volume sizes
docker system df

# Clean up unused resources
docker system prune -a
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs web

# Rebuild
docker-compose build --no-cache web
docker-compose up -d
```

### Database Connection Error

```bash
# Check database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Verify environment variables
docker-compose exec web env | grep DB_
```

### Static Files Not Loading

```bash
# Recollect static files
docker-compose exec web python manage.py collectstatic --clear --noinput

# Check Nginx config
docker-compose exec nginx nginx -t

# Restart Nginx
docker-compose restart nginx
```

### Out of Memory

```bash
# Check memory usage
docker stats

# Increase Docker memory limit
# Docker Desktop > Settings > Resources > Memory
```

## Production Checklist

- [ ] Change all default passwords
- [ ] Set `DEBUG=False`
- [ ] Configure valid SSL certificates
- [ ] Set up database backups
- [ ] Configure email service
- [ ] Set up monitoring (Sentry)
- [ ] Configure log aggregation
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Test disaster recovery
- [ ] Document runbook

## Development vs Production

### Development Setup

```bash
# Use development compose file
docker-compose -f docker-compose.dev.yml up
```

Features:
- DEBUG=True
- Code hot-reload
- No SSL required
- Console email backend

### Production Setup

```bash
# Use production compose file
docker-compose up -d
```

Features:
- DEBUG=False
- Gunicorn production server
- SSL enabled
- Real email service
- Redis cache
- Celery workers

## Related Documentation

- [Dockerfile Reference](../04_Explanation/dockerfile.md)
- [Nginx Configuration](../04_Explanation/nginx.md)
- [Production Deployment](production.md)
- [Monitoring Guide](monitoring.md)
