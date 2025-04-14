// Initialize dashboard functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Navigation handling is now in navigation.js
    
    // Initialize progress bars
    function initializeProgressBars() {
        document.querySelectorAll('.progress-bar').forEach(bar => {
            const progress = parseFloat(bar.getAttribute('aria-valuenow')) || 0;
            bar.style.width = `${progress}%`;
            
            // Set color based on progress
            if (progress < 25) {
                bar.classList.add('bg-danger');
            } else if (progress < 75) {
                bar.classList.add('bg-warning');
            } else {
                bar.classList.add('bg-success');
            }
        });
    }

    // Call initialization
    initializeProgressBars();

    // Initialize action buttons
    document.querySelectorAll('[data-action]').forEach(button => {
        button.addEventListener('click', function() {
            const action = this.dataset.action;
            const id = this.dataset.id;
            
            switch(action) {
                case 'view':
                    viewStudent(id);
                    break;
                case 'edit':
                    editStudent(id);
                    break;
                case 'delete':
                    deleteStudent(id);
                    break;
            }
        });
    });

    // Initialize Firebase and request notification permission
    console.log('Firebase available:', typeof firebase !== 'undefined');
    console.log('Firebase messaging available:', typeof firebase !== 'undefined' && typeof firebase.messaging !== 'undefined');
    console.log('Service Worker supported:', 'serviceWorker' in navigator);
    console.log('Notification permission:', Notification.permission);
    
    if (typeof getDeviceToken === 'function') {
        getDeviceToken().catch(error => {
            console.error('Error initializing Firebase:', error);
        });
    }
});

