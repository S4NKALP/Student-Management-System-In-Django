// Initialization code for the teacher dashboard

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    try {
        console.log('Initializing teacher dashboard and attendance functions...');

        // Handle hash navigation with priority
        const hash = window.location.hash;
        if (hash) {
            // Remove the # and get the section name
            const sectionId = hash.substring(1);
            console.log('Found hash navigation target:', sectionId);
            
            // Make all sections inactive and hidden first
            document.querySelectorAll('.content-section').forEach(section => {
                section.classList.remove('active');
                section.style.display = 'none';
            });
            
            // Then activate just the target section
            const targetSection = document.getElementById(sectionId);
            if (targetSection) {
                console.log('Activating section from hash:', sectionId);
                targetSection.classList.add('active');
                targetSection.style.display = 'block';
                
                // Also activate the correct nav item
                document.querySelectorAll('.nav-item').forEach(item => {
                    item.classList.remove('active');
                    const navSection = item.getAttribute('data-section');
                    if (navSection === sectionId) {
                        item.classList.add('active');
                    }
                });
                
                // If it's subjects, make sure the subjects nav is active
                if (sectionId === 'subjectsSection') {
                    document.querySelectorAll('.nav-item').forEach(item => {
                        const navSection = item.getAttribute('data-section');
                        if (navSection === 'subjects') {
                            item.classList.add('active');
                        }
                    });
                }
            }
        }

        // Hide attendance form container by default
        const attendanceFormContainer = document.getElementById('attendanceFormContainer');
        if (attendanceFormContainer) {
            attendanceFormContainer.style.display = 'none';
        }
        
        // Set today's date as default for date inputs
        const dateInputs = document.querySelectorAll('input[type="date"]');
        const today = new Date().toISOString().split('T')[0];
        
        dateInputs.forEach(input => {
            // Don't set a default value for the attendance date input
            if (input.id !== 'dateSelect' && !input.value) {
                input.value = today;
                console.log('Set date for input:', input.id);
                // Trigger any change event listeners
                const event = new Event('change');
                input.dispatchEvent(event);
            }
        });

        // Add event listeners for routine selection form
        const routineSelect = document.getElementById('routineSelect');
        const dateSelect = document.getElementById('dateSelect');

        if (routineSelect) {
            // Remove auto-selection of first routine option
            // We want nothing selected by default
            
            routineSelect.addEventListener('change', function() {
                console.log('Routine changed:', this.value);
                loadAttendanceData();
            });
        }

        if (dateSelect) {
            dateSelect.addEventListener('change', function() {
                console.log('Date changed:', this.value);
                loadAttendanceData();
            });
        }

        // Add event listeners for edit buttons
        document.querySelectorAll('.edit-attendance-btn').forEach(button => {
            button.addEventListener('click', function() {
                const routineId = this.getAttribute('data-routine-id');
                const date = this.getAttribute('data-date');
                console.log('Edit button clicked:', { routineId, date });
                editAttendance(routineId, date);
            });
        });
        
        // Add event listeners for today's classes attendance buttons
        document.querySelectorAll('.take-attendance-btn, .attendance-btn, .today-attendance-btn').forEach(button => {
            button.addEventListener('click', function() {
                console.log('Today attendance button clicked');
                const routineId = this.getAttribute('data-routine-id');
                const date = this.getAttribute('data-date') || today;
                
                if (routineId) {
                    console.log('Taking attendance for routine:', routineId, 'date:', date);
                    
                    // If this is a quick attendance button, open the modal
                    if (this.classList.contains('quick-attendance')) {
                        openAttendanceModal(routineId, date);
                    } else {
                        // Otherwise go to manage attendance view
                        editAttendance(routineId, date);
                    }
                } else {
                    console.error('Missing routine ID for attendance button');
                }
            });
        });

        // Load initial data if values are present
        if (routineSelect && dateSelect && routineSelect.value && dateSelect.value) {
            loadAttendanceData();
        }
        
        // Initialize file upload form submission
        const uploadForm = document.getElementById('uploadFileForm');
        if (uploadForm) {
            uploadForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const formData = new FormData(uploadForm);
                const submitBtn = uploadForm.querySelector('button[type="submit"]');
                const responseDiv = document.getElementById('uploadResponse');
                
                // Disable the submit button and show loading state
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Uploading...';
                }
                
                fetch('/app/manage-subject-files/', {
                    method: 'POST',
                    body: formData,
                    credentials: 'same-origin',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (responseDiv) {
                        responseDiv.style.display = 'block';
                        responseDiv.className = data.success ? 'alert alert-success' : 'alert alert-danger';
                        responseDiv.innerHTML = data.message;
                    }
                    
                    if (data.success) {
                        // Reload materials after successful upload
                        setTimeout(() => {
                            // Get the subject ID that was selected
                            const subjectId = document.getElementById('subject_id').value;
                            loadSubjectMaterials(subjectId);
                            closeUploadModal();
                        }, 1500);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    if (responseDiv) {
                        responseDiv.style.display = 'block';
                        responseDiv.className = 'alert alert-danger';
                        responseDiv.innerHTML = 'An error occurred while uploading the file. Please try again.';
                    }
                })
                .finally(() => {
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = '<i class="fas fa-upload me-1"></i> Upload';
                    }
                });
            });
        }
        
        // Initialize delete confirmation button
        const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
        if (confirmDeleteBtn) {
            confirmDeleteBtn.addEventListener('click', function() {
                if (!fileIdToDelete) {
                    closeConfirmationModal();
                    return;
                }
                
                // Disable the button and show loading state
                confirmDeleteBtn.disabled = true;
                confirmDeleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Deleting...';
                
                fetch('/app/delete-subject-file/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify({ file_id: fileIdToDelete })
                })
                .then(response => response.json())
                .then(data => {
                    closeConfirmationModal();
                    
                    if (data.success) {
                        // Store the current subject ID if displayed in the UI
                        const currentSubjectHeading = document.querySelector('#subjectMaterialsContent .card-header h5');
                        let currentSubjectId = null;
                        
                        if (currentSubjectHeading) {
                            // Find the subject ID from the upload button
                            const uploadBtn = currentSubjectHeading.closest('.card-header').querySelector('[data-subject-id]');
                            if (uploadBtn) {
                                currentSubjectId = uploadBtn.getAttribute('data-subject-id');
                            }
                        }
                        
                        // Reload the materials section with the same subject if we had one
                        loadSubjectMaterials(currentSubjectId);
                    } else {
                        alert(data.message || 'Error deleting file.');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    closeConfirmationModal();
                    alert('An error occurred while deleting the file. Please try again.');
                })
                .finally(() => {
                    confirmDeleteBtn.disabled = false;
                    confirmDeleteBtn.innerHTML = '<i class="fas fa-trash me-1"></i> Delete';
                });
            });
        }
    } catch (error) {
        console.error('Error initializing teacher dashboard:', error);
    }
}); 