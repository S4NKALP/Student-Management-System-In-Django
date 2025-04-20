# Core Django imports
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import messages


import uuid

# Local app imports
from app.models import Student, Staff, Parent, Institute
from app.utils import (
    generate_otp,
    generate_secret_key,
    store_secret_key,
    verify_otp,
    send_otp_sms,
    send_password_reset_email,
    verify_reset_code,
    store_reset_token,
    verify_reset_token
)



def reset_password_options(request):
    """View for selecting between phone and email password reset"""
    # Get institute for logo
    institute = Institute.objects.first()
    return render(request, "login/reset_options.html", {"institute": institute})

def password_reset_phone(request):
    """View for initiating password reset with phone number"""
    # Get institute for logo
    institute = Institute.objects.first()
    
    if request.method == "POST":
        phone = request.POST.get("phone")
        
        # Validate phone number
        if not phone or not phone.isdigit():
            return render(request, "login/password_reset_phone.html", {
                "error": "Please enter a valid phone number", 
                "is_email": False,
                "institute": institute
            })
        
        # Check if a user with this phone exists
        student = Student.objects.filter(phone=phone).first()
        staff = Staff.objects.filter(phone=phone).first()
        
        if not student and not staff:
            return render(request, "login/password_reset_phone.html", {
                "error": "No account found with this phone number", 
                "is_email": False,
                "institute": institute
            })
        
        # Generate secret key and store it
        secret_key = generate_secret_key()
        store_secret_key(phone, secret_key)
        
        # Generate and send OTP
        otp = generate_otp(secret_key)
        send_result = send_otp_sms(phone, otp)
        
        if send_result:
            # Redirect to OTP verification page
            return render(request, "login/password_reset_otp.html", {
                "phone": phone, 
                "is_email": False,
                "institute": institute
            })
        else:
            return render(request, "login/password_reset_phone.html", {
                "error": "Failed to send OTP. Please try again.", 
                "is_email": False,
                "institute": institute
            })
    
    return render(request, "login/password_reset_phone.html", {
        "is_email": False,
        "institute": institute
    })

def password_reset_phone_verify(request):
    """View for verifying OTP for password reset"""
    # Get institute for logo
    institute = Institute.objects.first()
    
    if request.method == "POST":
        phone = request.POST.get("phone")
        otp = request.POST.get("otp")
        
        if not phone or not otp:
            return render(request, "login/password_reset_otp.html", {
                "error": "Phone and OTP are required",
                "phone": phone,
                "is_email": False,
                "institute": institute
            })
        
        # Verify OTP
        if verify_otp(phone, otp):
            # Generate a secure token for this reset
            token = str(uuid.uuid4())
            # Store token in database
            store_reset_token(token, phone)
            
            # Redirect to set new password
            return render(request, "login/password_reset_set.html", {
                "phone": phone,
                "token": token,
                "is_email": False,
                "institute": institute
            })
        else:
            return render(request, "login/password_reset_otp.html", {
                "error": "Invalid or expired OTP",
                "phone": phone,
                "is_email": False,
                "institute": institute
            })
    
    # If GET request, redirect to phone login
    return redirect("phone_reset_password")

def resend_phone_otp(request):
    """View for resending OTP for password reset"""
    if request.method == "POST":
        phone = request.POST.get("phone")
        
        if not phone:
            return redirect("phone_reset_password")
        
        # Generate new secret key and store it
        secret_key = generate_secret_key()
        store_secret_key(phone, secret_key)
        
        # Generate and send new OTP
        otp = generate_otp(secret_key)
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
    # Get institute for logo
    institute = Institute.objects.first()
    
    if request.method == "POST":
        email = request.POST.get("email")
        
        # Validate email
        if not email:
            return render(request, "login/email_reset.html", {
                "error": "Please enter a valid email address", 
                "is_email": True,
                "institute": institute
            })
        
        # Check if a user with this email exists
        student = Student.objects.filter(email=email).first()
        staff = Staff.objects.filter(email=email).first()
        
        if not student and not staff:
            return render(request, "login/email_reset.html", {
                "error": "No account found with this email address", 
                "is_email": True,
                "institute": institute
            })
        
        # Get the user
        user = student or staff
        
        # Send password reset email
        if send_password_reset_email(user, request, email):
            # Redirect to verification page
            return render(request, "login/password_reset_otp.html", {
                "email": email, 
                "is_email": True,
                "institute": institute
            })
        else:
            return render(request, "login/email_reset.html", {
                "error": "Failed to send verification code. Please try again.", 
                "is_email": True,
                "institute": institute
            })
    
    return render(request, "login/email_reset.html", {
        "is_email": True,
        "institute": institute
    })

