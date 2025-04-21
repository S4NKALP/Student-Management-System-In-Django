# Standard library imports
import base64
import random
import os
import magic

# Core Django imports
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import logging
from django.core.exceptions import ValidationError

# Third-party app imports
import pyotp

# Local app imports
from app.models import ResetToken, Staff, Student, TOTPSecret, OTPAttempt

# OTP expiration time in seconds (5 minutes)
OTP_EXPIRY = int(os.getenv('OTP_EXPIRY', 300))

logger = logging.getLogger(__name__)

class FileUploadError(Exception):
    """Custom exception for file upload errors"""
    pass

def validate_file_type(file, allowed_types):
    """
    Validate file type using python-magic
    
    Args:
        file: Uploaded file object
        allowed_types: List of allowed MIME types
        
    Returns:
        bool: True if file type is allowed, False otherwise
    """
    try:
        # Read first 2048 bytes to determine file type
        file.seek(0)
        file_content = file.read(2048)
        file.seek(0)  # Reset file pointer
        
        mime_type = magic.from_buffer(file_content, mime=True)
        return mime_type in allowed_types
    except Exception as e:
        logger.error(f"Error validating file type: {e}")
        return False

def validate_file_size(file, max_size_bytes):
    """
    Validate file size
    
    Args:
        file: Uploaded file object
        max_size_bytes: Maximum allowed file size in bytes
        
    Returns:
        bool: True if file size is within limit, False otherwise
    """
    try:
        return file.size <= max_size_bytes
    except Exception as e:
        logger.error(f"Error validating file size: {e}")
        return False

