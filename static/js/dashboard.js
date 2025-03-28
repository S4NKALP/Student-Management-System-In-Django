document.addEventListener('DOMContentLoaded', function() {
  console.log("Dashboard script loaded");
  
  // Set default date to today for leave requests
  const dateInput = document.getElementById('customLeaveDate');
  if (dateInput) {
    const today = new Date();
    const year = today.getFullYear();
    let month = today.getMonth() + 1;
    let day = today.getDate();
    
    month = month < 10 ? '0' + month : month;
    day = day < 10 ? '0' + day : day;
    
    dateInput.min = `${year}-${month}-${day}`;
    dateInput.value = `${year}-${month}-${day}`;
  }

  // Close modals with Escape key
  document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
      // Check each modal and close if visible
      const modalIds = [
        { id: 'customLeaveModal', closeFn: closeLeaveModal },
        { id: 'profileModal', closeFn: closeProfileModal },
        { id: 'passwordModal', closeFn: closePasswordModal },
        { id: 'feedbackModal', closeFn: closeFeedbackModal },
        { id: 'pdfViewerModal', closeFn: closePdfViewerModal },
        { id: 'subjectFilesModal', closeFn: closeSubjectFilesModal }
      ];
      
      modalIds.forEach(modal => {
        const modalElement = document.getElementById(modal.id);
        if (modalElement && modalElement.style.display === 'block') {
          modal.closeFn();
        }
      });
    }
  });

  // Navigation
  const navItems = document.querySelectorAll('.nav-item');
  const contentSections = document.querySelectorAll('.content-section');

  // Function to scroll to section with smooth animation
  function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
      const offset = 20; // Offset from top
      const sectionPosition = section.getBoundingClientRect().top + window.pageYOffset - offset;
      
      window.scrollTo({
        top: sectionPosition,
        behavior: 'smooth'
      });
    }
  }

  // Function to update active state
  function updateActiveState(clickedItem) {
    // Remove active class from all nav items
    navItems.forEach(nav => {
      nav.classList.remove('active');
      nav.style.transform = 'scale(1)';
    });

    // Add active class to clicked item
    clickedItem.classList.add('active');
    clickedItem.style.transform = 'scale(1.1)';

    // Remove active class from all sections
    contentSections.forEach(section => {
      section.classList.remove('active');
      section.style.opacity = '0';
      section.style.transform = 'translateY(20px)';
    });

    // Add active class to target section
    const sectionId = clickedItem.dataset.section + 'Section';
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
      targetSection.classList.add('active');
      targetSection.style.opacity = '1';
      targetSection.style.transform = 'translateY(0)';
    }
  }

  // Add click event listeners to nav items
  navItems.forEach(item => {
    item.addEventListener('click', function(e) {
      e.preventDefault();
      const sectionId = this.dataset.section + 'Section';
      
      // Update active state
      updateActiveState(this);
      
      // Scroll to section
      scrollToSection(sectionId);
    });
  });

  // Add scroll event listener to update active state based on scroll position
  let scrollTimeout;
  window.addEventListener('scroll', function() {
    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(function() {
      const scrollPosition = window.scrollY + 100; // Offset for better detection
      
      contentSections.forEach(section => {
        const sectionTop = section.offsetTop - 100;
        const sectionBottom = sectionTop + section.offsetHeight;
        
        if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
          const sectionId = section.id;
          const navItem = document.querySelector(`.nav-item[data-section="${sectionId.replace('Section', '')}"]`);
          if (navItem) {
            updateActiveState(navItem);
          }
        }
      });
    }, 100);
  });

  // Add touch feedback
  navItems.forEach(item => {
    item.addEventListener('touchstart', function() {
      this.style.transform = 'scale(0.95)';
    });

    item.addEventListener('touchend', function() {
      this.style.transform = this.classList.contains('active') ? 'scale(1.1)' : 'scale(1)';
    });
  });

  // Initialize first section as active
  const firstNavItem = navItems[0];
  if (firstNavItem) {
    updateActiveState(firstNavItem);
  }
  
  // Initialize rating functionality
  setupStarRating();
  
  // Set up subject files buttons
  document.querySelectorAll('.view-subject-files').forEach(button => {
    button.addEventListener('click', function() {
      const subjectId = this.getAttribute('data-subject-id');
      viewSubjectFiles(subjectId);
    });
  });
  
  // Handle image loading errors
  document.querySelectorAll('img[src*="student.image.url"]').forEach(img => {
    img.addEventListener('error', function() {
      this.onerror = null;
      this.src = '/static/img/user.png';
    });
  });
  
  // Handle feedback form tabs
  setupFeedbackTabs();
  
  // Initialize Bootstrap tooltip and popover components
  initializeBootstrapComponents();

  // Setup custom tabs
  setupCustomTabs();
  
  // Add form validation for rating form
  setupRatingFormValidation();
});

