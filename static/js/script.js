// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navMenu = document.querySelector('nav ul');
    
    if (mobileMenuBtn && navMenu) {
        mobileMenuBtn.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }
    
    // Multi-step form functionality
    const formSteps = document.querySelectorAll('.form-step');
    const nextBtns = document.querySelectorAll('.next-step');
    const prevBtns = document.querySelectorAll('.prev-step');
    const progressSteps = document.querySelectorAll('.progress-step');
    const progressLines = document.querySelectorAll('.progress-line');
    
    if (formSteps.length > 0) {
        let currentStep = 0;
        
        // Initialize the form
        updateFormSteps();
        updateProgressBar();
        
        // Next button click event
        nextBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                if (validateStep(currentStep)) {
                    currentStep++;
                    updateFormSteps();
                    updateProgressBar();
                    window.scrollTo(0, 0);
                }
            });
        });
        
        // Previous button click event
        prevBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                currentStep--;
                updateFormSteps();
                updateProgressBar();
                window.scrollTo(0, 0);
            });
        });
        
        // Update form steps visibility
        function updateFormSteps() {
            formSteps.forEach((step, index) => {
                if (index === currentStep) {
                    step.classList.add('active');
                } else {
                    step.classList.remove('active');
                }
            });
        }
        
        // Update progress bar
        function updateProgressBar() {
            progressSteps.forEach((step, index) => {
                if (index <= currentStep) {
                    step.classList.add('active');
                    if (index < currentStep) {
                        step.classList.add('completed');
                    } else {
                        step.classList.remove('completed');
                    }
                } else {
                    step.classList.remove('active');
                    step.classList.remove('completed');
                }
            });
            
            progressLines.forEach((line, index) => {
                if (index < currentStep) {
                    line.classList.add('active');
                } else {
                    line.classList.remove('active');
                }
            });
        }
        
        // Validate each step before proceeding
        function validateStep(stepIndex) {
            const currentFormStep = formSteps[stepIndex];
            let isValid = true;
            
            // Get all required inputs in the current step
            const requiredInputs = currentFormStep.querySelectorAll('[required]');
            
            requiredInputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    showError(input, 'This field is required');
                } else {
                    clearError(input);
                    
                    // Additional validation based on input type
                    if (input.type === 'email' && !validateEmail(input.value)) {
                        isValid = false;
                        showError(input, 'Please enter a valid email address');
                    } else if (input.type === 'tel' && !validatePhone(input.value)) {
                        isValid = false;
                        showError(input, 'Please enter a valid phone number');
                    }
                }
            });
            
            // Check if at least one checkbox is selected in material categories
            if (stepIndex === 2) {
                const materialCheckboxes = currentFormStep.querySelectorAll('.material-category input[type="checkbox"]');
                let atLeastOneChecked = false;
                
                materialCheckboxes.forEach(checkbox => {
                    if (checkbox.checked) {
                        atLeastOneChecked = true;
                    }
                });
                
                if (!atLeastOneChecked) {
                    isValid = false;
                    const categoriesContainer = currentFormStep.querySelector('.material-categories');
                    showContainerError(categoriesContainer, 'Please select at least one category');
                } else {
                    const categoriesContainer = currentFormStep.querySelector('.material-categories');
                    clearContainerError(categoriesContainer);
                }
            }
            
            // Check terms acceptance in the final step
            if (stepIndex === 3) {
                const termsCheckbox = currentFormStep.querySelector('#terms');
                if (termsCheckbox && !termsCheckbox.checked) {
                    isValid = false;
                    showCheckboxError(termsCheckbox, 'You must accept the terms and conditions');
                } else if (termsCheckbox) {
                    clearCheckboxError(termsCheckbox);
                }
            }
            
            return isValid;
        }
        
        // Show error message for an input
        function showError(input, message) {
            const formGroup = input.closest('.form-group');
            let errorElement = formGroup.querySelector('.error-message');
            
            if (!errorElement) {
                errorElement = document.createElement('div');
                errorElement.className = 'error-message';
                formGroup.appendChild(errorElement);
            }
            
            errorElement.textContent = message;
            formGroup.classList.add('error');
            input.classList.add('error');
        }
        
        // Clear error message for an input
        function clearError(input) {
            const formGroup = input.closest('.form-group');
            const errorElement = formGroup.querySelector('.error-message');
            
            if (errorElement) {
                errorElement.textContent = '';
            }
            
            formGroup.classList.remove('error');
            input.classList.remove('error');
        }
        
        // Show error for container elements
        function showContainerError(container, message) {
            let errorElement = container.nextElementSibling;
            
            if (!errorElement || !errorElement.classList.contains('error-message')) {
                errorElement = document.createElement('div');
                errorElement.className = 'error-message';
                container.parentNode.insertBefore(errorElement, container.nextSibling);
            }
            
            errorElement.textContent = message;
            container.classList.add('error');
        }
        
        // Clear error for container elements
        function clearContainerError(container) {
            const errorElement = container.nextElementSibling;
            
            if (errorElement && errorElement.classList.contains('error-message')) {
                errorElement.textContent = '';
            }
            
            container.classList.remove('error');
        }
        
        // Show error for checkbox
        function showCheckboxError(checkbox, message) {
            const checkboxContainer = checkbox.closest('.checkbox-container');
            let errorElement = checkboxContainer.nextElementSibling;
            
            if (!errorElement || !errorElement.classList.contains('error-message')) {
                errorElement = document.createElement('div');
                errorElement.className = 'error-message';
                checkboxContainer.parentNode.insertBefore(errorElement, checkboxContainer.nextSibling);
            }
            
            errorElement.textContent = message;
            checkboxContainer.classList.add('error');
        }
        
        // Clear error for checkbox
        function clearCheckboxError(checkbox) {
            const checkboxContainer = checkbox.closest('.checkbox-container');
            const errorElement = checkboxContainer.nextElementSibling;
            
            if (errorElement && errorElement.classList.contains('error-message')) {
                errorElement.textContent = '';
            }
            
            checkboxContainer.classList.remove('error');
        }
    }
    
    // OTP input functionality
    const otpInputs = document.querySelectorAll('.otp-digit');
    
    if (otpInputs.length > 0) {
        otpInputs.forEach((input, index) => {
            input.addEventListener('keyup', function(e) {
                const currentInput = input;
                const nextInput = input.nextElementSibling;
                const prevInput = input.previousElementSibling;
                
                // If the value has length greater than 1, set it to the first digit
                if (currentInput.value.length > 1) {
                    currentInput.value = currentInput.value[0];
                    return;
                }
                
                // If the next input exists and the current input is not empty
                if (nextInput && currentInput.value !== '') {
                    nextInput.focus();
                }
                
                // If the backspace key is pressed
                if (e.key === 'Backspace') {
                    // Clear all inputs that come after
                    const inputs = [...otpInputs];
                    inputs.forEach((input, idx) => {
                        if (idx >= index) {
                            input.value = '';
                        }
                    });
                    
                    // Focus the previous input if it exists
                    if (prevInput) {
                        prevInput.focus();
                    }
                }
            });
            
            // Handle paste event
            input.addEventListener('paste', function(e) {
                e.preventDefault();
                const pastedData = e.clipboardData.getData('text');
                const otpDigits = pastedData.slice(0, otpInputs.length).split('');
                
                otpInputs.forEach((input, index) => {
                    if (otpDigits[index]) {
                        input.value = otpDigits[index];
                    }
                });
                
                // Focus the last input with a value or the first empty input
                let lastFilledIndex = otpInputs.length - 1;
                while (lastFilledIndex >= 0 && !otpInputs[lastFilledIndex].value) {
                    lastFilledIndex--;
                }
                
                if (lastFilledIndex < otpInputs.length - 1) {
                    otpInputs[lastFilledIndex + 1].focus();
                } else {
                    otpInputs[lastFilledIndex].focus();
                }
            });
        });
    }
    
    // Toggle password visibility
    const togglePasswordBtns = document.querySelectorAll('.toggle-password');
    
    if (togglePasswordBtns.length > 0) {
        togglePasswordBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const passwordInput = this.previousElementSibling;
                const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
                passwordInput.setAttribute('type', type);
                
                // Toggle icon
                this.innerHTML = type === 'password' ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
            });
        });
    }
    
    // File upload preview
    const fileUploadInputs = document.querySelectorAll('.file-upload input');
    
    if (fileUploadInputs.length > 0) {
        fileUploadInputs.forEach(input => {
            input.addEventListener('change', function() {
                const filePreview = this.closest('.file-upload').nextElementSibling;
                
                if (filePreview && filePreview.classList.contains('file-preview')) {
                    filePreview.innerHTML = '';
                    
                    if (this.files && this.files.length > 0) {
                        for (let i = 0; i < this.files.length; i++) {
                            const file = this.files[i];
                            const reader = new FileReader();
                            
                            reader.onload = function(e) {
                                const previewItem = document.createElement('div');
                                previewItem.className = 'file-preview-item';
                                
                                const img = document.createElement('img');
                                img.src = e.target.result;
                                
                                const removeBtn = document.createElement('div');
                                removeBtn.className = 'file-preview-remove';
                                removeBtn.innerHTML = '<i class="fas fa-times"></i>';
                                
                                previewItem.appendChild(img);
                                previewItem.appendChild(removeBtn);
                                filePreview.appendChild(previewItem);
                                
                                // Remove button functionality
                                removeBtn.addEventListener('click', function() {
                                    previewItem.remove();
                                    // Note: This doesn't actually remove the file from the input
                                    // In a real application, you would need to handle this properly
                                });
                            };
                            
                            reader.readAsDataURL(file);
                        }
                    }
                }
            });
        });
    }
    
    // Advanced search toggle
    const advancedSearchToggle = document.querySelector('.advanced-search-toggle');
    const advancedSearchFilters = document.querySelector('.advanced-search-filters');
    
    if (advancedSearchToggle && advancedSearchFilters) {
        advancedSearchToggle.addEventListener('click', function() {
            advancedSearchFilters.classList.toggle('active');
            
            // Update toggle text
            const toggleText = this.querySelector('span');
            if (toggleText) {
                toggleText.textContent = advancedSearchFilters.classList.contains('active') ? 'Hide Advanced Filters' : 'Show Advanced Filters';
            }
            
            // Update toggle icon
            const toggleIcon = this.querySelector('i');
            if (toggleIcon) {
                toggleIcon.className = advancedSearchFilters.classList.contains('active') ? 'fas fa-chevron-up' : 'fas fa-chevron-down';
            }
        });
    }
    
    // Helper validation functions
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    function validatePhone(phone) {
        // Basic phone validation - adjust as needed for your requirements
        const re = /^[0-9]{10}$/;
        return re.test(phone.replace(/[\s()-]/g, ''));
    }
});

