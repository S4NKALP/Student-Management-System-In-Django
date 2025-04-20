// Define functions in global scope
window.viewSubjectDetails = function(subjectId) {
    console.log('Viewing subject details for ID:', subjectId);
    // Fetch subject details from the server
    fetch(`/api/subjects/${subjectId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Populate the view modal with subject details
            document.getElementById('viewSubjectName').textContent = data.name;
            document.getElementById('viewSubjectCode').textContent = data.code || 'N/A';
            document.getElementById('viewSubjectPeriod').textContent = data.period_or_year;
            document.getElementById('viewSubjectTeacher').textContent = data.teacher ? data.teacher.name : 'Not Assigned';
            document.getElementById('viewSubjectStudents').textContent = data.total_students || '0';
            document.getElementById('viewSubjectClasses').textContent = data.classes_per_week || '0';

            // Show the view modal
            const viewModal = new bootstrap.Modal(document.getElementById('viewSubjectModal'));
            viewModal.show();
        })
        .catch(error => {
            console.error('Error fetching subject details:', error);
            showToast('Error', 'Failed to fetch subject details', 'error');
        });
};

window.editSubject = function(subjectId) {
    console.log('Editing subject with ID:', subjectId);
    // Fetch subject details for editing
    fetch(`/api/subjects/${subjectId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Populate the edit form
            document.getElementById('editSubjectId').value = data.id;
            document.getElementById('editSubjectName').value = data.name;
            document.getElementById('editSubjectCode').value = data.code || '';
            document.getElementById('editSubjectPeriod').value = data.period_or_year;
            document.getElementById('editSubjectTeacher').value = data.teacher ? data.teacher.id : '';

            // Show the edit modal
            const editModal = new bootstrap.Modal(document.getElementById('editSubjectModal'));
            editModal.show();
        })
        .catch(error => {
            console.error('Error fetching subject details:', error);
            showToast('Error', 'Failed to fetch subject details', 'error');
        });
};

window.updateSubject = function() {
    const subjectId = document.getElementById('editSubjectId').value;
    console.log('Updating subject with ID:', subjectId);
    
    const formData = new FormData(document.getElementById('editSubjectForm'));
    
    fetch(`/api/subjects/${subjectId}/`, {
        method: 'PUT',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Close the modal
        const editModal = bootstrap.Modal.getInstance(document.getElementById('editSubjectModal'));
        editModal.hide();
        
        // Show success message
        showToast('Success', 'Subject updated successfully', 'success');
        
        // Refresh the subjects table
        location.reload();
    })
    .catch(error => {
        console.error('Error updating subject:', error);
        showToast('Error', 'Failed to update subject', 'error');
    });
};

window.confirmDeleteSubject = function(subjectId) {
    console.log('Confirming deletion of subject with ID:', subjectId);
    if (confirm('Are you sure you want to delete this subject? This action cannot be undone.')) {
        fetch(`/api/subjects/${subjectId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            showToast('Success', 'Subject deleted successfully', 'success');
            location.reload();
        })
        .catch(error => {
            console.error('Error deleting subject:', error);
            showToast('Error', 'Failed to delete subject', 'error');
        });
    }
};

// Utility function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Utility function to show toast messages
function showToast(title, message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <strong>${title}</strong><br>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(container);
    return container;
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('HOD Subjects JS initialized');
    
    // Initialize all subject-related event listeners
    initializeSubjectEventListeners();
});

function initializeSubjectEventListeners() {
    // Get all subject action buttons
    const viewButtons = document.querySelectorAll('[onclick^="viewSubjectDetails"]');
    const editButtons = document.querySelectorAll('[onclick^="editSubject"]');
    const deleteButtons = document.querySelectorAll('[onclick^="confirmDeleteSubject"]');

    // Add event listeners to view buttons
    viewButtons.forEach(button => {
        const subjectId = button.getAttribute('onclick').match(/'([^']+)'/)[1];
        button.onclick = () => viewSubjectDetails(subjectId);
    });

    // Add event listeners to edit buttons
    editButtons.forEach(button => {
        const subjectId = button.getAttribute('onclick').match(/'([^']+)'/)[1];
        button.onclick = () => editSubject(subjectId);
    });

    // Add event listeners to delete buttons
    deleteButtons.forEach(button => {
        const subjectId = button.getAttribute('onclick').match(/'([^']+)'/)[1];
        button.onclick = () => confirmDeleteSubject(subjectId);
    });
} 