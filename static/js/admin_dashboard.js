// Function to get CSRF token
function getCSRFToken() {
    // Try getting from meta tag
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) {
        return metaTag.getAttribute('content');
    }
    
    // Try getting from form input
    const inputField = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (inputField) {
        return inputField.value;
    }
    
    // Try getting from cookie
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith('csrftoken=')) {
            return decodeURIComponent(cookie.substring('csrftoken='.length));
        }
    }
    
    console.error('CSRF token not found in meta tag, form input, or cookie');
    return null;
}

// Function to update leave requests
function updateLeaveRequests() {
    const csrfToken = getCSRFToken();
    if (!csrfToken) {
        console.error('No CSRF token available. Cannot make request.');
        return;
    }
    
    // Fetch staff leave requests
    fetch('/app/get-staff-leaves/', {
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        const staffLeavesContainer = document.querySelector('#staff-leaves-container');
        if (data.staff_leaves.length === 0) {
            staffLeavesContainer.innerHTML = `
                <div class="text-center">
                    <small class="text-muted">No pending staff leave requests</small>
                </div>
            `;
            return;
        }
        
        let staffLeavesHtml = '';
        data.staff_leaves.forEach(leave => {
            staffLeavesHtml += `
                <div class="d-flex align-items-center mb-3 pb-3 border-bottom">
                    <div class="flex-shrink-0 me-3">
                        <div class="rounded bg-light d-flex align-items-center justify-content-center" style="width: 60px; height: 60px;">
                            <i class="fas fa-calendar-times text-info"></i>
                        </div>
                    </div>
                    <div class="flex-grow-1">
                        <small class="mb-0 d-block fw-medium">${leave.staff_name}</small>
                        <small class="text-muted">From: ${leave.start_date}</small>
                        <small class="text-muted d-block">To: ${leave.end_date}</small>
                        <small class="text-muted d-block">${leave.message}</small>
                        <div class="mt-2">
                            <form method="post" action="/app/approve-staff-leave/${leave.id}/" class="d-inline">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                                <button type="submit" class="btn btn-success btn-sm">
                                    <i class="fas fa-check me-1"></i>Approve
                                </button>
                            </form>
                            <form method="post" action="/app/reject-staff-leave/${leave.id}/" class="d-inline ms-2">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                                <button type="submit" class="btn btn-danger btn-sm">
                                    <i class="fas fa-times me-1"></i>Reject
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            `;
        });
        staffLeavesContainer.innerHTML = staffLeavesHtml;
    });

    // Fetch student leave requests
    fetch('/app/get-student-leaves/', {
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        const studentLeavesContainer = document.querySelector('#student-leaves-container');
        if (data.student_leaves.length === 0) {
            studentLeavesContainer.innerHTML = `
                <div class="text-center">
                    <small class="text-muted">No pending student leave requests</small>
                </div>
            `;
            return;
        }
        
        let studentLeavesHtml = '';
        data.student_leaves.forEach(leave => {
            studentLeavesHtml += `
                <div class="d-flex align-items-center mb-3 pb-3 border-bottom">
                    <div class="flex-shrink-0 me-3">
                        <div class="rounded bg-light d-flex align-items-center justify-content-center" style="width: 60px; height: 60px;">
                            <i class="fas fa-calendar-times text-warning"></i>
                        </div>
                    </div>
                    <div class="flex-grow-1">
                        <small class="mb-0 d-block fw-medium">${leave.student_name}</small>
                        <small class="text-muted">From: ${leave.start_date}</small>
                        <small class="text-muted d-block">To: ${leave.end_date}</small>
                        <small class="text-muted d-block">${leave.message}</small>
                        <div class="mt-2">
                            <form method="post" action="/app/approve-student-leave/${leave.id}/" class="d-inline">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                                <button type="submit" class="btn btn-success btn-sm">
                                    <i class="fas fa-check me-1"></i>Approve
                                </button>
                            </form>
                            <form method="post" action="/app/reject-student-leave/${leave.id}/" class="d-inline ms-2">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                                <button type="submit" class="btn btn-danger btn-sm">
                                    <i class="fas fa-times me-1"></i>Reject
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            `;
        });
        studentLeavesContainer.innerHTML = studentLeavesHtml;
    });
}

