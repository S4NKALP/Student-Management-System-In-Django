/**
 * Routine management functionality for HOD dashboard
 */

document.addEventListener('DOMContentLoaded', function() {
  // Initialize period filter
  initPeriodFilter();
  
  // Initialize action buttons for existing routines
  initRoutineActionButtons();
});

/**
 * Initialize period filter buttons
 */
function initPeriodFilter() {
  const periodFilterButtons = document.querySelectorAll('#periodFilterButtons button');
  
  periodFilterButtons.forEach(button => {
    button.addEventListener('click', function() {
      // Remove active class from all buttons
      periodFilterButtons.forEach(btn => btn.classList.remove('active'));
      // Add active class to clicked button
      this.classList.add('active');
      
      // Filter routines based on selected period
      const selectedPeriod = this.dataset.period;
      filterRoutineByPeriod(selectedPeriod);
    });
  });
}

/**
 * Initialize action buttons for routine rows
 */
function initRoutineActionButtons() {
  // Edit buttons
  document.querySelectorAll('.edit-routine-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const routineId = this.getAttribute('data-routine-id');
      openEditRoutineModal(routineId);
    });
  });
  
  // Delete buttons
  document.querySelectorAll('.delete-routine-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const routineId = this.getAttribute('data-routine-id');
      openDeleteRoutineModal(routineId);
    });
  });
}

/**
 * Filter routine table based on selected period/year
 */
function filterRoutineByPeriod(selectedPeriod) {
  const routineRows = document.querySelectorAll('#routineTableBody tr.routine-row');
  let visibleRows = 0;
  
  routineRows.forEach(row => {
    if (selectedPeriod === 'all' || row.dataset.period === selectedPeriod) {
      row.style.display = '';
      visibleRows++;
    } else {
      row.style.display = 'none';
    }
  });
  
  // Show or hide "no classes" message
  const noClassesMessage = document.getElementById('noClassesMessage');
  if (noClassesMessage) {
    noClassesMessage.style.display = visibleRows === 0 ? 'block' : 'none';
  }
}

/**
 * Open add routine modal
 */
function openAddRoutineModal() {
  const modal = document.getElementById('addRoutineModal');
  if (modal) {
    // Reset form
    document.getElementById('addRoutineForm').reset();
    
    // Set default period/year based on subject selection
    const subjectSelect = document.getElementById('subjectId');
    if (subjectSelect) {
      subjectSelect.addEventListener('change', function() {
        const selectedOption = this.options[this.selectedIndex];
        const periodOrYear = selectedOption.textContent.match(/\((?:Semester|Year) (\d+)\)/);
        if (periodOrYear && periodOrYear[1]) {
          document.getElementById('periodOrYear').value = periodOrYear[1];
        }
      });
    }
    
    // Show modal
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
  }
}

/**
 * Close add routine modal
 */
function closeAddRoutineModal() {
  const modal = document.getElementById('addRoutineModal');
  if (modal) {
    modal.style.display = 'none';
    document.body.style.overflow = '';
  }
}

/**
 * Submit add routine form
 */
function submitAddRoutineForm() {
  const form = document.getElementById('addRoutineForm');
  if (!form) return;
  
  // Create form data
  const formData = new FormData(form);
  
  // Add course_id from the page
  const courseId = document.querySelector('#routineSection').getAttribute('data-course-id');
  if (courseId) {
    formData.append('course_id', courseId);
  } else {
    // If no explicit course ID, use the current course ID from the URL
    const urlPath = window.location.pathname;
    const urlMatch = urlPath.match(/\/hod\/(\d+)/);
    if (urlMatch && urlMatch[1]) {
      formData.append('course_id', urlMatch[1]);
    }
  }
  
  // Validate form
  const subjectId = formData.get('subject_id');
  const teacherId = formData.get('teacher_id');
  const startTime = formData.get('start_time');
  const endTime = formData.get('end_time');
  
  if (!subjectId || !teacherId || !startTime || !endTime) {
    showToast('error', 'Please fill in all required fields');
    return;
  }
  
  // Send request to server
  fetch('/app/api/hod/routines/', {
    method: 'POST',
    body: formData,
    headers: {
      'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
    }
  })
  .then(response => {
    if (!response.ok) {
      return response.json().then(data => {
        throw new Error(data.message || 'Failed to add routine');
      });
    }
    return response.json();
  })
  .then(data => {
    showToast('success', 'Routine added successfully');
    closeAddRoutineModal();
    setTimeout(() => {
      window.location.reload();
    }, 1000);
  })
  .catch(error => {
    console.error('Error adding routine:', error);
    showToast('error', error.message || 'Failed to add routine');
  });
}

