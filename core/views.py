"""
Core App Views - Authentication, Profile, and Dashboard
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, FormView
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponseForbidden
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
import pyotp
import qrcode
import io
import base64

from .models import UserAccount, Role, Tenant
from .forms import (
    LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm,
    ProfileForm, ChangePasswordForm
)
from .utils import send_email_notification, create_audit_log


class LoginView(FormView):
    """User login view"""
    template_name = 'auth/login.html'
    form_class = LoginForm
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('auth:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        remember_me = form.cleaned_data.get('remember_me', False)
        
        user = authenticate(self.request, email=email, password=password)
        
        if user is not None:
            if not user.is_active:
                messages.error(self.request, 'Your account is inactive.')
                return self.form_invalid(form)
            
            if user.two_factor_enabled:
                self.request.session['2fa_user_id'] = str(user.id)
                return redirect('auth:verify_2fa')
            
            login(self.request, user)
            
            if not remember_me:
                self.request.session.set_expiry(0)
            
            create_audit_log(
                user=user, action='login', resource_type='authentication',
                description='User logged in', tenant=user.tenant, request=self.request
            )
            
            messages.success(self.request, f'Welcome back, {user.get_full_name()}!')
            
            next_url = self.request.GET.get('next')
            return redirect(next_url) if next_url else redirect('auth:dashboard')
        else:
            messages.error(self.request, 'Invalid email or password.')
            return self.form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Login'
        return context


@login_required
def logout_view(request):
    """User logout"""
    user = request.user
    create_audit_log(
        user=user, action='logout', resource_type='authentication',
        description='User logged out', tenant=user.tenant if hasattr(user, 'tenant') else None,
        request=request
    )
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('auth:login')


class RegisterView(FormView):
    """User registration view"""
    template_name = 'auth/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('subscription:onboarding')
    
    def form_valid(self, form):
        try:
            with transaction.atomic():
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                user.email_verified = False
                user.save()
                
                self._send_verification_email(user)
                login(self.request, user)
                
                messages.success(self.request, 'Account created! Please verify your email.')
                return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f'Error creating account: {str(e)}')
            return self.form_invalid(form)
    
    def _send_verification_email(self, user):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verification_url = self.request.build_absolute_uri(
            reverse('auth:verify_email', kwargs={'uidb64': uid, 'token': token})
        )
        send_email_notification(
            subject='Verify Your Email', recipient_list=[user.email],
            template_name='email_verification',
            context={'user': user, 'verification_url': verification_url}
        )


class ForgotPasswordView(FormView):
    """Forgot password view"""
    template_name = 'auth/forgot_password.html'
    form_class = ForgotPasswordForm
    success_url = reverse_lazy('auth:login')
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            user = UserAccount.objects.get(email=email, is_active=True)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = self.request.build_absolute_uri(
                reverse('auth:reset_password', kwargs={'uidb64': uid, 'token': token})
            )
            send_email_notification(
                subject='Reset Your Password', recipient_list=[user.email],
                template_name='password_reset',
                context={'user': user, 'reset_url': reset_url}
            )
        except UserAccount.DoesNotExist:
            pass
        
        messages.success(self.request, 'Password reset instructions sent to your email.')
        return super().form_valid(form)


class ResetPasswordView(FormView):
    """Reset password view"""
    template_name = 'auth/reset_password.html'
    form_class = ResetPasswordForm
    success_url = reverse_lazy('auth:login')
    
    def dispatch(self, request, *args, **kwargs):
        self.user = self._get_user()
        if not self.user:
            messages.error(request, 'Invalid or expired reset link.')
            return redirect('auth:forgot_password')
        return super().dispatch(request, *args, **kwargs)
    
    def _get_user(self):
        try:
            uid = force_str(urlsafe_base64_decode(self.kwargs['uidb64']))
            user = UserAccount.objects.get(pk=uid, is_active=True)
            if default_token_generator.check_token(user, self.kwargs['token']):
                return user
        except (TypeError, ValueError, OverflowError, UserAccount.DoesNotExist):
            pass
        return None
    
    def form_valid(self, form):
        self.user.set_password(form.cleaned_data['password'])
        self.user.save()
        create_audit_log(
            user=self.user, action='password_reset', resource_type='authentication',
            description='Password reset successful', tenant=self.user.tenant, request=self.request
        )
        messages.success(self.request, 'Password reset successfully. You can now login.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.user
        return context


def verify_email(request, uidb64, token):
    """Verify email address"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UserAccount.objects.get(pk=uid)
        if default_token_generator.check_token(user, token):
            user.email_verified = True
            user.save()
            messages.success(request, 'Email verified successfully!')
            return redirect('auth:login')
        else:
            messages.error(request, 'Invalid or expired verification link.')
    except (TypeError, ValueError, OverflowError, UserAccount.DoesNotExist):
        messages.error(request, 'Invalid verification link.')
    return redirect('auth:login')


