// Attendance Functions for Teacher Dashboard

// Constants
const ATTENDANCE_MODAL_ID = 'attendanceModal';
const QUICK_ATTENDANCE_FORM_ID = 'quickAttendanceForm';
const ATTENDANCE_FORM_ID = 'attendanceForm';

// Attendance Modal Functions
async function openAttendanceModal(routineId, date) {
    try {
        console.log('Opening attendance modal for routine:', routineId, 'date:', date);
        
        // Validate and clean inputs
        routineId = routineId?.trim().replace(/['"]+/g, '');
        date = date || getCurrentDate();
        
        if (!routineId) {
            throw new Error('Invalid routine ID');
        }
        
        // Get required elements
        const modal = document.getElementById(ATTENDANCE_MODAL_ID);
        const modalRoutineId = document.getElementById('modalRoutineId');
        const modalDate = document.getElementById('modalDate');
        const modalStudentList = document.getElementById('modalStudentList');
        
        if (!modal || !modalRoutineId || !modalDate || !modalStudentList) {
            throw new Error('Required modal elements not found');
        }
        
        // Set form values
        modalRoutineId.value = routineId;
        modalDate.value = date;
        
        // Show loading state
        showLoadingSpinner(modalStudentList, 'Loading students...');
        
        // Show modal
        showModal(ATTENDANCE_MODAL_ID);
        
        // Fetch students
        const data = await apiRequest(`${API_BASE_URL}/get-students/?routine_id=${routineId}`);
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Render student list with enhanced UI
        renderStudentList(modalStudentList, data.students);
        
    } catch (error) {
        console.error('Error in openAttendanceModal:', error);
        showError(document.getElementById('modalStudentList'), error);
        hideModal(ATTENDANCE_MODAL_ID);
    }
}

function renderStudentList(container, students) {
    if (!container || !Array.isArray(students)) return;
    
    container.innerHTML = `
        <div class="table-responsive">
            <table class="table table-hover">
                <tbody>
                    ${students.map((student, index) => `
                        <tr>
                            <td>${index + 1}</td>
                            <td>${student.name}</td>
                            <td>${student.id}</td>
                            <td>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" 
                                        id="student_${student.id}" 
                                        name="student_${student.id}"
                                        aria-label="Mark ${student.name} as present">
                                </div>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
        
    `;
}

function closeAttendanceModal() {
    hideModal(ATTENDANCE_MODAL_ID);
    resetForm(QUICK_ATTENDANCE_FORM_ID);
}

// Attendance View Functions
function toggleAttendanceView(view) {
    const headerSection = document.getElementById('attendanceHeader');
    const manageView = document.getElementById('manageAttendanceView');
    const routineSelectionForm = document.getElementById('routineSelectionForm');
    const attendanceFormContainer = document.getElementById('attendanceFormContainer');

    if (view === 'recent') {
        // Show recent view
        headerSection.style.display = 'block';
        manageView.style.display = 'none';
        
        // Reset form and container
        if (attendanceFormContainer) {
            attendanceFormContainer.style.display = 'none';
            attendanceFormContainer.innerHTML = '';
        }
        
        // Safely reset routine selection form
        if (routineSelectionForm) {
            routineSelectionForm.style.display = 'block';
            // Reset form elements individually to avoid potential issues
            const routineSelect = routineSelectionForm.querySelector('#routineSelect');
            const dateSelect = routineSelectionForm.querySelector('#dateSelect');
            
            if (routineSelect) {
                routineSelect.selectedIndex = 0;
            }
            
            if (dateSelect) {
                dateSelect.value = '';
            }
            
            // Clear any error messages
            routineSelectionForm.querySelectorAll('.alert').forEach(alert => alert.remove());
        }
    } else {
        // Show manage view
        headerSection.style.display = 'none';
        manageView.style.display = 'block';
        
        // Load data if routine and date are selected
        const routineSelect = document.getElementById('routineSelect');
        const dateSelect = document.getElementById('dateSelect');
        
        if (routineSelect?.value && dateSelect?.value) {
            loadAttendanceData();
        } else if (attendanceFormContainer) {
            attendanceFormContainer.style.display = 'none';
            attendanceFormContainer.innerHTML = '';
        }
    }
}

// Attendance Data Functions
async function editAttendance(routineId, date) {
    try {
        console.log('Editing attendance for routine:', routineId, 'date:', date);
        
        // Switch to manage view
        toggleAttendanceView('manage');
        
        // Hide routine selection form
        const routineSelectionForm = document.getElementById('routineSelectionForm');
        if (routineSelectionForm) {
            routineSelectionForm.style.display = 'none';
        }
        
        // Update form inputs
        const attendanceForm = document.getElementById(ATTENDANCE_FORM_ID);
        if (attendanceForm) {
            const routineInput = attendanceForm.querySelector('input[name="routine_id"]');
            const dateInput = attendanceForm.querySelector('input[name="date"]');
            if (routineInput) routineInput.value = routineId;
            if (dateInput) dateInput.value = date;
        }
        
        // Show loading state
        const container = document.getElementById('attendanceFormContainer');
        if (!container) return;
        
        container.style.display = 'block';
        showLoadingSpinner(container, 'Loading attendance data...');
        
        // Fetch attendance data
        const [attendanceData, studentsData] = await Promise.all([
            apiRequest(`${API_BASE_URL}/get-attendance-form/?routine_id=${routineId}&date=${date}`),
            apiRequest(`${API_BASE_URL}/get-students/?routine_id=${routineId}`)
        ]);
        
        if (attendanceData.error || studentsData.error) {
            throw new Error(attendanceData.error || studentsData.error);
        }
        
        // Render attendance form
        renderAttendanceForm(container, routineId, date, attendanceData, studentsData.students);
        
    } catch (error) {
        console.error('Error editing attendance:', error);
        if (container) {
            showError(container, error);
        }
    }
}

function renderAttendanceForm(container, routineId, date, attendanceData, students) {
    if (!container || !Array.isArray(students)) return;
    
    container.innerHTML = `
        <form method="post" action="${API_BASE_URL}/save-attendance/" id="${ATTENDANCE_FORM_ID}">
            <input type="hidden" name="csrfmiddlewaretoken" value="${getCSRFToken()}">
            <input type="hidden" name="routine_id" value="${routineId}">
            <input type="hidden" name="date" value="${date}">
            
            <div class="row mb-3">
                <div class="col-md-6">
                    <div class="form-check form-switch">
                        <input class="form-check-input" type="checkbox" id="teacherAttend" 
                            name="teacher_attend" ${attendanceData.teacher_attend ? 'checked' : ''}>
                        <label class="form-check-label" for="teacherAttend">Teacher Present</label>
                    </div>
                </div>
                <div class="col-md-6">
                    <select class="form-select" id="classStatus" name="class_status">
                        <option value="True" ${attendanceData.class_status ? 'selected' : ''}>Conducted</option>
                        <option value="False" ${!attendanceData.class_status ? 'selected' : ''}>Not Conducted</option>
                    </select>
                </div>
            </div>

            <div class="table-responsive">
                <table class="table table-hover">
                    <thead class="table-light">
                        <tr>
                            <th width="5%">#</th>
                            <th width="40%">Name</th>
                            <th width="40%">Student ID</th>
                            <th width="15%">Present</th>
                        </tr>
                    </thead>
                    <tbody id="studentList">
                        ${students.map((student, index) => {
                            const isPresent = attendanceData.records && attendanceData.records[student.id] === true;
                            return `
                                <tr>
                                    <td>${index + 1}</td>
                                    <td>${student.name}</td>
                                    <td>${student.id}</td>
                                    <td>
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" 
                                                id="student_${student.id}" 
                                                name="student_${student.id}"
                                                ${isPresent ? 'checked' : ''}
                                                aria-label="Mark ${student.name} as present">
                                        </div>
                                    </td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            </div>
            
            <div class="mt-3 d-flex justify-content-between">
                <div>
                    <button type="button" class="btn btn-outline-success me-2" onclick="markAllPresent()">
                        <i class="fas fa-check-double me-1"></i> Mark All Present
                    </button>
                    <button type="button" class="btn btn-outline-danger" onclick="markAllAbsent()">
                        <i class="fas fa-times-circle me-1"></i> Mark All Absent
                    </button>
                </div>
                <button type="submit" class="btn btn-primary">
                    <i class="fas fa-save me-1"></i> Save Attendance
                </button>
            </div>
        </form>
    `;
}

// Attendance Marking Functions
function markAllPresent() {
    const checkboxes = document.querySelectorAll(`#${ATTENDANCE_FORM_ID} input[type="checkbox"], #${QUICK_ATTENDANCE_FORM_ID} input[type="checkbox"]`);
    checkboxes.forEach(checkbox => {
        if (checkbox.id !== 'teacherAttend' && checkbox.id !== 'modalTeacherAttend') {
            checkbox.checked = true;
        }
    });
}

function markAllAbsent() {
    const checkboxes = document.querySelectorAll(`#${ATTENDANCE_FORM_ID} input[type="checkbox"], #${QUICK_ATTENDANCE_FORM_ID} input[type="checkbox"]`);
    checkboxes.forEach(checkbox => {
        if (checkbox.id !== 'teacherAttend' && checkbox.id !== 'modalTeacherAttend') {
            checkbox.checked = false;
        }
    });
}

async function loadAttendanceData() {
    try {
        console.log('Loading attendance data...');
        const routineId = document.getElementById('routineSelect')?.value;
        const date = document.getElementById('dateSelect')?.value;
        const container = document.getElementById('attendanceFormContainer');
        
        if (!container) return;
        
        if (!routineId || !date) {
            container.style.display = 'none';
            container.innerHTML = '';
            return;
        }
        
        container.style.display = 'block';
        showLoadingSpinner(container, 'Loading attendance data...');
        
        const [attendanceData, studentsData] = await Promise.all([
            apiRequest(`${API_BASE_URL}/get-attendance-form/?routine_id=${routineId}&date=${date}`),
            apiRequest(`${API_BASE_URL}/get-students/?routine_id=${routineId}`)
        ]);
        
        if (attendanceData.error || studentsData.error) {
            throw new Error(attendanceData.error || studentsData.error);
        }
        
        renderAttendanceForm(container, routineId, date, attendanceData, studentsData.students);
        
    } catch (error) {
        console.error('Error loading attendance data:', error);
        if (container) {
            showError(container, error);
        }
    }
}

// Form Submission Handler
async function saveQuickAttendance() {
    try {
        const form = document.getElementById(QUICK_ATTENDANCE_FORM_ID);
        if (!form) return;
        
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        // Validate required fields
        if (!data.routine_id || !data.date) {
            throw new Error('Missing required fields');
        }
        
        // Show loading state
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Saving...';
        }
        
        // Submit attendance
        const response = await apiRequest(`${API_BASE_URL}/save-attendance/`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
        
        if (response.error) {
            throw new Error(response.error);
        }
        
        // Show success message
        showSuccess(form, 'Attendance saved successfully');
        
        // Close modal and reset form
        setTimeout(() => {
            closeAttendanceModal();
        }, 1500);
        
    } catch (error) {
        console.error('Error saving attendance:', error);
        showError(form, error);
        
        // Reset submit button
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = false;
            submitButton.innerHTML = '<i class="fas fa-save me-1"></i> Save Attendance';
        }
    }
} 