// Profile dropdown functionality
function toggleProfileDropdown() {
    const dropdown = document.getElementById('profileDropdown');
    dropdown.classList.toggle('show');
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const dropdown = document.getElementById('profileDropdown');
    const profileBtn = document.querySelector('.profile-btn');
    
    if (dropdown && profileBtn) {
        if (!profileBtn.contains(event.target) && !dropdown.contains(event.target)) {
            dropdown.classList.remove('show');
        }
    }
});

// Global notification functions
function updateNotificationCount(count) {
    const countElements = document.querySelectorAll('.notification-count, .cart-count, .unread-badge');
    countElements.forEach(element => {
        if (element) {
            element.textContent = count;
            element.style.display = count > 0 ? 'inline-block' : 'none';
        }
    });
}

// Load notification popup
function loadNotificationPopup() {
    fetch('/notifications/popup/')
        .then(response => response.text())
        .then(html => {
            // Remove existing popup
            const existingPopup = document.querySelector('.notifications-popup');
            if (existingPopup) {
                existingPopup.remove();
            }
            
            // Add new popup
            const popupContainer = document.createElement('div');
            popupContainer.innerHTML = html;
            document.body.appendChild(popupContainer.firstElementChild);
        })
        .catch(error => {
            console.error('Error loading notification popup:', error);
        });
}