// Modal Functions
function openLeaveModal() {
  document.getElementById('customLeaveModal').style.display = 'block';
  document.body.style.overflow = 'hidden';
}

function closeLeaveModal() {
  document.getElementById('customLeaveModal').style.display = 'none';
  document.body.style.overflow = '';
}

function openProfileModal() {
  document.getElementById('profileModal').style.display = 'block';
  document.body.style.overflow = 'hidden';
}

function closeProfileModal() {
  document.getElementById('profileModal').style.display = 'none';
  document.body.style.overflow = '';
}

function openPasswordModal() {
  document.getElementById('passwordModal').style.display = 'block';
  document.body.style.overflow = 'hidden';
}

function closePasswordModal() {
  document.getElementById('passwordModal').style.display = 'none';
  document.body.style.overflow = '';
}

function openFeedbackModal() {
  document.getElementById('feedbackModal').style.display = 'block';
  document.body.style.overflow = 'hidden';
}

function closeFeedbackModal() {
  document.getElementById('feedbackModal').style.display = 'none';
  document.body.style.overflow = '';
}

function openPdfViewerModal(url) {
  document.getElementById('pdfViewer').src = url;
  document.getElementById('pdfViewerModal').style.display = 'block';
  document.body.style.overflow = 'hidden';
}

function closePdfViewerModal() {
  document.getElementById('pdfViewerModal').style.display = 'none';
  document.body.style.overflow = '';
}

function openSubjectFilesModal(subjectId) {
  // Use the viewSubjectFiles function which fetches the files from the server
  viewSubjectFiles(subjectId);
}

function closeSubjectFilesModal() {
  document.getElementById('subjectFilesModal').style.display = 'none';
  document.body.style.overflow = '';
}

// Setup custom tabs
function setupCustomTabs() {
  const tabButtons = document.querySelectorAll('.custom-tab-btn');
  if (tabButtons.length > 0) {
    tabButtons.forEach(button => {
      button.addEventListener('click', function() {
        // Remove active class from all buttons
        tabButtons.forEach(btn => btn.classList.remove('active'));
        
        // Add active class to clicked button
        this.classList.add('active');
        
        // Hide all content
        document.querySelectorAll('.custom-tab-content').forEach(content => {
          content.classList.remove('active');
        });
        
        // Show target content
        const target = this.getAttribute('data-target');
        document.getElementById(target).classList.add('active');
      });
    });
  }
}

// Setup feedback form validation
function setupRatingFormValidation() {
  const ratingForm = document.querySelector('.feedback-form');
  const ratingInput = document.getElementById('selected_rating');
  const ratingError = document.getElementById('rating-error');
  
  if (ratingForm && ratingInput && ratingError) {
    // Add form validation before submission
    ratingForm.addEventListener('submit', function(e) {
      // Check if rating is selected
      if (!ratingInput.value) {
        e.preventDefault(); // Stop form submission
        if (ratingError) {
          ratingError.style.display = 'block';
          ratingError.scrollIntoView({ behavior: 'smooth' });
        }
        return false;
      }
      return true;
    });
  }
}

