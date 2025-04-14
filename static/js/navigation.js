document.addEventListener('DOMContentLoaded', function () {

    // Get all navigation items
    const navItems = document.querySelectorAll('.nav-item[data-section]');

    // Clear active state from all navigation items immediately
    navItems.forEach(nav => nav.classList.remove('active'));

    // Hide all sections initially to prevent flickering
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
        section.style.display = 'none';
        section.style.visibility = 'hidden';
    });

    // Function to switch to a section
    function switchToSection(targetSection, skipStorage = false) {
        if (!targetSection) return;

        if (!skipStorage) {
            sessionStorage.setItem('activeSection', targetSection);
        }

        // Remove active class from all nav items
        navItems.forEach(nav => nav.classList.remove('active'));

        // Add active class to corresponding nav item
        const activeNav = document.querySelector(`.nav-item[data-section="${targetSection}"]`);
        if (activeNav) {
            activeNav.classList.add('active');
        }

        // Hide all sections first
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
            section.style.display = 'none';
            section.style.visibility = 'hidden';
        });

        // Show the target section
        const targetElement = document.getElementById(`${targetSection}Section`);

        if (targetElement) {
            targetElement.classList.add('active');
            targetElement.style.display = 'block';
            targetElement.style.visibility = 'visible';

            // Update URL hash without scrolling
            history.replaceState(null, null, `#${targetSection}`);
        }

        // Make the page visible now that everything is ready
        document.body.style.opacity = "1";
    }

    // Handle initial page load before showing content
    function handleInitialLoad() {
        let targetSection = 'dashboard'; // Default section

        if (window.location.hash) {
            targetSection = window.location.hash.substring(1);
        } else if (sessionStorage.getItem('activeSection')) {
            targetSection = sessionStorage.getItem('activeSection');
        }

        // Switch to the target section without saving to sessionStorage again
        switchToSection(targetSection, true);
    }

    // Add event listeners to navigation items
    navItems.forEach(item => {
        const section = item.getAttribute('data-section');

        item.addEventListener('click', function (e) {
            e.preventDefault();
            switchToSection(section);
        });
    });

    // Handle hash changes (browser back/forward)
    window.addEventListener('hashchange', function () {
        const targetSection = window.location.hash.substring(1) || 'dashboard';
        switchToSection(targetSection);
    });

    // Run initial load before rendering content
    handleInitialLoad();
    
    // Expose the showSection function globally for backward compatibility with onclick handlers
    window.showSection = function(sectionId) {
        if (typeof sectionId === 'string') {
            // Remove 'Section' suffix if it exists
            const cleanSectionId = sectionId.replace('Section', '');
            switchToSection(cleanSectionId);
        }
    };
});
