import os
from django.http import HttpResponse, JsonResponse
from django.db import models
import firebase_admin
from firebase_admin import messaging, credentials
from student_management_system.settings import BASE_DIR


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

    def deactivate(self):
        """Deactivate this device token"""
        self.is_active = False
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


def get_firebase_js():
    """Generate Firebase JavaScript configuration"""
    firebase_config = {
        "apiKey": os.getenv("FIREBASE_API_KEY", ""),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", ""),
        "projectId": os.getenv("FIREBASE_PROJECT_ID", ""),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", ""),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", ""),
        "appId": os.getenv("FIREBASE_APP_ID", ""),
        "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID", ""),
    }

    data = """
        importScripts('https://www.gstatic.com/firebasejs/11.0.2/firebase-app-compat.js');
        importScripts('https://www.gstatic.com/firebasejs/11.0.2/firebase-messaging-compat.js');

        firebase.initializeApp({
            apiKey: "%s",
            authDomain: "%s",
            projectId: "%s",
            storageBucket: "%s",
            messagingSenderId: "%s",
            appId: "%s",
            measurementId: "%s"
        });

        const messaging = firebase.messaging();

        messaging.onBackgroundMessage(function(payload) {
            const notificationTitle = payload.notification.title;
            const notificationOptions = {
                body: payload.notification.body,
                icon: payload.notification.icon || '/static/img/logo.png'
            };

            return self.registration.showNotification(notificationTitle, notificationOptions);
        });
    """ % (
        firebase_config["apiKey"],
        firebase_config["authDomain"],
        firebase_config["projectId"],
        firebase_config["storageBucket"],
        firebase_config["messagingSenderId"],
        firebase_config["appId"],
        firebase_config["measurementId"],
    )
    return HttpResponse(data, content_type="application/javascript")


# --------------------------------------------------------------------
# Firebase Admin Initialization
# --------------------------------------------------------------------

# Initialize Firebase Admin
firebase_app = None
try:
    cert_path = os.path.join(BASE_DIR, "firebase-key.json")
    if os.path.exists(cert_path):
        cred = credentials.Certificate(cert_path)
        firebase_app = firebase_admin.initialize_app(cred)
except Exception:
    pass


# --------------------------------------------------------------------
# Push Notification Functions
# --------------------------------------------------------------------


def send_push_notification(title, message, tokens):
    """
    Send push notification using Firebase Cloud Messaging
    Returns a tuple of (success_count, failure_count, failed_tokens)
    """
    if not firebase_app or not tokens:
        return 0, len(tokens) if tokens else 0, tokens

    if not isinstance(tokens, (list, tuple)):
        tokens = list(tokens)  # Convert QuerySet to list

    success_count = 0
    failure_count = 0
    failed_tokens = []

    # Get only active devices that are not fallback tokens
    active_devices = FCMDevice.objects.filter(
        token__in=tokens,
        is_active=True,
        is_fallback=False,  # Skip fallback tokens for push notifications
    )

    # Count fallback tokens as "success" for reporting purposes
    fallback_count = FCMDevice.objects.filter(
        token__in=tokens, is_active=True, is_fallback=True
    ).count()

    success_count += fallback_count

    for device in active_devices:
        try:
            # Skip tokens that match our fallback pattern
            if device.token.startswith("fcm-token-") or device.token.startswith(
                "fallback-token-"
            ):
                device.is_fallback = True
                device.save()
                continue

            messaging.send(
                messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=message,
                    ),
                    token=str(device.token),  # Ensure token is a string
                )
            )
            success_count += 1
        except messaging.UnregisteredError:
            # Token is no longer valid, deactivate the device
            device.deactivate()
            failure_count += 1
            failed_tokens.append(device.token)
        except Exception:
            failure_count += 1
            failed_tokens.append(device.token)

    return success_count, failure_count, failed_tokens