// Implementation for subject files
function viewSubjectFiles(subjectId) {
  // Show loading state
  const filesList = document.getElementById('subjectFilesList');
  if (!filesList) return;
  
  filesList.innerHTML = `
      <div class="text-center py-4">
          <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2 text-muted">Loading syllabus...</p>
      </div>
  `;
  
  // Show modal
  document.getElementById('subjectFilesModal').style.display = 'block';
  document.body.style.overflow = 'hidden';
  
  // Fetch syllabus
  fetch(`/app/subject/${subjectId}/files/`)
      .then(response => {
          if (!response.ok) {
              throw new Error('Network response was not ok');
          }
          return response.json();
      })
      .then(data => {
          if (data.success) {
              if (!data.files || data.files.length === 0) {
                  filesList.innerHTML = `
                      <div class="text-center py-4">
                          <i class="fas fa-file-pdf fa-2x text-muted mb-3"></i>
                          <p class="text-muted mb-0">No syllabus available for this subject</p>
                      </div>
                  `;
              } else {
                  let html = '';
                  data.files.forEach(file => {
                      html += `
                          <div class="list-group-item">
                              <div class="d-flex w-100 justify-content-between align-items-center">
                                  <div>
                                      <h6 class="mb-1">
                                          <i class="fas fa-file-pdf text-danger me-2"></i>
                                          ${file.title}
                                      </h6>
                                      <p class="mb-1 small text-muted">${file.description || 'No description'}</p>
                                  </div>
                                  <div class="text-end">
                                      ${file.file_url ? `
                                          <a href="${file.file_url}" class="btn btn-sm btn-primary" download>
                                              <i class="fas fa-download"></i> Download
                                          </a>
                                      ` : `
                                          <span class="text-danger">
                                              <i class="fas fa-exclamation-circle"></i> File not available
                                          </span>
                                      `}
                                  </div>
                              </div>
                          </div>
                      `;
                  });
                  filesList.innerHTML = html;
              }
          } else {
              throw new Error(data.message || 'Failed to load syllabus');
          }
      })
      .catch(error => {
          console.error('Error:', error);
          filesList.innerHTML = `
              <div class="text-center py-4">
                  <i class="fas fa-exclamation-circle fa-2x text-danger mb-3"></i>
                  <p class="text-danger mb-0">Unable to load syllabus. Please try again later.</p>
                  <small class="text-muted">${error.message}</small>
              </div>
          `;
      });
}

// Setup feedback tabs
function setupFeedbackTabs() {
  const teacherTabBtn = document.getElementById('teacher-tab-btn');
  const instituteTabBtn = document.getElementById('institute-tab-btn');
  
  if (teacherTabBtn && instituteTabBtn) {
    teacherTabBtn.addEventListener('click', function() {
      switchFeedbackTab('teacher');
    });
    
    instituteTabBtn.addEventListener('click', function() {
      switchFeedbackTab('institute');
    });
  }
}

// Tab switching function
function switchFeedbackTab(tabId) {
  // Hide all tab contents
  document.querySelectorAll('.tab-pane').forEach(tab => {
    tab.classList.remove('active');
  });
  
  // Deactivate all tab buttons
  document.querySelectorAll('.feedback-tab-btn').forEach(btn => {
    btn.classList.remove('active');
  });
  
  // Show selected tab content and activate button
  document.getElementById(`${tabId}-tab-content`).classList.add('active');
  document.getElementById(`${tabId}-tab-btn`).classList.add('active');
}

// Initialize Bootstrap components
function initializeBootstrapComponents() {
  // Initialize tooltips if available
  if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
    });
  }
  
  // Initialize popovers if available
  if (typeof bootstrap !== 'undefined' && bootstrap.Popover) {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
      return new bootstrap.Popover(popoverTriggerEl);
    });
  }
}

