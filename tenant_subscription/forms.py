"""
Forms for tenant subscription app
"""
from django import forms
from django.core.validators import EmailValidator
from .models import TenantSubscription, Coupon
from core.models import Tenant, UserAccount


class TenantSignupForm(forms.Form):
    """Form for new tenant signup"""
    # Institution Details
    institution_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter institution name'
        })
    )
    subdomain = forms.SlugField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'your-college'
        }),
        help_text='Your unique subdomain: your-college.saasplatform.com'
    )
    
    # Contact Details
    email = forms.EmailField(
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'admin@institution.edu'
        })
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1234567890'
        })
    )
    
    # Address
    address_line1 = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Street address'
        })
    )
    address_line2 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apartment, suite, etc. (optional)'
        })
    )
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City'
        })
    )
    state = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'State/Province'
        })
    )
    postal_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Postal code'
        })
    )
    country = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Country'
        })
    )
    
    # Admin User Details
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )
    admin_email = forms.EmailField(
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'admin@institution.edu'
        }),
        help_text='This will be your login email'
    )
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password (min. 8 characters)'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    
    # Agreement
    agree_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='I agree to the Terms of Service and Privacy Policy'
    )
    
    def clean_subdomain(self):
        subdomain = self.cleaned_data['subdomain'].lower()
        
        # Check if subdomain already exists
        if Tenant.objects.filter(subdomain=subdomain).exists():
            raise forms.ValidationError('This subdomain is already taken. Please choose another.')
        
        # Reserved subdomains
        reserved = ['www', 'admin', 'api', 'app', 'mail', 'ftp', 'localhost', 'test', 'staging']
        if subdomain in reserved:
            raise forms.ValidationError('This subdomain is reserved. Please choose another.')
        
        return subdomain
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')
        
        return cleaned_data


class CouponForm(forms.Form):
    """Form for applying coupon codes"""
    coupon_code = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter coupon code'
        })
    )
    
    def clean_coupon_code(self):
        code = self.cleaned_data['coupon_code'].upper()
        
        try:
            coupon = Coupon.objects.get(code=code)
            if not coupon.is_valid():
                raise forms.ValidationError('This coupon is not valid or has expired.')
            return coupon
        except Coupon.DoesNotExist:
            raise forms.ValidationError('Invalid coupon code.')


class CancelSubscriptionForm(forms.Form):
    """Form for canceling subscription"""
    CANCELLATION_REASONS = [
        ('too_expensive', 'Too expensive'),
        ('missing_features', 'Missing features I need'),
        ('switching_platform', 'Switching to another platform'),
        ('not_using', 'Not using it enough'),
        ('technical_issues', 'Technical issues'),
        ('other', 'Other'),
    ]
    
    reason = forms.ChoiceField(
        choices=CANCELLATION_REASONS,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Why are you canceling?'
    )
    feedback = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Tell us more about your decision (optional)'
        }),
        label='Additional feedback'
    )
    cancel_immediately = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Cancel immediately (otherwise cancels at period end)',
        initial=False
    )


class ContactSalesForm(forms.Form):
    """Form for contacting sales team"""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your full name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1 (555) 000-0000'
        })
    )
    institution_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Institution name'
        })
    )
    number_of_students = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 500'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Tell us about your requirements...'
        }),
        label='Your message'
    )


class ImportUsersForm(forms.Form):
    """Form for importing users from CSV"""
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        }),
        help_text='Upload CSV file with user data'
    )
    user_type = forms.ChoiceField(
        choices=[
            ('teacher', 'Teachers'),
            ('student', 'Students'),
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='User type'
    )
    send_welcome_email = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Send welcome email to all imported users'
    )
    
    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            raise forms.ValidationError('Please upload a CSV file.')
        
        # Check file size (max 5MB)
        if csv_file.size > 5 * 1024 * 1024:
            raise forms.ValidationError('File size must be under 5MB.')
        
        return csv_file
