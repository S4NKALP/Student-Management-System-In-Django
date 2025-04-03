import os
from django.http import HttpResponse, JsonResponse
from django.db import models
import firebase_admin
from firebase_admin import messaging, credentials
from student_management_system.settings import BASE_DIR


class FCMDevice(models.Model):
    """Model to store Firebase Cloud Messaging device tokens"""
    id = models.BigAutoField(primary_key=True)
    token = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Device {self.id} ({self.token[:20]}...)"

    class Meta:
        verbose_name = "FCM Device"
        verbose_name_plural = "FCM Devices"
        ordering = ['-last_active']

    def deactivate(self):
        """Deactivate this device token"""
        self.is_active = False
        self.save()


def save_fcm_token(request, token):
    """Save FCM token to database"""
    try:
        # Delete any existing tokens for this user/device
        FCMDevice.objects.filter(token=token).delete()
        # Create new token
        FCMDevice.objects.create(token=token)
        return JsonResponse({'status': 'success'})
    except Exception as e:
        print(f"Error saving FCM token: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def get_firebase_js():
    """Generate Firebase JavaScript configuration"""
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
        os.getenv("FIREBASE_API_KEY", ""),
        os.getenv("FIREBASE_AUTH_DOMAIN", ""),
        os.getenv("FIREBASE_PROJECT_ID", ""),
        os.getenv("FIREBASE_STORAGE_BUCKET", ""),
        os.getenv("FIREBASE_MESSAGING_SENDER_ID", ""),
        os.getenv("FIREBASE_APP_ID", ""),
        os.getenv("FIREBASE_MEASUREMENT_ID", "")
    )
    return HttpResponse(data, content_type="application/javascript")


# Sending Firebase Push Notification
try:
    cred = credentials.Certificate(os.path.join(BASE_DIR, "firebase-key.json"))
    firebase_app = firebase_admin.initialize_app(cred)
except (ValueError, FileNotFoundError) as e:
    print(f"Warning: Could not initialize Firebase Admin: {e}")
except firebase_admin.exceptions.FirebaseError as e:
    print(f"Warning: Firebase Admin initialization error: {e}")


def send_push_notification(title, message, tokens):
    """
    Send push notification using Firebase Cloud Messaging
    Returns a tuple of (success_count, failure_count, failed_tokens)
    """
    if not isinstance(tokens, (list, tuple)):
        tokens = list(tokens)  # Convert QuerySet to list
        
    success_count = 0
    failure_count = 0
    failed_tokens = []
    
    # Get only active devices
    active_devices = FCMDevice.objects.filter(
        token__in=tokens,
        is_active=True
    )
    
    for device in active_devices:
        try:
            response = messaging.send(
                messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=message,
                    ),
                    token=str(device.token),  # Ensure token is a string
                )
            )
            print(f"Successfully sent message: {response}")
            success_count += 1
        except messaging.UnregisteredError:
            # Token is no longer valid, deactivate the device
            print(f"Token {device.token} is no longer valid, deactivating device")
            device.deactivate()
            failure_count += 1
            failed_tokens.append(device.token)
        except Exception as e:
            print(f"Failed to send message to token {device.token}: {e}")
            failure_count += 1
            failed_tokens.append(device.token)
            
    return success_count, failure_count, failed_tokens
