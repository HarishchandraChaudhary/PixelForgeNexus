document.addEventListener('DOMContentLoaded', function() {
    // 1. Automatic dismissal of flash messages
    // This makes success/info/danger messages disappear after a few seconds.
    const flashMessages = document.querySelectorAll('.flash-messages .alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            // After fade, remove from DOM to clean up space
            setTimeout(() => {
                message.remove();
            }, 500); // Corresponds to CSS transition duration
        }, 5000); // Message visible for 5 seconds
    });

    // 2. Client-side form validation examples (for better UX)
    // IMPORTANT: This is for UX only. Server-side validation is crucial for security.

    // Example for the Registration Form (Password Strength Visualizer)
    const registrationForm = document.querySelector('.form-container form[action*="/register"]');
    if (registrationForm) {
        const passwordField = registrationForm.querySelector('input[name="password"]');
        const password2Field = registrationForm.querySelector('input[name="password2"]');
        const passwordStrengthFeedback = document.createElement('div');
        passwordStrengthFeedback.id = 'password-strength-feedback';
        passwordStrengthFeedback.style.fontSize = '0.85em';
        passwordStrengthFeedback.style.marginTop = '5px';
        passwordStrengthFeedback.style.minHeight = '1.5em'; // Reserve space
        passwordField.parentNode.insertBefore(passwordStrengthFeedback, passwordField.nextSibling);

        const validatePasswordStrength = () => {
            const password = passwordField.value;
            let strength = 0;
            let feedback = '';
            let color = 'red';

            if (password.length >= 8) {
                strength++;
            } else {
                feedback += 'Must be at least 8 characters. ';
            }
            if (/[A-Z]/.test(password)) strength++; else feedback += 'Add uppercase. ';
            if (/[a-z]/.test(password)) strength++; else feedback += 'Add lowercase. ';
            if (/\d/.test(password)) strength++; else feedback += 'Add a number. ';
            if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength++; else feedback += 'Add special character. ';

            if (strength <= 2) {
                color = 'red';
                feedback = feedback || 'Very Weak.';
            } else if (strength <= 4) {
                color = 'orange';
                feedback = feedback || 'Medium Strength.';
            } else {
                color = 'green';
                feedback = 'Strong Password.';
            }

            passwordStrengthFeedback.textContent = feedback;
            passwordStrengthFeedback.style.color = color;
        };

        const validatePasswordsMatch = () => {
            if (password2Field.value && passwordField.value !== password2Field.value) {
                const matchErrorSpan = password2Field.parentNode.querySelector('.error.match-error');
                if (!matchErrorSpan) {
                    const newSpan = document.createElement('span');
                    newSpan.className = 'error match-error';
                    newSpan.textContent = 'Passwords do not match.';
                    password2Field.parentNode.insertBefore(newSpan, password2Field.nextSibling);
                }
            } else {
                const matchErrorSpan = password2Field.parentNode.querySelector('.error.match-error');
                if (matchErrorSpan) matchErrorSpan.remove();
            }
        };


        if (passwordField) {
            passwordField.addEventListener('input', validatePasswordStrength);
            if (password2Field) {
                 passwordField.addEventListener('input', validatePasswordsMatch); // Re-check match when password 1 changes
                 password2Field.addEventListener('input', validatePasswordsMatch);
            }
        }
    }

    // Client-side validation for Add Project Form (Date comparison)
    const addProjectForm = document.querySelector('.form-container form[action*="/projects/add"]');
    if (addProjectForm) {
        const deadlineField = addProjectForm.querySelector('input[name="deadline"]');
        if (deadlineField) {
            deadlineField.addEventListener('change', function() {
                const deadlineDate = new Date(this.value);
                const today = new Date();
                today.setHours(0, 0, 0, 0); // Normalize to start of day

                if (deadlineDate < today) {
                    let errorSpan = this.parentNode.querySelector('.error.date-error');
                    if (!errorSpan) {
                        errorSpan = document.createElement('span');
                        errorSpan.className = 'error date-error';
                        this.parentNode.insertBefore(errorSpan, this.nextSibling);
                    }
                    errorSpan.textContent = 'Deadline cannot be in the past.';
                    this.setCustomValidity('Deadline cannot be in the past.'); // HTML5 validation API
                } else {
                    const errorSpan = this.parentNode.querySelector('.error.date-error');
                    if (errorSpan) errorSpan.remove();
                    this.setCustomValidity(''); // Clear custom validation message
                }
            });
        }
    }


    // 3. User deletion confirmation (already in HTML, but good to note JS for more complex dialogs)
    // The HTML's `onsubmit="return confirm('Are you sure...');"` is simple and effective.
    // For more advanced confirmations (e.g., custom modals), you'd use JS.

    // 4. Highlight current active navigation link (optional)
    const navLinks = document.querySelectorAll('nav ul li a');
    const currentPath = window.location.pathname;

    navLinks.forEach(link => {
        // Simple check: if the link's href matches the current path
        // Adjust logic if your links are more complex (e.g., contain query params or sub-paths)
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active-nav');
        } else if (currentPath.startsWith('/project/') && link.getAttribute('href') === '/index') {
            // If on a project details page, highlight dashboard as related
            link.classList.add('active-nav'); // Or add a different class like 'parent-active'
        }
    });

    // Add CSS for active-nav in style.css:
    /*
    nav ul li a.active-nav {
        background-color: #0056b3; // Darker blue or distinct color
        font-weight: bold;
    }
    */
});