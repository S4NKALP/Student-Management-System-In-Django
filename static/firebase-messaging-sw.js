// Version identifier for cache busting
const SW_VERSION = '1.0.3';
console.log(`Firebase Messaging SW Version ${SW_VERSION} starting...`);

// Import Firebase scripts
try {
    importScripts('https://www.gstatic.com/firebasejs/9.22.0/firebase-app-compat.js');
    importScripts('https://www.gstatic.com/firebasejs/9.22.0/firebase-messaging-compat.js');
    console.log('Firebase scripts loaded successfully');
} catch (e) {
    console.error('Error loading Firebase scripts:', e);
    throw e; // Re-throw to prevent further execution
}

// Firebase configuration - this must match exactly with your main app configuration
const firebaseConfig = {
    apiKey: "AIzaSyAYgYXsf4-iwSDEEBcNAJ3YJxz76C3STsU",
    authDomain: "student-management-syste-2e040.firebaseapp.com",
    projectId: "student-management-syste-2e040",
    storageBucket: "student-management-syste-2e040.firebasestorage.app",
    messagingSenderId: "800148418884",
    appId: "1:800148418884:web:144b9c85bfeeec12252711",
    measurementId: "G-BNRM6QEJQV"
};

// Handle any errors during initialization
try {
    // Initialize Firebase
    firebase.initializeApp(firebaseConfig);
    console.log('Firebase initialized in service worker');
    
    const messaging = firebase.messaging();
    console.log('Firebase messaging initialized');

    // Handle background messages
    messaging.onBackgroundMessage(function(payload) {
        console.log('Received background message:', payload);
        
        // Generate a unique ID for this notification
        const notificationId = payload.data?.notificationId || `notification-${Date.now()}`;
        
        // Check if we already have a notification with this ID
        return self.registration.getNotifications({tag: notificationId})
            .then(function(notifications) {
                // Only show if no matching notification exists
                if (notifications.length === 0) {
                    const notificationTitle = payload.notification?.title || 'New Notification';
                    const notificationOptions = {
                        body: payload.notification?.body || 'You have a new message.',
                        icon: '/static/img/logo.png',
                        badge: '/static/img/logo.png',
                        tag: notificationId, // Tag helps prevent duplicates
                        data: payload.data || {}
                    };

                    return self.registration.showNotification(notificationTitle, notificationOptions);
                } else {
                    console.log('Prevented duplicate background notification', notificationId);
                    return Promise.resolve();
                }
            })
            .catch(error => {
                console.error('Error showing background notification:', error);
                return Promise.resolve();
            });
    });
} catch (error) {
    console.error('Firebase messaging initialization error:', error);
    throw error; // Re-throw to prevent further execution
}

// Improve service worker lifecycle for better compatibility
self.addEventListener('install', function(event) {
    console.log('Service Worker installed');
    self.skipWaiting();
});

self.addEventListener('activate', function(event) {
    console.log('Service Worker activated');
    event.waitUntil(
        Promise.all([
            self.clients.claim(),
            // Clean up old caches if needed
            caches.keys().then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName.startsWith('firebase-messaging-')) {
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
        ])
    );
});

// Add special handling for push events 
self.addEventListener('push', function(event) {
    console.log('Push event received in service worker', event);
    
    if (!event.data) {
        console.log('Push event has no data');
        return;
    }

    try {
        const payload = event.data.json();
        console.log('Push data:', payload);
        
        // Generate a unique ID for this notification
        const notificationId = payload.data?.notificationId || `push-${Date.now()}`;
        
        event.waitUntil(
            // Check for existing notifications first
            self.registration.getNotifications({tag: notificationId})
                .then(function(notifications) {
                    // Only show if no matching notification exists
                    if (notifications.length === 0) {
                        const title = payload.notification?.title || 'New Notification';
                        const options = {
                            body: payload.notification?.body || 'You have a new message',
                            icon: '/static/img/logo.png',
                            badge: '/static/img/logo.png',
                            tag: notificationId, // Add tag to identify this notification
                            data: payload.data || {}
                        };
                        
                        return self.registration.showNotification(title, options);
                    } else {
                        console.log('Prevented duplicate push notification', notificationId);
                        return Promise.resolve();
                    }
                })
        );
    } catch (error) {
        console.error('Error handling push event:', error);
    }
});

// Improve notification click handling for various environments
self.addEventListener('notificationclick', function(event) {
    console.log('Notification clicked:', event.notification);
    event.notification.close();
    
    const urlToOpen = event.notification.data?.url || '/app/dashboard/';

    event.waitUntil(
        clients.matchAll({type: 'window', includeUncontrolled: true}).then(windowClients => {
            // Check if there is already a window open with the target URL
            for (let i = 0; i < windowClients.length; i++) {
                const client = windowClients[i];
                // If so, focus on that window
                if (client.url === urlToOpen && 'focus' in client) {
                    return client.focus();
                }
            }
            // If not, open a new window
            if (clients.openWindow) {
                return clients.openWindow(urlToOpen);
            }
        })
    );
});
