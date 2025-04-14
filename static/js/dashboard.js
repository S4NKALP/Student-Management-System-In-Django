// Dashboard functionality

// Wait for the DOM to be fully loaded before running any code
document.addEventListener("DOMContentLoaded", function() {
    // More reliable login detection - check for dashboard-specific elements
    const isLoggedIn = (
        // Check for common dashboard elements
        !!document.querySelector('.dashboard-content') || 
        !!document.querySelector('.side-navbar') ||
        !!document.querySelector('#user-dropdown') ||
        !!document.querySelector('.user-menu') ||
        !!document.querySelector('.nav-link[href*="logout"]') ||
        // Check URL patterns that would only be accessible when logged in
        window.location.pathname.includes('/dashboard') ||
        window.location.pathname.includes('/profile') ||
        window.location.pathname.includes('/app/') ||
        // Explicit authentication flag
        window.IS_AUTHENTICATED === true
    );
    
    if (isLoggedIn) {
        // Call with a slight delay to ensure page is fully loaded
        setTimeout(function() {
            checkWeakPassword();
        }, 100);
    }
    
    // Initialize all components
    initializeComponents();
    
    // Set up event handlers
    setupEventHandlers();
    
    // Get device token for notifications
    if (typeof window.getDeviceToken === 'function' && isLoggedIn) {
        window.getDeviceToken();
    }
    
    // Add global keyboard event handler for Escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' || event.keyCode === 27) {
            closeAllModals();
        }
    });
    
    // Initialize responsive modals
    initResponsiveModals();
    
    // Make all tables responsive
    makeAllTablesResponsive();
    
    // Handle long content
    handleLongContent();
    
    // Process any dynamically added tables
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                makeAllTablesResponsive();
                handleLongContent();
            }
        });
    });
    
    // Start observing the document for added nodes
    observer.observe(document.body, { childList: true, subtree: true });
});

