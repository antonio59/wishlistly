// Child Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Wishlist Creation Wizard
    const createWishlistBtn = document.getElementById('createWishlistBtn');
    const wishlistWizard = document.getElementById('wishlistWizard');
    const wizardSteps = document.querySelectorAll('.wizard-step');
    let currentStep = 0;

    if (createWishlistBtn) {
        createWishlistBtn.addEventListener('click', () => {
            wishlistWizard.style.display = 'block';
            showWizardStep(0);
        });
    }

    // Wizard Navigation
    document.querySelectorAll('.wizard-next').forEach(btn => {
        btn.addEventListener('click', () => {
            if (validateCurrentStep()) {
                showWizardStep(currentStep + 1);
            }
        });
    });

    document.querySelectorAll('.wizard-prev').forEach(btn => {
        btn.addEventListener('click', () => {
            showWizardStep(currentStep - 1);
        });
    });

    function showWizardStep(step) {
        wizardSteps.forEach(s => s.classList.remove('active'));
        wizardSteps[step].classList.add('active');
        currentStep = step;
    }

    function validateCurrentStep() {
        const step = wizardSteps[currentStep];
        const requiredFields = step.querySelectorAll('[required]');
        return Array.from(requiredFields).every(field => field.value.trim() !== '');
    }

    // Close modal when clicking outside
    wishlistWizard.addEventListener('click', (e) => {
        if (e.target === wishlistWizard) {
            wishlistWizard.style.display = 'none';
        }
    });

    // Theme Customization
    const customizeBtn = document.getElementById('customizeBtn');
    const customizeModal = document.getElementById('customizeModal');
    const themeOptions = document.querySelectorAll('.theme-option');

    if (customizeBtn) {
        customizeBtn.addEventListener('click', () => {
            customizeModal.style.display = 'block';
        });
    }

    themeOptions.forEach(option => {
        option.addEventListener('click', () => {
            themeOptions.forEach(o => o.classList.remove('selected'));
            option.classList.add('selected');
            
            // Send theme update to server
            fetch('/update_theme', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    theme: option.dataset.theme
                })
            });
        });
    });

    // Progress bars animation
    const progressBars = document.querySelectorAll('.progress-bar-fill');
    progressBars.forEach(bar => {
        const width = bar.getAttribute('data-progress');
        bar.style.width = width + '%';
    });

    // Achievement badges hover effect
    const badges = document.querySelectorAll('.badge');
    badges.forEach(badge => {
        badge.addEventListener('mouseenter', () => {
            badge.style.transform = 'scale(1.1)';
        });
        badge.addEventListener('mouseleave', () => {
            badge.style.transform = 'scale(1)';
        });
    });

    // Wishlist card actions
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const wishlistId = e.target.closest('.wishlist-card').dataset.wishlistId;
            window.location.href = `/wishlist/${wishlistId}`;
        });
    });

    document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const wishlistId = e.target.closest('.wishlist-card').dataset.wishlistId;
            window.location.href = `/wishlist/${wishlistId}/edit`;
        });
    });

    // Form submission for new wishlist
    const wishlistForm = document.getElementById('wishlistForm');
    if (wishlistForm) {
        wishlistForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(wishlistForm);
            try {
                const response = await fetch('/create_wishlist', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    wishlistWizard.style.display = 'none';
                    window.location.reload();
                } else {
                    alert('Error creating wishlist. Please try again.');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error creating wishlist. Please try again.');
            }
        });
    }
});
