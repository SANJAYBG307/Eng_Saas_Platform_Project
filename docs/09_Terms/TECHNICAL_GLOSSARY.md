# 📖 Technical Terms Dictionary

## All Technical Words Used in the Django SaaS Platform Project

**Purpose**: This document explains every technical term used in this project in simple English.

---

## A

### API (Application Programming Interface)
**Simple**: A way for programs to talk to each other  
**Example**: Stripe API lets our app talk to Stripe to process payments  
**In Project**: We use APIs for Stripe payments, Celery tasks

### ASGI (Asynchronous Server Gateway Interface)
**Simple**: Modern way to run Django apps that supports real-time features  
**Example**: Like WSGI but can handle WebSockets  
**File**: `saas_platform/asgi.py`

### Abstract Base Class
**Simple**: A template model that other models inherit from  
**Example**: `BaseModel` has `company`, `created_at` - all models inherit these  
**In Project**: `core/models.py` - `class BaseModel(models.Model)`

### Aggregate
**Simple**: Calculating totals, averages, counts from database  
**Example**: Average grade for a class  
**Code**: `Grade.objects.aggregate(avg=Avg('score'))`

### Annotation
**Simple**: Adding calculated fields to query results  
**Example**: Add student count to each section  
**Code**: `Section.objects.annotate(student_count=Count('students'))`

### Authentication
**Simple**: Verifying who someone is (login system)  
**Example**: Username + password proves you're the real person  
**In Project**: Django's built-in auth + custom user model

### Authorization
**Simple**: Checking if someone has permission to do something  
**Example**: Only teachers can create assignments  
**In Project**: RBAC system with `@role_required` decorator

---

## B

### Backend
**Simple**: The server-side part users don't see  
**Example**: Database, business logic, API endpoints  
**In Project**: Django handles all backend

### Base Template
**Simple**: A master HTML template that other templates inherit from  
**Example**: `base.html` has navbar/footer, other pages extend it  
**File**: `templates/base.html`

### Bootstrap
**Simple**: CSS framework for making websites look good  
**Example**: Buttons, forms, cards all styled by Bootstrap  
**In Project**: Bootstrap 5 for all UI

### Broker (Message Broker)
**Simple**: System that delivers messages between programs  
**Example**: Redis acts as broker for Celery tasks  
**In Project**: Redis brokers Celery task messages

---

## C

### Cache
**Simple**: Storing data temporarily for faster access  
**Example**: Store timetable in Redis so we don't query DB every time  
**In Project**: Redis caching for sessions and frequently accessed data

### Celery
**Simple**: Tool for running tasks in the background  
**Example**: Sending 1000 emails without making users wait  
**In Project**: Email sending, report generation, bulk imports

### Celery Beat
**Simple**: Scheduler for running tasks automatically  
**Example**: Send attendance reminders every day at 9 AM  
**In Project**: Daily reminders, weekly reports, subscription checks

### Client Secret
**Simple**: Secret code that identifies a payment  
**Example**: Stripe gives us a secret to complete payment  
**In Project**: `payment_intent.client_secret` for Stripe checkout

### Containerization
**Simple**: Packaging app with everything it needs to run  
**Example**: Docker container has Python, Django, all dependencies  
**In Project**: Docker containers for web, database, Redis, Celery

### Coverage (Code Coverage)
**Simple**: Percentage of code that has tests  
**Example**: 85% coverage means 85% of code is tested  
**Tool**: `pytest --cov=.`

### CRUD
**Simple**: Create, Read, Update, Delete - basic database operations  
**Example**: Create user, Read user data, Update profile, Delete account  
**In Project**: Every model has CRUD operations

### CSRF (Cross-Site Request Forgery)
**Simple**: Security attack where someone tricks your browser into doing things  
**Protection**: Django's CSRF token prevents this  
**In Project**: All forms have `{% csrf_token %}`

---

## D

### Database Migration
**Simple**: Instructions for changing database structure  
**Example**: Adding a new column to a table  
**Command**: `python manage.py makemigrations`

### Decorator
**Simple**: Function that wraps another function to add behavior  
**Example**: `@role_required` checks role before running view  
**In Project**: `@role_required(['teacher'])` on views

### Docker
**Simple**: Tool to package and run apps in containers  
**Example**: One command deploys entire app with all dependencies  
**In Project**: `docker-compose up -d` starts everything

### Docker Compose
**Simple**: Tool to run multiple Docker containers together  
**Example**: Start web app, database, Redis all at once  
**File**: `docker-compose.yml`

### Dockerfile
**Simple**: Recipe for building a Docker image  
**Example**: Install Python, copy code, install dependencies  
**File**: `Dockerfile`