// Meeting-related functions
function viewMeetingNotes(meetingId) {
    const modal = document.getElementById('viewNotesModal');
    const errorDiv = document.getElementById('notesError');
    const loadingDiv = document.getElementById('notesLoading');
    const contentDiv = document.getElementById('meetingNotesContent');
    const notesText = document.getElementById('viewMeetingNotesText');
    
    // Reset states
    errorDiv.style.display = 'none';
    loadingDiv.style.display = 'block';
    contentDiv.style.display = 'none';
    notesText.textContent = '';
    
    // Show modal
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
    
    // Add keyboard event listener for Escape key
    document.addEventListener('keydown', handleNotesEscapeKey);

    // Fetch notes
    fetch(`/app/api/meetings/${meetingId}/notes/`, {
        headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new TypeError("Response was not JSON");
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            notesText.textContent = data.notes || 'No notes available';
            loadingDiv.style.display = 'none';
            contentDiv.style.display = 'block';
        } else {
            throw new Error(data.error || 'Failed to fetch notes');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        errorDiv.textContent = error.message;
        errorDiv.style.display = 'block';
        loadingDiv.style.display = 'none';
    });
}

function closeNotesModal() {
    const modal = document.getElementById('viewNotesModal');
    const errorDiv = document.getElementById('notesError');
    const loadingDiv = document.getElementById('notesLoading');
    const contentDiv = document.getElementById('meetingNotesContent');
    
    // Reset states
    errorDiv.style.display = 'none';
    loadingDiv.style.display = 'none';
    contentDiv.style.display = 'none';
    
    // Hide modal
    modal.style.display = 'none';
    document.body.style.overflow = '';
    
    // Remove keyboard event listener
    document.removeEventListener('keydown', handleNotesEscapeKey);
}

function handleNotesEscapeKey(event) {
    if (event.key === 'Escape') {
        closeNotesModal();
    }
}

// Make all meeting-related functions globally available
window.viewMeetingAgenda = function(meetingId) {
    const modal = document.getElementById('viewAgendaModal');
    const errorDiv = document.getElementById('agendaError');
    const loadingDiv = document.getElementById('agendaLoading');
    const contentDiv = document.getElementById('meetingAgendaContent');
    const agendaText = document.getElementById('viewMeetingAgendaText');
    
    // Reset states
    errorDiv.style.display = 'none';
    loadingDiv.style.display = 'block';
    contentDiv.style.display = 'none';
    agendaText.textContent = '';
    
    // Show modal
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
    
    // Add keyboard event listener for Escape key
    document.addEventListener('keydown', handleAgendaEscapeKey);

    // Fetch agenda
    fetch(`/app/api/meetings/${meetingId}/agenda/`, {
        headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Network response was not ok: ${response.status} ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Received agenda data:', data);
        loadingDiv.style.display = 'none';
        
        if (data.success && data.agenda) {
            agendaText.textContent = data.agenda;
            contentDiv.style.display = 'block';
        } else {
            errorDiv.textContent = 'No agenda available for this meeting';
            errorDiv.style.display = 'block';
        }
    })
    .catch(error => {
        console.error('Error fetching agenda:', error);
        loadingDiv.style.display = 'none';
        errorDiv.textContent = error.message || 'Failed to fetch agenda';
        errorDiv.style.display = 'block';
    });
};

window.closeAgendaModal = function() {
    const modal = document.getElementById('viewAgendaModal');
    const errorDiv = document.getElementById('agendaError');
    const loadingDiv = document.getElementById('agendaLoading');
    const contentDiv = document.getElementById('meetingAgendaContent');
    const agendaText = document.getElementById('viewMeetingAgendaText');
    
    // Reset states
    errorDiv.style.display = 'none';
    loadingDiv.style.display = 'none';
    contentDiv.style.display = 'none';
    agendaText.textContent = '';
    
    // Hide modal
    modal.style.display = 'none';
    document.body.style.overflow = '';
    
    // Remove keyboard event listener
    document.removeEventListener('keydown', handleAgendaEscapeKey);
};

window.handleAgendaEscapeKey = function(event) {
    if (event.key === 'Escape') {
        closeAgendaModal();
    }
};

