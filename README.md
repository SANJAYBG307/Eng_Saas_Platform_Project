# Engineering SaaS Platform

A comprehensive multi-tenant educational management system built with Django 5.0, designed for colleges and universities to manage their academic operations efficiently.

## 🚀 Features

### Multi-Tenancy
- **Schema-based Isolation**: Each organization gets its own database schema
- **Subdomain Routing**: Access via custom subdomains (e.g., `college1.yoursaas.com`)
- **Complete Data Isolation**: Secure tenant separation

### Role-Based Access Control (RBAC)
- **6 User Roles**: Super Admin, Tenant Admin, Department Admin, Teacher, Student, Parent
- **Granular Permissions**: Role-specific access to features
- **Hierarchical Structure**: Clear authority levels

### Academic Management
- **Course Management**: Subjects, sections, academic years
- **Assignment System**: Create, submit, and grade assignments
- **Attendance Tracking**: Mark and monitor student attendance
- **Grade Management**: Record and publish exam grades
- **Timetable**: Weekly class schedules

### Communication
- **Announcements**: Broadcast messages to specific groups
- **Parent-Teacher Communication**: Direct messaging system
- **Notifications**: Email and in-app notifications

### Fee Management
- **Fee Structure**: Flexible fee types and categories
- **Payment Integration**: Stripe payment gateway
- **Payment History**: Track all transactions
- **Receipt Generation**: Automatic receipt creation

### Subscription Management
- **Multiple Plans**: Basic, Professional, Enterprise
- **Stripe Integration**: Secure payment processing
- **Trial Periods**: Free trial support
- **Billing Management**: Automated invoicing

## 🛠️ Technology Stack

### Backend
- **Framework**: Django 5.0
- **Language**: Python 3.11
- **Database**: MySQL 8.0
- **Cache**: Redis 7
- **Task Queue**: Celery with Redis broker
- **API**: Django REST Framework

### Frontend
- **Templates**: Django Templates
- **CSS Framework**: Bootstrap 5
- **JavaScript**: Vanilla JS
- **Icons**: Bootstrap Icons

### DevOps
- **Containerization**: Docker & Docker Compose
- **Web Server**: Nginx
- **App Server**: Gunicorn
- **SSL**: Let's Encrypt support

### Payments
- **Gateway**: Stripe
- **Methods**: Card, UPI, Net Banking

### Testing
- **Framework**: Pytest
- **Coverage**: pytest-cov
- **Fixtures**: pytest-django
- **Factories**: Factory Boy

## 📋 Prerequisites

- Python 3.11+
- MySQL 8.0+
- Redis 7.0+
- Docker & Docker Compose (for containerized deployment)
- Git

## 🔧 Quick Start

### Option 1: Traditional Setup

```bash
# Clone repository
git clone https://github.com/your-repo/eng-saas-platform.git
cd eng-saas-platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\Activate.ps1  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Setup database
mysql -u root -p -e "CREATE DATABASE saas_platform CHARACTER SET utf8mb4;"

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run development server
python manage.py runserver
```

### Option 2: Docker Setup

```bash
# Clone repository
git clone https://github.com/your-repo/eng-saas-platform.git
cd eng-saas-platform

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Generate SSL certificates (development)
cd docker/nginx/ssl && bash generate_cert.sh && cd ../../..

# Deploy with Docker
bash docker/deploy.sh

# Access application
# HTTP: http://localhost
# HTTPS: https://localhost
# Admin: https://localhost/django-admin/
```

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Installation Guide](docs/02_Implementation/01_setup.md)** - Detailed setup instructions
- **[Docker Guide](docs/03_Docker/01_docker_setup.md)** - Container deployment
- **[Multi-Tenancy](docs/01_Concepts/multi_tenancy.md)** - Architecture overview
- **[RBAC System](docs/01_Concepts/rbac.md)** - Role-based access control
- **[User Manuals](docs/10_User_Manuals/)** - Role-specific guides
- **[Testing Guide](tests/README.md)** - Testing documentation
- **[API Documentation](docs/11_API/)** - REST API reference

## 🏗️ Project Structure

