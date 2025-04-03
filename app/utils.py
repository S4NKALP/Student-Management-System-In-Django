import random
import string
import requests
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils import timezone
import pyotp
import base64
from .models import TOTPSecret, ResetToken, Student, Staff

# OTP expiration time in seconds (5 minutes)
OTP_EXPIRY = 300


def generate_secret_key():
    """Generate a random secret key for TOTP"""
    return base64.b32encode(random.getrandbits(160).to_bytes(20, 'big')).decode('utf-8')


def generate_otp(secret_key):
    """Generate a TOTP using the secret key"""
    totp = pyotp.TOTP(secret_key, interval=OTP_EXPIRY)
    return totp.now()


def store_secret_key(identifier, secret_key):
    """Store secret key in database"""
    # Delete any existing secrets for this identifier
    TOTPSecret.objects.filter(identifier=identifier).delete()
    
    # Create new secret with expiration
    expires_at = timezone.now() + timezone.timedelta(seconds=OTP_EXPIRY)
    return TOTPSecret.objects.create(
        identifier=identifier,
        secret_key=secret_key,
        expires_at=expires_at
    )


def verify_otp(identifier, otp):
    """Verify OTP using TOTP"""
    try:
        # Get the most recent secret for this identifier
        secret = TOTPSecret.objects.filter(identifier=identifier).latest('created_at')
        
        # Check if secret is expired
        if secret.is_expired():
            return False
        
        # Verify OTP
        totp = pyotp.TOTP(secret.secret_key, interval=OTP_EXPIRY)
        return totp.verify(otp)
    except TOTPSecret.DoesNotExist:
        return False


def send_otp_sms(phone, otp):
    """Send OTP via SMS using a service"""
    try:
        # Get user details from phone number
        student = Student.objects.filter(phone=phone).first()
        staff = Staff.objects.filter(phone=phone).first()
        user = student or staff
        
        # Get user's name
        user_name = user.name if user else "User"
        
        # Calculate expiry time in minutes
        expiry_minutes = OTP_EXPIRY // 60

        # Render SMS message using template
        message = render_to_string("login/sms_templates/otp_message.txt", {
            "user_name": user_name,
            "otp": otp,
            "expiry_time": expiry_minutes
        })

        # This is a placeholder. You need to replace with actual SMS API implementation
        # Example using a generic SMS API
        # api_url = "https://api.example.com/send"
        # payload = {
        #     "apikey": settings.SMS_API_KEY,
        #     "to": phone,
        #     "message": message
        # }
        # response = requests.post(api_url, json=payload)
        # return response.status_code == 200

        print("\nSMS Message Preview:")
        print("-" * 50)
        print(message)
        print("-" * 50)
        return True
    except Exception as e:
        print(f"Error sending OTP: {str(e)}")
        return False


def send_password_reset_email(user, request, email):
    """
    Send password reset code to user's email using HTML template
    """
    try:
        # Generate a secret key for TOTP
        secret_key = generate_secret_key()
        
        # Store the secret key in database
        store_secret_key(email, secret_key)
        
        # Generate TOTP
        totp = pyotp.TOTP(secret_key, interval=OTP_EXPIRY)
        reset_code = totp.now()

        # Build email context
        context = {
            "user": user,
            "domain": request.META.get("HTTP_HOST", "localhost:8000"),
            "protocol": "https" if request.is_secure() else "http",
            "reset_code": reset_code,
        }

        # Render email content using template
        subject = render_to_string("login/email_templates/password_reset_subject.txt")
        message = render_to_string(
            "login/email_templates/password_reset_email.html", context
        )

        # Send email using console backend
        send_mail(
            subject=subject,
            message=message,
            from_email="noreply@studentmanagement.com",
            recipient_list=[email],
            html_message=message,
            fail_silently=False,
        )
        print(f"\nPassword reset code sent to {email}")
        print(f"Reset Code: {reset_code}\n")
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False


def verify_reset_code(email, code):
    """Verify password reset code using TOTP"""
    return verify_otp(email, code)


def store_reset_token(token, identifier):
    """Store reset token in database"""
    # Delete any existing tokens for this identifier
    ResetToken.objects.filter(identifier=identifier).delete()
    
    # Create new token with expiration (15 minutes)
    expires_at = timezone.now() + timezone.timedelta(minutes=15)
    return ResetToken.objects.create(
        token=token,
        identifier=identifier,
        expires_at=expires_at
    )


def verify_reset_token(token, identifier):
    """Verify reset token from database"""
    try:
        reset_token = ResetToken.objects.get(token=token)
        
        # Check if token is expired
        if reset_token.is_expired():
            return False
            
        return reset_token.identifier == identifier
    except ResetToken.DoesNotExist:
        return False


def cleanup_expired_tokens():
    """Clean up expired TOTP secrets and reset tokens"""
    TOTPSecret.objects.filter(expires_at__lt=timezone.now()).delete()
    ResetToken.objects.filter(expires_at__lt=timezone.now()).delete()

