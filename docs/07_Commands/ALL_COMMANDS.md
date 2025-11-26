# 📋 Complete List of Commands Used

## Django Engineering SaaS Platform - All Commands from Start to Finish

---

## 🚀 SECTION 1: Project Initialization Commands

### 1.1 Create Project Directory
```bash
# Create project folder
mkdir Eng_Saas_Platform_Project
cd Eng_Saas_Platform_Project
```

### 1.2 Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 1.3 Install Django and Dependencies
```bash
# Install Django
pip install django==5.0

# Install all dependencies
pip install -r requirements.txt

# Key packages installed:
pip install mysqlclient==2.2.0        # MySQL database driver
pip install redis==5.0.0              # Redis cache
pip install celery==5.3.4             # Background tasks
pip install stripe==7.4.0             # Payment processing
pip install python-dotenv==1.0.0      # Environment variables
pip install gunicorn==21.2.0          # WSGI server
pip install pytest==7.4.3             # Testing framework
pip install pytest-django==4.7.0      # Django testing plugin
pip install pytest-cov==4.1.0         # Coverage reporting
pip install factory-boy==3.3.0        # Test data factories
pip install Faker==20.1.0             # Fake data generation
```

### 1.4 Create Django Project
```bash
# Create Django project
django-admin startproject saas_platform .

# Note: The dot (.) creates project in current directory
```

---

## 📦 SECTION 2: App Creation Commands

### 2.1 Create All Django Apps
```bash
# Create core app (authentication, base models)
python manage.py startapp core

# Create company admin app
python manage.py startapp company_admin

# Create tenant subscription app
python manage.py startapp tenant_subscription

# Create college management app
python manage.py startapp college_management

# Create department management app
python manage.py startapp department_management

# Create teacher app
python manage.py startapp teacher

# Create student app
python manage.py startapp student

# Create parent app
python manage.py startapp parent
```

---

## 🗄️ SECTION 3: Database Commands

### 3.1 MySQL Database Setup
```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE saas_platform_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Create database user
CREATE USER 'saas_user'@'localhost' IDENTIFIED BY 'your_password';

# Grant permissions
GRANT ALL PRIVILEGES ON saas_platform_db.* TO 'saas_user'@'localhost';
FLUSH PRIVILEGES;

# Exit MySQL
EXIT;
```

### 3.2 Django Migration Commands
```bash
# Create migrations for all apps
python manage.py makemigrations

# Create migrations for specific app
python manage.py makemigrations core
python manage.py makemigrations company_admin
python manage.py makemigrations tenant_subscription
python manage.py makemigrations college_management
python manage.py makemigrations department_management
python manage.py makemigrations teacher
python manage.py makemigrations student
python manage.py makemigrations parent

# Apply migrations to database
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Migrate specific app
python manage.py migrate core
python manage.py migrate teacher

# Rollback migration
python manage.py migrate core 0001

# Show SQL for migration (without executing)
python manage.py sqlmigrate core 0001

# Check for migration issues
python manage.py makemigrations --check
python manage.py migrate --plan
```

### 3.3 Database Management
```bash
# Create database backup
python manage.py dumpdata > backup.json

# Load data from backup
python manage.py loaddata backup.json

# Dump specific app data
python manage.py dumpdata core > core_backup.json
python manage.py dumpdata teacher > teacher_backup.json

# Flush database (delete all data)
python manage.py flush

# Reset database completely
python reset_database.py

# Check database tables
python check_tables.py
```

---

## 👤 SECTION 4: User Management Commands

### 4.1 Create Users
```bash
# Create superuser (super_admin)
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: ********

# Create superuser non-interactively
python manage.py createsuperuser --username=admin --email=admin@example.com --no-input
```

