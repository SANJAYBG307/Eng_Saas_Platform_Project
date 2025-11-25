# Engineering SaaS Platform - Quick Start Guide

## 🎯 Overview
Multi-tenant SaaS platform for engineering colleges with role-based access control, subscription management, and comprehensive academic features.

## 📋 Prerequisites

- Python 3.11 or higher
- MySQL 8.0 or higher
- Redis 7.0 or higher (for caching)
- Git

## 🚀 Installation Steps

### 1. Clone Repository
```bash
cd "C:\ABSP\Django Projects\Eng_Saas_Platform_Project"
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create MySQL Database
```sql
CREATE DATABASE Eng_Saas_Platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'Saas_User'@'localhost' IDENTIFIED BY 'Saas@123';
GRANT ALL PRIVILEGES ON Eng_Saas_Platform.* TO 'Saas_User'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Configure Environment
Copy `.env.example` to `.env` and update if needed:
```bash
copy .env.example .env
```

### 6. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Initialize System Roles
```bash
python manage.py init_roles
```

Expected output:
```
✓ Created role: Super Administrator
✓ Created role: College Administrator
✓ Created role: Department Administrator (HOD)
✓ Created role: Teacher
✓ Created role: Student
✓ Created role: Parent/Guardian

Roles initialization complete!
Created: 6, Updated: 0
```

### 8. Create Super Admin User
```bash
python manage.py create_superadmin
```

You'll be prompted for:
- Email: admin@example.com
- Password: (your secure password)
- First Name: Admin
- Last Name: User

### 9. Create Static Files Directory
```bash
mkdir static
mkdir media
mkdir logs
```

### 10. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 11. Run Development Server
```bash
python manage.py runserver
```

Server will start at: **http://localhost:8000**

## 🔐 Default Login Credentials

After creating super admin:
- **Email:** admin@example.com (or what you entered)
- **Password:** (your password)
- **Role:** Super Administrator

## 📱 Application URLs

| App | URL | Role Required |
|-----|-----|---------------|
| Login | `/auth/login/` | Public |
| Register | `/auth/register/` | Public |
| Dashboard | `/auth/dashboard/` | All (redirects by role) |
| Profile | `/auth/profile/` | All authenticated users |
| Company Admin | `/company/` | Super Admin |
| College Admin | `/admin/` | Tenant Admin |
| Department | `/dept/` | Department Admin |
| Teacher | `/teacher/` | Teacher |
| Student | `/student/` | Student |
| Parent | `/parent/` | Parent |
| Django Admin | `/django-admin/` | Staff users |

## 🎨 System Roles

### 1. Super Administrator (super_admin)
- Full system access
- Manage all tenants
- System configuration
- Billing oversight

### 2. College Administrator (tenant_admin)
- Full access within their college
- Manage departments, users
- Subscription & billing
- Reports & analytics

### 3. Department Administrator (department_admin)
- Manage department
- Assign teachers
- View department students
- Department reports

### 4. Teacher (teacher)
- Manage assigned classes
- Take attendance
- Create assignments & assessments
- Grade students
- Communicate with students & parents

### 5. Student (student)
- View own attendance
- Submit assignments
- View grades
- Access learning resources
- View timetable

### 6. Parent/Guardian (parent)
- View child's attendance
- View child's grades
- Receive teacher communications
- Track child's progress

## 🏗️ Project Structure

```
Eng_Saas_Platform_Project/
├── saas_platform/          # Main project settings
│   ├── settings.py         # Django settings
│   ├── urls.py             # Main URL configuration
│   └── wsgi.py            # WSGI config
├── core/                   # Core app (authentication, multi-tenancy)
│   ├── models.py           # 21 models
│   ├── views.py            # Authentication views
│   ├── forms.py            # Forms
│   ├── middleware.py       # Multi-tenant & RBAC middleware
│   ├── utils.py            # Utility functions
│   ├── admin.py            # Django admin
│   └── management/         # Management commands
├── company_admin/          # Company admin app
├── tenant_subscription/    # Subscription app
├── college_management/     # College admin app
├── department_management/  # Department app
├── teacher/                # Teacher app
├── student/                # Student app
├── parent/                 # Parent app
├── templates/              # HTML templates
│   ├── base.html          # Base template
│   └── auth/              # Auth templates
├── static/                 # Static files (CSS, JS, images)
├── media/                  # User uploads
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
└── manage.py              # Django management script
```

