document.addEventListener('DOMContentLoaded', function() {
    // Force uppercase input for airport codes
    const airportInputs = document.querySelectorAll('input[id="origin"], input[id="destination"]');
    if (airportInputs) {
        airportInputs.forEach(input => {
            input.addEventListener('input', function() {
                this.value = this.value.toUpperCase();
                if (this.value.length > 3) {
                    this.value = this.value.slice(0, 3);
                }
            });
        });
    }
    
    // Set minimum date to today for date inputs
    const dateInputs = document.querySelectorAll('input[type="date"]');
    if (dateInputs) {
        const today = new Date().toISOString().split('T')[0];
        dateInputs.forEach(input => {
            if (!input.min) {
                input.min = today;
            }
        });
    }
    
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({ 
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add hover effects for cards with animation
    const cards = document.querySelectorAll('.card');
    if (cards) {
        cards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-5px)';
                this.style.boxShadow = '0 8px 20px rgba(0, 0, 0, 0.15)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = '0 6px 15px rgba(0, 0, 0, 0.1)';
            });
        });
    }
    
    // Add validation for the search form
    const searchForm = document.getElementById('flightSearchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const origin = document.getElementById('origin').value.trim();
            const destination = document.getElementById('destination').value.trim();
            const date = document.getElementById('date').value;
            
            let isValid = true;
            let errorMessage = '';
            
            // Validate airport codes
            if (origin.length !== 3 || !isValidAirportCode(origin)) {
                isValid = false;
                errorMessage = 'Please enter a valid 3-letter origin airport code';
            } else if (destination.length !== 3 || !isValidAirportCode(destination)) {
                isValid = false;
                errorMessage = 'Please enter a valid 3-letter destination airport code';
            } else if (origin === destination) {
                isValid = false;
                errorMessage = 'Origin and destination cannot be the same';
            }
            
            // Validate date
            if (!date) {
                isValid = false;
                errorMessage = 'Please select a travel date';
            } else {
                const selectedDate = new Date(date);
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                
                if (selectedDate < today) {
                    isValid = false;
                    errorMessage = 'Travel date cannot be in the past';
                }
                
                // Check if date is not too far in the future (e.g., 1 year max)
                const maxDate = new Date();
                maxDate.setFullYear(maxDate.getFullYear() + 1);
                
                if (selectedDate > maxDate) {
                    isValid = false;
                    errorMessage = 'Travel date cannot be more than 1 year in the future';
                }
            }
            
            if (!isValid) {
                e.preventDefault();
                showFormError(errorMessage);
            }
        });
    }
    
    // Helper function to check if a string is a valid airport code
    function isValidAirportCode(code) {
        return /^[A-Z]{3}$/.test(code);
    }
    
    // Function to show form errors
    function showFormError(message) {
        // Check if error alert already exists
        let errorAlert = document.querySelector('.search-form-error');
        
        if (!errorAlert) {
            // Create error alert
            errorAlert = document.createElement('div');
            errorAlert.className = 'alert alert-danger mt-3 search-form-error';
            errorAlert.setAttribute('role', 'alert');
            
            // Add dismiss button
            const dismissButton = document.createElement('button');
            dismissButton.type = 'button';
            dismissButton.className = 'btn-close';
            dismissButton.setAttribute('data-bs-dismiss', 'alert');
            dismissButton.setAttribute('aria-label', 'Close');
            
            errorAlert.appendChild(dismissButton);
            
            // Add to form
            const form = document.getElementById('flightSearchForm');
            form.appendChild(errorAlert);
        }
        
        // Update error message
        errorAlert.textContent = message;
        
        // Scroll to error message
        errorAlert.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
});