window.viewMeetingNotes = function(meetingId) {
    const modal = document.getElementById('viewNotesModal');
    const errorDiv = document.getElementById('notesError');
    const loadingDiv = document.getElementById('notesLoading');
    const contentDiv = document.getElementById('meetingNotesContent');
    const notesText = document.getElementById('viewMeetingNotesText');
    
    // Reset states
    errorDiv.style.display = 'none';
    loadingDiv.style.display = 'block';
    contentDiv.style.display = 'none';
    notesText.textContent = '';
    
    // Show modal
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
    
    // Add keyboard event listener for Escape key
    document.addEventListener('keydown', handleNotesEscapeKey);

    // Fetch notes
    fetch(`/app/api/meetings/${meetingId}/notes/`, {
        headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new TypeError("Response was not JSON");
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            notesText.textContent = data.notes || 'No notes available';
            loadingDiv.style.display = 'none';
            contentDiv.style.display = 'block';
        } else {
            throw new Error(data.error || 'Failed to fetch notes');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        errorDiv.textContent = error.message;
        errorDiv.style.display = 'block';
        loadingDiv.style.display = 'none';
    });
};

window.closeNotesModal = function() {
    const modal = document.getElementById('viewNotesModal');
    const errorDiv = document.getElementById('notesError');
    const loadingDiv = document.getElementById('notesLoading');
    const contentDiv = document.getElementById('meetingNotesContent');
    
    // Reset states
    errorDiv.style.display = 'none';
    loadingDiv.style.display = 'none';
    contentDiv.style.display = 'none';
    
    // Hide modal
    modal.style.display = 'none';
    document.body.style.overflow = '';
    
    // Remove keyboard event listener
    document.removeEventListener('keydown', handleNotesEscapeKey);
};

window.handleNotesEscapeKey = function(event) {
    if (event.key === 'Escape') {
        closeNotesModal();
    }
};

window.cancelMeeting = function(meetingId) {
    const modal = document.getElementById('cancelMeetingModal');
    const form = document.getElementById('cancelMeetingForm');
    const errorDiv = document.getElementById('cancelError');
    const loadingDiv = document.getElementById('cancelLoading');
    
    // Reset form and error states
    form.reset();
    errorDiv.style.display = 'none';
    loadingDiv.style.display = 'none';
    
    // Set meeting ID
    document.getElementById('cancelMeetingId').value = meetingId;
    
    // Show modal
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
    
    // Add keyboard event listener for Escape key
    document.addEventListener('keydown', handleCancelEscapeKey);
};

window.closeCancelModal = function() {
    const modal = document.getElementById('cancelMeetingModal');
    const form = document.getElementById('cancelMeetingForm');
    const errorDiv = document.getElementById('cancelError');
    const loadingDiv = document.getElementById('cancelLoading');
    
    // Reset form and error states
    form.reset();
    errorDiv.style.display = 'none';
    loadingDiv.style.display = 'none';
    
    // Hide modal
    modal.style.display = 'none';
    document.body.style.overflow = '';
    
    // Remove keyboard event listener
    document.removeEventListener('keydown', handleCancelEscapeKey);
};

window.handleCancelEscapeKey = function(event) {
    if (event.key === 'Escape') {
        closeCancelModal();
    }
};

