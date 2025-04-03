// Subject Materials Section Functions

function showSection(sectionId, forceOrSubjectId = null) {
    console.log('Showing section:', sectionId, 'force/subjectId:', forceOrSubjectId);
    
    // Special handling for subject materials section using the toggle function
    if (sectionId === 'subjectMaterialsSection') {
        const subjectId = forceOrSubjectId;
        toggleSubjectView('materials');
        
        // Get the section
        const section = document.getElementById(sectionId);
        if (section) {
            // Make sure the header div is visible and properly styled
            const headerDiv = section.querySelector('.d-flex.justify-content-between.align-items-center');
            if (headerDiv) {
                // Ensure header is visible with !important
                headerDiv.style.cssText = "display: flex !important; opacity: 1; visibility: visible;";
                
                // Make the heading more prominent
                const heading = headerDiv.querySelector('h3');
                if (heading) {
                    heading.style.fontWeight = 'bold';
                    heading.style.color = '#3F51B5';
                }
            }
            
            // Now load the content 
            loadSubjectMaterials(subjectId);
        }
        
        return;
    }
    
    // Special handling for subjects section using the toggle function
    if (sectionId === 'subjectsSection') {
        toggleSubjectView('subjects');
        return;
    }
    
    // Handle the case where we're being called from the back button
    const forceDisplay = forceOrSubjectId === true;
    // If not a boolean, treat as subjectId
    const subjectId = typeof forceOrSubjectId === 'boolean' ? null : forceOrSubjectId;
    
    // Special handling for forced navigation to subjects
    if (sectionId === 'subjectsSection' && forceDisplay) {
        console.log('FORCE NAVIGATION to subjects section');
        
        // Hide all other sections first
        document.querySelectorAll('.content-section').forEach(sect => {
            if (sect.id !== 'subjectsSection') {
                sect.style.display = 'none';
                sect.classList.remove('active');
            }
        });
        
        // Activate subjects section with high specificity
        const subjectsSection = document.getElementById('subjectsSection');
        if (subjectsSection) {
            // Force display using multiple methods
            subjectsSection.style.cssText = 'display: block !important; opacity: 1; visibility: visible;';
            subjectsSection.classList.add('active');
            
            // Force a redraw
            void subjectsSection.offsetHeight;
            
            // Add active class to subjects nav
            document.querySelectorAll('.nav-item').forEach(item => {
                const section = item.getAttribute('data-section');
                if (section === 'subjects') {
                    item.classList.add('active');
                } else {
                    item.classList.remove('active');
                }
            });
            
            // Update URL hash
            window.location.hash = 'subjectsSection';
            
            // Scroll to top
            window.scrollTo(0, 0);
            
            console.log('Force navigation complete.');
            return;
        }
    }
    
    // Special handling for subjects section to correctly set the active nav item
    if (sectionId === 'subjectsSection') {
        // Update URL hash to track the section
        window.location.hash = 'subjectsSection';
        console.log('Setting hash to subjectsSection');
    }
    
    // Debug output - list all sections in DOM
    const allSections = document.querySelectorAll('.content-section');
    console.log('Available sections:');
    allSections.forEach(section => {
        console.log('- Section ID:', section.id, 'Display:', section.style.display, 'Classes:', section.className);
    });
    
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
        section.style.display = 'none';
        console.log('Hiding section:', section.id);
    });
    
    // First remove active class from all nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Then add active class to the correct nav item
    document.querySelectorAll('.nav-item').forEach(item => {
        const navSection = item.getAttribute('data-section');
        console.log('Nav item section:', navSection, 'comparing with:', sectionId);
        
        if (navSection === sectionId || 
            (sectionId === 'subjectMaterialsSection' && navSection === 'subjects') ||
            (sectionId === 'subjectsSection' && navSection === 'subjects')) {
            item.classList.add('active');
            console.log('Activated nav item:', navSection);
        }
    });
    
    // Show the selected section
    const selectedSection = document.getElementById(sectionId);
    if (selectedSection) {
        console.log('Found section to show:', sectionId);
        selectedSection.classList.add('active');
        selectedSection.style.display = 'block';
        
        // Force browser to recognize the display change
        setTimeout(() => {
            selectedSection.style.opacity = '0.99';
            setTimeout(() => {
                selectedSection.style.opacity = '1';
            }, 10);
        }, 10);
    } else {
        console.error('Could not find section with ID:', sectionId);
    }
    
    // Special handling for subjects section to ensure it's visible
    if (sectionId === 'subjectsSection') {
        const subjectsSection = document.getElementById('subjectsSection');
        if (subjectsSection) {
            console.log('Forcing subjects section to display');
            subjectsSection.style.display = 'block';
            subjectsSection.classList.add('active');
            
            // The following forces a reflow
            void subjectsSection.offsetWidth;
        } else {
            console.error('Subjects section element not found in DOM');
        }
    }
    
    // Scroll to top
    window.scrollTo(0, 0);
}