def password_reset_email_verify(request):
    """View for verifying reset code for email"""
    # Get institute for logo
    institute = Institute.objects.first()
    
    if request.method == "POST":
        email = request.POST.get("email")
        code = request.POST.get("otp")
        
        if not email or not code:
            return render(request, "login/password_reset_otp.html", {
                "error": "Email and verification code are required",
                "email": email,
                "is_email": True,
                "institute": institute
            })
        
        # Verify code
        if verify_reset_code(email, code):
            # Generate a secure token for this reset
            token = str(uuid.uuid4())
            # Store token in database
            store_reset_token(token, email)
            
            # Redirect to set new password
            return render(request, "login/password_reset_set.html", {
                "email": email,
                "token": token,
                "is_email": True,
                "institute": institute
            })
        else:
            return render(request, "login/password_reset_otp.html", {
                "error": "Invalid or expired code",
                "email": email,
                "is_email": True,
                "message": "Please check your email for the verification code.",
                "institute": institute
            })
    
    # For GET request, show the verification form with email pre-filled
    email = request.GET.get("email")
    return render(request, "login/password_reset_otp.html", {
        "email": email,
        "is_email": True,
        "message": "Please check your email for the verification code.",
        "institute": institute
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
    # Get institute for logo
    institute = Institute.objects.first()
    
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
                "is_email": is_email,
                "institute": institute
            })
        
        # Verify token is valid
        if not verify_reset_token(token, identifier):
            return render(request, "login/password_reset_set.html", {
                "error": "Invalid or expired reset session",
                "phone": phone,
                "email": email,
                "token": token,
                "is_email": is_email,
                "institute": institute
            })
        
        # Check passwords match
        if new_password1 != new_password2:
            return render(request, "login/password_reset_set.html", {
                "error": "Passwords do not match",
                "phone": phone,
                "email": email,
                "token": token,
                "is_email": is_email,
                "institute": institute
            })
        
        # Find the user
        if is_email:
            student = Student.objects.filter(email=email).first()
            staff = Staff.objects.filter(email=email).first()
        else:
            student = Student.objects.filter(phone=phone).first()
            staff = Staff.objects.filter(phone=phone).first()
        
        user = student or staff
        if not user:
            return render(request, "login/password_reset_set.html", {
                "error": "User not found",
                "phone": phone,
                "email": email,
                "token": token,
                "is_email": is_email,
                "institute": institute
            })
        
        # Update password
        user.password = make_password(new_password1)
        user.save()
        
        # Redirect to login with success message
        messages.success(request, "Password has been reset successfully. Please login with your new password.")
        return redirect("login")
    
    return render(request, "login/password_reset_set.html", {"is_email": False, "institute": institute})

def custom_login(request):
    """Custom login view to handle authentication"""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        # Validate phone number format if it's a phone number
        if username.isdigit():
            if len(username) != 10:
                # Get institute for logo
                institute = Institute.objects.first()
                return render(request, "login/login.html", {
                    "error": "Phone number must be 10 digits",
                    "username": username,
                    "institute": institute
                })
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.POST.get("next", "/app/dashboard/")
            return redirect(next_url)
        else:
            # Get institute for logo
            institute = Institute.objects.first()
            return render(request, "login/login.html", {
                "error": "Invalid credentials",
                "username": username,
                "institute": institute
            })
    
    # Get institute for logo
    institute = Institute.objects.first()
    return render(request, "login/login.html", {"institute": institute}) 
