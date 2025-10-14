/**
 * Sidebar Navigation JavaScript
 * Handles sidebar collapse/expand and mobile drawer
 */

(function() {
    'use strict';

    // DOM Elements
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const collapsedToggleBtn = document.getElementById('collapsedToggleBtn');
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const mainWrapper = document.querySelector('.main-wrapper');

    // LocalStorage keys
    const SIDEBAR_STATE_KEY = 'wavebulk_sidebar_collapsed';

    // Initialize
    function init() {
        // Restore sidebar state from localStorage (desktop only)
        if (window.innerWidth >= 768) {
            const isCollapsed = localStorage.getItem(SIDEBAR_STATE_KEY) === 'true';
            if (isCollapsed) {
                sidebar.classList.add('collapsed');
            }
        }

        // Event Listeners
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', toggleSidebar);
        }

        if (collapsedToggleBtn) {
            collapsedToggleBtn.addEventListener('click', expandSidebar);
        }

        if (mobileMenuToggle) {
            mobileMenuToggle.addEventListener('click', openMobileMenu);
        }

        if (sidebarOverlay) {
            sidebarOverlay.addEventListener('click', closeMobileMenu);
        }

        // Close mobile menu on navigation link click
        const navLinks = sidebar.querySelectorAll('.sidebar-nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth < 768) {
                    closeMobileMenu();
                }
            });
        });

        // Handle window resize
        window.addEventListener('resize', handleResize);

        // Close mobile menu on ESC key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && sidebar.classList.contains('mobile-open')) {
                closeMobileMenu();
            }
        });
    }

    /**
     * Toggle Sidebar Collapse (Desktop)
     */
    function toggleSidebar() {
        console.log('Toggle sidebar clicked, width:', window.innerWidth);
        if (window.innerWidth >= 768) {
            sidebar.classList.toggle('collapsed');
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem(SIDEBAR_STATE_KEY, isCollapsed);
            console.log('Sidebar collapsed:', isCollapsed);
        }
    }

    /**
     * Expand Sidebar (from collapsed state)
     */
    function expandSidebar() {
        console.log('Expand sidebar clicked');
        if (window.innerWidth >= 768) {
            sidebar.classList.remove('collapsed');
            localStorage.setItem(SIDEBAR_STATE_KEY, 'false');
            console.log('Sidebar expanded');
        }
    }

    /**
     * Open Mobile Menu
     */
    function openMobileMenu() {
        sidebar.classList.add('mobile-open');
        sidebarOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    /**
     * Close Mobile Menu
     */
    function closeMobileMenu() {
        sidebar.classList.remove('mobile-open');
        sidebarOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    /**
     * Handle Window Resize
     */
    function handleResize() {
        // Close mobile menu on resize to desktop
        if (window.innerWidth >= 768) {
            closeMobileMenu();
            
            // Restore collapsed state
            const isCollapsed = localStorage.getItem(SIDEBAR_STATE_KEY) === 'true';
            if (isCollapsed) {
                sidebar.classList.add('collapsed');
            } else {
                sidebar.classList.remove('collapsed');
            }
        } else {
            // Remove collapsed class on mobile
            sidebar.classList.remove('collapsed');
        }
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose functions globally if needed
    window.WaveBulkSidebar = {
        toggle: toggleSidebar,
        expand: expandSidebar,
        openMobile: openMobileMenu,
        closeMobile: closeMobileMenu
    };
})();

