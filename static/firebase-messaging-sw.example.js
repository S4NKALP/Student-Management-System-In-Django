importScripts(
  "https://www.gstatic.com/firebasejs/9.22.0/firebase-app-compat.js",
);
importScripts(
  "https://www.gstatic.com/firebasejs/9.22.0/firebase-messaging-compat.js",
);

firebase.initializeApp({
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_AUTH_DOMAIN",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_STORAGE_BUCKET",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID",
  measurementId: "YOUR_MEASUREMENT_ID",
});

const messaging = firebase.messaging();

// Handle background messages
messaging.onBackgroundMessage((payload) => {
  console.log("Received background message:", payload);

  // Default notification options
  const notificationOptions = {
    body: "You have a new message.",
    icon: "/static/img/logo.png",
    badge: "/static/img/logo.png",
    timestamp: Date.now(),
    requireInteraction: true,
    vibrate: [200, 100, 200],
    tag: "notification-" + Date.now(),
    data: payload.data || {},
    actions: [
      {
        action: "open",
        title: "Open",
      },
      {
        action: "close",
        title: "Close",
      },
    ],
  };

  // Set notification title and body based on payload
  let notificationTitle = "New Notification";
  if (payload.notification) {
    notificationTitle = payload.notification.title || notificationTitle;
    notificationOptions.body =
      payload.notification.body || notificationOptions.body;
    if (payload.notification.icon) {
      notificationOptions.icon = payload.notification.icon;
    }
  } else if (payload.data) {
    notificationTitle = payload.data.title || notificationTitle;
    notificationOptions.body = payload.data.body || notificationOptions.body;
  }

  // Show the notification
  return self.registration
    .showNotification(notificationTitle, notificationOptions)
    .catch((error) => {
      console.error("Error showing notification:", error);
    });
});

// Handle notification click
self.addEventListener("notificationclick", (event) => {
  console.log("Notification clicked:", event);

  event.notification.close();

  if (event.action === "open") {
    // Handle open action
    const urlToOpen = event.notification.data.url || "/app/dashboard/";
    event.waitUntil(clients.openWindow(urlToOpen));
  }
});

// Handle service worker installation
self.addEventListener("install", (event) => {
  console.log("Service Worker installed");
  self.skipWaiting();
});

// Handle service worker activation
self.addEventListener("activate", (event) => {
  console.log("Service Worker activated");
  event.waitUntil(clients.claim());
});
