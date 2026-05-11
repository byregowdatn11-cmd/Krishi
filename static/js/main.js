// Campus Krishi - Main JavaScript File

// Global Variables
let cart = {};
let vegetables = [];

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    loadCartFromSession();
    setupEventListeners();
    startRealTimeUpdates();
    initializeAnimations();
    setupFormValidation();
}

// Cart Management
function loadCartFromSession() {
    // Cart is managed server-side, but we can enhance client-side experience
    updateCartBadge();
}

function updateCartBadge() {
    fetch('/api/cart-count')
        .then(response => response.json())
        .then(data => {
            const badge = document.querySelector('.navbar .badge');
            if (badge && data.count > 0) {
                badge.textContent = data.count;
                badge.style.display = 'inline-block';
            } else if (badge) {
                badge.style.display = 'none';
            }
        })
        .catch(error => console.log('Cart count update failed:', error));
}

// Real-time Updates
function startRealTimeUpdates() {
    // Update prices and stock every 5 seconds
    setInterval(updateVegetablesData, 5000);
    
    // Update cart badge every 3 seconds
    setInterval(updateCartBadge, 3000);
}

function updateVegetablesData() {
    fetch('/api/vegetables')
        .then(response => response.json())
        .then(data => {
            vegetables = data;
            updateVegetableCards();
            updatePriceComparison();
            showUpdateIndicator();
        })
        .catch(error => console.log('Real-time update failed:', error));
}

function updateVegetableCards() {
    const cards = document.querySelectorAll('.vegetable-card');
    cards.forEach(card => {
        const vegId = card.querySelector('[data-veg-id]')?.getAttribute('data-veg-id');
        if (vegId) {
            const vegetable = vegetables.find(v => v.id == vegId);
            if (vegetable) {
                updateCardPrice(card, vegetable);
                updateCardStock(card, vegetable);
            }
        }
    });
}

function updateCardPrice(card, vegetable) {
    const priceElement = card.querySelector('.text-success');
    if (priceElement && priceElement.textContent.includes('₹')) {
        const currentPrice = parseFloat(priceElement.textContent.replace('₹', '').replace('/kg', ''));
        const newPrice = vegetable.price;
        
        if (currentPrice !== newPrice) {
            priceElement.textContent = `₹${newPrice.toFixed(2)}/kg`;
            priceElement.classList.add('price-updated');
            setTimeout(() => priceElement.classList.remove('price-updated'), 2000);
        }
    }
}

function updateCardStock(card, vegetable) {
    const stockElement = card.querySelector('.badge');
    if (stockElement) {
        stockElement.textContent = `Stock: ${vegetable.stock}kg`;
        stockElement.className = 'badge';
        
        if (vegetable.stock > 20) {
            stockElement.classList.add('bg-success');
        } else if (vegetable.stock > 0) {
            stockElement.classList.add('bg-warning');
        } else {
            stockElement.classList.add('bg-danger');
        }
        
        // Update add to cart button
        const addButton = card.querySelector('.btn-success');
        if (addButton) {
            if (vegetable.stock === 0) {
                addButton.disabled = true;
                addButton.innerHTML = '<i class="fas fa-times-circle"></i> Out of Stock';
                addButton.classList.remove('btn-success');
                addButton.classList.add('btn-secondary');
            } else {
                addButton.disabled = false;
                addButton.innerHTML = '<i class="fas fa-cart-plus"></i> Add to Cart';
                addButton.classList.remove('btn-secondary');
                addButton.classList.add('btn-success');
            }
        }
    }
}

function updatePriceComparison() {
    const tableBody = document.getElementById('price-comparison');
    if (!tableBody) return;
    
    const rows = tableBody.querySelectorAll('tr');
    rows.forEach(row => {
        const vegName = row.cells[0].textContent;
        const vegetable = vegetables.find(v => v.name === vegName);
        if (vegetable) {
            row.cells[1].textContent = `₹${vegetable.price.toFixed(2)}`;
            row.cells[2].textContent = `₹${(vegetable.price * 1.3).toFixed(2)}`;
            row.cells[3].textContent = `₹${(vegetable.price * 0.3).toFixed(2)} (30%)`;
            
            const stockCell = row.cells[4];
            stockCell.innerHTML = vegetable.stock > 0 
                ? '<span class="badge bg-success">In Stock</span>'
                : '<span class="badge bg-danger">Out of Stock</span>';
        }
    });
}

function showUpdateIndicator() {
    const indicator = document.getElementById('update-indicator');
    if (indicator) {
        const toast = new bootstrap.Toast(indicator);
        toast.show();
    }
}