### 4.2 Django Shell Commands for User Creation
```bash
# Open Django shell
python manage.py shell

# In shell - Create tenant admin
from core.models import UserAccount, Company
company = Company.objects.create(name='Test College', subdomain='testcollege')
admin = UserAccount.objects.create_user(
    username='admin',
    email='admin@testcollege.com',
    password='password123',
    role='tenant_admin',
    company=company
)

# Create teacher
teacher = UserAccount.objects.create_user(
    username='teacher',
    email='teacher@testcollege.com',
    password='password123',
    role='teacher',
    company=company
)

# Create student
student = UserAccount.objects.create_user(
    username='student',
    email='student@testcollege.com',
    password='password123',
    role='student',
    company=company
)

# Exit shell
exit()
```

---

## 🏃 SECTION 5: Django Development Server Commands

### 5.1 Run Development Server
```bash
# Start server on default port (8000)
python manage.py runserver

# Start on specific port
python manage.py runserver 8080

# Start on specific IP and port
python manage.py runserver 0.0.0.0:8000

# Start with settings override
python manage.py runserver --settings=saas_platform.settings_dev
```

### 5.2 Check Project Health
```bash
# Check for common issues
python manage.py check

# Check deployment readiness
python manage.py check --deploy

# Check database configuration
python manage.py check --database default

# Check specific app
python manage.py check core
```

---

## 📂 SECTION 6: Static Files Commands

### 6.1 Collect Static Files
```bash
# Collect all static files to STATIC_ROOT
python manage.py collectstatic

# Collect without asking for confirmation
python manage.py collectstatic --noinput

# Clear existing static files before collecting
python manage.py collectstatic --clear

# Dry run (show what would be collected)
python manage.py collectstatic --dry-run
```

---

## 🧪 SECTION 7: Testing Commands

### 7.1 Run Django Tests
```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test core
python manage.py test teacher
python manage.py test student

# Run specific test class
python manage.py test core.tests.TestUserAccount

# Run specific test method
python manage.py test core.tests.TestUserAccount.test_create_user

# Run with verbose output
python manage.py test --verbosity=2

# Keep test database
python manage.py test --keepdb
```

### 7.2 Pytest Commands
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=.

# Generate HTML coverage report
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py

# Run specific test function
pytest tests/unit/test_models.py::test_user_creation

# Run tests matching pattern
pytest -k "test_rbac"

# Run tests with verbose output
pytest -v

# Run tests and stop on first failure
pytest -x

# Run last failed tests only
pytest --lf

# Show print statements
pytest -s

# Run tests in parallel (with pytest-xdist)
pytest -n 4

# Generate coverage report
pytest --cov=core --cov=teacher --cov-report=term-missing
```

---

## 🐳 SECTION 8: Docker Commands

### 8.1 Build Docker Images
```bash
# Build image from Dockerfile
docker build -t saas-platform:latest .

# Build with specific tag
docker build -t saas-platform:v1.0 .

# Build without cache
docker build --no-cache -t saas-platform:latest .
```

### 8.2 Docker Compose Commands
```bash
# Start all services (detached mode)
docker-compose up -d

# Start specific service
docker-compose up web

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View logs for specific service
docker-compose logs -f web

# Restart services
docker-compose restart

# Rebuild images
docker-compose build

# Rebuild and start
docker-compose up -d --build

# Run command in service
docker-compose exec web python manage.py migrate

# Run Django shell in container
docker-compose exec web python manage.py shell

# Access container shell
docker-compose exec web bash

# View running services
docker-compose ps

# Scale services
docker-compose up -d --scale celery_worker=3
```

### 8.3 One-Command Deployment
```bash
# Run deployment script
bash docker/deploy.sh

# Make script executable first (if needed)
chmod +x docker/deploy.sh
```

---

## 🔄 SECTION 9: Celery Commands

### 9.1 Start Celery Worker
```bash
# Start worker
celery -A saas_platform worker -l info

# Start worker on Windows
celery -A saas_platform worker -l info --pool=solo

# Start worker with specific queue
celery -A saas_platform worker -Q high_priority -l info

# Start multiple workers
celery -A saas_platform worker -l info --concurrency=4
```

### 9.2 Start Celery Beat (Scheduler)
```bash
# Start beat scheduler
celery -A saas_platform beat -l info

