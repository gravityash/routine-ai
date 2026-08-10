function toggleTheme() {
    document.documentElement.classList.toggle('dark-mode');
    const isDark = document.documentElement.classList.contains('dark-mode');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    if (typeof Chart !== 'undefined') {
        Chart.defaults.color = isDark ? '#94a3b8' : '#475569';
    }
}

function applyTheme() {
    if (localStorage.getItem('theme') === 'dark') {
        document.documentElement.classList.add('dark-mode');
        if (typeof Chart !== 'undefined') {
            Chart.defaults.color = '#94a3b8';
        }
    } else {
        document.documentElement.classList.remove('dark-mode');
        if (typeof Chart !== 'undefined') {
            Chart.defaults.color = '#475569';
        }
    }
}

// Apply immediately for seamless transition
applyTheme();

// Keep the theme instantly synced across multiple tabs
window.addEventListener('storage', (e) => {
    if (e.key === 'theme') {
        applyTheme();
    }
});