### Django
**Simple**: Python web framework for building websites  
**Example**: Like a toolkit with everything you need for web apps  
**In Project**: Django 5.0 is the foundation of everything

### Django ORM (Object-Relational Mapping)
**Simple**: Writing database queries using Python instead of SQL  
**Example**: `UserAccount.objects.filter(role='student')` instead of SQL  
**In Project**: All database operations use ORM

### DRY (Don't Repeat Yourself)
**Simple**: Write code once, reuse it everywhere  
**Example**: `BaseModel` has common fields, all models inherit it  
**In Project**: Mixins, decorators, base classes

---

## E

### Environment Variables
**Simple**: Settings stored outside code (secrets, passwords)  
**Example**: Database password stored in `.env` file  
**File**: `.env`

### E2E Testing (End-to-End)
**Simple**: Testing complete user journeys  
**Example**: From clicking signup to first login  
**In Project**: Signup flow, assignment workflow tests

---

## F

### Factory (Factory Pattern)
**Simple**: Tool to create test data easily  
**Example**: `factory_boy` creates 100 fake students in one line  
**In Project**: `conftest.py` has factories for users, companies

### Faker
**Simple**: Library to generate fake but realistic data  
**Example**: Fake names, emails, addresses for testing  
**In Project**: Used in test fixtures

### Foreign Key
**Simple**: Link between two database tables  
**Example**: Student has foreign key to Section (student belongs to section)  
**In Project**: Every model has `company` foreign key

### Frontend
**Simple**: The part of website users see and interact with  
**Example**: HTML pages, buttons, forms  
**In Project**: Django templates + Bootstrap

---

## G

### Gunicorn
**Simple**: Web server that runs Django in production  
**Example**: Like `python manage.py runserver` but for production  
**Command**: `gunicorn saas_platform.wsgi:application`

---

## H

### Health Check
**Simple**: Endpoint to verify app is running  
**Example**: `/health/` returns OK if app is healthy  
**In Project**: `/health/`, `/readiness/`, `/liveness/` endpoints

### HOD (Head of Department)
**Simple**: Person who manages a department  
**Example**: Computer Science department head  
**In Project**: `department_admin` role

---

## I

### Idempotency
**Simple**: Doing same action multiple times has same result  
**Example**: Charging payment twice should only charge once  
**In Project**: Stripe payment intents are idempotent

### Index (Database Index)
**Simple**: Makes database searches faster  
**Example**: Phone book index helps find names quickly  
**In Project**: Indexes on `company`, `created_at` fields

### Integration Test
**Simple**: Testing how multiple parts work together  
**Example**: Teacher creates assignment, student sees it  
**In Project**: View tests, workflow tests

---

## J

### JWT (JSON Web Token)
**Simple**: Secure way to prove identity without passwords  
**Example**: Like a concert wristband - shows you paid  
**Use**: API authentication (not used in current project)

---

## K

### Kwargs (Keyword Arguments)
**Simple**: Named parameters passed to functions  
**Example**: `create_user(username='john', email='john@example.com')`  
**In Project**: Used in views, model methods

---

## L

### Load Balancer
**Simple**: Distributes traffic across multiple servers  
**Example**: If 1000 users visit, split between 10 servers  
**In Project**: Nginx can act as load balancer

---

## M

### Many-to-Many Relationship
**Simple**: Multiple items relate to multiple other items  
**Example**: Students take multiple subjects, subjects have multiple students  
**In Project**: Section ↔ Teachers, Student ↔ Parents

### Middleware
**Simple**: Code that runs before every request  
**Example**: Check if user is logged in  
**In Project**: `TenantMiddleware`, `RoleMiddleware`

### Migration
**Simple**: Version control for database changes  
**Example**: Adding a column creates a migration file  
**Command**: `python manage.py makemigrations`

### Model
**Simple**: Python class representing a database table  
**Example**: `UserAccount` model = `core_useraccount` table  
**In Project**: 52 models across 8 apps

### MRR (Monthly Recurring Revenue)
**Simple**: Predictable monthly income from subscriptions  
**Example**: 10 colleges × $99/month = $990 MRR  
**In Project**: Calculated from active subscriptions

### Multi-Tenancy
**Simple**: One app serves many customers, data is isolated  
**Example**: 100 colleges use same app, can't see each other's data  
**In Project**: Schema-based multi-tenancy with `company` FK

### MySQL
**Simple**: Database system that stores all data  
**Example**: Stores users, assignments, grades in tables  
**In Project**: MySQL 8.0

---

## N

### Nginx
**Simple**: Web server and reverse proxy  
**Example**: Receives requests, sends to Django, serves static files  
**In Project**: Docker container with Nginx configuration

