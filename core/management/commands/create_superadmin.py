"""
Management Command to Create Super Admin User
"""

from django.core.management.base import BaseCommand
from core.models import UserAccount, Role


class Command(BaseCommand):
    help = 'Create super admin user'
    
    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Super admin email')
        parser.add_argument('--password', type=str, help='Super admin password')
        parser.add_argument('--first-name', type=str, help='First name')
        parser.add_argument('--last-name', type=str, help='Last name')
    
    def handle(self, *args, **options):
        email = options.get('email') or input('Email: ')
        password = options.get('password') or input('Password: ')
        first_name = options.get('first_name') or input('First Name: ')
        last_name = options.get('last_name') or input('Last Name: ')
        
        # Check if user already exists
        if UserAccount.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR(f'User with email {email} already exists!'))
            return
        
        # Get or create super_admin role
        super_admin_role, _ = Role.objects.get_or_create(
            name='super_admin',
            defaults={
                'display_name': 'Super Administrator',
                'description': 'Full system access',
                'scope_level': 1,
                'can_manage_tenants': True,
                'can_manage_users': True,
                'can_manage_departments': True,
                'can_manage_subjects': True,
                'can_manage_attendance': True,
                'can_manage_assessments': True,
                'can_view_reports': True,
                'can_manage_billing': True,
            }
        )
        
        # Create super admin user
        user = UserAccount.objects.create_superuser(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=super_admin_role,
            email_verified=True,
            is_staff=True,
            is_superuser=True
        )
        
        self.stdout.write(self.style.SUCCESS(f'✓ Super admin user created successfully!'))
        self.stdout.write(f'Email: {user.email}')
        self.stdout.write(f'Name: {user.get_full_name()}')
        self.stdout.write(f'Role: {user.role.display_name}')
