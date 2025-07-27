// Cart functionality
class Cart {
    constructor() {
        this.items = [];
        this.deliveryCharge = 50;
        this.init();
    }

    init() {
        this.loadCartFromStorage();
        this.setupEventListeners();
        this.updateCartUI();
    }

    setupEventListeners() {
        // Cart toggle
        document.getElementById('cart-toggle').addEventListener('click', () => {
            this.toggleCart();
        });

        // Close cart
        document.getElementById('close-cart').addEventListener('click', () => {
            this.closeCart();
        });

        // Checkout button
        document.getElementById('checkout-btn').addEventListener('click', () => {
            this.checkout();
        });

        // Modal controls
        document.getElementById('close-modal').addEventListener('click', () => {
            this.closeModal();
        });

        document.getElementById('increase-qty').addEventListener('click', () => {
            this.increaseModalQuantity();
        });

        document.getElementById('decrease-qty').addEventListener('click', () => {
            this.decreaseModalQuantity();
        });

        document.getElementById('add-to-cart-modal').addEventListener('click', () => {
            this.addToCartFromModal();
        });

        document.getElementById('buy-now-modal').addEventListener('click', () => {
            this.buyNowFromModal();
        });

        // Close modal on overlay click
        document.querySelector('.modal-overlay').addEventListener('click', () => {
            this.closeModal();
        });
    }

    addItem(product) {
        // Use Django API instead of localStorage
        const cartData = {
            product: {
                name: product.name,
                price: product.price,
                unit: product.unit || 'kg',
                category: product.category || 'general',
                description: product.description || '',
                image_url: product.image || ''
            },
            supplier: {
                place_id: product.supplierId,
                name: product.supplierName,
                address: product.supplierAddress || '',
                phone: product.supplierPhone || '',
                rating: product.supplierRating || 0,
                latitude: product.supplierLat || 0,
                longitude: product.supplierLng || 0
            },
            quantity: product.quantity
        };
        
        fetch('/orders/api/add-to-cart/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(cartData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update navbar cart count
                this.updateCartCount(data.cart_count);
                this.showNotification(data.message, 'success');
            } else {
                this.showNotification(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error adding to cart:', error);
            this.showNotification('Error adding item to cart', 'error');
        });
    }

    removeItem(productId, supplierId) {
        this.items = this.items.filter(item => 
            !(item.id === productId && item.supplierId === supplierId)
        );
        this.saveCartToStorage();
        this.updateCartUI();
    }

    updateQuantity(productId, supplierId, newQuantity) {
        const item = this.items.find(item => 
            item.id === productId && item.supplierId === supplierId
        );

        if (item) {
            if (newQuantity <= 0) {
                this.removeItem(productId, supplierId);
            } else {
                item.quantity = newQuantity;
                this.saveCartToStorage();
                this.updateCartUI();
            }
        }
    }

    getSubtotal() {
        return this.items.reduce((total, item) => total + (item.price * item.quantity), 0);
    }

    getTotal() {
        return this.getSubtotal() + this.deliveryCharge;
    }

    getItemCount() {
        return this.items.reduce((total, item) => total + item.quantity, 0);
    }

    updateCartUI() {
        this.updateCartCount();
        this.updateCartItems();
        this.updateCartTotals();
    }

    updateCartCount(count = null) {
        // If count is provided, use it; otherwise fetch from server
        if (count !== null) {
            this.updateCartCountDisplay(count);
        } else {
            // Fetch current cart count from server
            fetch('/orders/api/cart-count/')
            .then(response => response.json())
            .then(data => {
                this.updateCartCountDisplay(data.cart_count);
            })
            .catch(error => {
                console.error('Error fetching cart count:', error);
            });
        }
    }
    
    updateCartCountDisplay(count) {
        // Update navbar cart count
        const navbarCartCount = document.querySelector('.cart-count');
        if (navbarCartCount) {
            navbarCartCount.textContent = count;
            navbarCartCount.style.display = count > 0 ? 'inline' : 'none';
        }
        
        // Also update any other cart count elements
        const cartCountElements = document.querySelectorAll('#cart-count, .cart-count-display');
        cartCountElements.forEach(element => {
            element.textContent = count;
            element.classList.toggle('hidden', count === 0);
        });
    }