### Namespace
**Simple**: Grouping URLs to avoid name conflicts  
**Example**: `teacher:dashboard` vs `student:dashboard`  
**In Project**: Each app has its own namespace

---

## O

### ORM (Object-Relational Mapping)
**Simple**: Use Python objects instead of SQL queries  
**Example**: `User.objects.all()` instead of `SELECT * FROM users`  
**In Project**: Django ORM for all database operations

### Onboarding
**Simple**: Process of getting new users started  
**Example**: After signup, setup departments, import users  
**In Project**: Multi-step onboarding wizard

---

## P

### Payment Intent
**Simple**: Stripe object representing a payment attempt  
**Example**: Created before payment, confirmed after  
**In Project**: `stripe.PaymentIntent.create()`

### PCI Compliance
**Simple**: Security standards for handling credit cards  
**Example**: Never store credit card numbers  
**In Project**: Stripe handles cards, we never see them

### Prefetch Related
**Simple**: Load related objects efficiently (for many-to-many)  
**Example**: Load sections with all students in one query  
**Code**: `Section.objects.prefetch_related('students')`

### Primary Key
**Simple**: Unique identifier for database row  
**Example**: User ID = 1, 2, 3...  
**In Project**: Auto-generated ID for all models

### Pytest
**Simple**: Testing framework for Python  
**Example**: Write tests, run `pytest`, see results  
**In Project**: 100+ test cases

---

## Q

### Query
**Simple**: Request to get data from database  
**Example**: Get all students in section A  
**Code**: `Student.objects.filter(section__name='A')`

### QuerySet
**Simple**: Result of a database query  
**Example**: List of all students  
**Code**: `students = Student.objects.all()` returns QuerySet

---

## R

### RBAC (Role-Based Access Control)
**Simple**: Different users have different permissions  
**Example**: Teachers can grade, students can only view  
**In Project**: 6 roles (super_admin, tenant_admin, department_admin, teacher, student, parent)

### Redis
**Simple**: Fast in-memory data store  
**Example**: Like RAM for storing temporary data  
**In Project**: Caching, Celery broker

### Reverse Proxy
**Simple**: Server that sits in front of web app  
**Example**: Nginx receives requests, forwards to Django  
**In Project**: Nginx container

### REST API
**Simple**: Way for programs to communicate using HTTP  
**Example**: Mobile app talks to server via REST API  
**In Project**: Stripe API, future mobile app API

---

## S

### SaaS (Software as a Service)
**Simple**: Software you use online, don't install  
**Example**: Gmail, Netflix, this college platform  
**In Project**: Colleges pay monthly, use via web browser

### Schema
**Simple**: Structure of database (tables, columns)  
**Example**: `users` table has `id`, `name`, `email` columns  
**In Project**: Each tenant has separate schema

### Select Related
**Simple**: Load related objects efficiently (for foreign keys)  
**Example**: Load student with their section in one query  
**Code**: `Student.objects.select_related('section')`

### Serialization
**Simple**: Converting Python objects to JSON/text  
**Example**: Send user data to frontend as JSON  
**In Project**: JSON responses, Celery task data

### Session
**Simple**: Storing user data temporarily while they're logged in  
**Example**: Remember who's logged in  
**In Project**: Django sessions stored in Redis

### Signal
**Simple**: Automatic actions triggered by events  
**Example**: Send welcome email when user signs up  
**In Project**: Post-save signals for logging, notifications

### Soft Delete
**Simple**: Mark as deleted instead of actually deleting  
**Example**: Set `is_active=False` instead of DELETE  
**In Project**: `BaseModel` has `is_active` field

### Stripe
**Simple**: Payment processing service  
**Example**: Handles credit card payments securely  
**In Project**: Subscription payments, fee payments

### Subdomain
**Simple**: Prefix before main domain  
**Example**: `college1.platform.com` - `college1` is subdomain  
**In Project**: Used to identify tenant

---

## T

### Template
**Simple**: HTML file with placeholders for dynamic data  
**Example**: `<h1>Hello {{ user.name }}</h1>` becomes "Hello John"  
**In Project**: Django templates for all pages

### Tenant
**Simple**: One customer in multi-tenant system  
**Example**: One college using the platform  
**In Project**: Represented by `Company` model

### Test Fixture
**Simple**: Test data that can be reused  
**Example**: Create 10 fake students for every test  
**In Project**: `conftest.py` has fixtures

### Transaction
**Simple**: Multiple database changes treated as one  
**Example**: Transfer money: subtract from A, add to B - both must succeed  
**In Project**: Django's atomic transactions

---

## U

