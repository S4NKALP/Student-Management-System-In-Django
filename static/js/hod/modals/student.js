import { showToast, showMessageModal } from '../utils/notifications.js';

// Student Modal Functions
function openAddStudentModal() {
    document.getElementById('addStudentModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeAddStudentModal() {
    document.getElementById('addStudentModal').style.display = 'none';
    document.body.style.overflow = '';
    document.getElementById('addStudentForm').reset();
}

function openEditStudentModal(studentId) {
    loadStudentData(studentId);
    document.getElementById('editStudentModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeEditStudentModal() {
    document.getElementById('editStudentModal').style.display = 'none';
    document.body.style.overflow = '';
    document.getElementById('editStudentForm').reset();
}

function openViewStudentModal(studentId) {
    loadStudentViewData(studentId);
    document.getElementById('viewStudentModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeViewStudentModal() {
    document.getElementById('viewStudentModal').style.display = 'none';
    document.body.style.overflow = '';
}

// Function to load student data for edit modal
function loadStudentData(studentId) {
    fetch(`/app/get-student/${studentId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const student = data.student;
                document.getElementById('edit_student_id').value = student.id;
                document.getElementById('edit_name').value = student.name;
                document.getElementById('edit_email').value = student.email;
                document.getElementById('edit_phone').value = student.phone;
                document.getElementById('edit_gender').value = student.gender;
                document.getElementById('edit_birth_date').value = student.birth_date;
                document.getElementById('edit_admission_date').value = student.admission_date;
                document.getElementById('edit_temporary_address').value = student.temporary_address;
                document.getElementById('edit_permanent_address').value = student.permanent_address;
                document.getElementById('edit_parent_name').value = student.parent_name;
                document.getElementById('edit_parent_phone').value = student.parent_phone;
                document.getElementById('edit_citizenship_no').value = student.citizenship_no;
                
                if (student.image) {
                    document.getElementById('current_profile_picture').innerHTML = `
                        <img src="${student.image}" alt="Current Profile Picture" class="img-thumbnail" style="max-height: 100px;">
                    `;
                }
            } else {
                showToast('error', data.message || 'Error loading student data');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('error', 'An error occurred while loading student data');
        });
}

// Function to load student data for view modal
function loadStudentViewData(studentId) {
    fetch(`/app/get-student/${studentId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const student = data.student;
                
                // Set profile picture
                const profilePic = document.getElementById('view_profile_picture');
                if (student.image) {
                    profilePic.src = student.image;
                } else {
                    profilePic.src = '/static/img/user.png';
                }

                // Set basic information
                document.getElementById('view_name').textContent = student.name;
                document.getElementById('view_email').textContent = student.email;
                document.getElementById('view_phone').textContent = student.phone;
                document.getElementById('view_gender').textContent = student.gender === 'M' ? 'Male' : (student.gender === 'F' ? 'Female' : 'Other');

                // Set personal information
                document.getElementById('view_birth_date').textContent = student.birth_date;
                document.getElementById('view_admission_date').textContent = student.admission_date;
                document.getElementById('view_citizenship_no').textContent = student.citizenship_no;

                // Set address information
                document.getElementById('view_temporary_address').textContent = student.temporary_address;
                document.getElementById('view_permanent_address').textContent = student.permanent_address;

                // Set parent information
                document.getElementById('view_parent_name').textContent = student.parent_name;
                document.getElementById('view_parent_phone').textContent = student.parent_phone;

                // Set academic information
                document.getElementById('view_course').textContent = student.course_name;
                document.getElementById('view_current_semester').textContent = student.current_semester;
                document.getElementById('view_status').textContent = student.is_active ? 'Active' : 'Inactive';
            } else {
                showToast('error', data.message || 'Error loading student data');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('error', 'An error occurred while loading student data');
        });
}

// Function to confirm and handle student deletion
function confirmDeleteStudent(studentId) {
    if (confirm("Are you sure you want to delete this student? This action cannot be undone.")) {
        // If confirmed, redirect to the delete URL
        window.location.href = `/app/api/hod/students/${studentId}/delete/`;
    }
}

// Export functions
export {
    openAddStudentModal,
    closeAddStudentModal,
    openEditStudentModal,
    closeEditStudentModal,
    openViewStudentModal,
    closeViewStudentModal,
    loadStudentData,
    loadStudentViewData,
    confirmDeleteStudent
}; 