# Start with custom schedule file
celery -A saas_platform beat -l info -s /path/to/schedule
```

### 9.3 Celery Monitoring
```bash
# Start Flower (web-based monitoring)
celery -A saas_platform flower

# Access Flower at http://localhost:5555

# View active tasks
celery -A saas_platform inspect active

# View scheduled tasks
celery -A saas_platform inspect scheduled

# View registered tasks
celery -A saas_platform inspect registered

# Purge all tasks
celery -A saas_platform purge
```

---

## 🔍 SECTION 10: Debugging & Shell Commands

### 10.1 Django Shell
```bash
# Open Django shell
python manage.py shell

# Open IPython shell (if installed)
python manage.py shell -i ipython

# Run Python script in Django context
python manage.py shell < script.py
```

### 10.2 Common Shell Operations
```python
# In Django shell:

# Import models
from core.models import Company, UserAccount
from teacher.models import Assignment

# Query objects
UserAccount.objects.all()
UserAccount.objects.filter(role='teacher')
UserAccount.objects.get(id=1)

# Create objects
user = UserAccount.objects.create(username='test', email='test@example.com')

# Update objects
user.first_name = 'John'
user.save()

# Delete objects
user.delete()

# Complex queries
teachers = UserAccount.objects.filter(role='teacher', company__name='Test College')

# Aggregations
from django.db.models import Count, Avg
stats = Assignment.objects.aggregate(total=Count('id'), avg_grade=Avg('grade__score'))

# Clear cache
from django.core.cache import cache
cache.clear()
```

### 10.3 Database Shell
```bash
# Open database shell
python manage.py dbshell

# Execute SQL directly
python manage.py dbshell << EOF
SELECT * FROM core_useraccount LIMIT 10;
EOF
```

---

## 📊 SECTION 11: Database Query Commands

### 11.1 Check Models and Tables
```bash
# Show all models
python manage.py inspectdb

# Generate model code from existing database
python manage.py inspectdb > models.py

# Show SQL for model creation
python manage.py sqlmigrate core 0001
```

### 11.2 Data Import/Export
```bash
# Export data to JSON
python manage.py dumpdata core.UserAccount --indent 2 > users.json

# Import data from JSON
python manage.py loaddata users.json

# Export to CSV (custom command)
python manage.py export_to_csv core.UserAccount
```

---

## 🔐 SECTION 12: Security & Authentication Commands

### 12.1 Change User Password
```bash
# Change password for user
python manage.py changepassword username

# In shell:
python manage.py shell
from core.models import UserAccount
user = UserAccount.objects.get(username='admin')
user.set_password('new_password')
user.save()
```

### 12.2 Create Authentication Token
```bash
# If using Django REST Framework tokens
python manage.py drf_create_token username
```

---

## 🧹 SECTION 13: Cleanup & Maintenance Commands

### 13.1 Clear Sessions
```bash
# Clear expired sessions
python manage.py clearsessions