### Unit Test
**Simple**: Testing one small piece of code  
**Example**: Test if function calculates percentage correctly  
**In Project**: Model method tests, utility function tests

### URL Pattern
**Simple**: Mapping URLs to views  
**Example**: `/teacher/dashboard/` → `teacher_dashboard` view  
**File**: `*/urls.py` files

---

## V

### View
**Simple**: Function that handles web requests  
**Example**: When you visit `/dashboard/`, view gets data and returns HTML  
**In Project**: 88+ view functions across apps

### Virtual Environment
**Simple**: Isolated Python environment for project  
**Example**: Project's packages don't affect other projects  
**Folder**: `venv/`

---

## W

### Webhook
**Simple**: URL that receives automatic notifications  
**Example**: Stripe sends payment updates to our webhook  
**In Project**: `/webhook/stripe/` receives payment events

### WSGI (Web Server Gateway Interface)
**Simple**: Standard way to run Python web apps  
**Example**: How Gunicorn talks to Django  
**File**: `saas_platform/wsgi.py`

---

## X

### XSS (Cross-Site Scripting)
**Simple**: Security attack using malicious scripts  
**Protection**: Django automatically escapes HTML  
**In Project**: Template escaping enabled by default

---

## Acronyms Reference

| Acronym | Full Name | Simple Meaning |
|---------|-----------|----------------|
| API | Application Programming Interface | Programs talking to each other |
| ASGI | Asynchronous Server Gateway Interface | Modern Python web server |
| CRUD | Create, Read, Update, Delete | Basic database operations |
| CSRF | Cross-Site Request Forgery | Security attack Django prevents |
| CSS | Cascading Style Sheets | Makes websites look good |
| DB | Database | Where data is stored |
| DRY | Don't Repeat Yourself | Code reusability principle |
| E2E | End-to-End | Complete workflow testing |
| FK | Foreign Key | Link between database tables |
| HOD | Head of Department | Department manager |
| HTML | HyperText Markup Language | Web page structure |
| HTTP | HyperText Transfer Protocol | How browsers talk to servers |
| ID | Identifier | Unique number for database row |
| JS | JavaScript | Programming language for browsers |
| JWT | JSON Web Token | Secure authentication token |
| MRR | Monthly Recurring Revenue | Predictable monthly income |
| ORM | Object-Relational Mapping | Python instead of SQL |
| PCI | Payment Card Industry | Credit card security standards |
| RBAC | Role-Based Access Control | Permission system |
| REST | Representational State Transfer | API design style |
| SaaS | Software as a Service | Online software you pay for |
| SQL | Structured Query Language | Database query language |
| SSL | Secure Sockets Layer | Encryption for websites |
| TLS | Transport Layer Security | Modern version of SSL |
| UI | User Interface | What users see and click |
| URL | Uniform Resource Locator | Web address |
| WSGI | Web Server Gateway Interface | Python web server standard |
| XSS | Cross-Site Scripting | Security attack |

---

## Common Django Terms

| Term | Meaning |
|------|---------|
| App | Module with specific functionality |
| Model | Database table as Python class |
| View | Function handling web requests |
| Template | HTML with dynamic data |
| Form | Input validation and rendering |
| Migration | Database change instructions |
| QuerySet | Database query results |
| Manager | Interface for database queries |
| Signal | Automatic event handler |
| Middleware | Code running on every request |
| Context | Data passed to templates |
| Serializer | Object to JSON converter |

---

## Database Terms

| Term | Meaning |
|------|---------|
| Table | Collection of similar data |
| Row | Single record in table |
| Column | Field in table |
| Primary Key | Unique row identifier |
| Foreign Key | Link to another table |
| Index | Speed up searches |
| Query | Request for data |
| Schema | Database structure |
| Constraint | Rule for data validity |
| Transaction | Group of database changes |

---

## Testing Terms

| Term | Meaning |
|------|---------|
| Test Case | Single test scenario |
| Assertion | Check if something is true |
| Fixture | Reusable test data |
| Mock | Fake object for testing |
| Coverage | Percentage of code tested |
| Integration | Testing multiple parts together |
| Unit | Testing one small piece |
| E2E | Testing complete workflows |

---

## Deployment Terms

| Term | Meaning |
|------|---------|
| Container | Packaged app with dependencies |
| Image | Template for container |
| Volume | Persistent storage for container |
| Service | Running container |
| Network | Connection between containers |
| Port | Number identifying a service |
| Environment | Dev, staging, or production |
| CI/CD | Automated testing and deployment |

---

**Total Terms Explained**: 150+ technical terms  
**Use This**: Reference when you see unfamiliar words in code or documentation  
**Remember**: Every expert was once a beginner who learned these terms!
