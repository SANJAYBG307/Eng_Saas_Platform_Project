# Multi-Tenancy Architecture

## Overview

The Engineering SaaS Platform implements a **multi-tenant architecture** where multiple organizations (colleges/universities) can use the same application instance while maintaining complete data isolation.

## What is Multi-Tenancy?

Multi-tenancy is a software architecture where a single instance of the application serves multiple customers (tenants). Each tenant's data is isolated and invisible to other tenants.

### Benefits
- **Cost Efficiency**: Share infrastructure costs
- **Easy Maintenance**: Update all tenants simultaneously
- **Scalability**: Add new tenants without new deployments
- **Resource Optimization**: Better resource utilization

## Implementation Approach

We use a **shared database, separate schemas** approach:

### Schema-based Isolation
- Each tenant gets its own database schema
- Public schema stores shared/tenant metadata
- Tenant schemas store tenant-specific data

```
Database: saas_platform
├── public (shared schema)
│   ├── companies
│   ├── subscriptions
│   └── plans
├── company1 (tenant schema)
│   ├── users
│   ├── departments
│   ├── students
│   └── assignments
└── company2 (tenant schema)
    ├── users
    ├── departments
    ├── students
    └── assignments
```

## Key Components

### 1. Company Model
The `Company` model represents each tenant:

```python
class Company(models.Model):
    name = models.CharField(max_length=200)
    subdomain = models.CharField(max_length=63, unique=True)
    schema_name = models.CharField(max_length=63, unique=True)
    is_active = models.BooleanField(default=True)
```

### 2. TenantMiddleware
Middleware identifies the tenant from:
- Subdomain (e.g., `company1.yoursaas.com`)
- Custom domain (e.g., `company1.com`)
- User's company association

### 3. Schema Switching
- Automatically switches to tenant's schema
- All queries execute in tenant context
- Complete data isolation guaranteed

## Tenant Identification

### Subdomain-based
```
https://company1.yoursaas.com → Company 1 schema
https://company2.yoursaas.com → Company 2 schema
```

### Custom Domain
```
https://college.edu → Company mapping → Schema
```

### User-based
```
User login → User.company → Switch to company schema
```

## Data Isolation

### Tenant-Specific Models
Models that belong to a specific tenant:
- UserAccount (with company FK)
- Department
- Student
- Teacher
- Assignments
- Grades
- Attendance

### Shared Models
Models shared across all tenants:
- Company
- SubscriptionPlan
- Payment records
- System configurations

## Security Considerations

1. **Data Isolation**: Queries automatically filtered by tenant
2. **Schema Validation**: Prevent schema name injection
3. **Access Control**: Users can only access their company data
4. **Subdomain Validation**: Validate subdomain patterns
5. **Cross-tenant Prevention**: Middleware blocks cross-tenant access

## Scalability

### Horizontal Scaling
- Add more application servers
- Load balancer distributes traffic
- All servers access same database

### Vertical Scaling
- Upgrade database resources
- Each tenant benefits from improvements
- No per-tenant configuration needed

### Future: Database Sharding
For massive scale, split tenants across multiple databases:
```
Database 1: Tenants 1-1000
Database 2: Tenants 1001-2000
...
```

## Tenant Management

### Creating a New Tenant
1. Create Company record
2. Generate unique schema name
3. Create database schema
4. Run migrations for tenant schema
5. Create initial admin user
6. Activate subscription

### Deactivating a Tenant
1. Set `is_active = False`
2. Block access to application
3. Retain data for recovery
4. Optional: Archive to cold storage

### Deleting a Tenant
1. Export data (if required)
2. Delete tenant schema
3. Remove company record
4. Cancel subscription

## Best Practices

1. **Always use TenantMiddleware**: Ensures correct schema
2. **Filter by company**: Add `company` filter for safety
3. **Test isolation**: Verify data doesn't leak
4. **Monitor schema size**: Track per-tenant resource usage
5. **Backup strategy**: Per-tenant backup capability

## Common Patterns

### Getting Current Tenant
```python
# In view
def my_view(request):
    company = request.tenant
    
# In model method
user = request.user
company = user.company
```

### Querying Tenant Data
```python
# Automatically filtered by middleware
students = Student.objects.all()

# Explicit company filter (extra safety)
students = Student.objects.filter(company=request.tenant)
```

### Creating Tenant Records
```python
# Company FK automatically set
department = Department.objects.create(
    name='Computer Science',
    company=request.tenant
)
```

## Troubleshooting

### Wrong Schema Accessed
- Check middleware is active
- Verify subdomain routing
- Confirm user has correct company

### Cross-tenant Data Visible
- Review query filters
- Check foreign key relationships
- Verify middleware execution

### Schema Not Found
- Confirm schema exists in database
- Check schema_name in Company model
- Run migrations for tenant

## Related Documentation

- [RBAC System](rbac.md)
- [Subscription Management](subscriptions.md)
- [Database Architecture](../06_Architecture/database.md)
