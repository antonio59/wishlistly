document.addEventListener('DOMContentLoaded', function() {
    // Theme switcher
    const themeButtons = document.querySelectorAll('.theme-selector');
    themeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const theme = this.dataset.theme;
            document.querySelector('.wishlist-container').className = `wishlist-container theme-${theme}`;
            localStorage.setItem('selectedTheme', theme);
        });
    });

    // Restore previously selected theme
    const savedTheme = localStorage.getItem('selectedTheme');
    if (savedTheme) {
        document.querySelector('.wishlist-container')?.classList.add(`theme-${savedTheme}`);
    }

    // Share wishlist functionality
    const shareButtons = document.querySelectorAll('.share-button');
    shareButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const wishlistId = this.dataset.wishlistId;
            const shareUrl = `${window.location.origin}/wishlist/${wishlistId}`;
            
            try {
                await navigator.clipboard.writeText(shareUrl);
                showNotification('Link copied to clipboard! 🎉');
            } catch (err) {
                showNotification('Could not copy link automatically. Please copy it manually.');
            }
        });
    });

    // Add item to wishlist
    const addItemForm = document.getElementById('add-item-form');
    if (addItemForm) {
        addItemForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            
            try {
                const response = await fetch('/add_item', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    const result = await response.json();
                    addItemToList(result.item);
                    this.reset();
                    showNotification('Item added successfully! 🎉');
                } else {
                    showNotification('Could not add item. Please try again.');
                }
            } catch (err) {
                showNotification('An error occurred. Please try again.');
            }
        });
    }

    // Mark item as purchased
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('mark-purchased')) {
            const itemId = e.target.dataset.itemId;
            const wishlistId = e.target.dataset.wishlistId;
            
            fetch(`/mark_purchased/${wishlistId}/${itemId}`, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const item = document.querySelector(`#item-${itemId}`);
                    item.classList.add('purchased');
                    showNotification('Item marked as purchased! 🎁');
                }
            })
            .catch(() => {
                showNotification('Could not update item status.');
            });
        }
    });

    // Notification system
    function showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Trigger animation
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Remove notification after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    // Add new item to the wishlist DOM
    function addItemToList(item) {
        const itemsList = document.querySelector('.wishlist-items');
        if (!itemsList) return;

        const itemElement = document.createElement('div');
        itemElement.className = 'wishlist-item';
        itemElement.id = `item-${item.id}`;
        
        itemElement.innerHTML = `
            <h3 class="item-name">${item.name}</h3>
            <p class="item-description">${item.description || ''}</p>
            ${item.url ? `<a href="${item.url}" target="_blank" class="item-link">View Item</a>` : ''}
            ${item.price ? `<p class="item-price">$${item.price}</p>` : ''}
            <div class="item-actions">
                <button class="btn btn-sm btn-outline-danger remove-item" data-item-id="${item.id}">
                    Remove
                </button>
            </div>
        `;
        
        itemsList.appendChild(itemElement);
    }

    // Drag and drop reordering
    const sortableList = document.querySelector('.wishlist-items');
    if (sortableList) {
        new Sortable(sortableList, {
            animation: 150,
            ghostClass: 'sortable-ghost',
            onEnd: function(evt) {
                const itemId = evt.item.id.replace('item-', '');
                const newIndex = evt.newIndex;
                
                fetch('/reorder_item', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        item_id: itemId,
                        new_index: newIndex
                    })
                });
            }
        });
    }
});