def sanitize_filename(filename):
    """
    Sanitize filename to prevent directory traversal and other security issues
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove any path components
    filename = os.path.basename(filename)
    # Replace any non-alphanumeric characters (except ._-) with underscore
    filename = ''.join(c if c.isalnum() or c in '._-' else '_' for c in filename)
    return filename

def handle_file_upload(file, upload_path, allowed_types, max_size_bytes):
    """
    Handle file upload with security checks
    
    Args:
        file: Uploaded file object
        upload_path: Path where file should be uploaded
        allowed_types: List of allowed MIME types
        max_size_bytes: Maximum allowed file size in bytes
        
    Returns:
        str: Path to uploaded file if successful
        
    Raises:
        FileUploadError: If file validation fails
    """
    try:
        # Validate file type
        if not validate_file_type(file, allowed_types):
            raise FileUploadError(f"Invalid file type. Allowed types: {', '.join(allowed_types)}")
            
        # Validate file size
        if not validate_file_size(file, max_size_bytes):
            raise FileUploadError(f"File size too large. Maximum size: {max_size_bytes/1024/1024}MB")
            
        # Sanitize filename
        filename = sanitize_filename(file.name)
        
        # Create full upload path
        full_path = os.path.join(upload_path, filename)
        
        # Save file
        path = default_storage.save(full_path, ContentFile(file.read()))
        
        return path
        
    except Exception as e:
        logger.error(f"Error handling file upload: {e}")
        raise FileUploadError(str(e))

def cleanup_failed_upload(file_path):
    """
    Clean up failed file upload
    
    Args:
        file_path: Path to the file that needs to be cleaned up
    """
    try:
        if default_storage.exists(file_path):
            default_storage.delete(file_path)
    except Exception as e:
        logger.error(f"Error cleaning up failed upload: {e}")

# Constants for file uploads
ALLOWED_DOCUMENT_TYPES = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/plain',
    'application/rtf'
]

ALLOWED_IMAGE_TYPES = [
    'image/jpeg',
    'image/png',
    'image/gif'
]

MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10MB
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

# --------------------------------------------------------------------
# OTP and Secret Key Generation
# --------------------------------------------------------------------


def generate_secret_key():
    """Generate a random secret key for TOTP"""
    return base64.b32encode(random.getrandbits(160).to_bytes(20, "big")).decode("utf-8")


def generate_otp(secret_key):
    """Generate a TOTP using the secret key"""
    totp = pyotp.TOTP(secret_key, interval=OTP_EXPIRY)
    return totp.now()


# --------------------------------------------------------------------
# OTP Storage and Verification
# --------------------------------------------------------------------


def store_secret_key(identifier, secret_key):
    """Store secret key in database"""
    # Delete any existing secrets for this identifier
    TOTPSecret.objects.filter(identifier=identifier).delete()

    # Create new secret with expiration
    expires_at = timezone.now() + timezone.timedelta(seconds=OTP_EXPIRY)
    return TOTPSecret.objects.create(
        identifier=identifier, secret_key=secret_key, expires_at=expires_at
    )


def verify_otp(identifier, otp):
    """Verify OTP using TOTP with improved security"""
    try:
        # Check if identifier is locked out
        attempt, _ = OTPAttempt.objects.get_or_create(identifier=identifier)
        if attempt.is_locked_out():
            logger.warning(f"Identifier {identifier} is locked out from OTP attempts")
            return False

        # Get the most recent secret for this identifier
        secret = TOTPSecret.objects.filter(identifier=identifier).latest("created_at")

        # Check if secret is expired
        if secret.is_expired():
            attempt.increment_attempts()
            return False

        # Verify OTP
        totp = pyotp.TOTP(secret.secret_key, interval=OTP_EXPIRY)
        is_valid = totp.verify(otp)
        
        if is_valid:
            # Reset attempts on successful verification
            attempt.reset_attempts()
            # Clean up expired tokens
            cleanup_expired_tokens()
        else:
            # Increment failed attempts
            attempt.increment_attempts()
            
        return is_valid
    except TOTPSecret.DoesNotExist:
        return False


# --------------------------------------------------------------------
# SMS Communication
# --------------------------------------------------------------------


def validate_phone_number(phone):
    """Validate phone number format with improved validation"""
    if not phone or not isinstance(phone, str):
        raise ValidationError("Phone number must be a string")
    
    # Remove any non-digit characters
    phone = ''.join(filter(str.isdigit, phone))
    
    # Validate length and format
    if len(phone) < 10 or len(phone) > 15:
        raise ValidationError("Phone number must be between 10 and 15 digits")
    
    # Validate country code if present
    if phone.startswith('0'):
        raise ValidationError("Phone number cannot start with 0")
    
    # Additional validation for specific countries if needed
    if phone.startswith('91'):  # India
        if len(phone) != 12:
            raise ValidationError("Indian phone numbers must be 12 digits including country code")
    
    return True

def send_otp_sms(phone, otp):
    """Send OTP via SMS with improved error handling"""
    try:
        # Validate phone number first
        validate_phone_number(phone)
        
        # Check if phone is locked out
        attempt, _ = OTPAttempt.objects.get_or_create(identifier=phone)
        if attempt.is_locked_out():
            logger.warning(f"Phone {phone} is locked out from OTP attempts")
            return False
        
        # Get user name if available
        user = None
        student = Student.objects.filter(phone=phone).first()
        staff = Staff.objects.filter(phone=phone).first()
        if student:
            user = student
        elif staff:
            user = staff
            
        # Prepare context for template
        context = {
            'user_name': user.name if user else 'User',
            'otp': otp,
            'expiry_time': OTP_EXPIRY // 60  # Convert seconds to minutes
        }
        
        # Render message from template
        message = render_to_string('login/sms_templates/otp_message.txt', context)
        
        # Your SMS service implementation here
        # Example using Twilio:
        # from twilio.rest import Client
        # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        # message = client.messages.create(
        #     body=message,
        #     from_=settings.TWILIO_PHONE_NUMBER,
        #     to=f"+{phone}"
        # )
        
        # For now, just log the OTP
        logger.info(f"OTP message would be sent to {phone}: {message}")
        return True
        
    except ValidationError as e:
        logger.error(f"Invalid phone number format: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Failed to send SMS to {phone}: {str(e)}")
        return False


# --------------------------------------------------------------------
# Email Communication
# --------------------------------------------------------------------


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


# --------------------------------------------------------------------
# Token Management
# --------------------------------------------------------------------


def store_reset_token(token, identifier):
    """Store reset token with improved session management"""
    try:
        # Clean up any existing tokens for this identifier
        ResetToken.objects.filter(identifier=identifier).delete()
        
        # Create new token with expiration
        expires_at = timezone.now() + timezone.timedelta(minutes=15)  # 15 minutes expiration
        return ResetToken.objects.create(
            token=token,
            identifier=identifier,
            expires_at=expires_at
        )
    except Exception as e:
        logger.error(f"Error storing reset token: {str(e)}")
        return None


def verify_reset_token(token, identifier):
    """Verify reset token with improved security"""
    try:
        reset_token = ResetToken.objects.get(token=token)

        # Check if token is expired
        if reset_token.is_expired():
            return False

        # Verify identifier matches
        if reset_token.identifier != identifier:
            return False
            
        # Clean up expired tokens
        cleanup_expired_tokens()
        
        return True
    except ResetToken.DoesNotExist:
        return False


# --------------------------------------------------------------------
# Cleanup Functions
# --------------------------------------------------------------------


def cleanup_expired_tokens():
    """Clean up expired OTP secrets and reset tokens"""
    try:
        # Delete expired OTP secrets
        expired_otps = TOTPSecret.objects.filter(expires_at__lt=timezone.now())
        expired_otps_count = expired_otps.count()
        expired_otps.delete()
        
        # Delete expired reset tokens
        expired_reset_tokens = ResetToken.objects.filter(expires_at__lt=timezone.now())
        expired_reset_count = expired_reset_tokens.count()
        expired_reset_tokens.delete()
        
        logger.info(f"Cleaned up {expired_otps_count} expired OTPs and {expired_reset_count} expired reset tokens")
    except Exception as e:
        logger.error(f"Error cleaning up expired tokens: {str(e)}")
