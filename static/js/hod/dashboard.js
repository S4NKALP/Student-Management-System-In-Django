import { showToast, showMessageModal, closeMessageModal } from './utils/notifications.js';
import * as meetingModals from './modals/meeting.js';
import * as studentModals from './modals/student.js';
import * as staffModals from './modals/staff.js';

// Make functions available globally
window.showToast = showToast;
window.showMessageModal = showMessageModal;
window.closeMessageModal = closeMessageModal;

// Meeting functions
window.openAddMeetingModal = meetingModals.openAddMeetingModal;
window.closeAddMeetingModal = meetingModals.closeAddMeetingModal;
window.openEditMeetingModal = meetingModals.openEditMeetingModal;
window.closeEditMeetingModal = meetingModals.closeEditMeetingModal;
window.openCancelMeetingModal = meetingModals.openCancelMeetingModal;
window.closeCancelMeetingModal = meetingModals.closeCancelMeetingModal;
window.viewMeetingDetails = meetingModals.viewMeetingDetails;
window.closeViewMeetingModal = meetingModals.closeViewMeetingModal;
window.submitAddMeetingForm = meetingModals.submitAddMeetingForm;
window.submitEditMeetingForm = meetingModals.submitEditMeetingForm;
window.submitCancelMeetingForm = meetingModals.submitCancelMeetingForm;

// Student functions
window.openAddStudentModal = studentModals.openAddStudentModal;
window.closeAddStudentModal = studentModals.closeAddStudentModal;
window.openEditStudentModal = studentModals.openEditStudentModal;
window.closeEditStudentModal = studentModals.closeEditStudentModal;
window.openViewStudentModal = studentModals.openViewStudentModal;
window.closeViewStudentModal = studentModals.closeViewStudentModal;
window.submitAddStudentForm = studentModals.submitAddStudentForm;
window.submitEditStudentForm = studentModals.submitEditStudentForm;

// Staff functions
window.openAddStaffModal = staffModals.openAddStaffModal;
window.closeAddStaffModal = staffModals.closeAddStaffModal;
window.openEditStaffModal = staffModals.openEditStaffModal;
window.closeEditStaffModal = staffModals.closeEditStaffModal;
window.openViewStaffModal = staffModals.openViewStaffModal;
window.closeViewStaffModal = staffModals.closeViewStaffModal;
window.submitAddStaffForm = staffModals.submitAddStaffForm;
window.submitEditStaffForm = staffModals.submitEditStaffForm;

