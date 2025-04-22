// Get CSRF token from cookie or any other available source
function getCSRFToken() {
    // Try getting from cookie
    let token = getCookie('csrftoken');
    
    // If not in cookie, try getting from meta tag (Django often puts it there)
    if (!token) {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            token = metaTag.getAttribute('content');
        }
    }
    
    // Try getting from a hidden input field with name="csrfmiddlewaretoken"
    if (!token) {
        const inputField = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (inputField) {
            token = inputField.value;
        }
    }
    
    console.log('CSRF Token found:', token ? 'Yes (length: ' + token.length + ')' : 'No');
    return token || '';
}

// CSRF-safe fetch utility function
async function csrfFetch(url, options = {}) {
    // Default options
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'include'
    };
    
    // Merge provided options with defaults
    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };
    
    // Add CSRF token if not explicitly provided and it's a mutating request method
    const method = mergedOptions.method ? mergedOptions.method.toUpperCase() : 'GET';
    const needsCSRF = ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method);
    
    if (needsCSRF && !mergedOptions.headers['X-CSRFToken']) {
        const csrfToken = getCSRFToken();
        if (csrfToken) {
            // Set token in exactly the format Django expects (X-CSRFToken)
            // Django is case-sensitive and specifically looks for X-CSRFToken
            mergedOptions.headers['X-CSRFToken'] = csrfToken;
        } else {
            console.warn('No CSRF token available for a mutating request to:', url);
        }
    }
    
    try {
        console.log(`Making ${method} request to ${url} with headers:`, mergedOptions.headers);
        const response = await fetch(url, mergedOptions);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Server response:', response.status, errorText);
            throw new Error(`Request failed: ${response.status} ${response.statusText}`);
        }
        
        return response;
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

// Original getCookie function
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

        // Simple approach: send token to server using basic fetch
        try {
            const response = await fetch('/app/saveFCMToken/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ token: token })
            });
            
            if (response.ok) {
                console.log('FCM Token saved successfully');
            } else {
                console.error('Failed to save FCM token:', response.status);
            }
            
            return token;
        } catch (fetchError) {
            console.error('Error saving FCM token:', fetchError);
            return token; // Return token even if saving failed
        }
    } catch (error) {
        console.error('Error in getDeviceToken:', error);
        return null;
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

// Automatically initialize FCM when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Wait a moment for the page to fully initialize
    setTimeout(() => {
        getDeviceToken()
            .then(token => {
                if (token) {
                    console.log('FCM initialized successfully with token');
                }
            })
            .catch(error => {
                console.error('Failed to initialize FCM:', error);
            });
    }, 2000);
}); 