// Custom API function to get subject materials directly
function getSubjectMaterials(subjectId = null) {
    return new Promise((resolve, reject) => {
        // Get the CSRF token
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Build the URL for the API endpoint
        let url = '/app/get-teacher-subjects/';
        
        console.log('Fetching teacher subjects from:', url);
        
        // First fetch the subjects
        fetch(url, {
            headers: {
                'X-CSRFToken': csrftoken
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(subjectsData => {
            console.log('Teacher subjects data:', subjectsData);
            
            if (!subjectsData.success || !subjectsData.subjects || subjectsData.subjects.length === 0) {
                console.log('No subjects found or empty response');
                resolve({ subjects: [] });
                return;
            }
            
            let subjects = subjectsData.subjects;
            
            // If a specific subject is requested, filter the subjects
            if (subjectId) {
                console.log('Filtering subjects by ID:', subjectId);
                subjects = subjects.filter(subject => subject.id.toString() === subjectId.toString());
                
                if (subjects.length === 0) {
                    console.log('No matching subject found for ID:', subjectId);
                    resolve({ subjects: [] });
                    return;
                }
            }
            
            // Now we need to get the files for each subject
            // We'll use the manage_subject_files endpoint with a GET request
            // and parse the HTML response to extract the files
            
            // Create a result object to store the subjects with their files
            const result = {
                subjects: []
            };
            
            // Process each subject to get its files
            const promises = subjects.map(subject => {
                const filesUrl = `/app/manage-subject-files/?subject=${subject.id}`;
                console.log(`Fetching files for subject ${subject.name} (ID: ${subject.id}) from: ${filesUrl}`);
                
                return fetch(filesUrl, {
                    headers: {
                        'X-CSRFToken': csrftoken
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    return response.text();
                })
                .then(html => {
                    // Parse the HTML to extract the files
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    
                    console.log(`Parsing HTML response for subject ${subject.name}`);
                    
                    // Try different ways to find the subject card
                    let subjectCard = null;
                    let cardBody = null;
                    
                    // Method 1: Find by exact heading text
                    const headings = Array.from(doc.querySelectorAll('.card-header h5, .card-title'));
                    subjectCard = headings.find(h5 => h5.textContent.trim() === subject.name);
                    
                    if (subjectCard) {
                        console.log(`Found subject card for ${subject.name} using heading match`);
                        cardBody = subjectCard.closest('.card')?.querySelector('.card-body');
                    } else {
                        // Method 2: Find by card with subject ID in attributes
                        const cards = doc.querySelectorAll('.card[data-subject-id="' + subject.id + '"], .card[id*="subject-' + subject.id + '"]');
                        if (cards.length > 0) {
                            console.log(`Found subject card for ${subject.name} using ID attribute`);
                            subjectCard = cards[0];
                            cardBody = subjectCard.querySelector('.card-body');
                        } else {
                            // Method 3: Just take the first card if there's only one subject requested
                            if (subjectId) {
                                const allCards = doc.querySelectorAll('.card');
                                if (allCards.length > 0) {
                                    console.log(`Using first card for ${subject.name} as fallback`);
                                    subjectCard = allCards[0];
                                    cardBody = subjectCard.querySelector('.card-body');
                                }
                            }
                        }
                    }
                    
                    const files = [];
                    let hasSyllabus = false;
                    
                    // If we found a card body with a table, extract the files
                    if (cardBody) {
                        // Look for table rows
                        const fileRows = cardBody.querySelectorAll('table tbody tr');
                        console.log(`Found ${fileRows.length} file rows for subject ${subject.name}`);
                        
                        fileRows.forEach(row => {
                            const columns = row.querySelectorAll('td');
                            if (columns.length >= 3) {  // Need at least 3 columns
                                const title = columns[0].textContent.trim();
                                const description = columns.length > 1 ? columns[1].textContent.trim() : '';
                                const date = columns.length > 2 ? columns[2].textContent.trim() : '';
                                
                                // Extract file ID from the delete button
                                const deleteBtn = row.querySelector('button[onclick*="deleteFile"], button[data-file-id]');
                                let fileId = null;
                                
                                if (deleteBtn) {
                                    // Try onclick attribute
                                    const onClickAttr = deleteBtn.getAttribute('onclick');
                                    if (onClickAttr) {
                                        const match = onClickAttr.match(/deleteFile\(['"]([^'"]*)['"]\)/);
                                        if (match && match[1]) {
                                            fileId = match[1];
                                        }
                                    }
                                    
                                    // Try data attribute if onclick failed
                                    if (!fileId) {
                                        fileId = deleteBtn.getAttribute('data-file-id');
                                    }
                                }
                                
                                // Extract file URL from the download link
                                const actionCell = columns[columns.length - 1]; // Last column usually has actions
                                const downloadLink = actionCell.querySelector('a[href]:not([href="#"])');
                                let fileUrl = null;
                                
                                if (downloadLink) {
                                    fileUrl = downloadLink.getAttribute('href');
                                }
                                
                                // Check if this is a syllabus file based on title or other indicators
                                const isSyllabus = title.toLowerCase().includes('syllabus');
                                
                                // Set the syllabus flag for the subject if this file is a syllabus
                                if (isSyllabus) {
                                    hasSyllabus = true;
                                }
                                
                                files.push({
                                    id: fileId,
                                    title: title,
                                    description: description,
                                    uploaded_on: date,
                                    file_url: fileUrl,
                                    file_type: isSyllabus ? 'syllabus' : 'material'
                                });
                                
                                console.log(`Added file: ${title} for subject ${subject.name}`);
                            }
                        });
                    } else {
                        console.log(`Could not find card body for subject ${subject.name}`);
                    }
                    
                    // Check if the subject has a syllabus PDF using the View Syllabus button existence
                    const syllabusBtn = doc.querySelector(`a[href*="/subject/${subject.id}/syllabus/"], button[onclick*="viewSyllabus('${subject.id}')"]`);
                    if (syllabusBtn) {
                        console.log(`Found syllabus button for subject ${subject.name}`);
                        hasSyllabus = true;
                    }
                    
                    // Add this subject with its files to the result
                    result.subjects.push({
                        ...subject,
                        materials: files,
                        has_syllabus: hasSyllabus
                    });
                    
                    console.log(`Finished processing subject ${subject.name}, found ${files.length} files`);
                });
            });
            
            // Wait for all promises to resolve
            Promise.all(promises)
                .then(() => {
                    console.log('Final result:', result);
                    resolve(result);
                })
                .catch(error => {
                    console.error('Error processing subjects:', error);
                    reject(error);
                });
        })
        .catch(error => {
            console.error('Error fetching subjects:', error);
            reject(error);
        });
    });
}

function loadSubjectMaterials(subjectId = null) {
    const contentDiv = document.getElementById('subjectMaterialsContent');
    if (!contentDiv) {
        console.error('Subject materials content container not found');
        return;
    }
    
    // Show loading state in content area only
    contentDiv.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Loading subject materials...</p>
        </div>
    `;
    
    console.log('==== LOADING SUBJECT MATERIALS ====');
    console.log('Subject ID:', subjectId);
    
    // Build the URL with optional subject filter
    let url = '/app/manage-subject-files/';
    if (subjectId) {
        url += `?subject=${subjectId}`;
    }
    
    console.log('Fetching from URL:', url);
    
    // Create a direct link to the materials as a backup
    const directLink = document.createElement('div');
    directLink.className = 'text-center mt-3';
    directLink.innerHTML = `
        <p>If materials don't load automatically, try:</p>
        <a href="${url}" class="btn btn-outline-primary" target="_blank">
            <i class="fas fa-external-link-alt me-1"></i> Open Subject Materials in New Tab
        </a>
    `;
    
    // Fetch the materials page directly
    fetch(url, {
        headers: {
            'Accept': 'text/html',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        console.log('Response status:', response.status);
        console.log('Response type:', response.headers.get('content-type'));
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.text();
    })
    .then(html => {
        console.log('Received HTML content of length:', html.length);
        
        if (!html || html.trim().length === 0) {
            console.error('Empty response received');
            contentDiv.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>Empty response received from server</strong>
                </div>
            `;
            contentDiv.appendChild(directLink);
            return;
        }
        
        // Create a temporary div to hold the HTML content
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        
        console.log('HTML parsed, searching for content...');
        
        // Clear the content div
        contentDiv.innerHTML = '';
        
        // Add back button at the top of the content for mobile
        const mobileBackNav = document.createElement('div');
        mobileBackNav.className = 'd-block d-md-none text-center mb-3';
        mobileBackNav.innerHTML = `
            <button class="btn btn-secondary w-100" onclick="showSection('subjectsSection'); return false;">
                <i class="fas fa-arrow-left me-2"></i> Back to Subjects
            </button>
        `;
        contentDiv.appendChild(mobileBackNav);
        
        // Look for subjects and display them, trying multiple selectors
        let contentFound = false;
        
        // First approach: find the row of cards
        const subjectsRow = tempDiv.querySelector('.content-section .row, .content-card .row, .row');
        if (subjectsRow) {
            console.log('Found subjects row with', subjectsRow.children.length, 'children');
            contentDiv.innerHTML = '';
            const newRow = document.createElement('div');
            newRow.className = 'row';
            newRow.style.display = 'flex';
            newRow.style.flexWrap = 'wrap';
            newRow.style.margin = '0 -12px'; // Negative margin to offset the padding
            
            // Copy each card individually to avoid any parent context issues
            Array.from(subjectsRow.querySelectorAll('.col-md-6, .col-lg-4, .col')).forEach(col => {
                newRow.appendChild(col.cloneNode(true));
            });
            
            if (newRow.children.length > 0) {
                contentDiv.appendChild(newRow);
                contentFound = true;
                console.log('Added', newRow.children.length, 'subject cards to the content');
            }
        }
        
        // Second approach: find individual cards if no row found
        if (!contentFound) {
            const cards = tempDiv.querySelectorAll('.card');
            if (cards && cards.length > 0) {
                console.log('Found', cards.length, 'individual cards');
                contentDiv.innerHTML = '';
                const newRow = document.createElement('div');
                newRow.className = 'row';
                newRow.style.display = 'flex';
                newRow.style.flexWrap = 'wrap';
                newRow.style.margin = '0 -12px'; // Negative margin to offset the padding
                
                cards.forEach(card => {
                    const col = document.createElement('div');
                    col.className = 'col-md-6 col-lg-4 mb-4';
                    // Add explicit styling to ensure visibility
                    col.style.display = 'block';
                    col.style.padding = '0 12px';
                    col.style.marginBottom = '24px';
                    col.style.width = '33.333%';
                    col.style.minWidth = '300px';
                    
                    // Clone the card and add explicit styles
                    const cardClone = card.cloneNode(true);
                    cardClone.style.display = 'flex';
                    cardClone.style.flexDirection = 'column';
                    cardClone.style.height = '100%';
                    cardClone.style.border = '1px solid rgba(0,0,0,0.125)';
                    cardClone.style.borderRadius = '0.25rem';
                    cardClone.style.overflow = 'hidden';
                    cardClone.style.backgroundColor = '#fff';
                    
                    col.appendChild(cardClone);
                    newRow.appendChild(col);
                });
                
                // Clear and append with explicit styles
                contentDiv.style.display = 'block';
                contentDiv.style.width = '100%';
                contentDiv.style.visibility = 'visible';
                contentDiv.appendChild(newRow);
                contentFound = true;
                console.log('Added cards to content as individual items with explicit styles');
                
                // Force redraw
                setTimeout(() => {
                    contentDiv.style.opacity = '0.99';
                    setTimeout(() => {
                        contentDiv.style.opacity = '1';
                    }, 50);
                }, 50);
            }
        }
        
        // Third approach: try to find any content card
        if (!contentFound) {
            const contentCard = tempDiv.querySelector('.content-card');
            if (contentCard) {
                console.log('Found content card, using its content');
                // Remove header if present to avoid duplicate headers
                const header = contentCard.querySelector('.d-flex.justify-content-between.align-items-center');
                if (header) {
                    console.log('Removing header from content card');
                    header.remove();
                }
                
                contentDiv.innerHTML = contentCard.innerHTML;
                contentFound = true;
            }
        }
        
        // Fourth approach: direct render of subjects
        if (!contentFound) {
            console.log('No content found in HTML, trying to manually render subjects');
            // Directly call the API to get subjects
            fetch('/app/get-teacher-subjects/')
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.subjects && data.subjects.length > 0) {
                        console.log('Got', data.subjects.length, 'subjects from API');
                        
                        // Filter by subject ID if provided
                        let subjects = data.subjects;
                        if (subjectId) {
                            subjects = subjects.filter(s => s.id == subjectId);
                        }
                        
                        if (subjects.length === 0) {
                            contentDiv.innerHTML = `
                                <div class="alert alert-info">
                                    <i class="fas fa-info-circle me-2"></i>
                                    No subjects found matching your criteria.
                                </div>
                            `;
                            contentDiv.appendChild(directLink);
                            return;
                        }
                        
                        // Manually render subjects
                        contentDiv.innerHTML = '';
                        const row = document.createElement('div');
                        row.className = 'row';
                        row.style.display = 'flex';
                        row.style.flexWrap = 'wrap';
                        row.style.margin = '0 -12px';
                        
                        subjects.forEach(subject => {
                            const col = document.createElement('div');
                            col.className = 'col-md-6 col-lg-4 mb-4';
                            col.style.display = 'block';
                            col.style.padding = '0 12px';
                            col.style.marginBottom = '24px';
                            col.style.width = '33.333%';
                            col.style.minWidth = '300px';
                            
                            const card = document.createElement('div');
                            card.className = 'card border-0 shadow-sm h-100';
                            card.style.display = 'flex';
                            card.style.flexDirection = 'column';
                            card.style.height = '100%';
                            card.style.border = '1px solid rgba(0,0,0,0.125)';
                            card.style.borderRadius = '0.25rem';
                            card.style.overflow = 'hidden';
                            card.style.backgroundColor = '#fff';
                            
                            const cardHeader = document.createElement('div');
                            cardHeader.className = 'card-header bg-light py-3';
                            cardHeader.style.backgroundColor = '#f8f9fa';
                            cardHeader.style.padding = '1rem';
                            
                            const title = document.createElement('h5');
                            title.className = 'card-title mb-0';
                            title.textContent = subject.name;
                            
                            const subtitle = document.createElement('p');
                            subtitle.className = 'text-muted mb-0 small';
                            subtitle.textContent = `${subject.course__name || ''} - ${subject.semester_or_year || 'N/A'}`;
                            
                            cardHeader.appendChild(title);
                            cardHeader.appendChild(subtitle);
                            
                            const cardBody = document.createElement('div');
                            cardBody.className = 'card-body';
                            cardBody.style.padding = '1rem';
                            cardBody.style.flexGrow = '1';
                            
                            const fileStatus = document.createElement('p');
                            fileStatus.className = 'text-muted small mb-3';
                            fileStatus.innerHTML = '<i class="fas fa-file me-1"></i> Loading files...';
                            
                            const btnContainer = document.createElement('div');
                            btnContainer.className = 'mb-3';
                            
                            const uploadBtn = document.createElement('button');
                            uploadBtn.className = 'btn btn-primary w-100';
                            uploadBtn.innerHTML = `<i class="fas fa-file-upload me-1"></i> Upload to ${subject.name}`;
                            uploadBtn.onclick = function() { openUploadModal(subject.id); };
                            
                            btnContainer.appendChild(uploadBtn);
                            cardBody.appendChild(fileStatus);
                            cardBody.appendChild(btnContainer);
                            
                            card.appendChild(cardHeader);
                            card.appendChild(cardBody);
                            col.appendChild(card);
                            row.appendChild(col);
                        });
                        
                        contentDiv.appendChild(row);
                        contentFound = true;
                    } else {
                        console.log('No subjects returned from API');
                        contentDiv.innerHTML = `
                            <div class="alert alert-info">
                                <i class="fas fa-info-circle me-2"></i>
                                No subjects assigned to you. Please contact administrator.
                            </div>
                        `;
                        contentDiv.appendChild(directLink);
                    }
                })
                .catch(error => {
                    console.error('Error fetching subjects:', error);
                    contentDiv.innerHTML = `
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-circle me-2"></i>
                            Error fetching subjects: ${error.message}
                        </div>
                    `;
                    contentDiv.appendChild(directLink);
                });
        }
        
        // If all else fails, show a simple message
        if (!contentFound) {
            console.log('All content extraction methods failed');
            contentDiv.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    <span>Unable to display subject materials automatically.</span>
                </div>
            `;
            contentDiv.appendChild(directLink);
        }
        
        // Re-attach event handlers for the buttons after a short delay
        setTimeout(() => {
            console.log('Attaching event handlers to buttons');
            // Add event listeners for upload buttons
            contentDiv.querySelectorAll('[onclick*="openUploadModal"]').forEach(button => {
                const match = button.getAttribute('onclick')?.match(/openUploadModal\(['"]([^'"]*)['"]\)/);
                if (match) {
                    const id = match[1];
                    console.log('Found upload button for subject ID:', id);
                    button.setAttribute('onclick', `openUploadModal('${id}')`);
                }
            });
            
            // Add event listeners for delete buttons
            contentDiv.querySelectorAll('[onclick*="deleteFile"]').forEach(button => {
                const match = button.getAttribute('onclick')?.match(/deleteFile\(['"]([^'"]*)['"]\)/);
                if (match) {
                    const id = match[1];
                    console.log('Found delete button for file ID:', id);
                    button.setAttribute('onclick', `deleteFile('${id}')`);
                }
            });
            
            // Add upload button if none exists
            if (!contentDiv.querySelector('[onclick*="openUploadModal"]')) {
                console.log('No upload buttons found, adding one');
                const uploadBtn = document.createElement('div');
                uploadBtn.className = 'text-center mt-4';
                uploadBtn.innerHTML = `
                    <button class="btn btn-primary" onclick="openUploadModal()">
                        <i class="fas fa-file-upload me-1"></i> Upload New Material
                    </button>
                `;
                contentDiv.appendChild(uploadBtn);
            }
        }, 200);
    })
    .catch(error => {
        console.error('Error loading subject materials:', error);
        contentDiv.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>
                <strong>Error loading subject materials: ${error.message}</strong>
            </div>
            <div class="text-center mt-4">
                <button class="btn btn-primary" onclick="openUploadModal()">
                    <i class="fas fa-file-upload me-1"></i> Upload New Material
                </button>
                <a href="${url}" class="btn btn-outline-secondary ms-2" target="_blank">
                    <i class="fas fa-external-link-alt me-1"></i> Open in New Tab
                </a>
            </div>
        `;
    });
}

