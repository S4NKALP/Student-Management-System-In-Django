// Subject Materials JavaScript

// Global variable for file deletion
window.fileIdToDelete = null;

// Modal Functions
function openUploadModal(subjectId = '') {
    const modal = document.getElementById('uploadFileModal');
    const subjectSelect = document.getElementById('subject_id');
    const responseDiv = document.getElementById('uploadResponse');
    
    // Reset the form
    const uploadForm = document.getElementById('uploadFileForm');
    if (uploadForm) {
        uploadForm.reset();
    
    // Hide response div
    if (responseDiv) {
        responseDiv.style.display = 'none';
    }
    }
    
  // Pre-select subject if provided
    if (subjectId && subjectSelect) {
        subjectSelect.value = subjectId;
    }
    
  // Show modal
  if (modal) {
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
  }
}

// Close upload modal
function closeUploadModal() {
    const modal = document.getElementById('uploadFileModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
    }
}

// Delete file
function deleteFile(fileId) {
  window.fileIdToDelete = fileId;
    const modal = document.getElementById('confirmationModal');
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
}

// Close confirmation modal
function closeConfirmationModal() {
    const modal = document.getElementById('confirmationModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
    }
  window.fileIdToDelete = null;
}

// Make modal functions globally accessible
window.openUploadModal = openUploadModal;
window.closeUploadModal = closeUploadModal;
window.deleteFile = deleteFile;
window.closeConfirmationModal = closeConfirmationModal;