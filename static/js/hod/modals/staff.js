import { showToast, showMessageModal } from '../utils/notifications.js';

// Staff Modal Functions
function openAddStaffModal() {
    document.getElementById('addStaffModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeAddStaffModal() {
    document.getElementById('addStaffModal').style.display = 'none';
    document.getElementById('addStaffForm').reset();
    document.body.style.overflow = '';
}

function openViewStaffModal(staffId) {
    fetch(`/app/staff/${staffId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const staff = data.staff;
                const profilePicture = document.getElementById('staffProfilePicture');
                profilePicture.src = staff.image || "/static/img/user.png";
                
                // Basic Information
                document.getElementById('staffName').textContent = staff.name || '-';
                document.getElementById('staffDesignation').textContent = staff.designation || '-';
                document.getElementById('staffEmail').textContent = staff.email || '-';
                document.getElementById('staffPhone').textContent = staff.phone || '-';
                document.getElementById('staffGender').textContent = staff.gender || '-';
                document.getElementById('staffBirthDate').textContent = staff.birth_date || '-';
                document.getElementById('staffMaritalStatus').textContent = staff.marital_status || '-';
                
                // Additional Information
                document.getElementById('staffJoiningDate').textContent = staff.joining_date || '-';
                document.getElementById('staffStatus').textContent = staff.is_active ? 'Active' : 'Inactive';
                document.getElementById('staffParentName').textContent = staff.parent_name || '-';
                document.getElementById('staffParentPhone').textContent = staff.parent_phone || '-';
                document.getElementById('staffCitizenshipNo').textContent = staff.citizenship_no || '-';
                document.getElementById('staffPassport').textContent = staff.passport || '-';
                
                // Address Information
                document.getElementById('staffTemporaryAddress').textContent = staff.temporary_address || '-';
                document.getElementById('staffPermanentAddress').textContent = staff.permanent_address || '-';
                
                // Assigned Subjects
                const subjectsContainer = document.getElementById('staffSubjects');
                subjectsContainer.innerHTML = '';
                if (staff.subjects && staff.subjects.length > 0) {
                    staff.subjects.forEach(subject => {
                        const badge = document.createElement('span');
                        badge.className = 'badge bg-primary';
                        badge.textContent = subject.name;
                        subjectsContainer.appendChild(badge);
                    });
                } else {
                    subjectsContainer.innerHTML = '<span class="text-muted">No subjects assigned</span>';
                }
                
                document.getElementById('viewStaffModal').style.display = 'block';
                document.body.style.overflow = 'hidden';
            } else {
                showMessageModal('Error', data.message);
            }
        })
        .catch(error => {
            showMessageModal('Error', 'Failed to fetch staff details.');
        });
}

function closeViewStaffModal() {
    document.getElementById('viewStaffModal').style.display = 'none';
    document.body.style.overflow = '';
}

function openEditStaffModal(staffId) {
    fetch(`/app/staff/${staffId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const staff = data.staff;
                document.getElementById('editStaffId').value = staff.id;
                document.getElementById('editStaffName').value = staff.name;
                document.getElementById('editStaffEmail').value = staff.email;
                document.getElementById('editStaffPhone').value = staff.phone;
                document.getElementById('editStaffStatus').value = staff.is_active;
                document.getElementById('editStaffProfilePicture').src = staff.image || "/static/img/user.png";
                
                // Set selected subjects
                const subjectsSelect = document.getElementById('editStaffSubjects');
                if (staff.subjects && staff.subjects.length > 0) {
                    Array.from(subjectsSelect.options).forEach(option => {
                        option.selected = staff.subjects.some(subject => subject.id === parseInt(option.value));
                    });
                }
                
                document.getElementById('editStaffModal').style.display = 'block';
                document.body.style.overflow = 'hidden';
            } else {
                showMessageModal('Error', data.message);
            }
        })
        .catch(error => {
            showMessageModal('Error', 'Failed to fetch staff details.');
        });
}

function closeEditStaffModal() {
    document.getElementById('editStaffModal').style.display = 'none';
    document.getElementById('editStaffForm').reset();
    document.body.style.overflow = '';
}

function submitAddStaffForm() {
    const form = document.getElementById('addStaffForm');
    const formData = new FormData(form);

    fetch('/app/add-staff/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        closeAddStaffModal();
        showMessageModal('Success', data.message);
        // Refresh the staff table
        location.reload();
    })
    .catch(error => {
        showMessageModal('Error', 'Failed to add staff member.');
    });
}

function submitEditStaffForm() {
    const form = document.getElementById('editStaffForm');
    const formData = new FormData(form);
    const staffId = document.getElementById('editStaffId').value;

    fetch(`/app/staff/${staffId}/edit/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        closeEditStaffModal();
        showMessageModal('Success', data.message);
        // Refresh the staff table
        location.reload();
    })
    .catch(error => {
        showMessageModal('Error', 'Failed to update staff member.');
    });
}

function confirmDeleteStaff(staffId) {
    // Display the confirmation modal
    const confirmationModal = document.getElementById('confirmationModal');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    
    // Update confirmation message
    const messageElement = confirmationModal.querySelector('div p');
    messageElement.textContent = 'Are you sure you want to delete this staff member? This action cannot be undone.';
    
    // Show the modal
    confirmationModal.style.display = 'block';
    document.body.style.overflow = 'hidden';
    
    // Set up the delete button action
    confirmDeleteBtn.onclick = function() {
        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Send DELETE request
        fetch(`/app/delete-staff/${staffId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show success message
                showToast('success', data.message);
                // Reload the page after successful deletion
                setTimeout(() => window.location.reload(), 1500);
            } else {
                // Show error message
                showToast('error', data.message || 'Error deleting staff member');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('error', 'An error occurred while deleting the staff member');
        })
        .finally(() => {
            // Close the modal
            closeConfirmationModal();
        });
    };
}

// Helper function to close the confirmation modal
function closeConfirmationModal() {
    document.getElementById('confirmationModal').style.display = 'none';
    document.body.style.overflow = '';
}

// Helper function to show toast messages
function showToast(type, message) {
    // Assuming you have a toast notification system
    // If not, you can implement one or use browser's alert
    if (typeof Toastify === 'function') {
        Toastify({
            text: message,
            duration: 3000,
            gravity: "top",
            position: 'right',
            backgroundColor: type === 'success' ? '#4caf50' : '#f44336'
        }).showToast();
    } else {
        alert(message);
    }
}

// Make functions available globally
window.closeConfirmationModal = closeConfirmationModal;
window.confirmDeleteStaff = confirmDeleteStaff;

// Export functions
export {
    openAddStaffModal,
    closeAddStaffModal,
    openViewStaffModal,
    closeViewStaffModal,
    openEditStaffModal,
    closeEditStaffModal,
    submitAddStaffForm,
    submitEditStaffForm,
    confirmDeleteStaff
}; 