## 🗄️ Database Schema

**Core Models:**
- Tenant (colleges/institutions)
- UserAccount (custom user model)
- Role (6 predefined roles)
- Department
- Subject
- AcademicYear
- Section (batches/classes)
- TeacherSubjectAssignment
- StudentEnrollment
- ParentStudentLink

**Academic Models:**
- Attendance
- Assignment
- AssignmentSubmission
- Assessment (exams/quizzes)
- Grade
- Timetable
- LearningResource

**Communication Models:**
- Message (internal messaging)
- Notification
- Announcement

**System Models:**
- AuditLog
- TenantDomain

## 🔧 Configuration

### Environment Variables (.env)

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=Eng_Saas_Platform
DB_USER=Saas_User
DB_PASSWORD=Saas@123
DB_HOST=localhost
DB_PORT=3306

# Redis (for caching)
REDIS_HOST=localhost
REDIS_PORT=6379

# Email (SendGrid)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Stripe
STRIPE_PUBLIC_KEY=pk_test_xxx
STRIPE_SECRET_KEY=sk_test_xxx
```

## 🧪 Testing

Run tests:
```bash
python manage.py test
```

With coverage:
```bash
pytest --cov=. --cov-report=html
```

## 📊 Admin Interface

Access Django admin at: **http://localhost:8000/django-admin/**

Features:
- Manage all models
- View audit logs
- User management
- Tenant management
- Search & filters

## 🚨 Troubleshooting

### Issue: Cannot connect to MySQL
**Solution:** Ensure MySQL is running and credentials are correct in `.env`

### Issue: ModuleNotFoundError
**Solution:** Ensure virtual environment is activated and all dependencies are installed
```bash
pip install -r requirements.txt
```

### Issue: Static files not loading
**Solution:** Run collectstatic command
```bash
python manage.py collectstatic --noinput
```

### Issue: Migration errors
**Solution:** Reset migrations (development only)
```bash
python manage.py migrate --run-syncdb
```

## 📝 Common Commands

```bash
# Create new app
python manage.py startapp app_name

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py create_superadmin

# Initialize roles
python manage.py init_roles

# Run development server
python manage.py runserver

# Open Python shell
python manage.py shell

# Run tests
python manage.py test

# Collect static files
python manage.py collectstatic
```

## 🔐 Security Notes

1. **Change SECRET_KEY** in production
2. **Set DEBUG=False** in production
3. **Use strong passwords** for database and admin users
4. **Enable HTTPS** in production
5. **Configure ALLOWED_HOSTS** properly
6. **Keep dependencies updated**
7. **Enable two-factor authentication** for admin accounts
8. **Regular backups** of database

## 🌐 Multi-Tenancy

### Tenant Identification Methods:
1. **Subdomain:** college1.saasplatform.com
2. **Custom Domain:** college.edu
3. **Session:** For super admin testing
4. **Header:** X-Tenant-ID (for API requests)

### Creating a Test Tenant:

```python
from core.models import Tenant
from django.utils.text import slugify

tenant = Tenant.objects.create(
    name="Test College",
    slug="test-college",
    subdomain="test-college",
    email="contact@testcollege.edu",
    phone="+1234567890",
    address_line1="123 Main St",
    city="New York",
    state="NY",
    country="USA",
    postal_code="10001",
    subscription_status="trial"
)
```

## 📞 Support

For issues or questions:
- Check BUILD_SUMMARY.md for detailed information
- Review code comments
- Check Django documentation
- Review project documentation (when available)

## 🎯 Next Steps

1. ✅ System is ready for development
2. 🔄 Build tenant subscription flow
3. 🔄 Build company admin interface
4. 🔄 Build college management interface
5. 🔄 Build remaining role-specific interfaces
6. 🔄 Add Stripe integration
7. 🔄 Create Docker configuration
8. 🔄 Write tests
9. 🔄 Complete documentation

## 📚 Additional Resources

- Django Documentation: https://docs.djangoproject.com/
- Bootstrap 5: https://getbootstrap.com/
- Stripe API: https://stripe.com/docs/api
- MySQL Documentation: https://dev.mysql.com/doc/

---

**Project Status:** ~25% Complete  
**Ready for:** Development & Testing  
**Last Updated:** November 25, 2025
