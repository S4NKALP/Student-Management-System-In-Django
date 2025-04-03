// Utility functions for the teacher dashboard

// Global variables and constants
let fileIdToDelete = null;
const API_BASE_URL = '/app';
const DEFAULT_ERROR_MESSAGE = 'An error occurred. Please try again.';

// Type checking utilities
const isString = (value) => typeof value === 'string';
const isObject = (value) => value !== null && typeof value === 'object';
const isEmpty = (value) => value === null || value === undefined || value === '';

// CSRF token management
function getCSRFToken() {
    try {
        const cookies = document.cookie.split(';');
        const csrfCookie = cookies.find(cookie => cookie.trim().startsWith('csrftoken='));
        return csrfCookie ? decodeURIComponent(csrfCookie.split('=')[1]) : null;
    } catch (error) {
        console.error('Error getting CSRF token:', error);
        return null;
    }
}

// API request helper with better error handling and retries
async function apiRequest(url, options = {}, retries = 3) {
    const defaultOptions = {
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
    };

    for (let attempt = 1; attempt <= retries; attempt++) {
        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP error! Status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            if (attempt === retries) {
                console.error(`API Request Error (attempt ${attempt}/${retries}):`, error);
                throw error;
            }
            await new Promise(resolve => setTimeout(resolve, 1000 * attempt)); // Exponential backoff
        }
    }
}

// UI Helpers with enhanced styling and accessibility
function showLoadingSpinner(container, message = 'Loading...') {
    if (!container) return;
    
    container.innerHTML = `
        <div class="text-center py-4" role="status" aria-live="polite">
            <div class="spinner-border text-primary" role="presentation">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2 text-muted">${message}</p>
        </div>
    `;
}

function showError(container, error, withRetryButton = false) {
    if (!container) return;
    
    const errorMessage = error?.message || DEFAULT_ERROR_MESSAGE;
    container.innerHTML = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            <i class="fas fa-exclamation-circle me-2"></i>
            <strong>${errorMessage}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
        ${withRetryButton ? `
            <div class="text-center mt-3">
                <button class="btn btn-primary" onclick="window.location.reload()">
                    <i class="fas fa-sync me-1"></i> Retry
                </button>
            </div>
        ` : ''}
    `;
}

function showSuccess(container, message, autoHide = true) {
    if (!container) return;
    
    container.innerHTML = `
        <div class="alert alert-success alert-dismissible fade show" role="alert">
            <i class="fas fa-check-circle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    if (autoHide) {
        setTimeout(() => {
            const alert = container.querySelector('.alert');
            if (alert) {
                alert.classList.remove('show');
                setTimeout(() => alert.remove(), 150);
            }
        }, 5000);
    }
}

// Modal Helpers with enhanced functionality
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;
    
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
    
    // Focus trap for accessibility
    const focusableElements = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
    if (focusableElements.length > 0) {
        focusableElements[0].focus();
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;
    
    modal.style.display = 'none';
    document.body.style.overflow = '';
}

// Form Helpers with validation
function resetForm(formOrId) {
    let form;
    
    // Handle both form element and form ID
    if (typeof formOrId === 'string') {
        form = document.getElementById(formOrId);
    } else if (formOrId instanceof HTMLFormElement) {
        form = formOrId;
    } else {
        console.warn('Invalid form reference:', formOrId);
        return;
    }
    
    if (!form) {
        console.warn('Form not found:', formOrId);
        return;
    }
    
    // Reset form values
    form.reset();
    
    // Clear all alerts and validation states
    form.querySelectorAll('.alert, .is-invalid, .is-valid').forEach(el => {
        el.classList.remove('alert', 'is-invalid', 'is-valid');
    });
    
    // Reset all checkboxes to unchecked state
    form.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
        checkbox.checked = false;
    });
    
    // Reset all select elements to first option
    form.querySelectorAll('select').forEach(select => {
        if (select.options.length > 0) {
            select.selectedIndex = 0;
        }
    });
}

// Date Helpers with enhanced formatting options
function formatDate(date, format = 'YYYY-MM-DD') {
    const d = new Date(date);
    if (isNaN(d.getTime())) return '';
    
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    
    return format
        .replace('YYYY', year)
        .replace('MM', month)
        .replace('DD', day);
}

function getCurrentDate() {
    return formatDate(new Date());
}

// Validation Helpers
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    const re = /^\+?[\d\s-]{10,}$/;
    return re.test(phone);
}

// Export all functions
window.getCSRFToken = getCSRFToken;
window.apiRequest = apiRequest;
window.showLoadingSpinner = showLoadingSpinner;
window.showError = showError;
window.showSuccess = showSuccess;
window.showModal = showModal;
window.hideModal = hideModal;
window.resetForm = resetForm;
window.formatDate = formatDate;
window.getCurrentDate = getCurrentDate;
window.validateEmail = validateEmail;
window.validatePhone = validatePhone; 