// Function to show notification toast
function showNotification(title, message, type = 'success') {
  const toast = document.getElementById('notificationToast');
  if (!toast) return;
  
  const toastTitle = document.getElementById('toastTitle');
  const toastMessage = document.getElementById('toastMessage');
  
  toastTitle.innerText = title;
  toastMessage.innerText = message;
  
  // Set toast color based on type
  toast.className = 'toast';
  if (type === 'success') {
    toast.classList.add('bg-success', 'text-white');
  } else if (type === 'error') {
    toast.classList.add('bg-danger', 'text-white');
  } else if (type === 'warning') {
    toast.classList.add('bg-warning');
  } else if (type === 'info') {
    toast.classList.add('bg-info', 'text-white');
  }
  
  const bsToast = new bootstrap.Toast(toast);
  bsToast.show();
}

// Function to set up star rating
function setupStarRating() {
  // Teacher feedback
  setupStarRatingComponent('teacher-rating', 'teacherStar');
  // Institute feedback
  setupStarRatingComponent('institute-rating', 'instituteStar');
  // Generic rating stars
  setupGenericRatingStars();
}

function setupStarRatingComponent(containerId, inputPrefix) {
  const container = document.getElementById(containerId);
  if (!container) return;
  
  const stars = container.querySelectorAll('.form-check-label');
  const inputs = Array.from(container.querySelectorAll('input[type="radio"]'));
  
  stars.forEach((star, index) => {
    // Click event
    star.addEventListener('click', function() {
      // Update visual state
      updateStars(stars, index);
      
      // Update form input
      inputs[index].checked = true;
    });
    
    // Hover effects
    star.addEventListener('mouseenter', function() {
      highlightStars(stars, index);
    });
    
    container.addEventListener('mouseleave', function() {
      resetStars(stars, inputs);
    });
  });
}

function setupGenericRatingStars() {
  const stars = document.querySelectorAll('.rating-star');
  const ratingInput = document.getElementById('selected_rating');
  const ratingError = document.getElementById('rating-error');
  
  if (stars.length > 0 && ratingInput) {
    stars.forEach(star => {
      // Click event
      star.addEventListener('click', function() {
        const value = parseInt(this.getAttribute('data-value'));
        ratingInput.value = value;
        
        // Update the stars
        stars.forEach((s, index) => {
          if (index < value) {
            s.className = 'fas fa-star fs-4 text-warning rating-star';
          } else {
            s.className = 'far fa-star fs-4 text-warning rating-star';
          }
        });
        
        // Hide error message if displayed
        if (ratingError) ratingError.style.display = 'none';
      });
      
      // Hover events
      star.addEventListener('mouseenter', function() {
        const value = parseInt(this.getAttribute('data-value'));
        
        stars.forEach((s, index) => {
          if (index < value) {
            s.className = 'fas fa-star fs-4 text-warning rating-star';
          }
        });
      });
      
      star.addEventListener('mouseleave', function() {
        const selectedValue = parseInt(ratingInput.value) || 0;
        
        stars.forEach((s, index) => {
          if (index < selectedValue) {
            s.className = 'fas fa-star fs-4 text-warning rating-star';
          } else {
            s.className = 'far fa-star fs-4 text-warning rating-star';
          }
        });
      });
    });
  }
}

function updateStars(stars, selectedIndex) {
  stars.forEach((star, i) => {
    const starIcon = star.querySelector('i');
    if (i <= selectedIndex) {
      starIcon.className = 'fas fa-star fs-4';
    } else {
      starIcon.className = 'far fa-star fs-4';
    }
  });
}

function highlightStars(stars, hoverIndex) {
  stars.forEach((star, i) => {
    const starIcon = star.querySelector('i');
    if (i <= hoverIndex) {
      starIcon.className = 'fas fa-star fs-4';
    }
  });
}

function resetStars(stars, inputs) {
  const selectedIndex = inputs.findIndex(input => input.checked);
  stars.forEach((star, i) => {
    const starIcon = star.querySelector('i');
    if (selectedIndex >= 0 && i <= selectedIndex) {
      starIcon.className = 'fas fa-star fs-4';
    } else {
      starIcon.className = 'far fa-star fs-4';
    }
  });
} 