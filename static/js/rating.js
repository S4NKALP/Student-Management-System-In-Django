// Function to set up star rating
function setupStarRating() {
    console.log("Setting up star rating...");
    
    // Handle display of existing ratings (read-only stars)
    setupExistingRatings();
}

// Function to set up existing ratings (read-only stars)
function setupExistingRatings() {
    // Find all rating divs (not in forms)
    document.querySelectorAll('.rating').forEach(container => {
        if (!container) return;
        
        // Make sure the stars have the right color
        const stars = container.querySelectorAll('i.fas, i.far');
        stars.forEach(star => {
            if (star.classList.contains('fas')) {
                star.style.color = '#FFC107';
            }
        });
    });
}

// Add CSS styles for rating stars
(function() {
    const style = document.createElement('style');
    style.textContent = `
        .rating-star {
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .rating-star.hover,
        .rating-star:hover,
        .rating-star.active,
        .rating-star.selected {
            color: #FFD700 !important;
            transform: scale(1.1);
        }
    `;
    document.head.appendChild(style);
})();

// Global function to select rating stars
function selectRating(star, inputId) {
    console.log('selectRating called with star value:', star.getAttribute('data-value'), 'for input:', inputId);
    
    // Get the value
    const value = parseInt(star.getAttribute('data-value'));
    
    // Find and update the input
    const input = document.getElementById(inputId);
    if (input) {
        input.value = value;
        console.log('Updated input value to:', value);
    } else {
        console.error('Input element not found with ID:', inputId);
    }
    
    // Update the stars
    const container = star.closest('.rating-stars');
    if (container) {
        const stars = container.querySelectorAll('.rating-star');
        stars.forEach(s => {
            const starValue = parseInt(s.getAttribute('data-value'));
            if (starValue <= value) {
                s.classList.remove('far');
                s.classList.add('fas');
                s.classList.add('selected');
            } else {
                s.classList.remove('fas');
                s.classList.add('far');
                s.classList.remove('selected');
            }
        });
    } else {
        console.error('Rating container not found');
    }
    
    // Hide error message if any
    let errorId;
    if (inputId === 'teacher_rating') {
        errorId = 'teacher-rating-error';
    } else if (inputId === 'institute_rating') {
        errorId = 'institute-rating-error';
    } else if (inputId === 'teacher_modal_rating') {
        errorId = 'teacher-modal-rating-error';
    }
    
    if (errorId) {
        const errorElement = document.getElementById(errorId);
        if (errorElement) {
            errorElement.style.display = 'none';
        }
    }
    
    return false;
}

// Initialize rating functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM fully loaded");
    setupStarRating();

    // Add an additional check after a short delay to catch dynamically loaded content
    setTimeout(setupStarRating, 500);
});

// Initialize on document load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Rating.js loaded');
    
    // Apply rating stars to static ratings (read-only)
    const ratingContainers = document.querySelectorAll('.rating');
    console.log('Found', ratingContainers.length, 'static rating containers');
    
    ratingContainers.forEach(container => {
        const stars = container.querySelectorAll('i');
        stars.forEach(star => {
            if (star.classList.contains('fas')) {
                star.style.color = '#FFC107';
            }
        });
    });
    
    // Apply hover effects to rating stars
    const ratingStars = document.querySelectorAll('.rating-star');
    console.log('Found', ratingStars.length, 'interactive rating stars');
    
    ratingStars.forEach(star => {
        star.addEventListener('mouseover', function() {
            // Find all stars in the same container
            const container = this.closest('.rating-stars');
            if (container) {
                const stars = container.querySelectorAll('.rating-star');
                const value = parseInt(this.getAttribute('data-value'));
                
                stars.forEach(s => {
                    const starValue = parseInt(s.getAttribute('data-value'));
                    if (starValue <= value) {
                        s.classList.add('hover');
                    } else {
                        s.classList.remove('hover');
                    }
                });
            }
        });
        
        star.addEventListener('mouseout', function() {
            // Find all stars in the same container
            const container = this.closest('.rating-stars');
            if (container) {
                const stars = container.querySelectorAll('.rating-star');
                stars.forEach(s => {
                    s.classList.remove('hover');
                });
            }
        });
    });
});

// Make function globally available
window.selectRating = selectRating; 