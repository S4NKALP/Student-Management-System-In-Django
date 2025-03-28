document.addEventListener('DOMContentLoaded', function() {
  // Handle star rating selection for teacher feedback
  const teacherStars = document.querySelectorAll('[id^="teacherStar"]');
  const teacherLabels = document.querySelectorAll('label[for^="teacherStar"]');
  
  teacherLabels.forEach(label => {
    label.addEventListener('click', function() {
      const starId = this.getAttribute('for');
      const starNumber = parseInt(starId.replace('teacherStar', ''));
      
      // Update visual appearance
      teacherLabels.forEach((lbl, index) => {
        const star = lbl.querySelector('i');
        if (index < starNumber) {
          star.className = 'fas fa-star fs-4 text-warning';
        } else {
          star.className = 'far fa-star fs-4 text-warning';
        }
      });
      
      // Set the correct radio button
      document.getElementById(starId).checked = true;
    });
    
    // Add hover effects
    label.addEventListener('mouseenter', function() {
      const starId = this.getAttribute('for');
      const starNumber = parseInt(starId.replace('teacherStar', ''));
      
      teacherLabels.forEach((lbl, index) => {
        const star = lbl.querySelector('i');
        if (index < starNumber) {
          star.className = 'fas fa-star fs-4 text-warning';
        }
      });
    });
    
    label.addEventListener('mouseleave', function() {
      // Reset to selected state
      let selectedValue = 0;
      teacherStars.forEach((radio, index) => {
        if (radio.checked) {
          selectedValue = index + 1;
        }
      });
      
      teacherLabels.forEach((lbl, index) => {
        const star = lbl.querySelector('i');
        if (index < selectedValue) {
          star.className = 'fas fa-star fs-4 text-warning';
        } else {
          star.className = 'far fa-star fs-4 text-warning';
        }
      });
    });
  });
  
  // Handle star rating selection for institute feedback
  const instituteStars = document.querySelectorAll('[id^="instituteStar"]');
  const instituteLabels = document.querySelectorAll('label[for^="instituteStar"]');
  
  instituteLabels.forEach(label => {
    label.addEventListener('click', function() {
      const starId = this.getAttribute('for');
      const starNumber = parseInt(starId.replace('instituteStar', ''));
      
      // Update visual appearance
      instituteLabels.forEach((lbl, index) => {
        const star = lbl.querySelector('i');
        if (index < starNumber) {
          star.className = 'fas fa-star fs-4 text-warning';
        } else {
          star.className = 'far fa-star fs-4 text-warning';
        }
      });
      
      // Set the correct radio button
      document.getElementById(starId).checked = true;
    });
    
    // Add hover effects
    label.addEventListener('mouseenter', function() {
      const starId = this.getAttribute('for');
      const starNumber = parseInt(starId.replace('instituteStar', ''));
      
      instituteLabels.forEach((lbl, index) => {
        const star = lbl.querySelector('i');
        if (index < starNumber) {
          star.className = 'fas fa-star fs-4 text-warning';
        }
      });
    });
    
    label.addEventListener('mouseleave', function() {
      // Reset to selected state
      let selectedValue = 0;
      instituteStars.forEach((radio, index) => {
        if (radio.checked) {
          selectedValue = index + 1;
        }
      });
      
      instituteLabels.forEach((lbl, index) => {
        const star = lbl.querySelector('i');
        if (index < selectedValue) {
          star.className = 'fas fa-star fs-4 text-warning';
        } else {
          star.className = 'far fa-star fs-4 text-warning';
        }
      });
    });
  });
}); 