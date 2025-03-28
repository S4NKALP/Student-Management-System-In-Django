from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
import uuid
from .models import Student, Staff
from .utils import (
    generate_otp,
    store_otp,
    verify_otp,
    send_otp_sms,
    send_password_reset_email,
    verify_reset_code
)

def reset_password_options(request):
    """View for selecting between phone and email password reset"""
    return render(request, "login/reset_options.html")

def password_reset_phone(request):
    """View for initiating password reset with phone number"""
    if request.method == "POST":
        phone = request.POST.get("phone")
        
        # Validate phone number
        if not phone or not phone.isdigit():
            return render(request, "login/password_reset_phone.html", {"error": "Please enter a valid phone number", "is_email": False})
        
        # Check if a user with this phone exists
        student = Student.objects.filter(phone=phone).first()
        staff = Staff.objects.filter(phone=phone).first()
        
        if not student and not staff:
            return render(request, "login/password_reset_phone.html", {"error": "No account found with this phone number", "is_email": False})
        
        # Generate and store OTP
        otp = generate_otp()
        store_otp(phone, otp)
        
        # Send OTP via SMS
        send_result = send_otp_sms(phone, otp)
        
        if send_result:
            # Redirect to OTP verification page
            return render(request, "login/password_reset_otp.html", {"phone": phone, "is_email": False})
        else:
            return render(request, "login/password_reset_phone.html", {"error": "Failed to send OTP. Please try again.", "is_email": False})
    
    return render(request, "login/password_reset_phone.html", {"is_email": False})

def password_reset_phone_verify(request):
    """View for verifying OTP for password reset"""
    if request.method == "POST":
        phone = request.POST.get("phone")
        otp = request.POST.get("otp")
        
        if not phone or not otp:
            return render(request, "login/password_reset_otp.html", {
                "error": "Phone and OTP are required",
                "phone": phone,
                "is_email": False
            })
        
        # Verify OTP
        if verify_otp(phone, otp):
            # Generate a secure token for this reset
            token = str(uuid.uuid4())
            # Store token with phone in cache for 15 minutes
            cache.set(f"reset_token_{token}", phone, 60 * 15)
            
            # Redirect to set new password
            return render(request, "login/password_reset_set.html", {
                "phone": phone,
                "token": token,
                "is_email": False
            })
        else:
            return render(request, "login/password_reset_otp.html", {
                "error": "Invalid or expired OTP",
                "phone": phone,
                "is_email": False
            })
    
    # If GET request, redirect to phone login
    return redirect("phone_reset_password")

def resend_phone_otp(request):
    """View for resending OTP for password reset"""
    if request.method == "POST":
        phone = request.POST.get("phone")
        
        if not phone:
            return redirect("phone_reset_password")
        
        # Generate and store new OTP
        otp = generate_otp()
        store_otp(phone, otp)
        
        # Send OTP via SMS
        send_result = send_otp_sms(phone, otp)
        
        if send_result:
            return render(request, "login/password_reset_otp.html", {
                "phone": phone,
                "message": "OTP resent successfully",
                "is_email": False
            })
        else:
            return render(request, "login/password_reset_otp.html", {
                "phone": phone,
                "error": "Failed to resend OTP",
                "is_email": False
            })
    
    return redirect("phone_reset_password")

def password_reset_email(request):
    """View for initiating password reset with email"""
    if request.method == "POST":
        email = request.POST.get("email")
        
        # Validate email
        if not email:
            return render(request, "login/email_reset.html", {"error": "Please enter a valid email address", "is_email": True})
        
        # Check if a user with this email exists
        student = Student.objects.filter(email=email).first()
        staff = Staff.objects.filter(email=email).first()
        
        if not student and not staff:
            return render(request, "login/email_reset.html", {"error": "No account found with this email address", "is_email": True})
        
        # Get the user
        user = student or staff
        
        # Send password reset email
        if send_password_reset_email(user, request, email):
            # Redirect to verification page
            return render(request, "login/password_reset_otp.html", {"email": email, "is_email": True})
        else:
            return render(request, "login/email_reset.html", {"error": "Failed to send verification code. Please try again.", "is_email": True})
    
    return render(request, "login/email_reset.html", {"is_email": True})