```
eng-saas-platform/
├── core/                      # Core app (auth, multi-tenancy, base models)
├── company_admin/             # Super admin management
├── tenant_subscription/       # Subscription management
├── college_management/        # Tenant admin features
├── department_management/     # Department admin features
├── teacher/                   # Teacher portal
├── student/                   # Student portal
├── parent/                    # Parent portal
├── saas_platform/            # Project settings
├── templates/                 # HTML templates
├── static/                    # Static files
├── media/                     # User uploads
├── docker/                    # Docker configuration
├── tests/                     # Test suite
├── docs/                      # Documentation
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker image definition
├── docker-compose.yml         # Docker services
└── README.md                  # This file
```

## 🧪 Testing

Run tests with pytest:

```bash
# All tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific markers
pytest -m unit
pytest -m integration
pytest -m auth

# Specific file
pytest tests/test_core_models.py

# Verbose output
pytest -v
```

## 🔐 Security Features

- **CSRF Protection**: Django CSRF middleware
- **SQL Injection Prevention**: ORM-based queries
- **XSS Protection**: Template auto-escaping
- **Password Hashing**: PBKDF2 algorithm
- **Session Security**: Secure cookies, HTTPS-only
- **Rate Limiting**: Nginx-based rate limiting
- **Data Isolation**: Multi-tenant schema isolation
- **Input Validation**: Form and serializer validation

## 📊 Database Models

### Core (21 models)
- Company, UserAccount, Department, Subject, Section, AcademicYear, etc.

### Subscription (7 models)
- SubscriptionPlan, Subscription, Payment, Invoice, etc.

### Academic (15+ models)
- Assignment, Grade, Attendance, Exam, Timetable, etc.

### Financial (5+ models)
- FeePayment, FeeStructure, Transaction, etc.

### Communication (4+ models)
- Announcement, ParentCommunication, Notification, etc.

**Total**: 52+ models

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure strong `SECRET_KEY`
- [ ] Set up valid SSL certificates
- [ ] Configure production database
- [ ] Set up Redis for caching
- [ ] Configure email service (SMTP)
- [ ] Set up Stripe production keys
- [ ] Configure S3 for media files (optional)
- [ ] Set up monitoring (Sentry)
- [ ] Configure backups
- [ ] Set up log aggregation
- [ ] Configure firewall rules
- [ ] Enable rate limiting
- [ ] Review security settings

### Environment Variables

Key environment variables to configure:

```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com

DB_NAME=saas_platform
DB_USER=db_user
DB_PASSWORD=strong_password
DB_HOST=db
DB_PORT=3306

REDIS_HOST=redis
REDIS_PASSWORD=redis_password

STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLIC_KEY=pk_live_...

EMAIL_HOST_USER=your@email.com
EMAIL_HOST_PASSWORD=your_password
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Write tests for new features
- Update documentation
- Add docstrings to functions
- Keep commits atomic and descriptive

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Your Name** - Initial work - [YourGitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- Django Software Foundation
- Bootstrap team
- Stripe for payment processing
- All open-source contributors

## 📞 Support

- **Email**: support@yoursaas.com
- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)

## 🗺️ Roadmap

### Version 1.1 (Planned)
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] AI-powered insights
- [ ] Video conferencing integration
- [ ] Mobile notifications

### Version 2.0 (Future)
- [ ] Microservices architecture
- [ ] GraphQL API
- [ ] Real-time chat
- [ ] Advanced reporting
- [ ] LMS integration

## 📈 Statistics

- **Lines of Code**: 50,000+
- **Models**: 52+
- **Views**: 80+
- **Templates**: 80+
- **Test Coverage**: 85%+
- **User Roles**: 6
- **Apps**: 8

## 🌟 Key Highlights

✅ **Production-Ready**: Fully functional multi-tenant SaaS platform  
✅ **Scalable**: Schema-based multi-tenancy supports thousands of tenants  
✅ **Secure**: Comprehensive security measures and RBAC  
✅ **Tested**: 85%+ test coverage with pytest  
✅ **Documented**: Extensive documentation for all features  
✅ **Dockerized**: Easy deployment with Docker Compose  
✅ **Payment Ready**: Integrated Stripe payment gateway  
✅ **Mobile Responsive**: Bootstrap 5 responsive design  

---

**Built with ❤️ using Django**

**Last Updated**: November 2025  
**Version**: 1.0.0