@login_required
def resend_verification(request):
    """Resend email verification"""
    if request.user.email_verified:
        messages.info(request, 'Your email is already verified.')
        return redirect('auth:profile')
    
    token = default_token_generator.make_token(request.user)
    uid = urlsafe_base64_encode(force_bytes(request.user.pk))
    verification_url = request.build_absolute_uri(
        reverse('auth:verify_email', kwargs={'uidb64': uid, 'token': token})
    )
    send_email_notification(
        subject='Verify Your Email', recipient_list=[request.user.email],
        template_name='email_verification',
        context={'user': request.user, 'verification_url': verification_url}
    )
    messages.success(request, 'Verification email sent!')
    return redirect('auth:profile')


@login_required
def setup_2fa(request):
    """Setup two-factor authentication"""
    if request.method == 'POST':
        code = request.POST.get('code')
        secret = request.session.get('2fa_secret')
        if secret:
            totp = pyotp.TOTP(secret)
            if totp.verify(code):
                request.user.two_factor_enabled = True
                request.user.two_factor_secret = secret
                request.user.save()
                del request.session['2fa_secret']
                messages.success(request, 'Two-factor authentication enabled!')
                return redirect('auth:profile')
            else:
                messages.error(request, 'Invalid code.')
        else:
            messages.error(request, 'Session expired.')
            return redirect('auth:setup_2fa')
    
    secret = pyotp.random_base32()
    request.session['2fa_secret'] = secret
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(name=request.user.email, issuer_name=settings.SITE_NAME)
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    qr_code = base64.b64encode(buffer.getvalue()).decode()
    
    return render(request, 'auth/setup_2fa.html', {
        'secret': secret, 'qr_code': qr_code, 'page_title': 'Setup 2FA'
    })


@login_required
def verify_2fa(request):
    """Verify 2FA code during login"""
    user_id = request.session.get('2fa_user_id')
    if not user_id:
        return redirect('auth:login')
    
    try:
        user = UserAccount.objects.get(id=user_id, is_active=True)
    except UserAccount.DoesNotExist:
        del request.session['2fa_user_id']
        return redirect('auth:login')
    
    if request.method == 'POST':
        code = request.POST.get('code')
        totp = pyotp.TOTP(user.two_factor_secret)
        if totp.verify(code):
            login(request, user)
            del request.session['2fa_user_id']
            create_audit_log(
                user=user, action='login_2fa', resource_type='authentication',
                description='User logged in with 2FA', tenant=user.tenant, request=request
            )
            messages.success(request, f'Welcome back, {user.get_full_name()}!')
            return redirect('auth:dashboard')
        else:
            messages.error(request, 'Invalid code.')
    
    return render(request, 'auth/verify_2fa.html', {'page_title': '2FA Verification'})


@login_required
def disable_2fa(request):
    """Disable two-factor authentication"""
    if request.method == 'POST':
        request.user.two_factor_enabled = False
        request.user.two_factor_secret = None
        request.user.save()
        messages.success(request, 'Two-factor authentication disabled.')
        return redirect('auth:profile')
    return render(request, 'auth/disable_2fa.html', {'page_title': 'Disable 2FA'})


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile view"""
    template_name = 'auth/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'My Profile'
        return context


class EditProfileView(LoginRequiredMixin, FormView):
    """Edit user profile"""
    template_name = 'auth/edit_profile.html'
    form_class = ProfileForm
    success_url = reverse_lazy('auth:profile')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Profile'
        return context


class ChangePasswordView(LoginRequiredMixin, FormView):
    """Change password view"""
    template_name = 'auth/change_password.html'
    form_class = ChangePasswordForm
    success_url = reverse_lazy('auth:profile')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        self.request.user.set_password(form.cleaned_data['new_password'])
        self.request.user.save()
        update_session_auth_hash(self.request, self.request.user)
        create_audit_log(
            user=self.request.user, action='password_change', resource_type='authentication',
            description='Password changed', tenant=self.request.user.tenant, request=self.request
        )
        messages.success(self.request, 'Password changed successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Change Password'
        return context


@login_required
def dashboard_redirect(request):
    """Redirect to appropriate dashboard based on user role"""
    user = request.user
    
    if not user.role:
        messages.error(request, 'No role assigned. Contact administrator.')
        return redirect('auth:profile')
    
    role_dashboards = {
        'super_admin': 'company:dashboard',
        'tenant_admin': 'college:dashboard',
        'department_admin': 'department:dashboard',
        'teacher': 'teacher:home',
        'student': 'student:home',
        'parent': 'parent:home',
    }
    
    dashboard = role_dashboards.get(user.role.name)
    if dashboard:
        return redirect(dashboard)
    
    messages.error(request, 'Invalid role. Contact administrator.')
    return redirect('auth:profile')