window.submitCancelForm = function() {
    const form = document.getElementById('cancelMeetingForm');
    const errorDiv = document.getElementById('cancelError');
    const loadingDiv = document.getElementById('cancelLoading');
    const submitBtn = form.querySelector('button[type="button"]');
    const reason = document.getElementById('cancellationReason');
    
    // Validate form
    if (!reason.value.trim()) {
        reason.classList.add('is-invalid');
        return;
    }
    
    // Show loading state
    loadingDiv.style.display = 'block';
    errorDiv.style.display = 'none';
    submitBtn.disabled = true;
    
    const meetingId = document.getElementById('cancelMeetingId').value;
    
    fetch(`/app/api/meetings/${meetingId}/cancel/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({ reason: reason.value })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new TypeError("Response was not JSON");
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            closeCancelModal();
            window.location.reload();
        } else {
            throw new Error(data.error || 'Failed to cancel meeting');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        errorDiv.textContent = error.message;
        errorDiv.style.display = 'block';
    })
    .finally(() => {
        loadingDiv.style.display = 'none';
        submitBtn.disabled = false;
    });
};

window.rescheduleMeeting = function(meetingId) {
    const modal = document.getElementById('rescheduleMeetingModal');
    const form = document.getElementById('rescheduleMeetingForm');
    const errorDiv = document.getElementById('rescheduleError');
    const loadingDiv = document.getElementById('rescheduleLoading');
    
    // Reset form and error states
    form.reset();
    errorDiv.style.display = 'none';
    loadingDiv.style.display = 'none';
    
    // Set meeting ID and minimum date
    document.getElementById('rescheduleMeetingId').value = meetingId;
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('rescheduleDate').min = today;
    
    // Show modal
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
    
    // Add keyboard event listener for Escape key
    document.addEventListener('keydown', handleRescheduleEscapeKey);
};

window.closeRescheduleModal = function() {
    const modal = document.getElementById('rescheduleMeetingModal');
    const form = document.getElementById('rescheduleMeetingForm');
    const errorDiv = document.getElementById('rescheduleError');
    const loadingDiv = document.getElementById('rescheduleLoading');
    
    // Reset form and error states
    form.reset();
    errorDiv.style.display = 'none';
    loadingDiv.style.display = 'none';
    
    // Hide modal
    modal.style.display = 'none';
    document.body.style.overflow = '';
    
    // Remove keyboard event listener
    document.removeEventListener('keydown', handleRescheduleEscapeKey);
};

window.handleRescheduleEscapeKey = function(event) {
    if (event.key === 'Escape') {
        closeRescheduleModal();
    }
};

window.submitRescheduleForm = function() {
    const form = document.getElementById('rescheduleMeetingForm');
    const errorDiv = document.getElementById('rescheduleError');
    const loadingDiv = document.getElementById('rescheduleLoading');
    const submitBtn = form.querySelector('button[type="button"]');
    const date = document.getElementById('rescheduleDate');
    const time = document.getElementById('rescheduleTime');
    
    // Validate form
    let isValid = true;
    if (!date.value) {
        date.classList.add('is-invalid');
        isValid = false;
    }
    if (!time.value) {
        time.classList.add('is-invalid');
        isValid = false;
    }
    if (!isValid) return;
    
    // Show loading state
    loadingDiv.style.display = 'block';
    errorDiv.style.display = 'none';
    submitBtn.disabled = true;
    
    const meetingId = document.getElementById('rescheduleMeetingId').value;
    
    fetch(`/app/api/meetings/${meetingId}/reschedule/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
            meeting_date: date.value,
            meeting_time: time.value
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new TypeError("Response was not JSON");
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            closeRescheduleModal();
            window.location.reload();
        } else {
            throw new Error(data.error || 'Failed to reschedule meeting');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        errorDiv.textContent = error.message;
        errorDiv.style.display = 'block';
    })
    .finally(() => {
        loadingDiv.style.display = 'none';
        submitBtn.disabled = false;
    });
};

// Schedule Meeting Modal Functions
window.openScheduleMeetingModal = function() {
    const modal = document.getElementById('scheduleMeetingModal');
    const form = document.getElementById('scheduleMeetingForm');
    const errorDiv = document.getElementById('scheduleMeetingError');
    const loadingDiv = document.getElementById('scheduleMeetingLoading');
    
    // Reset form and error states
    form.reset();
    errorDiv.style.display = 'none';
    loadingDiv.style.display = 'none';
    
    // Show modal
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
    
    // Set minimum date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('meetingDate').min = today;

    // Add keyboard event listener for Escape key
    document.addEventListener('keydown', handleEscapeKey);
};

window.closeScheduleMeetingModal = function() {
    const modal = document.getElementById('scheduleMeetingModal');
    const form = document.getElementById('scheduleMeetingForm');
    const errorDiv = document.getElementById('scheduleMeetingError');
    const loadingDiv = document.getElementById('scheduleMeetingLoading');
    
    // Reset form and error states
    form.reset();
    errorDiv.style.display = 'none';
    loadingDiv.style.display = 'none';
    
    // Hide modal
    modal.style.display = 'none';
    document.body.style.overflow = '';

    // Remove keyboard event listener
    document.removeEventListener('keydown', handleEscapeKey);
};

// Function to handle Escape key press
window.handleEscapeKey = function(event) {
    if (event.key === 'Escape') {
        closeScheduleMeetingModal();
    }
};

