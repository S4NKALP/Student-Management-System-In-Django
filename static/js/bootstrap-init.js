// Initialize Bootstrap components
function initializeBootstrapComponents() {
    // Initialize tooltips if available
    if (typeof bootstrap !== "undefined" && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(
            document.querySelectorAll('[data-bs-toggle="tooltip"]'),
        );
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Initialize popovers if available
    if (typeof bootstrap !== "undefined" && bootstrap.Popover) {
        const popoverTriggerList = [].slice.call(
            document.querySelectorAll('[data-bs-toggle="popover"]'),
        );
        popoverTriggerList.map(function(popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
}

// Make function globally accessible
window.initializeBootstrapComponents = initializeBootstrapComponents; 