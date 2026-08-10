document.addEventListener('DOMContentLoaded', async () => {
    if ('Notification' in window && 'serviceWorker' in navigator) {
        try {
            // Register service worker at root scope if possible, or static scope
            const reg = await navigator.serviceWorker.register('/static/sw.js');
            const permission = await Notification.requestPermission();
            
            if (permission === 'granted') {
                checkAndNotify();
                // Check every hour if tab is open
                setInterval(checkAndNotify, 60 * 60 * 1000);
            }
        } catch(e) {
            console.error("Service Worker registration failed:", e);
        }
    }
});

async function checkAndNotify() {
    try {
        const res = await fetch('/api/profile');
        if(!res.ok) return;
        const data = await res.json();
        
        const lastLogStr = localStorage.getItem('lastNotificationDate');
        const todayStr = new Date().toDateString();
        
        if (lastLogStr === todayStr) {
            return; // Already notified today
        }

        let needsLogging = true;
        if (data.timestamp) {
            const logDateStr = new Date(data.timestamp).toDateString();
            if (logDateStr === todayStr) {
                needsLogging = false; // Already logged today
            }
        }
        
        if (needsLogging) {
            navigator.serviceWorker.ready.then(reg => {
                reg.showNotification('WellnessIQ Reminder 🔔', {
                    body: "Don't forget to enter your daily insights today to keep your streak going!",
                    icon: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" fill="%23ef4444"/></svg>',
                    vibrate: [200, 100, 200]
                });
            });
            localStorage.setItem('lastNotificationDate', todayStr);
        }

    } catch(e) {
        console.error("Notification check failed", e);
    }
}