// Toggle notification popup
function toggleNotificationPopup() {
    const popup = document.getElementById('notificationPopup');
    const isVisible = popup.style.display !== 'none';
    
    if (isVisible) {
        popup.style.display = 'none';
        popup.innerHTML = '';
    } else {
        // Load and show popup
        fetch('/notifications/popup/')
            .then(response => response.text())
            .then(html => {
                popup.innerHTML = html;
                popup.style.display = 'block';
            })
            .catch(error => {
                console.error('Error loading notification popup:', error);
                // Fallback to notifications page
                window.location.href = '/notifications/';
            });
    }
}

// Close notification popup when clicking outside
document.addEventListener('click', function(event) {
    const popup = document.getElementById('notificationPopup');
    const bell = document.querySelector('.notification-bell');
    
    if (popup && bell && popup.style.display !== 'none') {
        if (!bell.contains(event.target) && !popup.contains(event.target)) {
            popup.style.display = 'none';
            popup.innerHTML = '';
        }
    }
});

// Show notifications function - now shows popup or redirects
function showNotifications() {
    // Close the profile dropdown first
    const dropdown = document.getElementById('profileDropdown');
    if (dropdown) {
        dropdown.classList.remove('show');
    }
    
    // Check if we're on mobile or prefer popup
    const isMobile = window.innerWidth <= 768;
    
    if (isMobile) {
        // On mobile, redirect to notifications page
        window.location.href = '/notifications/';
    } else {
        // On desktop, show popup
        toggleNotificationPopup();
    }
}