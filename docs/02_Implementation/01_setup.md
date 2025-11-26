# Installation and Setup Guide

## Prerequisites

### System Requirements
- **OS**: Windows 10/11, macOS, or Linux
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 20GB free space
- **Python**: 3.11+
- **MySQL**: 8.0+
- **Redis**: 7.0+ (optional for development)

### Required Software
- Python 3.11 or higher
- MySQL 8.0
- Git
- Virtual environment tool (venv)
- Code editor (VS Code recommended)

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/your-repo/eng-saas-platform.git
cd eng-saas-platform
```

### 2. Create Virtual Environment

**Windows**:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/Mac**:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment

Create `.env` file from example:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` file:

```env
# Django Settings
SECRET_KEY=your-very-long-secret-key-here-min-50-characters
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=saas_platform
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Email (for development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### 5. Create Database

**MySQL**:
```sql
CREATE DATABASE saas_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**Or via command line**:
```bash
mysql -u root -p -e "CREATE DATABASE saas_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### 6. Run Migrations

```bash
python manage.py migrate
```

Expected output:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, core, ...
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
```

### 7. Create Superuser

```bash
python manage.py createsuperuser
```

Follow prompts:
```
Username: admin
Email: admin@example.com
Password: ********
Password (again): ********
Superuser created successfully.
```

### 8. Collect Static Files

```bash
python manage.py collectstatic
```

### 9. Run Development Server

```bash
python manage.py runserver
```

Server will start at: `http://127.0.0.1:8000/`

### 10. Verify Installation

Open browser and navigate to:
- **Application**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/django-admin/

Login with superuser credentials.

## Optional Components

### Redis Setup

**Windows**:
- Download Redis for Windows
- Or use WSL/Docker

**Linux**:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
```

**Mac**:
```bash
brew install redis
brew services start redis
```

Verify Redis:
```bash
redis-cli ping
# Should return: PONG
```

### Celery Setup

Start Celery worker:

**Windows**:
```powershell
celery -A saas_platform worker --loglevel=info --pool=solo
```

**Linux/Mac**:
```bash
celery -A saas_platform worker --loglevel=info
```

Start Celery beat (scheduler):
```bash
celery -A saas_platform beat --loglevel=info
```

## Initial Data Setup

### Create Test Company

```bash
python manage.py shell
```

```python
from core.models import Company

company = Company.objects.create(
    name='Test College',
    subdomain='testcollege',
    schema_name='testcollege',
    contact_email='contact@testcollege.edu',
    contact_phone='+1234567890',
    is_active=True
)
```

### Create Academic Year

```python
from core.models import AcademicYear

year = AcademicYear.objects.create(
    name='2024-2025',
    start_date='2024-08-01',
    end_date='2025-07-31',
    is_active=True
)
```

## Troubleshooting

### Database Connection Error

**Error**: `django.db.utils.OperationalError: (2003, "Can't connect to MySQL server")`

**Solution**:
1. Check MySQL is running
2. Verify credentials in `.env`
3. Check MySQL port (default 3306)
4. Test connection: `mysql -u root -p`

### Import Error

**Error**: `ModuleNotFoundError: No module named 'mysqlclient'`

**Solution**:
```bash
pip install mysqlclient

# If fails, try:
pip install pymysql
```

Then add to `settings.py`:
```python
import pymysql
pymysql.install_as_MySQLdb()
```

### Migration Conflicts

**Error**: `Migration conflicts detected`

**Solution**:
```bash
python manage.py makemigrations --merge
python manage.py migrate
```

### Port Already in Use

**Error**: `Error: That port is already in use.`

**Solution**:
```bash
# Use different port
python manage.py runserver 8080

# Or find and kill process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill
```

### Static Files Not Loading

**Solution**:
1. Run `python manage.py collectstatic`
2. Check `STATIC_ROOT` in settings
3. Verify `DEBUG=True` for development
4. Clear browser cache

## Development Workflow

### 1. Activate Environment
```bash
# Always activate venv first
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\Activate.ps1  # Windows
```

### 2. Pull Latest Changes
```bash
git pull origin main
pip install -r requirements.txt
python manage.py migrate
```

### 3. Make Changes
- Edit code
- Create/modify models
- Write tests

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Test Changes
```bash
python manage.py runserver
# Or run tests
pytest
```

### 6. Commit and Push
```bash
git add .
git commit -m "Description of changes"
git push origin main
```

## Next Steps

- [Docker Setup](../03_Docker/01_docker_setup.md)
- [User Management](user_management.md)
- [Creating Your First Tenant](first_tenant.md)
- [Configuration Guide](configuration.md)

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Redis Documentation](https://redis.io/documentation)
- [Celery Documentation](https://docs.celeryproject.org/)