# Clear all sessions
python manage.py flush_sessions
```

### 13.2 Clear Cache
```bash
# In Django shell
python manage.py shell
from django.core.cache import cache
cache.clear()
```

### 13.3 Remove Migration Files
```bash
# Windows
Remove-Item -Recurse -Force */migrations/*.py

# Linux/Mac
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
```

---

## 📦 SECTION 14: Dependency Management Commands

### 14.1 Pip Commands
```bash
# Install from requirements.txt
pip install -r requirements.txt

# Update requirements.txt
pip freeze > requirements.txt

# Update specific package
pip install --upgrade django

# Uninstall package
pip uninstall package_name

# Show installed packages
pip list

# Show outdated packages
pip list --outdated

# Show package details
pip show django
```

---

## 🌐 SECTION 15: Git Commands (Version Control)

### 15.1 Initialize Repository
```bash
# Initialize git
git init

# Add remote
git remote add origin https://github.com/SANJAYBG307/Eng_Saas_Platform_Project.git

# Check remote
git remote -v
```

### 15.2 Daily Git Workflow
```bash
# Check status
git status

# Stage all files
git add .

# Stage specific file
git add filename.py

# Commit changes
git commit -m "Add teacher assignment feature"

# Push to remote
git push origin master

# Pull latest changes
git pull origin master

# Create new branch
git checkout -b feature/new-feature

# Switch branch
git checkout master

# Merge branch
git merge feature/new-feature

# View commit history
git log

# View changes
git diff
```

---

## 🔧 SECTION 16: Configuration Commands

### 16.1 Environment Variables
```bash
# Copy example env file
cp .env.example .env

# Windows
copy .env.example .env

# Edit environment variables
nano .env  # Linux/Mac
notepad .env  # Windows
```

### 16.2 Django Settings
```bash
# Run with specific settings file
python manage.py runserver --settings=saas_platform.settings_dev

# Set environment variable for settings
# Windows
set DJANGO_SETTINGS_MODULE=saas_platform.settings_prod

# Linux/Mac
export DJANGO_SETTINGS_MODULE=saas_platform.settings_prod
```

---

## 📋 SECTION 17: Quick Reference - Most Used Commands

### Development
```bash
python manage.py runserver                    # Start dev server
python manage.py makemigrations              # Create migrations
python manage.py migrate                     # Apply migrations
python manage.py createsuperuser             # Create admin user
python manage.py shell                       # Django shell
```

### Testing
```bash
pytest                                       # Run all tests
pytest --cov=.                              # Run with coverage
pytest -k "test_name"                       # Run specific test
python manage.py test                       # Django test runner
```

### Docker
```bash
docker-compose up -d                        # Start all services
docker-compose down                         # Stop all services
docker-compose logs -f                      # View logs
docker-compose exec web bash               # Access container
```

### Database
```bash
python manage.py dbshell                    # Database shell
python manage.py dumpdata > backup.json    # Backup data
python manage.py loaddata backup.json      # Restore data
```

### Static Files
```bash
python manage.py collectstatic --noinput   # Collect static files
```

### Celery
```bash
celery -A saas_platform worker -l info     # Start worker
celery -A saas_platform beat -l info       # Start scheduler
celery -A saas_platform flower             # Start monitoring
```

---

## 🚀 SECTION 18: Production Deployment Commands

### 18.1 Prepare for Production
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check deployment readiness
python manage.py check --deploy

# Migrate database
python manage.py migrate --noinput

# Create superuser (non-interactive)
python manage.py createsuperuser --username=admin --email=admin@example.com --noinput
```

### 18.2 Start Production Server
```bash
# Using Gunicorn
gunicorn saas_platform.wsgi:application --bind 0.0.0.0:8000 --workers 4

# With specific settings
gunicorn saas_platform.wsgi:application --bind 0.0.0.0:8000 --workers 4 --env DJANGO_SETTINGS_MODULE=saas_platform.settings_prod
```

### 18.3 Docker Production Deployment
```bash
# Build production image
docker build -t saas-platform:prod -f Dockerfile.prod .

# Run with docker-compose
docker-compose -f docker-compose.yml up -d

# View production logs
docker-compose -f docker-compose.yml logs -f
```

---

## 📝 SECTION 19: Custom Management Commands

If you create custom commands, they would be run like:

```bash
# Example custom commands
python manage.py send_daily_reports          # Send reports to admins
python manage.py cleanup_old_data           # Remove old data
python manage.py import_students students.csv # Import from CSV
python manage.py generate_invoices          # Generate monthly invoices
```

---

## 🎯 Command Execution Order (From Start to Finish)

```bash
# 1. Setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 2. Create database
mysql -u root -p < create_database.sql

# 3. Create apps
python manage.py startapp app_name

# 4. Make migrations
python manage.py makemigrations
python manage.py migrate

# 5. Create superuser
python manage.py createsuperuser

# 6. Collect static files
python manage.py collectstatic

# 7. Run tests
pytest --cov=.

# 8. Start development server
python manage.py runserver

# 9. (Production) Deploy with Docker
bash docker/deploy.sh
```

---

**Total Commands**: 100+ commands documented  
**Categories**: 19 sections  
**Use Case**: Complete reference from development to production