function openUploadModal(subjectId = '') {
    console.log('Opening upload modal with subject ID:', subjectId);
    const modal = document.getElementById('uploadFileModal');
    const subjectSelect = document.getElementById('subject_id');
    const responseDiv = document.getElementById('uploadResponse');
    
    if (!modal || !subjectSelect) {
        console.error('Modal or subject select not found');
        return;
    }
    
    // Reset the form
    const uploadForm = document.getElementById('uploadFileForm');
    if (uploadForm) {
        uploadForm.reset();
    }
    
    if (responseDiv) {
        responseDiv.style.display = 'none';
    }
    
    // If a subject ID was provided, pre-select it
    if (subjectId && subjectSelect) {
        subjectSelect.value = subjectId;
    }
    
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeUploadModal() {
    const modal = document.getElementById('uploadFileModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
    }
}

function deleteFile(fileId) {
    fileIdToDelete = fileId;
    const modal = document.getElementById('confirmationModal');
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
}

function closeConfirmationModal() {
    const modal = document.getElementById('confirmationModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
    }
    fileIdToDelete = null;
}

// Function to view subject syllabus
function viewSyllabus(subjectId) {
    if (!subjectId) return;
    
    // Get the button element that was clicked
    const syllabusButton = document.querySelector(`.syllabus-button[data-subject-id="${subjectId}"]`);
    
    // Check if button was hidden - if so, there's no syllabus available
    if (syllabusButton && syllabusButton.style.display === 'none') {
        alert('No syllabus available for this subject.');
        return;
    }
    
    // Show loading indicator
    const loadingModal = document.createElement('div');
    loadingModal.style.position = 'fixed';
    loadingModal.style.top = '0';
    loadingModal.style.left = '0';
    loadingModal.style.width = '100%';
    loadingModal.style.height = '100%';
    loadingModal.style.backgroundColor = 'rgba(0,0,0,0.5)';
    loadingModal.style.display = 'flex';
    loadingModal.style.justifyContent = 'center';
    loadingModal.style.alignItems = 'center';
    loadingModal.style.zIndex = '10000';
    
    loadingModal.innerHTML = `
        <div class="bg-white p-4 rounded shadow-sm text-center">
            <div class="spinner-border text-primary mb-3" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mb-0">Loading syllabus...</p>
        </div>
    `;
    
    document.body.appendChild(loadingModal);
    
    // Get the CSRF token
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Fetch the syllabus URL
    fetch(`/app/subject/${subjectId}/syllabus/`, {
        headers: {
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => {
        if (!response.ok) {
            // If response is not OK (e.g., 404), throw an error with status
            if (response.status === 404) {
                throw new Error('Syllabus not found');
            }
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // Remove loading indicator
        document.body.removeChild(loadingModal);
        
        if (data.success) {
            // Open the syllabus in a new tab
            window.open(data.file_url, '_blank');
        } else {
            // Show error message
            alert(data.message || 'No syllabus available for this subject.');
        }
    })
    .catch(error => {
        console.error('Error fetching syllabus:', error);
        document.body.removeChild(loadingModal);
        
        // Show a more user-friendly message
        if (error.message === 'Syllabus not found') {
            alert('No syllabus available for this subject.');
            
            // Hide the button to prevent future attempts
            if (syllabusButton) {
                syllabusButton.style.display = 'none';
            }
        } else {
            alert('Error fetching syllabus. Please try again.');
        }
    });
}

// Function to toggle between subjects list and subject materials
function toggleSubjectView(view) {
    const subjectsSection = document.getElementById('subjectsSection');
    const materialsSection = document.getElementById('subjectMaterialsSection');
    
    console.log('Toggling subject view to:', view);
    
    if (view === 'subjects') {
        // Show subjects section
        subjectsSection.style.display = 'block';
        subjectsSection.classList.add('active');
        
        // Hide materials section
        materialsSection.style.display = 'none';
        materialsSection.classList.remove('active');
        
        // Activate the correct nav item
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            const navSection = item.getAttribute('data-section');
            if (navSection === 'subjects') {
                item.classList.add('active');
            }
        });
        
        console.log('Switched to subjects view');
    } else if (view === 'materials') {
        // Show materials section
        materialsSection.style.display = 'block';
        materialsSection.classList.add('active');
        
        // Hide subjects section
        subjectsSection.style.display = 'none';
        subjectsSection.classList.remove('active');
        
        // Keep the subjects nav item active
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            const navSection = item.getAttribute('data-section');
            if (navSection === 'subjects') {
                item.classList.add('active');
            }
        });
        
        console.log('Switched to materials view');
    }
} 