/**
 * Open edit routine modal
 */
function openEditRoutineModal(routineId) {
  const modal = document.getElementById('editRoutineModal');
  if (!modal || !routineId) return;
  
  // Fetch routine data
  fetch(`/app/api/hod/routines/${routineId}/`)
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to fetch routine data');
      }
      return response.json();
    })
    .then(data => {
      // Populate form fields
      document.getElementById('editRoutineId').value = routineId;
      document.getElementById('editSubjectId').value = data.subject_id;
      document.getElementById('editTeacherId').value = data.teacher_id;
      document.getElementById('editStartTime').value = data.start_time;
      document.getElementById('editEndTime').value = data.end_time;
      document.getElementById('editPeriodOrYear').value = data.period_or_year;
      
      // Show modal
      modal.style.display = 'block';
      document.body.style.overflow = 'hidden';
    })
    .catch(error => {
      console.error('Error fetching routine data:', error);
      showToast('error', error.message || 'Failed to fetch routine data');
    });
}

/**
 * Close edit routine modal
 */
function closeEditRoutineModal() {
  const modal = document.getElementById('editRoutineModal');
  if (modal) {
    modal.style.display = 'none';
    document.body.style.overflow = '';
  }
}

/**
 * Submit edit routine form
 */
function submitEditRoutineForm() {
  const form = document.getElementById('editRoutineForm');
  if (!form) return;
  
  // Get routine ID
  const routineId = document.getElementById('editRoutineId').value;
  if (!routineId) {
    showToast('error', 'Routine ID is missing');
    return;
  }
  
  // Create form data
  const formData = new FormData(form);
  
  // Validate form
  const subjectId = formData.get('subject_id');
  const teacherId = formData.get('teacher_id');
  const startTime = formData.get('start_time');
  const endTime = formData.get('end_time');
  
  if (!subjectId || !teacherId || !startTime || !endTime) {
    showToast('error', 'Please fill in all required fields');
    return;
  }
  
  // Send request to server
  fetch(`/app/api/hod/routines/${routineId}/`, {
    method: 'PUT',
    body: formData,
    headers: {
      'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
    }
  })
  .then(response => {
    if (!response.ok) {
      return response.json().then(data => {
        throw new Error(data.message || 'Failed to update routine');
      });
    }
    return response.json();
  })
  .then(data => {
    showToast('success', 'Routine updated successfully');
    closeEditRoutineModal();
    setTimeout(() => {
      window.location.reload();
    }, 1000);
  })
  .catch(error => {
    console.error('Error updating routine:', error);
    showToast('error', error.message || 'Failed to update routine');
  });
}

/**
 * Open delete routine modal
 */
function openDeleteRoutineModal(routineId) {
  const modal = document.getElementById('deleteRoutineModal');
  if (!modal || !routineId) return;
  
  // Set routine ID in the form
  document.getElementById('deleteRoutineId').value = routineId;
  
  // Show modal
  modal.style.display = 'block';
  document.body.style.overflow = 'hidden';
}

/**
 * Close delete routine modal
 */
function closeDeleteRoutineModal() {
  const modal = document.getElementById('deleteRoutineModal');
  if (modal) {
    modal.style.display = 'none';
    document.body.style.overflow = '';
  }
}

/**
 * Submit delete routine form
 */
function submitDeleteRoutineForm() {
  const routineId = document.getElementById('deleteRoutineId').value;
  if (!routineId) {
    showToast('error', 'Routine ID is missing');
    return;
  }
  
  // Send request to server
  fetch(`/app/api/hod/routines/${routineId}/`, {
    method: 'DELETE',
    headers: {
      'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
    }
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Failed to delete routine');
    }
    showToast('success', 'Routine deleted successfully');
    closeDeleteRoutineModal();
    setTimeout(() => {
      window.location.reload();
    }, 1000);
  })
  .catch(error => {
    console.error('Error deleting routine:', error);
    showToast('error', error.message || 'Failed to delete routine');
  });
}

// Export functions for use in other files
export {
  filterRoutineByPeriod,
  openAddRoutineModal,
  closeAddRoutineModal,
  submitAddRoutineForm,
  openEditRoutineModal,
  closeEditRoutineModal,
  submitEditRoutineForm,
  openDeleteRoutineModal,
  closeDeleteRoutineModal,
  submitDeleteRoutineForm
}; 