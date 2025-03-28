import random
import string
from django.core.cache import cache
import requests
from firebase_admin import messaging, initialize_app, get_app, credentials
import os
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

# OTP expiration time in seconds (5 minutes)
OTP_EXPIRY = 300


def generate_otp(length=6):
    """Generate a numeric OTP of specified length"""
    digits = string.digits
    return "".join(random.choice(digits) for _ in range(length))


def store_otp(phone, otp):
    """Store OTP in cache with phone as key"""
    cache_key = f"otp_{phone}"
    cache.set(cache_key, otp, OTP_EXPIRY)
    return True


def verify_otp(phone, otp):
    """Verify if the provided OTP matches the stored OTP for the phone"""
    cache_key = f"otp_{phone}"
    stored_otp = cache.get(cache_key)

    if stored_otp and stored_otp == otp:
        # Delete the OTP after successful verification
        cache.delete(cache_key)
        return True
    return False


def send_otp_sms(phone, otp):
    """Send OTP via SMS using a service like Twilio, MSG91, etc."""
    try:
        # This is a placeholder. You need to replace with actual SMS API implementation
        # Example using a generic SMS API
        # api_url = "https://api.example.com/send"
        # payload = {
        #     "apikey": settings.SMS_API_KEY,
        #     "to": phone,
        #     "message": f"Your OTP for SMS login is: {otp}. Valid for 5 minutes."
        # }
        # response = requests.post(api_url, json=payload)
        # return response.status_code == 200

        print(f"OTP for {phone}: {otp}")
        return True
    except Exception as e:
        print(f"Error sending OTP: {str(e)}")
        return False


def send_push_notification(title, message, tokens):
    """
    Send push notification using Firebase Cloud Messaging
    """
    try:
        try:
            app = get_app()
        except ValueError:
            # Initialize Firebase Admin SDK if not already initialized
            cred_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "firebase-key.json",
            )
            if not os.path.exists(cred_path):
                print(f"Firebase credentials file not found at {cred_path}")
                return

            cred = credentials.Certificate(cred_path)
            app = initialize_app(cred)

        if not tokens:
            print("No FCM tokens available to send notifications")
            return

        # Create message
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=message,
            ),
            tokens=list(tokens),
        )

        # Send message
        response = messaging.send_multicast(message)

        if response.failure_count > 0:
            failures = []
            for idx, resp in enumerate(response.responses):
                if not resp.success:
                    failures.append(
                        f"Failed to send message to token {tokens[idx]}: {resp.exception}"
                    )
            print("\n".join(failures))

    except Exception as e:
        print(f"Error sending notification: {e}")
        # Don't raise the exception to prevent save from failing
        pass


def send_password_reset_email(user, request, email):
    """
    Send password reset code to user's email using HTML template
    """
    try:
        # Generate a reset code (OTP)
        reset_code = generate_otp(length=6)

        # Store the reset code in cache with user's email as key
        cache_key = f"reset_code_{email}"
        cache.set(cache_key, reset_code, OTP_EXPIRY)  # 5 minutes expiry

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
    """
    Verify if the provided reset code matches the stored code for the email
    """
    cache_key = f"reset_code_{email}"
    stored_code = cache.get(cache_key)

    if stored_code and stored_code == code:
        # Delete the code after successful verification
        cache.delete(cache_key)
        return True
    return False