// Toggle meeting link field based on online meeting checkbox
document.addEventListener('DOMContentLoaded', function() {
    const isOnlineCheckbox = document.getElementById('isOnline');
    if (isOnlineCheckbox) {
        isOnlineCheckbox.addEventListener('change', function() {
            const linkContainer = document.getElementById('meetingLinkContainer');
            const linkInput = document.getElementById('meetingLink');
            
            if (this.checked) {
                linkContainer.style.display = 'block';
                linkInput.required = true;
            } else {
                linkContainer.style.display = 'none';
                linkInput.required = false;
            }
        });
    }

    // Initialize all tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize all popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Update leave requests every 30 seconds
    setInterval(updateLeaveRequests, 30000);

    // Initial update
    updateLeaveRequests();
});

// Function to validate form
window.validateMeetingForm = function() {
    const form = document.getElementById('scheduleMeetingForm');
    const date = document.getElementById('meetingDate');
    const time = document.getElementById('meetingTime');
    const duration = document.getElementById('meetingDuration');
    const isOnline = document.getElementById('isOnline');
    const link = document.getElementById('meetingLink');
    
    let isValid = true;
    
    // Reset validation states
    form.classList.remove('was-validated');
    
    // Validate date
    if (!date.value) {
        date.classList.add('is-invalid');
        isValid = false;
    } else {
        date.classList.remove('is-invalid');
    }
    
    // Validate time
    if (!time.value) {
        time.classList.add('is-invalid');
        isValid = false;
    } else {
        time.classList.remove('is-invalid');
    }
    
    // Validate duration
    if (!duration.value || duration.value < 15 || duration.value > 120) {
        duration.classList.add('is-invalid');
        isValid = false;
    } else {
        duration.classList.remove('is-invalid');
    }
    
    // Validate meeting link if online meeting
    if (isOnline.checked && !link.value) {
        link.classList.add('is-invalid');
        isValid = false;
    } else {
        link.classList.remove('is-invalid');
    }
    
    return isValid;
};

