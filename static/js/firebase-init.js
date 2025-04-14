// Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
const messaging = firebase.messaging();

async function registerServiceWorker() {
    try {
        if (!('serviceWorker' in navigator)) {
            throw new Error('Service Worker is not supported in this browser');
        }

        // Unregister any existing service workers
        const existingRegistrations = await navigator.serviceWorker.getRegistrations();
        for (let registration of existingRegistrations) {
            await registration.unregister();
        }

        // Register the new service worker
        const registration = await navigator.serviceWorker.register('/firebase-messaging-sw.js', {
            scope: '/',
            updateViaCache: 'none'
        });

        console.log('Service Worker registered with scope:', registration.scope);
        await navigator.serviceWorker.ready;
        return registration;
    } catch (error) {
        console.error('Service Worker registration failed:', error);
        throw error;
    }
}

async function getDeviceToken() {
    try {
        const registration = await registerServiceWorker();
        
        // Request notification permission if not already granted
        let permission = Notification.permission;
        if (permission === 'default') {
            permission = await Notification.requestPermission();
        }

        if (permission !== 'granted') {
            throw new Error('Notification permission not granted');
        }

        // Get FCM token
        const token = await messaging.getToken({
            vapidKey: vapidKey,
            serviceWorkerRegistration: registration
        });

        if (!token) {
            throw new Error('Failed to get FCM token');
        }

        console.log('Got FCM token:', token);

        // Get CSRF token
        const csrftoken = getCookie('csrftoken');
        if (!csrftoken) {
            throw new Error('CSRF token not found');
        }

        // Send the token to your backend for storage
        const response = await fetch('/app/saveFCMToken/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({ token: token })
        });

        if (!response.ok) {
            throw new Error('Failed to save token to server');
        }

        console.log('FCM Token saved successfully');
        return token;
    } catch (error) {
        console.error('Error in getDeviceToken:', error);
        try {
            // Clean up and retry on failure
            await messaging.deleteToken().catch(console.error);
            const registrations = await navigator.serviceWorker.getRegistrations();
            for (let registration of registrations) {
                await registration.unregister();
            }
            await new Promise(resolve => setTimeout(resolve, 1000));
            return getDeviceToken();
        } catch (retryError) {
            console.error('Error during cleanup and retry:', retryError);
            throw error;
        }
    }
}

// Make getDeviceToken available globally
window.getDeviceToken = getDeviceToken;

// Handle token refresh
messaging.onTokenRefresh = async () => {
    try {
        await getDeviceToken();
    } catch (error) {
        console.error('Error refreshing token:', error);
    }
};

// Handle foreground messages
messaging.onMessage((payload) => {
    console.log('Foreground message received:', payload);
    
    if (Notification.permission === 'granted') {
        const notificationTitle = payload.notification.title;
        const notificationOptions = {
            body: payload.notification.body,
            icon: payload.notification.icon || '/static/img/logo.png',
            badge: '/static/img/logo.png',
            timestamp: Date.now(),
            requireInteraction: true,
            vibrate: [200, 100, 200],
            tag: 'notification-' + Date.now(),
            data: payload.data || {},
            actions: [
                {
                    action: 'open',
                    title: 'Open'
                },
                {
                    action: 'close',
                    title: 'Close'
                }
            ]
        };

        navigator.serviceWorker.ready.then(registration => {
            registration.showNotification(notificationTitle, notificationOptions)
                .catch(error => {
                    console.error('Error showing notification:', error);
                });
        });
    }
}); 
