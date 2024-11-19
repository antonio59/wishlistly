document.addEventListener('DOMContentLoaded', function() {
    // Initialize progress bars
    initializeProgressBars();

    // Add smooth hover effects
    initializeHoverEffects();

    // Initialize activity feed auto-update
    initializeActivityFeed();
});

function initializeProgressBars() {
    const progressBars = document.querySelectorAll('.progress-fill');
    progressBars.forEach(bar => {
        // Add animation when the bar comes into view
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const width = bar.style.width;
                    bar.style.width = '0';
                    setTimeout(() => {
                        bar.style.width = width;
                    }, 100);
                    observer.unobserve(bar);
                }
            });
        });
        observer.observe(bar);
    });
}

function initializeHoverEffects() {
    // Add hover effects to child cards
    const childCards = document.querySelectorAll('.child-card');
    childCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-5px)';
            card.style.transition = 'transform 0.3s ease';
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
        });
    });

    // Add hover effects to buttons
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', () => {
            button.style.transform = 'scale(1.05)';
            button.style.transition = 'transform 0.2s ease';
        });
        button.addEventListener('mouseleave', () => {
            button.style.transform = 'scale(1)';
        });
    });
}

function initializeActivityFeed() {
    // Auto-update activity feed every 5 minutes
    setInterval(updateActivityFeed, 5 * 60 * 1000);
}

async function updateActivityFeed() {
    try {
        const response = await fetch('/api/activities/latest');
        if (!response.ok) {
            throw new Error('Failed to fetch activities');
        }
        
        const activities = await response.json();
        updateActivityDisplay(activities);
    } catch (error) {
        console.error('Error updating activity feed:', error);
    }
}

function updateActivityDisplay(activities) {
    const activityFeeds = document.querySelectorAll('.activity-feed');
    activityFeeds.forEach(feed => {
        const childId = feed.closest('.child-card').dataset.childId;
        const childActivities = activities.filter(a => a.child_id === childId);
        
        if (childActivities.length > 0) {
            const activityHtml = childActivities.map(activity => `
                <div class="activity-item">
                    ${activity.message} ${activity.emoji}
                    <div class="activity-time">${formatDate(activity.timestamp)}</div>
                </div>
            `).join('');
            
            const activityContainer = feed.querySelector(':scope > div');
            if (activityContainer) {
                activityContainer.innerHTML = activityHtml;
            }
        }
    });
}

function formatDate(timestamp) {
    const date = new Date(timestamp);
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

// Handle child account switching
function switchToChildAccount(childId) {
    window.location.href = `/switch-to-child/${childId}`;
}

// Handle child account management
function manageChildAccount(childId) {
    window.location.href = `/parent/child/${childId}`;
}

// Add new child account
function addNewChild() {
    window.location.href = '/register-child';
}

// Export functions for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initializeProgressBars,
        initializeHoverEffects,
        initializeActivityFeed,
        updateActivityFeed,
        updateActivityDisplay,
        formatDate
    };
}
