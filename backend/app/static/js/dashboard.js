/**
 * WaveBulk - Dashboard
 * Handles dashboard functionality and real-time updates
 */

document.addEventListener('DOMContentLoaded', function() {
    // Auto-refresh pending tasks
    const pendingCount = document.querySelector('[data-pending-count]');
    
    if (pendingCount && parseInt(pendingCount.dataset.pendingCount) > 0) {
        // Refresh dashboard every 10 seconds if there are pending tasks
        setInterval(() => {
            fetch(window.location.href)
                .then(response => response.text())
                .then(html => {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    
                    // Update stats
                    const newStats = doc.querySelectorAll('.stat-value');
                    const currentStats = document.querySelectorAll('.stat-value');
                    
                    newStats.forEach((newStat, index) => {
                        if (currentStats[index]) {
                            currentStats[index].textContent = newStat.textContent;
                        }
                    });
                    
                    // Update recent files if needed
                    const newRecentFiles = doc.querySelector('.files-grid');
                    const currentRecentFiles = document.querySelector('.files-grid');
                    
                    if (newRecentFiles && currentRecentFiles) {
                        currentRecentFiles.innerHTML = newRecentFiles.innerHTML;
                    }
                })
                .catch(error => console.error('Dashboard refresh failed:', error));
        }, 10000);
    }
    
    // Animate stat values on load
    const statValues = document.querySelectorAll('.stat-value');
    statValues.forEach(stat => {
        const finalValue = parseInt(stat.textContent) || parseFloat(stat.textContent) || 0;
        if (typeof finalValue === 'number' && !isNaN(finalValue)) {
            let currentValue = 0;
            const increment = finalValue / 30;
            const timer = setInterval(() => {
                currentValue += increment;
                if (currentValue >= finalValue) {
                    stat.textContent = stat.textContent; // Keep original format
                    clearInterval(timer);
                } else {
                    stat.textContent = Math.floor(currentValue);
                }
            }, 20);
        }
    });
});

