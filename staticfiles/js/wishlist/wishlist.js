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
            productIds.forEach(productId => {
                checkWishlistStatus(productId);
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
    fetch(`/wishlist/toggle/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateWishlistButton(button, data.added);
            
            // Show toast notification
            showToast(data.message);
        }
    })
    .catch(error => {
        console.error('Error toggling wishlist:', error);
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
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const buttons = document.querySelectorAll(`.wishlist-btn[data-product-id="${productId}"], .wishlist-toggle[data-product-id="${productId}"]`);
            buttons.forEach(button => {
                updateWishlistButton(button, data.in_wishlist);
            });
        }
    })
    .catch(error => {
        console.error('Error checking wishlist status:', error);
    });
}

/**
 * Update wishlist button appearance
 */
function updateWishlistButton(button, inWishlist) {
    // Update button class
    if (inWishlist) {
        button.classList.remove('btn-outline-primary');
        button.classList.add('btn-danger');
    } else {
        button.classList.remove('btn-danger');
        button.classList.add('btn-outline-primary');
    }
    
    // Update icon
    const icon = button.querySelector('.wishlist-icon');
    if (icon) {
        if (inWishlist) {
            icon.classList.remove('far');
            icon.classList.add('fas');
            icon.style.color = 'white';
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
 */
function showToast(message) {
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
    
    toast.innerHTML = `
        <div class="toast-header">
            <i class="fas fa-heart me-2 text-danger"></i>
            <strong class="me-auto">Wishlist</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
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