// Event Listeners
function setupEventListeners() {
    // Quick add buttons
    document.querySelectorAll('.quick-add').forEach(button => {
        button.addEventListener('click', handleQuickAdd);
    });
    
    // Quantity update buttons in cart
    document.querySelectorAll('.qty-update').forEach(button => {
        button.addEventListener('click', handleQuantityUpdate);
    });
    
    // Quantity input changes
    document.querySelectorAll('.qty-input').forEach(input => {
        input.addEventListener('change', handleQuantityChange);
    });
    
    // Search functionality
    const searchInput = document.getElementById('search-vegetables');
    if (searchInput) {
        searchInput.addEventListener('input', handleSearch);
    }
    
    // Sort functionality
    const sortSelect = document.getElementById('sort-vegetables');
    if (sortSelect) {
        sortSelect.addEventListener('change', handleSort);
    }
    
    // Filter functionality
    const filterSelect = document.getElementById('filter-stock');
    if (filterSelect) {
        filterSelect.addEventListener('change', handleFilter);
    }
}

// Cart Operations
function handleQuickAdd(e) {
    e.preventDefault();
    const vegId = e.target.getAttribute('data-veg-id');
    const qtyInput = document.getElementById(`qty-${vegId}`);
    const quantity = parseInt(qtyInput.value) || 1;
    
    addToCart(vegId, quantity);
}

function addToCart(vegId, quantity) {
    fetch(`/add_to_cart/${vegId}`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.text())
    .then(html => {
        // Show success message
        showNotification('Product added to cart!', 'success');
        updateCartBadge();
        
        // Update button state
        const button = document.querySelector(`[data-veg-id="${vegId}"]`);
        if (button) {
            button.innerHTML = '<i class="fas fa-check"></i> Added!';
            button.classList.remove('btn-outline-success');
            button.classList.add('btn-success');
            
            setTimeout(() => {
                button.innerHTML = '<i class="fas fa-cart-plus"></i> Quick Add';
                button.classList.remove('btn-success');
                button.classList.add('btn-outline-success');
            }, 2000);
        }
    })
    .catch(error => {
        console.error('Add to cart failed:', error);
        showNotification('Failed to add product to cart', 'error');
    });
}

function handleQuantityUpdate(e) {
    e.preventDefault();
    const vegId = e.target.getAttribute('data-veg-id');
    const action = e.target.getAttribute('data-action');
    const input = document.querySelector(`.qty-input[data-veg-id="${vegId}"]`);
    
    if (!input) return;
    
    let currentValue = parseInt(input.value) || 1;
    const maxValue = parseInt(input.getAttribute('max')) || 999;
    
    if (action === 'increase' && currentValue < maxValue) {
        currentValue++;
    } else if (action === 'decrease' && currentValue > 1) {
        currentValue--;
    }
    
    input.value = currentValue;
    updateCartItem(vegId, currentValue);
}

function handleQuantityChange(e) {
    const vegId = e.target.getAttribute('data-veg-id');
    const quantity = parseInt(e.target.value) || 1;
    updateCartItem(vegId, quantity);
}

function updateCartItem(vegId, quantity) {
    const formData = new FormData();
    formData.append('veg_id', vegId);
    formData.append('quantity', quantity);
    
    fetch('/update_cart', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update subtotal
            const subtotalElement = document.querySelector(`.subtotal-${vegId}`);
            if (subtotalElement) {
                subtotalElement.textContent = `₹${data.subtotal.toFixed(2)}`;
            }
            
            // Update cart total
            const totalElements = document.querySelectorAll('.cart-total');
            totalElements.forEach(element => {
                element.textContent = `₹${data.cart_total.toFixed(2)}`;
            });
            
            showNotification(data.message, 'success');
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Cart update failed:', error);
        showNotification('Failed to update cart', 'error');
    });
}

// Search and Filter
function handleSearch(e) {
    const searchTerm = e.target.value.toLowerCase();
    const products = document.querySelectorAll('.vegetable-item');
    
    products.forEach(product => {
        const name = product.getAttribute('data-name') || '';
        if (name.includes(searchTerm)) {
            product.style.display = 'block';
        } else {
            product.style.display = 'none';
        }
    });
}