// Initialize event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize duration filter for subjects
    const durationButtons = document.querySelectorAll('#durationFilter button');
    const subjectRows = document.querySelectorAll('#subjectsTableBody tr[data-period]');

    durationButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            durationButtons.forEach(btn => btn.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');

            const selectedDuration = this.dataset.duration;
            
            // Show/hide rows based on selected duration
            subjectRows.forEach(row => {
                if (selectedDuration === 'all' || row.dataset.period === selectedDuration) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });

            // Show/hide "no subjects" message
            const noSubjectsRow = document.querySelector('#subjectsTableBody tr:not([data-period])');
            if (noSubjectsRow) {
                const visibleRows = Array.from(subjectRows).filter(row => row.style.display !== 'none');
                noSubjectsRow.style.display = visibleRows.length === 0 ? '' : 'none';
            }
        });
    });

    // Initialize online meeting toggle listeners
    const isOnlineCheckbox = document.getElementById('isOnline');
    const meetingLinkContainer = document.getElementById('meetingLinkContainer');
    
    if (isOnlineCheckbox) {
        isOnlineCheckbox.addEventListener('change', function() {
            meetingLinkContainer.style.display = this.checked ? 'block' : 'none';
        });
    }
    
    const editIsOnlineCheckbox = document.getElementById('editIsOnline');
    const editMeetingLinkContainer = document.getElementById('editMeetingLinkContainer');
    
    if (editIsOnlineCheckbox) {
        editIsOnlineCheckbox.addEventListener('change', function() {
            editMeetingLinkContainer.style.display = this.checked ? 'block' : 'none';
        });
    }

    // Add event listeners for closing modals with Escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            const meetingNotesModal = document.getElementById('meetingNotesModal');
            const meetingAgendaModal = document.getElementById('meetingAgendaModal');
            const cancellationReasonModal = document.getElementById('cancellationReasonModal');
            const addMeetingModal = document.getElementById('addMeetingModal');
            const editMeetingModal = document.getElementById('editMeetingModal');
            const cancelMeetingModal = document.getElementById('cancelMeetingModal');
            const viewMeetingModal = document.getElementById('viewMeetingModal');

            if (meetingNotesModal && meetingNotesModal.classList.contains('show')) {
                meetingModals.closeMeetingNotesModal();
            }
            if (meetingAgendaModal && meetingAgendaModal.classList.contains('show')) {
                meetingModals.closeMeetingAgendaModal();
            }
            if (cancellationReasonModal && cancellationReasonModal.classList.contains('show')) {
                meetingModals.closeCancellationReasonModal();
            }
            if (addMeetingModal && addMeetingModal.classList.contains('show')) {
                meetingModals.closeAddMeetingModal();
            }
            if (editMeetingModal && editMeetingModal.classList.contains('show')) {
                meetingModals.closeEditMeetingModal();
            }
            if (cancelMeetingModal && cancelMeetingModal.classList.contains('show')) {
                meetingModals.closeCancelMeetingModal();
            }
            if (viewMeetingModal && viewMeetingModal.classList.contains('show')) {
                meetingModals.closeViewMeetingModal();
            }
        }
    });
    
    // Initialize search functionality for progress section
    const progressSearchInput = document.getElementById('progressSearchInput');
    const progressSearchButton = document.getElementById('progressSearchButton');
    
    if (progressSearchInput && progressSearchButton) {
        // Function to perform search
        const performSearch = () => {
            const searchTerm = progressSearchInput.value.toLowerCase().trim();
            const progressRows = document.querySelectorAll('#progressTable tbody tr');
            let visibleRowCount = 0;
            
            progressRows.forEach(row => {
                // Skip the "No progress data available" row if it exists
                if (!row.querySelector('td[colspan]')) {
                    // Get text content from student name and batch columns
                    const studentNameCell = row.querySelector('td:nth-child(1)');
                    const batchCell = row.querySelector('td:nth-child(2)');
                    
                    const studentText = studentNameCell ? studentNameCell.textContent.toLowerCase() : '';
                    const batchText = batchCell ? batchCell.textContent.toLowerCase() : '';
                    
                    // Show row if search term is found in student name or batch
                    if (searchTerm === '' || 
                        studentText.includes(searchTerm) || 
                        batchText.includes(searchTerm)) {
                        row.style.display = '';
                        visibleRowCount++;
                    } else {
                        row.style.display = 'none';
                    }
                }
            });
            
            // Show/hide "no data" message
            const noProgressDataMessage = document.getElementById('noProgressDataMessage');
            if (noProgressDataMessage) {
                noProgressDataMessage.style.display = (visibleRowCount === 0 && searchTerm !== '') ? 'block' : 'none';
            }
            
            // Update summary cards with filtered data
            updateProgressSummary(progressRows, searchTerm);
        };
        
        // Button click event listener
        progressSearchButton.addEventListener('click', performSearch);
        
        // Enter key press event listener
        progressSearchInput.addEventListener('keyup', function(event) {
            if (event.key === 'Enter') {
                performSearch();
            }
        });
        
        // Add input event listener for real-time filtering (optional)
        progressSearchInput.addEventListener('input', function() {
            // Only perform search if the input has at least 3 characters or is empty
            if (this.value.length >= 3 || this.value.length === 0) {
                performSearch();
            }
        });
    }
    
    // Function to update progress summary based on visible rows
    function updateProgressSummary(rows, searchTerm) {
        if (!searchTerm || searchTerm === '') {
            // If no search is applied, revert to original values
            if (document.getElementById('avgCompletion')) {
                document.getElementById('avgCompletion').textContent = originalAvgCompletion + '%';
            }
            if (document.getElementById('studentsOnTrack')) {
                document.getElementById('studentsOnTrack').textContent = originalStudentsOnTrack;
            }
            if (document.getElementById('studentsAtRisk')) {
                document.getElementById('studentsAtRisk').textContent = originalStudentsAtRisk;
            }
            return;
        }
        
        let totalCompletion = 0;
        let studentsOnTrack = 0;
        let studentsAtRisk = 0;
        let visibleStudents = 0;
        
        rows.forEach(row => {
            if (row.style.display !== 'none' && !row.querySelector('td[colspan]')) {
                visibleStudents++;
                
                // Get completion percentage from the progress bar
                const progressCell = row.querySelector('td:nth-child(4)');
                if (progressCell) {
                    const percentText = progressCell.querySelector('.small')?.textContent || '0%';
                    const completionPercentage = parseFloat(percentText);
                    
                    if (!isNaN(completionPercentage)) {
                        totalCompletion += completionPercentage;
                        
                        // Count students on track and at risk
                        if (completionPercentage >= 75) {
                            studentsOnTrack++;
                        } else if (completionPercentage < 40) {
                            studentsAtRisk++;
                        }
                    }
                }
            }
        });
        
        // Update summary cards with filtered data
        const avgCompletion = visibleStudents > 0 ? Math.round(totalCompletion / visibleStudents) : 0;
        
        if (document.getElementById('avgCompletion')) {
            document.getElementById('avgCompletion').textContent = avgCompletion + '%';
        }
        if (document.getElementById('studentsOnTrack')) {
            document.getElementById('studentsOnTrack').textContent = studentsOnTrack;
        }
        if (document.getElementById('studentsAtRisk')) {
            document.getElementById('studentsAtRisk').textContent = studentsAtRisk;
        }
    }
    
    // Store original summary values
    const originalAvgCompletion = document.getElementById('avgCompletion') ? document.getElementById('avgCompletion').textContent.replace('%', '') : '0';
    const originalStudentsOnTrack = document.getElementById('studentsOnTrack') ? document.getElementById('studentsOnTrack').textContent : '0';
    const originalStudentsAtRisk = document.getElementById('studentsAtRisk') ? document.getElementById('studentsAtRisk').textContent : '0';
}); 