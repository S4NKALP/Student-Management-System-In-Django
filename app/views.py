from app.models import FCMDevice
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
# Create your views here.


# FireBase
def saveFCMToken(request, token):
    try:
        FCMDevice(token=token).save()
    except:
        pass
    return JsonResponse({})


def showFirebaseJS(request):
    data = """
        importScripts('https://www.gstatic.com/firebasejs/11.0.2/firebase-app-compat.js');
        importScripts('https://www.gstatic.com/firebasejs/11.0.2/firebase-messaging-compat.js');

        firebase.initializeApp({
            apiKey: "AIzaSyAVzOJh5v8_oZg4MoQkq0CzrAbeyHGn4z4",
            authDomain: "institute-management-sys-a2d20.firebaseapp.com",
            projectId: "institute-management-sys-a2d20",
            storageBucket: "institute-management-sys-a2d20.firebasestorage.app",
            messagingSenderId: "777235542100",
            appId: "1:777235542100:web:4d0cb9553918cb3cc23dc1",
            measurementId: "G-4QP9GYV0SJ"
        });

        const messaging = firebase.messaging();

        messaging.onBackgroundMessage((payload) => {

            const notificationTitle = payload.notification.title;
            const notificationOptions = {
                body: payload.notification.body,
                icon: payload.notification.icon
            };

            return self.registration.showNotification(notificationTitle, notificationOptions);
        });
    """
    return HttpResponse(data, content_type="text/javascript")
