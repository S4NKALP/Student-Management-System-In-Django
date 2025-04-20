import { showToast } from '../utils/notifications.js';

// Meeting status badge helper
function getStatusBadgeClass(status) {
    switch (status) {
        case 'scheduled':
            return 'bg-primary';
        case 'completed':
            return 'bg-success';
        case 'cancelled':
            return 'bg-danger';
        case 'rescheduled':
            return 'bg-warning';
        default:
            return 'bg-secondary';
    }
}

// Meeting Modal Functions
function openAddMeetingModal() {
    document.getElementById('addMeetingModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeAddMeetingModal() {
    document.getElementById('addMeetingModal').style.display = 'none';
    document.body.style.overflow = '';
    document.getElementById('addMeetingForm').reset();
}

function openEditMeetingModal(meetingId) {
    fetch(`/app/api/hod/meetings/${meetingId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('editMeetingId').value = meetingId;
            document.getElementById('editMeetingDate').value = data.meeting_date;
            document.getElementById('editMeetingTime').value = data.meeting_time;
            document.getElementById('editDuration').value = data.duration;
            document.getElementById('editAgenda').value = data.agenda || '';
            document.getElementById('editIsOnline').checked = data.is_online;
            document.getElementById('editMeetingLink').value = data.meeting_link || '';
            document.getElementById('editNotes').value = data.notes || '';
            
            if (data.is_online) {
                document.getElementById('editMeetingLinkContainer').style.display = 'block';
            } else {
                document.getElementById('editMeetingLinkContainer').style.display = 'none';
            }
            
            // Show modal using direct style manipulation
            document.getElementById('editMeetingModal').style.display = 'block';
            document.body.style.overflow = 'hidden';
        })
        .catch(error => {
            console.error('Error fetching meeting details:', error);
            if (typeof window.showMessageModal === 'function') {
                window.showMessageModal('Error', 'Failed to load meeting details');
            } else if (typeof showToast === 'function') {
                showToast('error', 'Failed to load meeting details');
            } else {
                alert('Failed to load meeting details');
            }
        });
}

function closeEditMeetingModal() {
    document.getElementById('editMeetingModal').style.display = 'none';
    document.body.style.overflow = '';
    document.getElementById('editMeetingForm').reset();
}

function openCancelMeetingModal(meetingId) {
    document.getElementById('cancelMeetingId').value = meetingId;
    document.getElementById('cancellationReason').value = '';
    document.getElementById('cancelMeetingModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeCancelMeetingModal() {
    document.getElementById('cancelMeetingModal').style.display = 'none';
    document.body.style.overflow = '';
    document.getElementById('cancelMeetingForm').reset();
}

function viewMeetingDetails(meetingId) {
    fetch(`/app/api/hod/meetings/${meetingId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('viewMeetingDate').textContent = new Date(data.meeting_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
            document.getElementById('viewMeetingTime').textContent = new Date('1970-01-01T' + data.meeting_time).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
            document.getElementById('viewMeetingDuration').textContent = `${data.duration} minutes`;
            document.getElementById('viewMeetingStatus').innerHTML = `<span class="badge ${getStatusBadgeClass(data.status)}">${data.status_display}</span>`;
            document.getElementById('viewMeetingAgenda').textContent = data.agenda || 'No agenda available';
            document.getElementById('viewMeetingNotes').textContent = data.notes || 'No notes available';
            document.getElementById('viewMeetingType').textContent = data.is_online ? 'Online Meeting' : 'In-Person Meeting';
            
            if (data.is_online && data.meeting_link) {
                document.getElementById('viewMeetingLinkContainer').style.display = 'block';
                document.getElementById('viewMeetingLink').innerHTML = `<a href="${data.meeting_link}" target="_blank">${data.meeting_link}</a>`;
            } else {
                document.getElementById('viewMeetingLinkContainer').style.display = 'none';
            }
            
            // Handle cancellation reason
            const cancellationContainer = document.getElementById('viewCancellationReasonContainer');
            const cancellationReason = document.getElementById('viewCancellationReason');
            if (data.status === 'cancelled' && data.cancellation_reason) {
                cancellationContainer.style.display = 'block';
                cancellationReason.textContent = data.cancellation_reason;
            } else {
                cancellationContainer.style.display = 'none';
            }
            
            // Set up edit button
            const editBtn = document.getElementById('editMeetingBtn');
            if (editBtn) {
                editBtn.onclick = () => {
                    closeViewMeetingModal();
                    openEditMeetingModal(meetingId);
                };
            }
            
            // Show modal using direct style manipulation
            const modal = document.getElementById('viewMeetingModal');
            if (modal) {
                modal.style.display = 'block';
                document.body.style.overflow = 'hidden';
            } else {
                console.error('Modal element not found!');
                alert('Error: Modal element not found in the page.');
            }
        })
        .catch(error => {
            console.error('Error fetching meeting details:', error);
            if (typeof window.showMessageModal === 'function') {
                window.showMessageModal('Error', 'Failed to load meeting details');
            } else if (typeof showToast === 'function') {
                showToast('error', 'Failed to load meeting details');
            } else {
                alert('Failed to load meeting details');
            }
        });
}

function closeViewMeetingModal() {
    document.getElementById('viewMeetingModal').style.display = 'none';
    document.body.style.overflow = '';
}

function submitAddMeetingForm() {
    const form = document.getElementById('addMeetingForm');
    const formData = new FormData(form);
    
    // IMPORTANT: Ensure meeting_link is always sent and not null
    if (!formData.has('meeting_link') || formData.get('meeting_link') === null) {
        formData.set('meeting_link', '');
    }
    
    fetch('/app/api/hod/meetings/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok: ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        closeAddMeetingModal();
        if (typeof window.showMessageModal === 'function') {
            window.showMessageModal('Success', 'Meeting scheduled successfully');
        } else if (typeof showToast === 'function') {
            showToast('success', 'Meeting scheduled successfully');
        } else {
            alert('Meeting scheduled successfully');
        }
        setTimeout(() => {
            location.reload();
        }, 1500);
    })
    .catch(error => {
        console.error('Error scheduling meeting:', error);
        if (typeof window.showMessageModal === 'function') {
            window.showMessageModal('Error', 'Failed to schedule meeting. Please try again.');
        } else if (typeof showToast === 'function') {
            showToast('error', 'Failed to schedule meeting. Please try again.');
        } else {
            alert('Failed to schedule meeting. Please try again.');
        }
    });
}

function submitEditMeetingForm() {
    const form = document.getElementById('editMeetingForm');
    const formData = new FormData(form);
    const meetingId = document.getElementById('editMeetingId').value;
    
    // Update is_online to be a string
    formData.set('is_online', document.getElementById('editIsOnline').checked ? 'true' : 'false');
    
    // IMPORTANT: Always include meeting_link (empty string if not online) to satisfy NOT NULL constraint
    if (!formData.has('meeting_link') || formData.get('meeting_link') === null) {
        formData.set('meeting_link', '');
    }
    
    // Ensure notes field is included
    if (document.getElementById('editNotes')) {
        formData.set('notes', document.getElementById('editNotes').value || '');
    }
    
    console.log("Submitting edit meeting form for meeting ID:", meetingId);
    
    fetch(`/app/api/hod/meetings/${meetingId}/edit/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => {
                console.error("Server response:", text);
                throw new Error('Server error: ' + response.status);
            });
        }
        return response.json();
    })
    .then(data => {
        // Close modal using direct style manipulation (not Bootstrap)
        document.getElementById('editMeetingModal').style.display = 'none';
        document.body.style.overflow = '';
        document.getElementById('editMeetingForm').reset();
        
        // Show success message
        if (typeof window.showMessageModal === 'function') {
            window.showMessageModal('Success', 'Meeting updated successfully');
        } else if (typeof showToast === 'function') {
            showToast('success', 'Meeting updated successfully');
        } else {
            alert('Meeting updated successfully');
        }
        
        // Reload the page after a short delay
        setTimeout(() => {
            location.reload();
        }, 1500);
    })
    .catch(error => {
        console.error('Error updating meeting:', error);
        if (typeof window.showMessageModal === 'function') {
            window.showMessageModal('Error', 'Failed to update meeting. Please try again.');
        } else if (typeof showToast === 'function') {
            showToast('error', 'Failed to update meeting. Please try again.');
        } else {
            alert('Failed to update meeting. Please try again.');
        }
    });
}

function submitCancelMeetingForm() {
    const form = document.getElementById('cancelMeetingForm');
    const formData = new FormData(form);
    const meetingId = document.getElementById('cancelMeetingId').value;
    
    fetch(`/app/api/hod/meetings/${meetingId}/cancel/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok: ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        closeCancelMeetingModal();
        if (typeof window.showMessageModal === 'function') {
            window.showMessageModal('Success', 'Meeting cancelled successfully');
        } else if (typeof showToast === 'function') {
            showToast('success', 'Meeting cancelled successfully');
        } else {
            alert('Meeting cancelled successfully');
        }
        setTimeout(() => {
            location.reload();
        }, 1500);
    })
    .catch(error => {
        console.error('Error cancelling meeting:', error);
        if (typeof window.showMessageModal === 'function') {
            window.showMessageModal('Error', 'Failed to cancel meeting. Please try again.');
        } else if (typeof showToast === 'function') {
            showToast('error', 'Failed to cancel meeting. Please try again.');
        } else {
            alert('Failed to cancel meeting. Please try again.');
        }
    });
}

// Export functions
export {
    getStatusBadgeClass,
    openAddMeetingModal,
    closeAddMeetingModal,
    openEditMeetingModal,
    closeEditMeetingModal,
    openCancelMeetingModal,
    closeCancelMeetingModal,
    viewMeetingDetails,
    closeViewMeetingModal,
    submitAddMeetingForm,
    submitEditMeetingForm,
    submitCancelMeetingForm
}; 