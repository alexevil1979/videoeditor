// Main application JavaScript

// Auto-refresh job status every 30 seconds
setInterval(() => {
    if (window.location.pathname.includes('/dashboard')) {
        // Refresh page to update job status
        // In production, use AJAX to update only job status
    }
}, 30000);