// Function to submit the meeting form
window.submitMeetingForm = function() {
    if (!validateMeetingForm()) {
        return;
    }
    
    const form = document.getElementById('scheduleMeetingForm');
    const errorDiv = document.getElementById('scheduleMeetingError');
    const loadingDiv = document.getElementById('scheduleMeetingLoading');
    const submitBtn = form.querySelector('button[type="button"]');
    
    // Show loading state
    loadingDiv.style.display = 'block';
    errorDiv.style.display = 'none';
    submitBtn.disabled = true;
    
    const formData = new FormData(form);
    const data = {
        meeting_date: formData.get('meeting_date'),
        meeting_time: formData.get('meeting_time'),
        duration: parseInt(formData.get('duration')),
        is_online: document.getElementById('isOnline').checked,
        meeting_link: formData.get('meeting_link'),
        agenda: document.getElementById('scheduleMeetingAgenda').value
    };

    fetch('/app/api/meetings/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Failed to schedule meeting');
            });
        }
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new TypeError("Response was not JSON");
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            closeScheduleMeetingModal();
            // Show success message
            const successDiv = document.createElement('div');
            successDiv.className = 'alert alert-success alert-dismissible fade show';
            successDiv.innerHTML = `
                <strong>Success!</strong> Meeting scheduled successfully.
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            document.querySelector('.content-card').insertAdjacentElement('afterbegin', successDiv);
            // Reload after a short delay
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            throw new Error(data.error || 'Failed to schedule meeting');
        }
    })
    .catch(error => {
        console.error('Error scheduling meeting:', error);
        errorDiv.textContent = error.message;
        errorDiv.style.display = 'block';
    })
    .finally(() => {
        loadingDiv.style.display = 'none';
        submitBtn.disabled = false;
    });
};

window.completeMeeting = function(meetingId) {
    const modal = document.getElementById('completeMeetingModal');
    const form = document.getElementById('completeMeetingForm');
    const errorDiv = document.getElementById('completeError');
    const loadingDiv = document.getElementById('completeLoading');
    
    // Reset form and error states
    form.reset();
    errorDiv.style.display = 'none';
    loadingDiv.style.display = 'none';
    
    // Set meeting ID
    document.getElementById('completeMeetingId').value = meetingId;
    
    // Show modal
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
    
    // Add keyboard event listener for Escape key
    document.addEventListener('keydown', handleCompleteEscapeKey);
};

window.closeCompleteModal = function() {
    const modal = document.getElementById('completeMeetingModal');
    const form = document.getElementById('completeMeetingForm');
    const errorDiv = document.getElementById('completeError');
    const loadingDiv = document.getElementById('completeLoading');
    
    // Reset form and error states
    form.reset();
    errorDiv.style.display = 'none';
    loadingDiv.style.display = 'none';
    
    // Hide modal
    modal.style.display = 'none';
    document.body.style.overflow = '';
    
    // Remove keyboard event listener
    document.removeEventListener('keydown', handleCompleteEscapeKey);
};

window.handleCompleteEscapeKey = function(event) {
    if (event.key === 'Escape') {
        closeCompleteModal();
    }
};

window.viewCancellationReason = function(meetingId) {
    const modal = document.getElementById('viewReasonModal');
    const errorDiv = document.getElementById('reasonError');
    const loadingDiv = document.getElementById('reasonLoading');
    const contentDiv = document.getElementById('meetingReasonContent');
    const reasonText = document.getElementById('viewMeetingReasonText');
    
    // Reset states
    errorDiv.style.display = 'none';
    loadingDiv.style.display = 'block';
    contentDiv.style.display = 'none';
    reasonText.textContent = '';
    
    // Show modal
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
    
    // Add keyboard event listener for Escape key
    document.addEventListener('keydown', handleReasonEscapeKey);

    // Fetch cancellation reason
    fetch(`/app/api/meetings/${meetingId}/cancellation-reason/`, {
        headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success && data.reason) {
            reasonText.textContent = data.reason;
            loadingDiv.style.display = 'none';
            contentDiv.style.display = 'block';
        } else {
            throw new Error(data.error || 'No cancellation reason available');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        errorDiv.textContent = error.message;
        errorDiv.style.display = 'block';
        loadingDiv.style.display = 'none';
    });
};

window.closeReasonModal = function() {
    const modal = document.getElementById('viewReasonModal');
    const errorDiv = document.getElementById('reasonError');
    const loadingDiv = document.getElementById('reasonLoading');
    const contentDiv = document.getElementById('meetingReasonContent');
    const reasonText = document.getElementById('viewMeetingReasonText');
    
    // Reset states
    errorDiv.style.display = 'none';
    loadingDiv.style.display = 'none';
    contentDiv.style.display = 'none';
    reasonText.textContent = '';
    
    // Hide modal
    modal.style.display = 'none';
    document.body.style.overflow = '';
    
    // Remove keyboard event listener
    document.removeEventListener('keydown', handleReasonEscapeKey);
};

window.handleReasonEscapeKey = function(event) {
    if (event.key === 'Escape') {
        closeReasonModal();
    }
};

// Notice Modal Functions
window.openAddNoticeModal = function() {
    document.getElementById('addNoticeModal').style.display = 'block';
    document.addEventListener('keydown', handleNoticeEscapeKey);
}

window.closeAddNoticeModal = function() {
    document.getElementById('addNoticeModal').style.display = 'none';
    document.removeEventListener('keydown', handleNoticeEscapeKey);
    // Reset form
    document.getElementById('addNoticeForm').reset();
    // Hide error and loading states
    document.getElementById('addNoticeError').style.display = 'none';
    document.getElementById('addNoticeLoading').style.display = 'none';
}

window.handleNoticeEscapeKey = function(event) {
    if (event.key === 'Escape') {
        closeAddNoticeModal();
    }
}

window.submitNoticeForm = function() {
    const form = document.getElementById('addNoticeForm');
    const formData = new FormData(form);
    
    // Show loading state
    document.getElementById('addNoticeLoading').style.display = 'block';
    document.getElementById('addNoticeError').style.display = 'none';
    
    fetch('/app/add-notice/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Close modal and refresh page to show new notice
            closeAddNoticeModal();
            window.location.reload();
        } else {
            // Show error message
            document.getElementById('addNoticeError').textContent = data.error || 'Failed to add notice';
            document.getElementById('addNoticeError').style.display = 'block';
        }
    })
    .catch(error => {
        document.getElementById('addNoticeError').textContent = 'An error occurred while adding the notice';
        document.getElementById('addNoticeError').style.display = 'block';
    })
    .finally(() => {
        document.getElementById('addNoticeLoading').style.display = 'none';
    });
} 