// Teacher Modals JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Teacher modals initialized');
    
    // Initialize any modals that need to be shown
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (modal.classList.contains('show')) {
            const modalInstance = new bootstrap.Modal(modal);
            modalInstance.show();
        }
    });

    // Handle modal close events
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('hidden.bs.modal', function () {
            // Clean up any form data or reset states
            const forms = modal.querySelectorAll('form');
            forms.forEach(form => form.reset());
        });
    });
}); 