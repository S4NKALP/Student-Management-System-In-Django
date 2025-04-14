// Global variables to track current filters
let currentPeriodFilter = '';
let currentSearchText = '';

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('HOD Dashboard initializing...');
    
    // Initialize filters
    initializeFilters();
    
    // Initialize Firebase if available
    if (typeof getDeviceToken === 'function') {
        getDeviceToken().catch(error => {
            console.error('Error initializing Firebase:', error);
        });
    }
});

// Initialize all filters
function initializeFilters() {
    // Get the filter elements
    const periodFilter = document.getElementById('periodFilter');
    const searchBox = document.getElementById('subjectSearch');
    const tableBody = document.getElementById('subjectsTableBody');

    if (!periodFilter || !searchBox || !tableBody) {
        console.error('Required elements not found');
        return;
    }

    // Reset filter values
    periodFilter.value = '';
    searchBox.value = '';
    currentPeriodFilter = '';
    currentSearchText = '';

    // Add event listeners
    periodFilter.addEventListener('change', function() {
        currentPeriodFilter = this.value;
        console.log('Period filter changed to:', currentPeriodFilter);
        applyFilters();
    });

    searchBox.addEventListener('input', function() {
        currentSearchText = this.value.toLowerCase();
        console.log('Search text changed to:', currentSearchText);
        applyFilters();
    });

    searchBox.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            this.value = '';
            currentSearchText = '';
            applyFilters();
        }
    });
}

// Apply both filters
function applyFilters() {
    const tableBody = document.getElementById('subjectsTableBody');
    if (!tableBody) {
        console.error('Subject table body not found');
        return;
    }
    
    const rows = tableBody.getElementsByTagName('tr');
    let visibleCount = 0;
    
    for (let i = 0; i < rows.length; i++) {
        const row = rows[i];
        
        // Skip the "no results" row
        if (row.cells.length === 1) continue;
        
        // Get cells content
        const nameCell = row.cells[0].textContent.toLowerCase();
        const codeCell = row.cells[1].textContent.toLowerCase();
        const periodCell = row.cells[2];
        
        // Get the period number from the cell
        let periodNumber = '';
        if (periodCell.hasAttribute('data-period')) {
            periodNumber = periodCell.getAttribute('data-period');
        } else {
            // Extract just the period number from text content
            const periodText = periodCell.textContent.trim();
            periodNumber = periodText.split(' ')[0];
        }
        
        // Clean up the period number (remove any non-numeric characters)
        periodNumber = periodNumber.replace(/\D/g, '');
        
        // Determine matches
        const matchesPeriod = !currentPeriodFilter || periodNumber === currentPeriodFilter;
        const matchesSearch = !currentSearchText || 
                            nameCell.includes(currentSearchText) || 
                            codeCell.includes(currentSearchText);
        
        // Show or hide based on both conditions
        if (matchesPeriod && matchesSearch) {
            row.style.display = '';
            visibleCount++;
        } else {
            row.style.display = 'none';
        }
    }
    
    // Show/hide "no results" message
    const noResultsRow = tableBody.querySelector('tr td[colspan="5"]');
    if (noResultsRow) {
        const parentRow = noResultsRow.parentElement;
        if (visibleCount === 0) {
            parentRow.style.display = '';
        } else {
            parentRow.style.display = 'none';
        }
    }
    
    console.log('Filter applied. Visible rows:', visibleCount);
}

// Initialize charts using Chart.js
function initializeCharts() {
    const chartCanvas = document.getElementById('subjectDistributionChart');
    if (!chartCanvas) return;
    
    const ctx = chartCanvas.getContext('2d');
    if (!ctx) return;
    
    // Get data attributes
    const courseName = chartCanvas.getAttribute('data-course-name') || 'Course';
    const durationType = chartCanvas.getAttribute('data-duration-type') || 'Year';
    
    // Parse chart data
    let chartData;
    try {
        chartData = JSON.parse(chartCanvas.getAttribute('data-chart-data') || '[]');
    } catch (e) {
        console.error('Error parsing chart data:', e);
        chartData = [0, 0, 0, 0];
    }
    
    // Create labels based on duration type
    const labels = [];
    chartData.forEach((value, index) => {
        const num = index + 1;
        const suffix = getSuffix(num);
        labels.push(`${num}${suffix} ${durationType}`);
    });
    
    // Create chart
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: chartData,
                backgroundColor: [
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 206, 86, 0.7)',
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(153, 102, 255, 0.7)',
                    'rgba(255, 159, 64, 0.7)',
                    'rgba(199, 199, 199, 0.7)',
                    'rgba(83, 102, 255, 0.7)'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                title: {
                    display: true,
                    text: `${courseName} Subjects by ${durationType}`
                }
            }
        }
    });
}

// Get ordinal suffix (1st, 2nd, 3rd, etc.)
function getSuffix(num) {
    if (num >= 11 && num <= 13) return 'th';
    
    switch (num % 10) {
        case 1: return 'st';
        case 2: return 'nd';
        case 3: return 'rd';
        default: return 'th';
    }
}

// Initialize section navigation
function initializeSectionNavigation() {
    const navButtons = document.querySelectorAll('[data-target]');
    
    navButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            showSection(targetId);
        });
    });
    
    // Initial section display
    const hash = window.location.hash.replace('#', '');
    if (hash && document.getElementById(hash)) {
        showSection(hash);
    }
}

// Show a specific section and update navigation
function showSection(sectionId) {
    // Hide all sections
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => {
        section.style.display = 'none';
    });
    
    // Show the selected section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.style.display = 'block';
        
        // Update navigation
        const navButtons = document.querySelectorAll('[data-target]');
        navButtons.forEach(button => {
            const isActive = button.getAttribute('data-target') === sectionId;
            if (isActive) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });
        
        // Update URL hash without scrolling
        const scrollPos = window.scrollY;
        window.location.hash = sectionId;
        window.scrollTo(0, scrollPos);
        
        // Apply filters if we're in the subjects section
        if (sectionId === 'subjectsSection') {
            setTimeout(applyFilters, 50);
        }
    }
}

// Subject action functions
function viewSubjectDetails(subjectId) {
    alert(`View details for subject ${subjectId}`);
}

function editSubject(subjectId) {
    alert(`Edit subject ${subjectId}`);
}

function confirmDeleteSubject(subjectId) {
    if (confirm('Are you sure you want to delete this subject?')) {
        alert(`Delete subject ${subjectId}`);
    }
}

function openAddSubjectModal() {
    alert('Add new subject');
}
