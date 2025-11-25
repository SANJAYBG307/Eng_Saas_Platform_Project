"""
Management Command to Initialize Roles
Creates all required roles in the system
"""

from django.core.management.base import BaseCommand
from core.models import Role


class Command(BaseCommand):
    help = 'Initialize all system roles'
    
    def handle(self, *args, **options):
        self.stdout.write('Initializing roles...')
        
        roles_data = [
            {
                'name': 'super_admin',
                'display_name': 'Super Administrator',
                'description': 'Full system access - can manage all tenants and system configuration',
                'scope_level': 1,
                'can_manage_tenants': True,
                'can_manage_users': True,
                'can_manage_departments': True,
                'can_manage_subjects': True,
                'can_manage_attendance': True,
                'can_manage_assessments': True,
                'can_view_reports': True,
                'can_manage_billing': True,
            },
            {
                'name': 'tenant_admin',
                'display_name': 'College Administrator',
                'description': 'Full access within their college/tenant',
                'scope_level': 2,
                'can_manage_tenants': False,
                'can_manage_users': True,
                'can_manage_departments': True,
                'can_manage_subjects': True,
                'can_manage_attendance': True,
                'can_manage_assessments': True,
                'can_view_reports': True,
                'can_manage_billing': True,
            },
            {
                'name': 'department_admin',
                'display_name': 'Department Administrator (HOD)',
                'description': 'Manage department, teachers, and students within their department',
                'scope_level': 3,
                'can_manage_tenants': False,
                'can_manage_users': True,
                'can_manage_departments': False,
                'can_manage_subjects': True,
                'can_manage_attendance': True,
                'can_manage_assessments': True,
                'can_view_reports': True,
                'can_manage_billing': False,
            },
            {
                'name': 'teacher',
                'display_name': 'Teacher',
                'description': 'Manage assigned classes, attendance, and assessments',
                'scope_level': 4,
                'can_manage_tenants': False,
                'can_manage_users': False,
                'can_manage_departments': False,
                'can_manage_subjects': False,
                'can_manage_attendance': True,
                'can_manage_assessments': True,
                'can_view_reports': True,
                'can_manage_billing': False,
            },
            {
                'name': 'student',
                'display_name': 'Student',
                'description': 'View own attendance, grades, and assignments',
                'scope_level': 5,
                'can_manage_tenants': False,
                'can_manage_users': False,
                'can_manage_departments': False,
                'can_manage_subjects': False,
                'can_manage_attendance': False,
                'can_manage_assessments': False,
                'can_view_reports': True,
                'can_manage_billing': False,
            },
            {
                'name': 'parent',
                'display_name': 'Parent/Guardian',
                'description': 'View child\'s attendance, grades, and reports',
                'scope_level': 5,
                'can_manage_tenants': False,
                'can_manage_users': False,
                'can_manage_departments': False,
                'can_manage_subjects': False,
                'can_manage_attendance': False,
                'can_manage_assessments': False,
                'can_view_reports': True,
                'can_manage_billing': False,
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for role_data in roles_data:
            role, created = Role.objects.update_or_create(
                name=role_data['name'],
                defaults=role_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created role: {role.display_name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'⟳ Updated role: {role.display_name}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nRoles initialization complete!'))
        self.stdout.write(f'Created: {created_count}, Updated: {updated_count}')
