// Setup feedback form validation
function setupRatingFormValidation() {
    const ratingForm = document.querySelector(".feedback-form");
    const ratingInput = document.getElementById("selected_rating");
    const ratingError = document.getElementById("rating-error");

    if (ratingForm && ratingInput && ratingError) {
        // Add form validation before submission
        ratingForm.addEventListener("submit", function(e) {
            // Check if rating is selected
            if (!ratingInput.value) {
                e.preventDefault(); // Stop form submission
                if (ratingError) {
                    ratingError.style.display = "block";
                    ratingError.scrollIntoView({ behavior: "smooth" });
                }
                return false;
            }
            return true;
        });
    }
}

// Make function globally accessible
window.setupRatingFormValidation = setupRatingFormValidation; 