// Student Management Functions
function viewStudent(id) {
    fetch(`/app/student/${id}/`)
        .then(response => response.json())
        .then(data => {
            const modal = document.getElementById('studentDetailsModal');
            if (modal) {
                document.getElementById('studentName').textContent = data.name;
                document.getElementById('studentPhone').textContent = data.phone;
                document.getElementById('studentEmail').textContent = data.email || 'Not provided';
                document.getElementById('studentAddress').textContent = data.permanent_address || 'Not provided';
                document.getElementById('studentCourse').textContent = data.course?.name || 'Not assigned';
                document.getElementById('studentStatus').textContent = data.status || 'Not set';
                modal.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error fetching student details:', error);
            alert('Error loading student details');
        });
}

function editStudent(id) {
    fetch(`/app/student/${id}/edit/`)
        .then(response => response.json())
        .then(data => {
            const modal = document.getElementById('editStudentModal');
            if (modal) {
                document.getElementById('editStudentId').value = data.id;
                document.getElementById('editStudentName').value = data.name;
                document.getElementById('editStudentPhone').value = data.phone;
                document.getElementById('editStudentEmail').value = data.email || '';
                document.getElementById('editStudentAddress').value = data.permanent_address || '';
                document.getElementById('editStudentCourse').value = data.course?.id || '';
                document.getElementById('editStudentStatus').value = data.status || '';
                modal.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error fetching student data:', error);
            alert('Error loading student data');
        });
}

function deleteStudent(id) {
    if (confirm('Are you sure you want to delete this student?')) {
        fetch(`/app/student/${id}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const row = document.querySelector(`tr[data-student-id="${id}"]`);
                if (row) {
                    row.remove();
                }
                alert('Student deleted successfully');
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error deleting student:', error);
            alert('Error deleting student');
        });
    }
}

// Batch Management Functions
function editBatch(id) {
    fetch(`/app/batch/${id}/edit/`)
        .then(response => response.json())
        .then(data => {
            const modal = document.getElementById('editBatchModal');
            if (modal) {
                document.getElementById('editBatchId').value = data.id;
                document.getElementById('editBatchName').value = data.name;
                document.getElementById('editBatchYear').value = data.year;
                document.getElementById('editBatchStatus').checked = data.is_active;
                modal.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error fetching batch data:', error);
            alert('Error loading batch data');
        });
}

function deleteBatch(id) {
    if (confirm('Are you sure you want to delete this batch?')) {
        fetch(`/app/batch/${id}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const row = document.querySelector(`tr[data-batch-id="${id}"]`);
                if (row) {
                    row.remove();
                }
                alert('Batch deleted successfully');
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error deleting batch:', error);
            alert('Error deleting batch');
        });
    }
}

// Tracking Management Functions
function editTracking(id) {
    fetch(`/app/tracking/${id}/edit/`)
        .then(response => response.json())
        .then(data => {
            const modal = document.getElementById('editTrackingModal');
            if (modal) {
                document.getElementById('editTrackingId').value = data.id;
                document.getElementById('editTrackingStudent').value = data.student_id;
                document.getElementById('editTrackingCourse').value = data.course_id;
                document.getElementById('editTrackingProgress').value = data.progress_status;
                document.getElementById('editTrackingPercentage').value = data.completion_percentage;
                document.getElementById('editTrackingStartDate').value = data.start_date;
                document.getElementById('editTrackingCurrentPeriod').value = data.current_period;
                modal.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error fetching tracking data:', error);
            alert('Error loading tracking data');
        });
}

function deleteTracking(id) {
    if (confirm('Are you sure you want to delete this tracking record?')) {
        fetch(`/app/tracking/${id}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const row = document.querySelector(`tr[data-tracking-id="${id}"]`);
                if (row) {
                    row.remove();
                }
                alert('Tracking record deleted successfully');
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error deleting tracking record:', error);
            alert('Error deleting tracking record');
        });
    }
}

// Filter Functions
function filterStudents() {
    const searchText = document.getElementById('studentSearch').value.toLowerCase();
    const statusFilter = document.getElementById('statusFilter').value;
    const table = document.getElementById('studentTable');
    const rows = table.getElementsByTagName('tr');

    for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        const cells = row.getElementsByTagName('td');
        if (cells.length === 0) continue;

        const studentDetails = cells[1].textContent.toLowerCase();
        const contactInfo = cells[2].textContent.toLowerCase();
        const parentInfo = cells[3].textContent.toLowerCase();
        const courseInfo = cells[4].textContent.toLowerCase();
        const status = cells[5].textContent.trim().toLowerCase();

        const matchesSearch = studentDetails.includes(searchText) || 
                            contactInfo.includes(searchText) || 
                            parentInfo.includes(searchText) ||
                            courseInfo.includes(searchText);
        const matchesStatus = !statusFilter || status.includes(statusFilter.toLowerCase());

        row.style.display = (matchesSearch && matchesStatus) ? '' : 'none';
    }
}

function filterTrackings() {
    const searchText = document.getElementById('trackingSearch').value.toLowerCase();
    const progressFilter = document.getElementById('progressFilter').value;
    const table = document.getElementById('trackingTable');
    const rows = table.getElementsByTagName('tr');

    for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        const cells = row.getElementsByTagName('td');
        if (cells.length === 0) continue;

        const student = cells[0].textContent.toLowerCase();
        const course = cells[1].textContent.toLowerCase();
        const progress = cells[2].textContent.trim().toLowerCase();

        const matchesSearch = student.includes(searchText) || course.includes(searchText);
        const matchesProgress = !progressFilter || progress === progressFilter.toLowerCase();

        row.style.display = (matchesSearch && matchesProgress) ? '' : 'none';
    }
}

// Close modals when clicking outside
window.onclick = function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}

// Close modals with close button
document.querySelectorAll('.close-modal').forEach(button => {
    button.onclick = function() {
        const modal = this.closest('.modal');
        if (modal) {
            modal.style.display = 'none';
        }
    };
});

// Modal Functions
function openAddCourseTrackingModal() {
    // Reset form before showing modal
    const form = document.getElementById('addCourseTrackingForm');
    if (form) {
        form.reset();
    }
    
    // Load students for dropdown
    fetch('/app/get-students/', {
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Accept': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error('Response was not JSON');
        }
        return response.json();
    })
    .then(data => {
        const studentSelect = document.querySelector('#student');
        if (!studentSelect) {
            console.error('Student select element not found');
            return;
        }
        
        studentSelect.innerHTML = '<option value="">Select Student</option>';
        
        if (data.success && data.students && Array.isArray(data.students)) {
            data.students.forEach(student => {
                if (student && student.id && student.display_name) {
                    studentSelect.innerHTML += `<option value="${student.id}">${student.display_name}</option>`;
                }
            });
        } else {
            studentSelect.innerHTML = '<option value="" selected>No students available</option>';
        }
    })
    .catch(error => {
        console.error('Error loading students:', error);
        const studentSelect = document.querySelector('#student');
        if (studentSelect) {
            studentSelect.innerHTML = '<option value="" selected>Failed to load students</option>';
        }
    });
    
    // Load courses for dropdown
    fetch('/app/get-courses/', {
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Accept': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error('Response was not JSON');
        }
        return response.json();
    })
    .then(data => {
        const courseSelect = document.querySelector('#track_course');
        if (!courseSelect) {
            console.error('Course select element not found');
            return;
        }
        
        courseSelect.innerHTML = '<option value="">Select Course</option>';
        
        if (data.success && data.courses && Array.isArray(data.courses)) {
            data.courses.forEach(course => {
                if (course && course.id && course.display_name) {
                    courseSelect.innerHTML += `<option value="${course.id}">${course.display_name}</option>`;
                }
            });
        } else {
            courseSelect.innerHTML = '<option value="" selected>No courses available</option>';
        }
    })
    .catch(error => {
        console.error('Error loading courses:', error);
        const courseSelect = document.querySelector('#track_course');
        if (courseSelect) {
            courseSelect.innerHTML = '<option value="" selected>Failed to load courses</option>';
        }
    });
    
    // Show the modal
    const modal = document.getElementById('addCourseTrackingModal');
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
}

function closeAddCourseTrackingModal() {
    document.getElementById('addCourseTrackingModal').style.display = 'none';
    document.body.style.overflow = '';
}