function handleSort(e) {
    const sortValue = e.target.value;
    const container = document.getElementById('vegetables-grid');
    if (!container) return;
    
    const products = Array.from(container.querySelectorAll('.vegetable-item'));
    
    products.sort((a, b) => {
        switch(sortValue) {
            case 'name':
                const nameA = a.getAttribute('data-name') || '';
                const nameB = b.getAttribute('data-name') || '';
                return nameA.localeCompare(nameB);
            case 'price-low':
                const priceA = parseFloat(a.getAttribute('data-price')) || 0;
                const priceB = parseFloat(b.getAttribute('data-price')) || 0;
                return priceA - priceB;
            case 'price-high':
                const priceHighA = parseFloat(a.getAttribute('data-price')) || 0;
                const priceHighB = parseFloat(b.getAttribute('data-price')) || 0;
                return priceHighB - priceHighA;
            case 'stock':
                const stockA = parseInt(a.getAttribute('data-stock')) || 0;
                const stockB = parseInt(b.getAttribute('data-stock')) || 0;
                return stockB - stockA;
            default:
                return 0;
        }
    });
    
    products.forEach(product => container.appendChild(product));
}

function handleFilter(e) {
    const filterValue = e.target.value;
    const products = document.querySelectorAll('.vegetable-item');
    
    products.forEach(product => {
        const stock = parseInt(product.getAttribute('data-stock')) || 0;
        
        switch(filterValue) {
            case 'instock':
                product.style.display = stock > 0 ? 'block' : 'none';
                break;
            case 'outofstock':
                product.style.display = stock === 0 ? 'block' : 'none';
                break;
            case 'lowstock':
                product.style.display = stock > 0 && stock < 10 ? 'block' : 'none';
                break;
            default:
                product.style.display = 'block';
        }
    });
}

// Form Validation
function setupFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// Notifications
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : 'success'} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Animations
function initializeAnimations() {
    // Add fade-in animation to elements
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, observerOptions);
    
    // Observe all cards and sections
    document.querySelectorAll('.card, .feature-box, .vegetable-card').forEach(el => {
        observer.observe(el);
    });
}

// Loading States
function showLoading() {
    const loader = document.createElement('div');
    loader.id = 'global-loader';
    loader.className = 'position-fixed top-0 start-0 w-100 h-100 bg-dark bg-opacity-50 d-flex align-items-center justify-content-center';
    loader.style.cssText = 'z-index: 9999;';
    loader.innerHTML = `
        <div class="spinner-border text-success" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    `;
    document.body.appendChild(loader);
}

function hideLoading() {
    const loader = document.getElementById('global-loader');
    if (loader) {
        loader.remove();
    }
}

// Checkout Form Enhancement
function enhanceCheckoutForm() {
    const checkoutForm = document.getElementById('checkout-form');
    if (!checkoutForm) return;
    
    checkoutForm.addEventListener('submit', function(e) {
        showLoading();
        
        // Form will submit normally, but show loading state
        setTimeout(() => {
            hideLoading();
        }, 3000);
    });
}

// Gallery Enhancement
function enhanceGallery() {
    const galleryItems = document.querySelectorAll('.gallery-item');
    galleryItems.forEach(item => {
        item.addEventListener('click', function() {
            const img = this.querySelector('img');
            if (img) {
                // Create lightbox effect
                createLightbox(img.src, img.alt);
            }
        });
    });
}

function createLightbox(src, alt) {
    const lightbox = document.createElement('div');
    lightbox.className = 'position-fixed top-0 start-0 w-100 h-100 bg-dark bg-opacity-90 d-flex align-items-center justify-content-center';
    lightbox.style.cssText = 'z-index: 9999;';
    lightbox.innerHTML = `
        <div class="position-relative">
            <img src="${src}" alt="${alt}" class="img-fluid rounded" style="max-height: 90vh;">
            <button type="button" class="position-absolute top-0 end-0 btn btn-light m-2" onclick="this.closest('.position-fixed').remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    lightbox.addEventListener('click', function(e) {
        if (e.target === lightbox) {
            lightbox.remove();
        }
    });
    
    document.body.appendChild(lightbox);
}

// Initialize specific page features
document.addEventListener('DOMContentLoaded', function() {
    // Page-specific initializations
    if (document.querySelector('.vegetables-page')) {
        enhanceVegetablesPage();
    }
    
    if (document.querySelector('.cart-page')) {
        enhanceCartPage();
    }
    
    if (document.querySelector('.checkout-page')) {
        enhanceCheckoutForm();
    }
    
    if (document.querySelector('.gallery-page')) {
        enhanceGallery();
    }
});

function enhanceVegetablesPage() {
    // Add hover effects to vegetable cards
    const cards = document.querySelectorAll('.vegetable-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

function enhanceCartPage() {
    // Add confirmation for item removal
    const removeButtons = document.querySelectorAll('a[href*="remove_from_cart"]');
    removeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to remove this item from your cart?')) {
                e.preventDefault();
            }
        });
    });
}

// Utility Functions
function formatPrice(price) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(price);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export for use in other scripts
window.FarmFresh = {
    showNotification,
    showLoading,
    hideLoading,
    formatPrice,
    debounce
};