def password_reset_email_verify(request):
    """View for verifying reset code for email"""
    if request.method == "POST":
        email = request.POST.get("email")
        code = request.POST.get("otp")
        
        if not email or not code:
            return render(request, "login/password_reset_otp.html", {
                "error": "Email and verification code are required",
                "email": email,
                "is_email": True
            })
        
        # Verify code
        if verify_reset_code(email, code):
            # Generate a secure token for this reset
            token = str(uuid.uuid4())
            # Store token with email in cache for 15 minutes
            cache.set(f"reset_token_{token}", email, 60 * 15)
            
            # Redirect to set new password
            return render(request, "login/password_reset_set.html", {
                "email": email,
                "token": token,
                "is_email": True
            })
        else:
            return render(request, "login/password_reset_otp.html", {
                "error": "Invalid or expired code",
                "email": email,
                "is_email": True,
                "message": "Please check your email for the verification code."
            })
    
    # For GET request, show the verification form with email pre-filled
    email = request.GET.get("email")
    return render(request, "login/password_reset_otp.html", {
        "email": email,
        "is_email": True,
        "message": "Please check your email for the verification code."
    })

def resend_email_code(request):
    """View for resending verification code for password reset"""
    if request.method == "POST":
        email = request.POST.get("email")
        
        if not email:
            return redirect("email_reset_password")
        
        # Find the user
        student = Student.objects.filter(email=email).first()
        staff = Staff.objects.filter(email=email).first()
        user = student or staff
        
        if not user:
            return render(request, "login/password_reset_otp.html", {
                "email": email,
                "is_email": True,
                "error": "User not found"
            })
        
        # Send new verification code
        if send_password_reset_email(user, request, email):
            return render(request, "login/password_reset_otp.html", {
                "email": email,
                "is_email": True,
                "message": "Verification code resent successfully"
            })
        else:
            return render(request, "login/password_reset_otp.html", {
                "email": email,
                "is_email": True,
                "error": "Failed to resend verification code"
            })
    
    return redirect("email_reset_password")

def set_new_password(request):
    """View for setting new password after verification"""
    if request.method == "POST":
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        token = request.POST.get("token")
        new_password1 = request.POST.get("new_password1")
        new_password2 = request.POST.get("new_password2")
        
        identifier = phone or email
        is_email = bool(email)
        
        # Validate inputs
        if not all([identifier, token, new_password1, new_password2]):
            return render(request, "login/password_reset_set.html", {
                "error": "All fields are required",
                "phone": phone,
                "email": email,
                "token": token,
                "is_email": is_email
            })
        
        # Verify token is valid
        stored_identifier = cache.get(f"reset_token_{token}")
        if not stored_identifier or stored_identifier != identifier:
            return render(request, "login/password_reset_set.html", {
                "error": "Invalid or expired reset session",
                "phone": phone,
                "email": email,
                "token": token,
                "is_email": is_email
            })
        
        # Check passwords match
        if new_password1 != new_password2:
            return render(request, "login/password_reset_set.html", {
                "error": "Passwords do not match",
                "phone": phone,
                "email": email,
                "token": token,
                "is_email": is_email
            })
        
        # Find the user
        if is_email:
            student = Student.objects.filter(email=email).first()
            staff = Staff.objects.filter(email=email).first()
        else:
            student = Student.objects.filter(phone=phone).first()
            staff = Staff.objects.filter(phone=phone).first()
        
        user = student or staff
        
        if user:
            # Set new password
            user.password = make_password(new_password1)
            user.save()
            
            # Invalidate reset token
            cache.delete(f"reset_token_{token}")
            
            # Show success message
            return render(request, "login/password_reset_complete.html")
        else:
            return render(request, "login/password_reset_set.html", {
                "error": "User not found",
                "phone": phone,
                "email": email,
                "token": token,
                "is_email": is_email
            })
    
    # If GET request, redirect to options page
    return redirect("reset_password_options") 