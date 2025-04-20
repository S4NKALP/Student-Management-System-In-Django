// Subjects Section
function openAddSubjectModal() {
  document.getElementById('addSubjectModal').style.display = 'block';
}

function closeAddSubjectModal() {
  document.getElementById('addSubjectModal').style.display = 'none';
}

function confirmDeleteSubject(subjectId) {
  if (confirm('Are you sure you want to delete this subject? This action cannot be undone.')) {
    // Create a form and submit it
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/app/delete-subject/${subjectId}/`;
    
    // Add CSRF token
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = document.querySelector('[name=csrfmiddlewaretoken]').value;
    form.appendChild(csrfInput);
    
    // Submit the form
    document.body.appendChild(form);
    form.submit();
  }
}

// Staff Section
function confirmDeleteStaff(staffId) {
  if (confirm('Are you sure you want to delete this staff member? This action cannot be undone.')) {
    // Create a form and submit it
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/app/staff/remove/${staffId}/`;
    
    // Add CSRF token
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = document.querySelector('[name=csrfmiddlewaretoken]').value;
    form.appendChild(csrfInput);
    
    // Submit the form
    document.body.appendChild(form);
    form.submit();
  }
} 