/**
 * Wishlist functionality for the e-commerce site
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize wishlist buttons
    initWishlistButtons();
    
    // Check wishlist status for all products on the page if user is authenticated
    if (isUserAuthenticated()) {
        const productIds = Array.from(document.querySelectorAll('[data-product-id]')).map(el => el.dataset.productId);
        if (productIds.length > 0) {
            // Use a delay to avoid overwhelming the server with requests
            productIds.forEach((productId, index) => {
                setTimeout(() => {
                    checkWishlistStatus(productId);
                }, index * 100); // Stagger requests by 100ms
            });
        }
    }
});

/**
 * Check if user is authenticated
 */
function isUserAuthenticated() {
    return document.body.classList.contains('user-authenticated');
}

/**
 * Initialize wishlist buttons
 */
function initWishlistButtons() {
    const wishlistButtons = document.querySelectorAll('.wishlist-btn, .wishlist-toggle');
    
    wishlistButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // If user is not authenticated, redirect to login
            if (!isUserAuthenticated()) {
                window.location.href = '/accounts/login/?next=' + window.location.pathname;
                return;
            }
            
            const productId = this.dataset.productId;
            toggleWishlist(productId, this);
        });
    });
}

/**
 * Toggle wishlist status
 */
function toggleWishlist(productId, button) {
    // Add loading state
    button.classList.add('disabled');
    const icon = button.querySelector('.wishlist-icon');
    if (icon) {
        icon.classList.add('fa-spin');
    }
    
    fetch(`/wishlist/toggle/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // Remove loading state
        button.classList.remove('disabled');
        if (icon) {
            icon.classList.remove('fa-spin');
        }
        
        if (data.success) {
            updateWishlistButton(button, data.added);
            
            // Add animation
            if (icon) {
                icon.classList.add('animate');
                setTimeout(() => {
                    icon.classList.remove('animate');
                }, 1000);
            }
            
            // Show toast notification
            showToast(data.message, data.added ? 'success' : 'danger');
            
            // Update all buttons for this product
            updateAllProductButtons(productId, data.added);
            
            // Update wishlist count with the server-provided count
            if (data.wishlist_count !== undefined) {
                updateWishlistCount(data.wishlist_count);
            }
        } else {
            showToast(data.message || 'An error occurred', 'warning');
        }
    })
    .catch(error => {
        // Remove loading state
        button.classList.remove('disabled');
        if (icon) {
            icon.classList.remove('fa-spin');
        }
        
        console.error('Error toggling wishlist:', error);
        showToast('Could not update wishlist. Please try again.', 'danger');
    });
}

/**
 * Check wishlist status
 */
function checkWishlistStatus(productId) {
    fetch(`/wishlist/check/${productId}/`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Use the updateAllProductButtons function to update all buttons for this product
            updateAllProductButtons(productId, data.in_wishlist);
            
            // Update wishlist count with the server-provided count
            if (data.wishlist_count !== undefined) {
                updateWishlistCount(data.wishlist_count);
            }
        }
    })
    .catch(error => {
        console.error('Error checking wishlist status:', error);
        // Don't show toast for status checks to avoid overwhelming the user
    });
}

/**
 * Update all buttons for the same product
 */
function updateAllProductButtons(productId, inWishlist) {
    const buttons = document.querySelectorAll(`.wishlist-btn[data-product-id="${productId}"], .wishlist-toggle[data-product-id="${productId}"]`);
    buttons.forEach(button => {
        updateWishlistButton(button, inWishlist);
    });
    
    // Update wishlist count in the header if it exists
    updateWishlistCount(inWishlist);
}

/**
 * Update wishlist count in the header
 * @param {boolean|number} addedOrCount - Either a boolean indicating if an item was added, or the new count from the server
 */
function updateWishlistCount(addedOrCount) {
    const wishlistCountElement = document.querySelector('.wishlist-count');
    if (wishlistCountElement) {
        let count;
        
        // If we received a number directly from the server, use that
        if (typeof addedOrCount === 'number') {
            count = addedOrCount;
        } else {
            // Otherwise calculate based on current count
            count = parseInt(wishlistCountElement.textContent || '0');
            if (addedOrCount === true) {
                count++;
            } else if (addedOrCount === false) {
                count = Math.max(0, count - 1);
            }
        }
        
        wishlistCountElement.textContent = count;
        
        // Show/hide based on count
        if (count > 0) {
            wishlistCountElement.classList.remove('d-none');
        } else {
            wishlistCountElement.classList.add('d-none');
        }
    }
}

/**
 * Update wishlist button appearance
 */
function updateWishlistButton(button, inWishlist) {
    // Update button class
    if (inWishlist) {
        button.classList.remove('btn-outline-primary');
        button.classList.add('btn-danger', 'active');
    } else {
        button.classList.remove('btn-danger', 'active');
        button.classList.add('btn-outline-primary');
    }
    
    // Update icon
    const icon = button.querySelector('.wishlist-icon');
    if (icon) {
        if (inWishlist) {
            icon.classList.remove('far');
            icon.classList.add('fas');
            icon.style.color = button.classList.contains('wishlist-toggle') ? 'white' : '';
        } else {
            icon.classList.remove('fas');
            icon.classList.add('far');
            icon.style.color = '';
        }
    }
    
    // Update text if present
    const textEl = button.querySelector('.wishlist-btn-text');
    if (textEl) {
        textEl.textContent = inWishlist ? 'Remove from Wishlist' : 'Add to Wishlist';
    }
}

/**
 * Show toast notification
 * @param {string} message - The message to display
 * @param {string} type - The type of toast: 'success', 'danger', 'warning', or 'info'
 */
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '5000';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.id = toastId;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    // Set icon and color based on type
    let icon, bgColor, textColor;
    switch (type) {
        case 'success':
            icon = 'fas fa-check-circle';
            bgColor = 'bg-success';
            textColor = 'text-white';
            break;
        case 'danger':
            icon = 'fas fa-exclamation-circle';
            bgColor = 'bg-danger';
            textColor = 'text-white';
            break;
        case 'warning':
            icon = 'fas fa-exclamation-triangle';
            bgColor = 'bg-warning';
            textColor = 'text-dark';
            break;
        default: // info
            icon = 'fas fa-heart';
            bgColor = '';
            textColor = '';
    }
    
    // Create toast content
    if (type === 'success' || type === 'danger' || type === 'warning') {
        // Colored background toast
        toast.classList.add(bgColor, textColor);
        toast.innerHTML = `
            <div class="toast-body d-flex align-items-center">
                <i class="${icon} me-2"></i>
                <div>${message}</div>
                <button type="button" class="btn-close ms-auto ${textColor === 'text-white' ? 'btn-close-white' : ''}" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
    } else {
        // Standard toast with header
        toast.innerHTML = `
            <div class="toast-header">
                <i class="${icon} me-2 text-${type === 'info' ? 'primary' : type}"></i>
                <strong class="me-auto">Wishlist</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;
    }
    
    toastContainer.appendChild(toast);
    
    // Show toast
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 3000
    });
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

/**
 * Helper function to get CSRF token
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
