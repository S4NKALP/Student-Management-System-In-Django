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
            apiKey: "",
            authDomain: "",
            projectId: "",
            storageBucket: "",
            messagingSenderId: "",
            appId: "",
            measurementId: ""
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
