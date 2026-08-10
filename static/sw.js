self.addEventListener('push', function(e) {
    // Placeholder for true server push
});

self.addEventListener('notificationclick', function(e) {
    e.notification.close();
    e.waitUntil(
        clients.openWindow('/dashboard')
    );
});