    updateCartItems() {
        const cartItems = document.getElementById('cart-items');
        const cartEmpty = document.querySelector('.cart-empty');

        if (this.items.length === 0) {
            cartItems.style.display = 'none';
            cartEmpty.classList.remove('hidden');
            return;
        }

        cartItems.style.display = 'flex';
        cartEmpty.classList.add('hidden');

        cartItems.innerHTML = this.items.map(item => `
            <div class="cart-item" data-id="${item.id}" data-supplier="${item.supplierId}">
                <div class="cart-item-image">
                    <img src="${item.image}" alt="${item.name}" onerror="this.style.display='none'">
                    <i class="fas fa-box" style="display: none; color: var(--text-lighter);"></i>
                </div>
                <div class="cart-item-details">
                    <div class="cart-item-name">${item.name}</div>
                    <div class="cart-item-supplier">by ${item.supplierName}</div>
                    <div class="cart-item-controls">
                        <div class="cart-quantity-controls">
                            <button class="cart-quantity-btn" onclick="cart.updateQuantity('${item.id}', '${item.supplierId}', ${item.quantity - 1})">-</button>
                            <span class="cart-quantity">${item.quantity}</span>
                            <button class="cart-quantity-btn" onclick="cart.updateQuantity('${item.id}', '${item.supplierId}', ${item.quantity + 1})">+</button>
                        </div>
                        <div class="cart-item-price">₹${(item.price * item.quantity).toFixed(2)}</div>
                        <button class="cart-remove" onclick="cart.removeItem('${item.id}', '${item.supplierId}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    updateCartTotals() {
        const subtotal = this.getSubtotal();
        const total = this.getTotal();

        document.getElementById('cart-subtotal').textContent = `₹${subtotal.toFixed(2)}`;
        document.getElementById('cart-total').textContent = `₹${total.toFixed(2)}`;
    }

    toggleCart() {
        const cartSidebar = document.getElementById('cart-sidebar');
        cartSidebar.classList.toggle('open');
    }

    closeCart() {
        const cartSidebar = document.getElementById('cart-sidebar');
        cartSidebar.classList.remove('open');
    }

    openProductModal(product) {
        console.log('Opening product modal with product:', product);
        const modal = document.getElementById('product-modal');
        
        if (!modal) {
            console.error('Product modal not found');
            return;
        }
        
        // Populate modal content
        document.getElementById('modal-product-name').textContent = product.name;
        document.getElementById('modal-supplier-name').textContent = product.supplierName;
        document.getElementById('modal-supplier-rating').textContent = product.rating || '4.5';
        document.getElementById('modal-product-price').textContent = `₹${product.price}`;
        document.getElementById('modal-product-unit').textContent = product.unit;
        document.getElementById('modal-product-description').textContent = product.description || 'High quality product from verified supplier.';
        document.getElementById('modal-product-image').src = product.image;
        document.getElementById('modal-quantity').value = 1;

        // Store current product data
        modal.dataset.productId = product.id;
        modal.dataset.supplierId = product.supplierId;
        modal.dataset.productName = product.name;
        modal.dataset.productPrice = product.price;
        modal.dataset.productUnit = product.unit;
        modal.dataset.supplierName = product.supplierName;
        modal.dataset.productImage = product.image;

        // Show modal
        modal.classList.remove('hidden');
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        
        console.log('Modal should now be visible');
    }

    closeModal() {
        const modal = document.getElementById('product-modal');
        modal.classList.add('hidden');
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }

    increaseModalQuantity() {
        const quantityInput = document.getElementById('modal-quantity');
        const currentValue = parseInt(quantityInput.value);
        quantityInput.value = Math.min(currentValue + 1, 100);
    }

    decreaseModalQuantity() {
        const quantityInput = document.getElementById('modal-quantity');
        const currentValue = parseInt(quantityInput.value);
        quantityInput.value = Math.max(currentValue - 1, 1);
    }

    addToCartFromModal() {
        const modal = document.getElementById('product-modal');
        const quantity = parseInt(document.getElementById('modal-quantity').value);

        const product = {
            id: modal.dataset.productId,
            name: modal.dataset.productName,
            price: parseFloat(modal.dataset.productPrice),
            unit: modal.dataset.productUnit,
            quantity: quantity,
            supplierId: modal.dataset.supplierId,
            supplierName: modal.dataset.supplierName,
            image: modal.dataset.productImage
        };

        this.addItem(product);
        this.closeModal();
    }

    buyNowFromModal() {
        this.addToCartFromModal();
        this.toggleCart();
    }

    async checkout() {
        if (this.items.length === 0) {
            this.showNotification('Your cart is empty!', 'error');
            return;
        }

        try {
            // Create order object
            const order = {
                id: 'ORD_' + Date.now(),
                items: this.items,
                subtotal: this.getSubtotal(),
                deliveryCharge: this.deliveryCharge,
                total: this.getTotal(),
                status: 'pending',
                createdAt: new Date().toISOString(),
                vendorInfo: {
                    // This would come from user session in real app
                    name: 'Demo Vendor',
                    phone: '+91 9876543210',
                    address: 'Demo Address'
                }
            };

            // Save order to database
            await database.saveOrder(order);

            // Clear cart
            this.items = [];
            this.saveCartToStorage();
            this.updateCartUI();
            this.closeCart();

            this.showNotification('Order placed successfully!', 'success');
            
            // Redirect to order confirmation or show order details
            this.showOrderConfirmation(order);

        } catch (error) {
            console.error('Checkout error:', error);
            this.showNotification('Failed to place order. Please try again.', 'error');
        }
    }

    showOrderConfirmation(order) {
        const confirmationHtml = `
            <div class="order-confirmation">
                <div class="confirmation-header">
                    <i class="fas fa-check-circle"></i>
                    <h3>Order Placed Successfully!</h3>
                    <p>Order ID: ${order.id}</p>
                </div>
                <div class="confirmation-details">
                    <h4>Order Summary:</h4>
                    <ul>
                        ${order.items.map(item => `
                            <li>${item.name} x ${item.quantity} - ₹${(item.price * item.quantity).toFixed(2)}</li>
                        `).join('')}
                    </ul>
                    <div class="confirmation-total">
                        <strong>Total: ₹${order.total.toFixed(2)}</strong>
                    </div>
                </div>
            </div>
        `;

        // You can show this in a modal or redirect to an order page
        console.log('Order confirmed:', order);
    }

    saveCartToStorage() {
        localStorage.setItem('streetEatsCart', JSON.stringify(this.items));
        // Also save in format compatible with cart.html page
        this.syncWithCartPage();
    }
    
    syncWithCartPage() {
        // Convert cart items to format expected by cart.html
        const cartPageItems = {};
        this.items.forEach((item, index) => {
            const itemId = index + 1;
            cartPageItems[itemId] = {
                name: item.name,
                price: item.price,
                qty: item.quantity,
                unit: item.unit || 'kg',
                supplier: item.supplierName,
                id: item.id,
                supplierId: item.supplierId
            };
        });
        
        // Save for cart page
        localStorage.setItem('streetEatsCartPageData', JSON.stringify(cartPageItems));
        
        // Update navbar cart count immediately
        this.updateCartCount();
    }

    loadCartFromStorage() {
        const savedCart = localStorage.getItem('streetEatsCart');
        if (savedCart) {
            this.items = JSON.parse(savedCart);
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'error' ? 'exclamation-circle' : type === 'success' ? 'check-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;

        notification.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: ${type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#3b82f6'};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 1002;
            display: flex;
            align-items: center;
            gap: 10px;
            max-width: 400px;
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 4000);
    }
}

// Initialize cart when DOM is loaded
let cart;
document.addEventListener('DOMContentLoaded', function() {
    cart = new Cart();
    // Make cart available globally after initialization
    window.cart = cart;
    console.log('Cart initialized:', cart);
});

// Also make it available immediately
window.cart = null;