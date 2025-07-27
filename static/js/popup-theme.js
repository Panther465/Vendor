/* ===== THEMED POPUP SYSTEM ===== */

class ThemedPopup {
    constructor() {
        this.activeModal = null;
        this.toastContainer = null;
        this.init();
    }

    init() {
        // Create toast container
        this.createToastContainer();
        
        // Override default alert, confirm functions
        this.overrideDefaults();
        
        // Handle escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.activeModal) {
                this.closeModal();
            }
        });
    }

    createToastContainer() {
        this.toastContainer = document.createElement('div');
        this.toastContainer.className = 'toast-container';
        document.body.appendChild(this.toastContainer);
    }

    overrideDefaults() {
        // Override window.alert
        window.alert = (message, title = 'Alert', type = 'info') => {
            return this.showAlert(message, title, type);
        };

        // Override window.confirm
        window.confirm = (message, title = 'Confirm', options = {}) => {
            return this.showConfirm(message, title, options);
        };
    }

    createModal(type = 'default') {
        const overlay = document.createElement('div');
        overlay.className = `modal-overlay modal-${type}`;
        
        const container = document.createElement('div');
        container.className = 'modal-container';
        
        overlay.appendChild(container);
        document.body.appendChild(overlay);
        
        // Close on overlay click
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                this.closeModal();
            }
        });
        
        return { overlay, container };
    }

    showAlert(message, title = 'Alert', type = 'info') {
        return new Promise((resolve) => {
            const { overlay, container } = this.createModal('alert');
            this.activeModal = overlay;

            const iconMap = {
                info: 'fas fa-info-circle',
                success: 'fas fa-check-circle',
                warning: 'fas fa-exclamation-triangle',
                error: 'fas fa-times-circle'
            };

            container.innerHTML = `
                <div class="modal-header">
                    <h3 class="modal-title">
                        <i class="${iconMap[type] || iconMap.info}"></i>
                        ${title}
                    </h3>
                    <button class="modal-close" onclick="themedPopup.closeModal()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <p class="modal-message">${message}</p>
                </div>
                <div class="modal-footer">
                    <button class="modal-btn modal-btn-primary" onclick="themedPopup.closeModal(); themedPopup.resolveModal(true);">
                        <i class="fas fa-check"></i>
                        OK
                    </button>
                </div>
            `;

            this.currentResolve = resolve;
            this.showModal(overlay);
        });
    }

    showConfirm(message, title = 'Confirm', options = {}) {
        return new Promise((resolve) => {
            const { overlay, container } = this.createModal('confirm');
            this.activeModal = overlay;

            const {
                confirmText = 'Confirm',
                cancelText = 'Cancel',
                confirmClass = 'modal-btn-danger',
                cancelClass = 'modal-btn-secondary',
                icon = 'fas fa-question-circle'
            } = options;

            container.innerHTML = `
                <div class="modal-header">
                    <h3 class="modal-title">
                        <i class="${icon}"></i>
                        ${title}
                    </h3>
                    <button class="modal-close" onclick="themedPopup.closeModal(); themedPopup.resolveModal(false);">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <p class="modal-message">${message}</p>
                </div>
                <div class="modal-footer">
                    <button class="modal-btn ${cancelClass}" onclick="themedPopup.closeModal(); themedPopup.resolveModal(false);">
                        <i class="fas fa-times"></i>
                        ${cancelText}
                    </button>
                    <button class="modal-btn ${confirmClass}" onclick="themedPopup.closeModal(); themedPopup.resolveModal(true);">
                        <i class="fas fa-check"></i>
                        ${confirmText}
                    </button>
                </div>
            `;

            this.currentResolve = resolve;
            this.showModal(overlay);
        });
    }

    showCustomModal(content, options = {}) {
        return new Promise((resolve) => {
            const { overlay, container } = this.createModal(options.type || 'default');
            this.activeModal = overlay;

            container.innerHTML = content;
            this.currentResolve = resolve;
            this.showModal(overlay);
        });
    }

    showModal(overlay) {
        // Add to DOM and trigger animation
        setTimeout(() => {
            overlay.classList.add('active');
        }, 10);
    }

    closeModal() {
        if (this.activeModal) {
            this.activeModal.classList.remove('active');
            setTimeout(() => {
                if (this.activeModal && this.activeModal.parentNode) {
                    this.activeModal.parentNode.removeChild(this.activeModal);
                }
                this.activeModal = null;
            }, 300);
        }
    }

    resolveModal(result) {
        if (this.currentResolve) {
            this.currentResolve(result);
            this.currentResolve = null;
        }
    }

    // Toast notifications
    showToast(message, title = '', type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        const iconMap = {
            success: 'fas fa-check-circle',
            error: 'fas fa-times-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };

        toast.innerHTML = `
            <div class="toast-icon">
                <i class="${iconMap[type] || iconMap.info}"></i>
            </div>
            <div class="toast-content">
                ${title ? `<div class="toast-title">${title}</div>` : ''}
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

        this.toastContainer.appendChild(toast);

        // Trigger animation
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);

        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.classList.remove('show');
                    setTimeout(() => {
                        if (toast.parentNode) {
                            toast.parentNode.removeChild(toast);
                        }
                    }, 300);
                }
            }, duration);
        }

        return toast;
    }

    // Convenience methods
    success(message, title = 'Success') {
        return this.showToast(message, title, 'success');
    }

    error(message, title = 'Error') {
        return this.showToast(message, title, 'error');
    }

    warning(message, title = 'Warning') {
        return this.showToast(message, title, 'warning');
    }

    info(message, title = 'Info') {
        return this.showToast(message, title, 'info');
    }

    // Loading modal
    showLoading(message = 'Loading...') {
        const { overlay, container } = this.createModal('loading');
        this.activeModal = overlay;

        container.innerHTML = `
            <div class="modal-loading">
                <div class="modal-spinner"></div>
                <p style="margin-left: 15px; color: var(--text-color);">${message}</p>
            </div>
        `;

        this.showModal(overlay);
        return overlay;
    }

    // Notification-specific methods
    confirmDelete(itemName = 'this item') {
        return this.showConfirm(
            `Are you sure you want to delete ${itemName}? This action cannot be undone.`,
            'Delete Confirmation',
            {
                confirmText: 'Delete',
                cancelText: 'Cancel',
                confirmClass: 'modal-btn-danger',
                icon: 'fas fa-trash-alt'
            }
        );
    }

    confirmDeleteAll(itemType = 'items') {
        return this.showConfirm(
            `Are you sure you want to delete ALL ${itemType}? This action cannot be undone.`,
            'Delete All Confirmation',
            {
                confirmText: 'Delete All',
                cancelText: 'Cancel',
                confirmClass: 'modal-btn-danger',
                icon: 'fas fa-exclamation-triangle'
            }
        );
    }

    confirmMarkAllRead() {
        return this.showConfirm(
            'Mark all notifications as read?',
            'Mark All Read',
            {
                confirmText: 'Mark All Read',
                cancelText: 'Cancel',
                confirmClass: 'modal-btn-success',
                icon: 'fas fa-check-double'
            }
        );
    }
}

// Initialize the themed popup system
const themedPopup = new ThemedPopup();

// Export for use in other scripts
window.themedPopup = themedPopup;