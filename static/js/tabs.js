// Setup custom tabs
function setupCustomTabs() {
    const tabButtons = document.querySelectorAll(".custom-tab-btn");
    if (tabButtons.length > 0) {
        tabButtons.forEach((button) => {
            button.addEventListener("click", function() {
                // Remove active class from all buttons
                tabButtons.forEach((btn) => btn.classList.remove("active"));

                // Add active class to clicked button
                this.classList.add("active");

                // Hide all content
                document.querySelectorAll(".custom-tab-content").forEach((content) => {
                    content.classList.remove("active");
                });

                // Show target content
                const target = this.getAttribute("data-target");
                document.getElementById(target).classList.add("active");
            });
        });
    }
}

// Setup feedback tabs
function setupFeedbackTabs() {
    const teacherTabBtn = document.getElementById("teacher-tab-btn");
    const instituteTabBtn = document.getElementById("institute-tab-btn");

    if (teacherTabBtn && instituteTabBtn) {
        teacherTabBtn.addEventListener("click", function() {
            switchFeedbackTab("teacher");
        });

        instituteTabBtn.addEventListener("click", function() {
            switchFeedbackTab("institute");
        });
    }
}

// Tab switching function
function switchFeedbackTab(tabId) {
    // Hide all tab contents
    document.querySelectorAll(".tab-pane").forEach((tab) => {
        tab.classList.remove("active");
    });

    // Deactivate all tab buttons
    document.querySelectorAll(".feedback-tab-btn").forEach((btn) => {
        btn.classList.remove("active");
    });

    // Show selected tab content and activate button
    document.getElementById(`${tabId}-tab-content`).classList.add("active");
    document.getElementById(`${tabId}-tab-btn`).classList.add("active");
}

// Make functions globally accessible
window.setupCustomTabs = setupCustomTabs;
window.setupFeedbackTabs = setupFeedbackTabs;
window.switchFeedbackTab = switchFeedbackTab; 