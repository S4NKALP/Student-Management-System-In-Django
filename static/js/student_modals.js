// Functions for handling student modals

// Close PDF viewer modal
function closePdfViewerModal() {
  document.getElementById('pdfViewerModal').style.display = 'none';
  document.body.style.overflow = '';
}

// Close subject files modal
function closeSubjectFilesModal() {
  document.getElementById('subjectFilesModal').style.display = 'none';
  document.body.style.overflow = '';
}

// Open subject files modal and load content
function openSubjectFilesModal(subjectId) {
  const modal = document.getElementById('subjectFilesModal');
  const filesList = document.getElementById('subjectFilesList');
  
  modal.style.display = 'block';
  document.body.style.overflow = 'hidden';
  
  filesList.innerHTML = `
    <div class="text-center py-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading subject files...</p>
    </div>
  `;

  fetch(`/app/subject/${subjectId}/files/`)
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      if (!data.success) {
        filesList.innerHTML = `
          <div class="alert alert-info">
            <i class="fas fa-info-circle me-2"></i> ${data.message || 'No files available for this subject'}
          </div>
        `;
        return;
      }

      if (!data.files || data.files.length === 0) {
        filesList.innerHTML = `
          <div class="alert alert-info">
            <i class="fas fa-info-circle me-2"></i> No study materials available for this subject.
          </div>
        `;
        return;
      }

      filesList.innerHTML = data.files.map(file => {
        const fileExtension = file.file_url ? file.file_url.split('.').pop().toLowerCase() : '';
        const iconClass = getFileIcon(fileExtension);
        const fileIcon = `<i class="fas ${iconClass} ${fileExtension === 'pdf' ? 'text-danger' : 'text-primary'} me-2"></i>`;
        
        return `
          <div class="list-group-item">
            <div class="d-flex w-100 justify-content-between align-items-center">
              <div>
                <h6 class="mb-1">
                  ${fileIcon}
                  ${file.title}
                </h6>
                <p class="mb-1 small text-muted">${file.description || 'No description'}</p>
                <small class="text-muted">
                  ${file.file_type === 'syllabus' 
                    ? '<span class="badge bg-info me-1">Syllabus</span>' 
                    : '<span class="badge bg-primary me-1">Study Material</span>'}
                  ${file.uploaded_by ? `<span>Uploaded by: ${file.uploaded_by}</span>` : ''}
                  ${file.uploaded_at ? `<span class="ms-2">• ${formatDate(file.uploaded_at)}</span>` : ''}
                </small>
              </div>
              <div>
                ${file.file_url ? `
                  <div class="btn-group" role="group">
                    <a href="${file.file_url}" class="btn btn-primary btn-sm" target="_blank">
                      <i class="fas fa-download me-1"></i> Download
                    </a>
                    <a href="${file.file_url}" class="btn btn-secondary btn-sm" target="_blank">
                      <i class="fas fa-eye me-1"></i> View
                    </a>
                  </div>
                ` : `
                  <span class="text-danger">
                    <i class="fas fa-exclamation-circle me-1"></i> File not available
                  </span>
                `}
              </div>
            </div>
          </div>
        `;
      }).join('');
    })
    .catch(error => {
      console.error('Error fetching subject files:', error);
      filesList.innerHTML = `
        <div class="alert alert-danger">
          <i class="fas fa-exclamation-circle me-2"></i> Failed to load files. Please try again.
        </div>
      `;
    });
}

// Get appropriate icon based on file type
function getFileIcon(fileType) {
  const iconMap = {
    'pdf': 'fa-file-pdf',
    'doc': 'fa-file-word',
    'docx': 'fa-file-word',
    'xls': 'fa-file-excel',
    'xlsx': 'fa-file-excel',
    'ppt': 'fa-file-powerpoint',
    'pptx': 'fa-file-powerpoint',
    'txt': 'fa-file-alt',
    'zip': 'fa-file-archive',
    'rar': 'fa-file-archive',
    'image': 'fa-file-image',
    'video': 'fa-file-video',
    'audio': 'fa-file-audio'
  };
  return iconMap[fileType] || 'fa-file';
}

// Format file size for display
function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Format date for display
function formatDate(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  });
}

// Initialize event listeners when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Handle Escape key to close modals
  document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
      // Close all open modals
      const pdfModal = document.getElementById('pdfViewerModal');
      const filesModal = document.getElementById('subjectFilesModal');
      
      if (pdfModal && pdfModal.style.display === 'block') {
        closePdfViewerModal();
      }
      
      if (filesModal && filesModal.style.display === 'block') {
        closeSubjectFilesModal();
      }
    }
  });
}); 