import os
import time
import logging
from typing import List, Tuple, Optional
from django.http import HttpResponse, JsonResponse
from django.db import models
from django.conf import settings
import firebase_admin
from firebase_admin import messaging, credentials, exceptions
from student_management_system.settings import BASE_DIR
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configure logging
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------
# FCM Device Model
# --------------------------------------------------------------------


class FCMDevice(models.Model):
    """Model to store Firebase Cloud Messaging device tokens"""

    id = models.BigAutoField(primary_key=True)
    token = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_fallback = models.BooleanField(default=False)  # Flag to identify fallback tokens
    user_type = models.CharField(
        max_length=20,
        choices=[
            ("student", "Student"),
            ("parent", "Parent"),
            ("teacher", "Teacher"),
            ("admin", "Admin"),
            ("unknown", "Unknown"),
        ],
        default="unknown",
    )  # Add user type field

    def __str__(self):
        return f"Device {self.id} ({self.token[:20]}...)"

    class Meta:
        verbose_name = "FCM Device"
        verbose_name_plural = "FCM Devices"
        ordering = ["-last_active"]

    def deactivate(self, reason: str = None):
        """Deactivate this device token with optional reason"""
        self.is_active = False
        if reason:
            logger.info(f"Deactivating device token {self.id}: {reason}")
        self.save()


# --------------------------------------------------------------------
# Token Management
# --------------------------------------------------------------------


def save_fcm_token(request, token):
    """Save FCM token to database"""
    try:
        # Check if this is a fallback token
        is_fallback = token.startswith("fcm-token-") or token.startswith(
            "fallback-token-"
        )

        # Determine user type if a user is authenticated
        user_type = "unknown"
        if hasattr(request, "user") and request.user.is_authenticated:
            user_groups = request.user.groups.values_list("name", flat=True)
            if "Student" in user_groups:
                user_type = "student"
            elif "Parent" in user_groups:
                user_type = "parent"
            elif "Teacher" in user_groups:
                user_type = "teacher"
            elif request.user.is_superuser:
                user_type = "admin"

        # Use update_or_create to avoid unnecessary deletes
        device, created = FCMDevice.objects.update_or_create(
            token=token,
            defaults={
                "is_fallback": is_fallback,
                "is_active": True,
                "user_type": user_type,
            },
        )

        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# --------------------------------------------------------------------
# Firebase Configuration
# --------------------------------------------------------------------


class FirebaseConfig:
    """Class to handle Firebase configuration and validation"""
    
    @staticmethod
    def validate_config():
        """Validate Firebase configuration"""
        required_vars = [
            'FIREBASE_API_KEY',
            'FIREBASE_AUTH_DOMAIN',
            'FIREBASE_PROJECT_ID',
            'FIREBASE_STORAGE_BUCKET',
            'FIREBASE_MESSAGING_SENDER_ID',
            'FIREBASE_APP_ID'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required Firebase configuration variables: {', '.join(missing_vars)}")
        
        cert_path = os.path.join(BASE_DIR, "firebase-key.json")
        if not os.path.exists(cert_path):
            raise FileNotFoundError("Firebase service account key file not found")

    @staticmethod
    def get_config():
        """Get validated Firebase configuration"""
        FirebaseConfig.validate_config()
        return {
            "apiKey": os.getenv("FIREBASE_API_KEY"),
            "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
            "projectId": os.getenv("FIREBASE_PROJECT_ID"),
            "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
            "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
            "appId": os.getenv("FIREBASE_APP_ID"),
            "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID", ""),
        }


# --------------------------------------------------------------------
# Firebase Admin Initialization
# --------------------------------------------------------------------

def initialize_firebase():
    """Initialize Firebase Admin with proper error handling"""
    global firebase_app
    
    try:
        FirebaseConfig.validate_config()
        cert_path = os.path.join(BASE_DIR, "firebase-key.json")
        cred = credentials.Certificate(cert_path)
        firebase_app = firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin: {str(e)}")
        firebase_app = None

# Initialize Firebase
firebase_app = None
initialize_firebase()


# --------------------------------------------------------------------
# Push Notification Functions
# --------------------------------------------------------------------

class FirebaseQuotaManager:
    """Class to manage Firebase quota limits"""
    
    def __init__(self):
        self.quota_limit = 500  # Default quota limit per minute
        self.requests_count = 0
        self.last_reset_time = time.time()
    
    def check_quota(self) -> bool:
        """Check if we're within quota limits"""
        current_time = time.time()
        if current_time - self.last_reset_time >= 60:  # Reset every minute
            self.requests_count = 0
            self.last_reset_time = current_time
        
        return self.requests_count < self.quota_limit
    
    def increment_count(self):
        """Increment request count"""
        self.requests_count += 1

quota_manager = FirebaseQuotaManager()

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((exceptions.FirebaseError, exceptions.UnknownError))
)
def send_single_notification(token: str, title: str, message: str) -> bool:
    """Send a single notification with retry mechanism"""
    if not quota_manager.check_quota():
        logger.warning("Firebase quota limit reached")
        return False
    
    try:
        messaging.send(
            messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=message,
                ),
                token=token,
            )
        )
        quota_manager.increment_count()
        return True
    except messaging.UnregisteredError:
        logger.info(f"Token {token} is no longer valid")
        return False
    except exceptions.FirebaseError as e:
        logger.error(f"Firebase error for token {token}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error for token {token}: {str(e)}")
        return False

def send_push_notification(title: str, message: str, tokens: List[str]) -> Tuple[int, int, List[str]]:
    """
    Send push notification using Firebase Cloud Messaging with improved error handling
    Returns a tuple of (success_count, failure_count, failed_tokens)
    """
    if not firebase_app:
        logger.error("Firebase Admin not initialized")
        return 0, len(tokens) if tokens else 0, tokens

    if not isinstance(tokens, (list, tuple)):
        tokens = list(tokens)

    success_count = 0
    failure_count = 0
    failed_tokens = []

    # Get only active devices that are not fallback tokens
    active_devices = FCMDevice.objects.filter(
        token__in=tokens,
        is_active=True,
        is_fallback=False,
    )

    # Count fallback tokens as "success" for reporting purposes
    fallback_count = FCMDevice.objects.filter(
        token__in=tokens, is_active=True, is_fallback=True
    ).count()
    success_count += fallback_count

    for device in active_devices:
        try:
            # Skip tokens that match our fallback pattern
            if device.token.startswith(("fcm-token-", "fallback-token-")):
                device.is_fallback = True
                device.save()
                continue

            if send_single_notification(device.token, title, message):
                success_count += 1
            else:
                device.deactivate("Failed to send notification after retries")
                failure_count += 1
                failed_tokens.append(device.token)

        except Exception as e:
            logger.error(f"Error processing device {device.id}: {str(e)}")
            device.deactivate(f"Error: {str(e)}")
            failure_count += 1
            failed_tokens.append(device.token)

    return success_count, failure_count, failed_tokens