// Function to initialize all dashboard components
function initializeComponents() {
    // Initialize any Bootstrap components
    if (typeof bootstrap !== 'undefined') {
        // Initialize tooltips
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // Initialize popovers
        var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function(popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
    
    // Handle image loading errors
    document.querySelectorAll('img').forEach(function(img) {
        img.addEventListener("error", function() {
            this.onerror = null;
            this.src = "/static/img/user.png";
        });
    });
    
    // Setup star rating if elements exist
    if (typeof window.setupStarRating === 'function') {
        window.setupStarRating();
    }
    
    // Setup tabs if elements exist
    if (typeof window.setupCustomTabs === 'function') {
        window.setupCustomTabs();
    }
    
    // Setup feedback tabs if elements exist
    if (typeof window.setupFeedbackTabs === 'function') {
        window.setupFeedbackTabs();
    }
    
    // Initialize Bootstrap components
    if (typeof window.initializeBootstrapComponents === 'function') {
        window.initializeBootstrapComponents();
    }
    
    // Set up form validation
    if (typeof window.setupRatingFormValidation === 'function') {
        window.setupRatingFormValidation();
    }
    
    // Ensure notifications.js is loaded
    if (typeof window.showNotification !== 'function') {
        // Dynamically load the notifications script if not already available
        const script = document.createElement('script');
        script.src = '/static/js/notifications.js';
        script.async = true;
        document.head.appendChild(script);
    }
    
    // Ensure notification toast container exists
    if (!document.getElementById('notificationToast')) {
        const toastContainer = document.createElement('div');
        toastContainer.innerHTML = `
            <div class="toast-container position-fixed bottom-0 end-0 p-3">
                <div id="notificationToast" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                    <div class="toast-header">
                        <strong class="me-auto" id="toastTitle">Notification</strong>
                        <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                    </div>
                    <div class="toast-body" id="toastMessage">
                        Message goes here
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(toastContainer.firstElementChild);
    }
}

// Star rating functionality
function setupStarRating() {
    document.querySelectorAll('.rating').forEach(function(container) {
        var stars = container.querySelectorAll('.star');
        var ratingInput = container.querySelector('input[type="hidden"]');
        
        stars.forEach(function(star, index) {
            // Set initial state
            if (ratingInput && parseInt(ratingInput.value) > index) {
                star.classList.add('active');
            }
            
            // Add click handlers
            star.addEventListener('click', function() {
                // Update hidden input
                if (ratingInput) {
                    ratingInput.value = index + 1;
                }
                
                // Update star display
                stars.forEach(function(s, i) {
                    if (i <= index) {
                        s.classList.add('active');
                    } else {
                        s.classList.remove('active');
                    }
                });
            });
            
            // Add hover effects
            star.addEventListener('mouseenter', function() {
                stars.forEach(function(s, i) {
                    if (i <= index) {
                        s.classList.add('hover');
                    } else {
                        s.classList.remove('hover');
                    }
                });
            });
            
            container.addEventListener('mouseleave', function() {
                stars.forEach(function(s) {
                    s.classList.remove('hover');
                });
            });
        });
    });
}

// Function to set up custom tabs
function setupCustomTabs() {
    var tabLinks = document.querySelectorAll('.custom-tabs .tab-link');
    
    tabLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            var target = this.getAttribute('data-target');
            
            // Hide all tab content
            document.querySelectorAll('.custom-tabs .tab-content').forEach(function(tab) {
                tab.classList.remove('active');
            });
            
            // Deactivate all tab links
            tabLinks.forEach(function(tabLink) {
                tabLink.classList.remove('active');
            });
            
            // Activate clicked tab and content
            this.classList.add('active');
            document.getElementById(target).classList.add('active');
        });
    });
    
    // Activate first tab if none active
    if (document.querySelector('.custom-tabs .tab-link.active') === null) {
        var firstTab = document.querySelector('.custom-tabs .tab-link');
        if (firstTab) {
            firstTab.click();
        }
    }
}

// Function to set up feedback tabs
function setupFeedbackTabs() {
    var tabLinks = document.querySelectorAll('.feedback-tabs .tab-link');
    
    tabLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            var target = this.getAttribute('data-target');
            
            // Hide all tab content
            document.querySelectorAll('.feedback-tabs .tab-content').forEach(function(tab) {
                tab.classList.remove('active');
            });
            
            // Deactivate all tab links
            tabLinks.forEach(function(tabLink) {
                tabLink.classList.remove('active');
            });
            
            // Activate clicked tab and content
            this.classList.add('active');
            document.getElementById(target).classList.add('active');
        });
    });
}

// Function to check if the current user's password is weak and show a popup if needed
function checkWeakPassword() {
    // Only skip on login/register pages
    if (window.location.pathname.indexOf('/login') !== -1 || 
        window.location.pathname.indexOf('/register') !== -1 ||
        window.location.pathname === '/') {
        return;
    }
    
    // On dashboard page, we should definitely be logged in
    const onDashboard = window.location.pathname.includes('/dashboard') ||
                       window.location.pathname.includes('/app/');
    
    try {
        // Basic fetch with no extra options to keep it simple
        fetch('/app/check-weak-password/')
        .then(function(response) { 
            // Handle unauthorized responses (not logged in)
            if (response.status === 401 || response.status === 403) {
                return null;
            }
            
            // Check if response is valid JSON
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return response.json().catch(error => {
                    return response.text().then(text => {
                        // Only show if there's an indication of a weak password
                        return text.includes('weak') ? { is_weak: true } : { is_weak: false };
                    });
                });
            } else {
                // Not JSON, try to get text instead
                return response.text().then(text => {
                    // Only show if there's an indication of a weak password
                    return text.includes('weak') ? { is_weak: true } : { is_weak: false };
                });
            }
        })
        .then(function(data) {
            // Skip if null (user not authenticated)
            if (data === null) return;
            
            if (data && data.is_weak === true) {
                // Show modal immediately
                showWeakPasswordModal();
            }
        })
        .catch(function(error) {
            console.error('Error checking password strength:', error);
        });
    } catch (e) {
        console.error('Error in checkWeakPassword:', e);
    }
}

// Function to create and show the weak password modal
function showWeakPasswordModal() {
    // Check if modal already exists (prevent duplicates)
    if (document.getElementById('weakPasswordModal')) {
        document.getElementById('weakPasswordModal').style.display = 'block';
        return;
    }
    
    // Get CSRF token
    var csrfToken = '';
    var csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    
    if (csrfInput) {
        csrfToken = csrfInput.value;
    } else {
        // Try to get from cookie if not found in form
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.startsWith('csrftoken=')) {
                csrfToken = cookie.substring('csrftoken='.length, cookie.length);
                break;
            }
        }
    }
    
    // Create modal HTML with password inputs
    var modalHtml = `
    <div id="weakPasswordModal" class="modal" style="display:block; position:fixed; z-index:2000; left:0; top:0; width:100%; height:100%; overflow:auto; background-color:rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center;">
        <div class="modal-content" style="background-color:#fefefe; padding:20px; border:1px solid #888; width:90%; max-width:500px; border-radius:8px; box-shadow:0 4px 8px rgba(0,0,0,0.2); margin:0 auto;">
            <div class="modal-header">
                <h5 class="modal-title">Security Alert</h5>
            </div>
            <div class="modal-body">
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>Your current password is weak and poses a security risk.</strong>
                </div>
                <p>Please change your password to a more secure one to continue using the system.</p>
                <form id="password-form-div" onsubmit="return false;">
                    <div class="mb-3">
                        <label for="current_password" class="form-label">Current Password</label>
                        <input type="password" class="form-control" id="current_password" name="current_password" value="123" readonly required>
                        <input type="hidden" id="current_password_hidden" name="current_password_hidden" value="123">
                    </div>
                    <div class="mb-3">
                        <label for="new_password_area" class="form-label">New Password</label>
                        <input type="password" class="form-control" id="new_password_area" placeholder="Enter new password (min 8 characters)" required>
                        <div class="form-text">Password must be at least 8 characters long.</div>
                    </div>
                    <div class="mb-3">
                        <label for="confirm_password_area" class="form-label">Confirm New Password</label>
                        <input type="password" class="form-control" id="confirm_password_area" placeholder="Confirm new password" required>
                    </div>
                    <div class="mb-3">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="show_password">
                            <label class="form-check-label" for="show_password">
                                Show password
                            </label>
                        </div>
                    </div>
                    <div class="d-grid">
                        <button type="submit" id="password-change-btn" class="btn btn-primary">Change Password</button>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <div class="text-center w-100">
                    <small class="text-muted">For security reasons, you must change your default password.</small>
                </div>
            </div>
        </div>
    </div>`;
    
    // Append modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Add media query styles for better responsiveness
    const styleEl = document.createElement('style');
    styleEl.textContent = `
        @media (max-width: 576px) {
            #weakPasswordModal .modal-content {
                width: 95% !important;
                padding: 15px !important;
            }
            
            #weakPasswordModal .modal-title {
                font-size: 1.1rem !important;
            }
            
            #weakPasswordModal .form-label {
                font-size: 0.9rem !important;
            }
        }
        
        @media (max-height: 640px) {
            #weakPasswordModal {
                align-items: flex-start !important;
                padding-top: 20px !important;
            }
        }
    `;
    document.head.appendChild(styleEl);
    
    // Set up password handling directly
    var passwordArea = document.getElementById('new_password_area');
    var confirmArea = document.getElementById('confirm_password_area');
    var lengthDisplay = document.getElementById('password-length-display');
    var changeBtn = document.getElementById('password-change-btn');
    var showPasswordCheckbox = document.getElementById('show_password');
    var passwordForm = document.getElementById('password-form-div');
    
    if (passwordArea && lengthDisplay) {
        // Focus on password field
        setTimeout(function() {
            passwordArea.focus();
        }, 100);
        
        // Update function that directly reads the password field
        function updateLengthDisplay() {
            var password = passwordArea.value || '';
            // Update display with current length
            lengthDisplay.textContent = 'Current length: ' + password.length + ' characters';
        }
        
        // Add multiple event listeners to catch all input cases
        ['input', 'keyup', 'keydown', 'change', 'paste'].forEach(function(eventType) {
            passwordArea.addEventListener(eventType, updateLengthDisplay);
        });
        
        // Add keydown event for Enter key
        passwordArea.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                // Focus on confirm field if Enter is pressed in password field
                confirmArea.focus();
            }
        });
        
        // Add keydown event for Enter key on confirm field
        confirmArea.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                // Trigger submit button click if Enter is pressed in confirm field
                if (changeBtn) {
                    changeBtn.click();
                }
            }
        });
        
        // Initial update
        updateLengthDisplay();
    }
    
    // Toggle password visibility
    if (showPasswordCheckbox) {
        showPasswordCheckbox.addEventListener('change', function() {
            var type = this.checked ? 'text' : 'password';
            passwordArea.type = type;
            confirmArea.type = type;
        });
    }
    
    if (changeBtn) {
        changeBtn.addEventListener('click', function() {
            // Get the current password from the hidden field (more reliable)
            var currentPassword = document.getElementById('current_password_hidden').value || '123';
            var newPassword = passwordArea.value || '';
            var confirmPassword = confirmArea.value || '';
            
            // Check for empty fields first
            if (!newPassword) {
                alert('New password is required.');
                passwordArea.focus();
                return;
            }
            
            if (!confirmPassword) {
                alert('Please confirm your password.');
                confirmArea.focus();
                return;
            }
            
            // Validate passwords
            if (newPassword.length < 8) {
                alert('Password must be at least 8 characters long! Your password is ' + newPassword.length + ' characters.');
                passwordArea.focus();
                return;
            }
            
            if (newPassword !== confirmPassword) {
                alert('Passwords do not match!');
                confirmArea.focus();
                return;
            }
            
            // Get CSRF token
            var csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value || '';
            
            // Create form data
            var formData = new FormData();
            formData.append('csrfmiddlewaretoken', csrfToken);
            formData.append('current_password', currentPassword);
            formData.append('new_password', newPassword);
            formData.append('confirm_password', confirmPassword);
            
            // Submit form
            fetch('/app/change-password/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(function(data) {
                if (data.success) {
                    // Show success message
                    if (typeof window.showNotification === 'function') {
                        window.showNotification('Password Updated', data.message || 'Your password has been changed successfully. Please login again.', 'success');
                    } else {
                        alert(data.message || 'Password changed successfully. Please login again.');
                    }
                    
                    // Close the modal
                    document.getElementById('weakPasswordModal')?.remove();
                    
                    // Wait a moment for the notification to be visible
                    setTimeout(function() {
                        // Redirect to login page
                        window.location.href = data.redirect || '/login/';
                    }, 1500);
                } else if (data.error) {
                    // Show error notification
                    if (typeof window.showNotification === 'function') {
                        window.showNotification('Error', data.error, 'error');
                    } else {
                        alert(data.error);
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                window.location.reload();
            });
        });
    }
    
    // Handle form submission (including Enter key)
    if (passwordForm) {
        passwordForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // Trigger the password change button click
            if (changeBtn) {
                changeBtn.click();
            }
        });
    }
}

// Function to set up event handlers
function setupEventHandlers() {
    // Set up any tab switching behavior
    var tabLinks = document.querySelectorAll('[data-bs-toggle="tab"]');
    tabLinks.forEach(function(tabLink) {
        tabLink.addEventListener('click', function(event) {
            event.preventDefault();
            var targetTab = document.querySelector(this.getAttribute('href'));
            if (targetTab) {
                // Hide all tabs
                document.querySelectorAll('.tab-pane').forEach(function(tab) {
                    tab.classList.remove('active', 'show');
                });
                
                // Show target tab
                targetTab.classList.add('active', 'show');
                
                // Update active state on tab links
                tabLinks.forEach(function(link) {
                    link.classList.remove('active');
                });
                this.classList.add('active');
            }
        });
    });
    
    // Close any alerts after a delay
    var alerts = document.querySelectorAll('.alert:not(.alert-warning)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.display = 'none';
        }, 5000);
    });
}

// Function to close all custom modals
function closeAllModals() {
    // Close standard modals with display:none style
    document.querySelectorAll('[id$="Modal"]').forEach(modal => {
        if (modal.style && modal.style.display === 'block') {
            modal.style.display = 'none';
            
            // If there's a specific close function, try to call it
            const modalId = modal.id;
            const closeFunction = window['close' + modalId.charAt(0).toUpperCase() + modalId.slice(1)];
            if (typeof closeFunction === 'function') {
                closeFunction();
            } else {
                // Reset body overflow as a fallback
                document.body.style.overflow = '';
            }
        }
    });
    
    // Explicitly handle the weak password modal - but only allow force close
    const weakPasswordModal = document.getElementById('weakPasswordModal');
    if (weakPasswordModal && weakPasswordModal.style.display === 'block') {
        // Do not auto-close the weak password modal
        // This will be handled by the specific close function
    }
    
    // Close Bootstrap modals
    const bootstrapModals = document.querySelectorAll('.modal.show');
    bootstrapModals.forEach(modal => {
        if (window.bootstrap && window.bootstrap.Modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        }
    });
}

// Set up direct event handlers without jQuery
function setupDirectPasswordHandlers() {
    // Get references to the new password elements
    var passwordArea = document.getElementById('new_password_area');
    var confirmArea = document.getElementById('confirm_password_area');
    var lengthDisplay = document.getElementById('password-length-display');
    var changeBtn = document.getElementById('password-change-btn');
    var passwordForm = document.getElementById('password-form-div');
    
    if (passwordArea && lengthDisplay) {
        // Focus on password field
        setTimeout(function() {
            passwordArea.focus();
        }, 100);
        
        // Update function that directly reads the password field
        function updateLengthDisplay() {
            var password = passwordArea.value || '';
            // Update display with current length
            lengthDisplay.textContent = 'Current length: ' + password.length + ' characters';
        }
        
        // Add multiple event listeners to catch all input cases
        ['input', 'keyup', 'keydown', 'change', 'paste'].forEach(function(eventType) {
            passwordArea.addEventListener(eventType, updateLengthDisplay);
        });
        
        // Add keydown event for Enter key
        passwordArea.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                // Focus on confirm field if Enter is pressed in password field
                confirmArea.focus();
            }
        });
        
        // Add keydown event for Enter key on confirm field
        confirmArea.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                // Trigger submit button click if Enter is pressed in confirm field
                if (changeBtn) {
                    changeBtn.click();
                }
            }
        });
        
        // Initial update
        updateLengthDisplay();
    }
    
    // Handle form submission (including Enter key)
    if (passwordForm) {
        passwordForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // Trigger the password change button click
            if (changeBtn) {
                changeBtn.click();
            }
        });
    }
    
    if (changeBtn) {
        changeBtn.addEventListener('click', function() {
            // Get the current password from the hidden field (more reliable)
            var currentPassword = document.getElementById('current_password_hidden').value || '123';
            var newPassword = passwordArea.value || '';
            var confirmPassword = confirmArea.value || '';
            
            // Check for empty fields first
            if (!newPassword) {
                alert('New password is required.');
                passwordArea.focus();
                return;
            }
            
            if (!confirmPassword) {
                alert('Please confirm your password.');
                confirmArea.focus();
                return;
            }
            
            // Validate passwords
            if (newPassword.length < 8) {
                alert('Password must be at least 8 characters long! Your password is ' + newPassword.length + ' characters.');
                passwordArea.focus();
                return;
            }
            
            if (newPassword !== confirmPassword) {
                alert('Passwords do not match!');
                confirmArea.focus();
                return;
            }
            
            // Get CSRF token
            var csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value || '';
            
            // Create form data
            var formData = new FormData();
            formData.append('csrfmiddlewaretoken', csrfToken);
            formData.append('current_password', currentPassword);
            formData.append('new_password', newPassword);
            formData.append('confirm_password', confirmPassword);
            
            // Submit form
            fetch('/app/change-password/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(function(data) {
                if (data.success) {
                    // Show success message
                    if (typeof window.showNotification === 'function') {
                        window.showNotification('Password Updated', data.message || 'Your password has been changed successfully. Please login again.', 'success');
                    } else {
                        alert(data.message || 'Password changed successfully. Please login again.');
                    }
                    
                    // Close the modal
                    document.getElementById('weakPasswordModal')?.remove();
                    
                    // Wait a moment for the notification to be visible
                    setTimeout(function() {
                        // Redirect to login page
                        window.location.href = data.redirect || '/login/';
                    }, 1500);
                } else if (data.error) {
                    // Show error notification
                    if (typeof window.showNotification === 'function') {
                        window.showNotification('Error', data.error, 'error');
                    } else {
                        alert(data.error);
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                window.location.reload();
            });
        });
    }
}

// Function to initialize responsive modals
function initResponsiveModals() {
    // Function to update modal styles based on screen size
    function updateModalStyles() {
        const isMobile = window.innerWidth < 768;
        const isSmallMobile = window.innerWidth < 576;
        
        document.querySelectorAll('.modal-dialog').forEach(function(dialog) {
            if (isSmallMobile) {
                dialog.classList.add('modal-fullscreen-sm-down');
                dialog.classList.remove('modal-dialog-centered');
            } else if (isMobile) {
                dialog.classList.remove('modal-fullscreen-sm-down');
                dialog.classList.add('modal-dialog-centered');
            } else {
                dialog.classList.remove('modal-fullscreen-sm-down', 'modal-dialog-centered');
            }
        });
    }
    
    // Initial update
    updateModalStyles();
    
    // Update on resize
    window.addEventListener('resize', debounce(updateModalStyles, 250));
    
    // Update when modal is shown
    document.querySelectorAll('.modal').forEach(function(modal) {
        modal.addEventListener('show.bs.modal', updateModalStyles);
    });
}

// Function to make all tables responsive
function makeAllTablesResponsive() {
    document.querySelectorAll('table:not(.table-responsive)').forEach(function(table) {
        if (!table.parentElement.classList.contains('table-responsive')) {
            const wrapper = document.createElement('div');
            wrapper.classList.add('table-responsive');
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });
}

// Function to handle long content
function handleLongContent() {
    const isMobile = window.innerWidth < 768;
    
    // Handle text truncation
    document.querySelectorAll('[data-truncate-mobile]').forEach(function(element) {
        if (isMobile) {
            const fullText = element.getAttribute('data-full-text') || element.textContent;
            const maxLength = parseInt(element.getAttribute('data-truncate-mobile'), 10) || 50;
            
            if (!element.getAttribute('data-full-text')) {
                element.setAttribute('data-full-text', fullText);
            }
            
            if (fullText.length > maxLength) {
                element.textContent = fullText.substring(0, maxLength) + '...';
            }
        } else {
            // Restore full text on desktop
            if (element.getAttribute('data-full-text')) {
                element.textContent = element.getAttribute('data-full-text');
            }
        }
    });
    
    // Handle long tables
    document.querySelectorAll('.table-responsive').forEach(function(table) {
        if (isMobile) {
            table.style.maxHeight = '400px';
            table.style.overflowY = 'auto';
        } else {
            table.style.maxHeight = '';
            table.style.overflowY = '';
        }
    });
}

// Debounce function to limit the rate at which a function can fire
function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(function() {
            func.apply(context, args);
        }, wait);
    };
}