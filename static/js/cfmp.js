// CFMP Main JavaScript Application
class CFMP {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupPageLoader();
        this.setupCSRF();
        this.setupFormValidation();
        this.setupSearchHandlers();
        this.setupModalHandlers();
        this.setupTimeAgo();
        this.setupImageUpload();
        this.setupSidebar();
        this.setupNavbarScroll();
        this.setupNotifications();
        
        console.log('CFMP application initialized');
    }
    
    // Page loader functionality
    setupPageLoader() {
        // Hide page loader once DOM is ready
        setTimeout(() => {
            const loader = document.getElementById('pageLoader');
            if (loader) {
                loader.classList.add('hidden');
                setTimeout(() => {
                    loader.style.display = 'none';
                }, 300);
            }
        }, 500);
        
        // Show loader for page navigation
        window.addEventListener('beforeunload', () => {
            const loader = document.getElementById('pageLoader');
            if (loader) {
                loader.style.display = 'flex';
                loader.classList.remove('hidden');
            }
        });
    }
    
    // CSRF token setup for AJAX requests
    setupCSRF() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (!csrfToken) return;
        
        const token = csrfToken.value;
        
        // Set up CSRF for fetch requests
        const originalFetch = window.fetch;
        window.fetch = function(url, options = {}) {
            if (options.method && options.method.toUpperCase() !== 'GET') {
                options.headers = {
                    'X-CSRFToken': token,
                    ...options.headers
                };
            }
            return originalFetch.apply(this, [url, options]);
        };
    }
    
    // Enhanced form validation
    setupFormValidation() {
        const forms = document.querySelectorAll('.needs-validation, form');
        
        forms.forEach(form => {
            form.addEventListener('submit', (event) => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                    
                    // Focus on first invalid field
                    const firstInvalid = form.querySelector(':invalid');
                    if (firstInvalid) {
                        firstInvalid.focus();
                        firstInvalid.scrollIntoView({ 
                            behavior: 'smooth', 
                            block: 'center' 
                        });
                    }
                }
                form.classList.add('was-validated');
            });
            
            // Real-time validation
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('blur', () => {
                    if (form.classList.contains('was-validated')) {
                        input.checkValidity();
                    }
                });
            });
        });
    }
    
    // Real-time search functionality
    setupSearchHandlers() {
        const searchInput = document.querySelector('#donation-search, input[name="search"]');
        if (!searchInput) return;
        
        let searchTimeout;
        
        searchInput.addEventListener('input', (event) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.performSearch(event.target.value);
            }, 300);
        });
        
        // Search filters
        const filterSelects = document.querySelectorAll('select[name="food_type"], select[name="status"]');
        filterSelects.forEach(select => {
            select.addEventListener('change', () => {
                this.performSearch(searchInput.value);
            });
        });
    }
    
    async performSearch(query) {
        const searchContainer = document.querySelector('#search-results, #donations-container');
        if (!searchContainer) return;
        
        const url = new URL(window.location.href);
        url.searchParams.set('search', query);
        
        // Add other filter parameters
        const filterInputs = document.querySelectorAll('select[name], input[name]:checked');
        filterInputs.forEach(input => {
            if (input.value && input.name !== 'search') {
                url.searchParams.set(input.name, input.value);
            }
        });
        
        try {
            this.showLoadingSpinner(searchContainer);
            
            const response = await fetch(url.toString(), {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json, text/html'
                }
            });
            
            if (response.ok) {
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const data = await response.json();
                    this.updateSearchResults(data);
                } else {
                    const html = await response.text();
                    searchContainer.innerHTML = html;
                }
            }
        } catch (error) {
            console.error('Search error:', error);
            this.showNotification('Search failed. Please try again.', 'error');
        } finally {
            this.hideLoadingSpinner(searchContainer);
        }
    }
    
    updateSearchResults(data) {
        const container = document.querySelector('#donations-container');
        if (!container) return;
        
        // Update results count
        const countElement = document.querySelector('#results-count');
        if (countElement && data.count !== undefined) {
            countElement.textContent = `${data.count} donation${data.count !== 1 ? 's' : ''} found`;
        }
        
        // Update pagination if provided
        if (data.pagination_html) {
            const paginationContainer = document.querySelector('.pagination');
            if (paginationContainer) {
                paginationContainer.outerHTML = data.pagination_html;
            }
        }
    }
    
    // Modal handling
    setupModalHandlers() {
        // Donation claim modal
        document.addEventListener('click', (event) => {
            if (event.target.matches('.claim-donation-btn, [data-claim-donation]')) {
                const donationId = event.target.dataset.donationId || 
                                  event.target.dataset.claimDonation;
                this.showClaimModal(donationId);
            }
            
            // Confirm delete modal
            if (event.target.matches('.delete-donation-btn, [data-delete-donation]')) {
                const donationId = event.target.dataset.donationId || 
                                  event.target.dataset.deleteDonation;
                this.showDeleteConfirmation(donationId);
            }
        });
        
        // Modal close handlers
        document.addEventListener('click', (event) => {
            if (event.target.matches('.modal-backdrop')) {
                const modal = event.target.closest('.modal');
                if (modal) {
                    const bsModal = bootstrap.Modal.getInstance(modal);
                    if (bsModal) bsModal.hide();
                }
            }
        });
    }
    
    async showClaimModal(donationId) {
        const modal = document.getElementById('claimModal');
        if (!modal) return;
        
        const modalBody = modal.querySelector('.modal-body');
        
        try {
            const response = await fetch(`/donations/${donationId}/claim/`);
            if (response.ok) {
                modalBody.innerHTML = await response.text();
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            }
        } catch (error) {
            console.error('Error loading claim modal:', error);
            this.showNotification('Failed to load claim form. Please try again.', 'error');
        }
    }
    
    showDeleteConfirmation(donationId) {
        const confirmed = confirm('Are you sure you want to delete this donation? This action cannot be undone.');
        if (confirmed) {
            this.deleteDonation(donationId);
        }
    }
    
    async deleteDonation(donationId) {
        try {
            const response = await fetch(`/donations/${donationId}/delete/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
            });
            
            if (response.ok) {
                this.showNotification('Donation deleted successfully', 'success');
                // Redirect or remove from list
                const donationCard = document.querySelector(`[data-donation-id="${donationId}"]`);
                if (donationCard) {
                    donationCard.remove();
                } else {
                    window.location.href = '/donations/';
                }
            } else {
                throw new Error('Delete failed');
            }
        } catch (error) {
            console.error('Delete error:', error);
            this.showNotification('Failed to delete donation. Please try again.', 'error');
        }
    }
    
    // Time ago functionality
    setupTimeAgo() {
        const timeElements = document.querySelectorAll('[data-time]');
        
        timeElements.forEach(element => {
            const timestamp = new Date(element.dataset.time);
            element.textContent = this.timeAgo(timestamp);
            element.title = timestamp.toLocaleDateString() + ' ' + timestamp.toLocaleTimeString();
        });
        
        // Update every minute
        setInterval(() => {
            timeElements.forEach(element => {
                const timestamp = new Date(element.dataset.time);
                element.textContent = this.timeAgo(timestamp);
            });
        }, 60000);
    }
    
    timeAgo(date) {
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);
        
        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
        if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)} days ago`;
        
        return date.toLocaleDateString();
    }
    
    // Image upload functionality
    setupImageUpload() {
        const uploadAreas = document.querySelectorAll('.image-upload-area');
        
        uploadAreas.forEach(area => {
            const input = area.querySelector('input[type="file"]');
            if (!input) return;
            
            // Click to upload
            area.addEventListener('click', (e) => {
                if (e.target === input) return;
                input.click();
            });
            
            // Drag and drop
            area.addEventListener('dragover', (e) => {
                e.preventDefault();
                area.classList.add('dragover');
            });
            
            area.addEventListener('dragleave', () => {
                area.classList.remove('dragover');
            });
            
            area.addEventListener('drop', (e) => {
                e.preventDefault();
                area.classList.remove('dragover');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    input.files = files;
                    this.previewImage(files[0], area);
                }
            });
            
            // File input change
            input.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    this.previewImage(e.target.files[0], area);
                }
            });
        });
    }
    
    previewImage(file, container) {
        if (!file || !file.type.startsWith('image/')) return;
        
        // Validate file size (5MB limit)
        if (file.size > 5 * 1024 * 1024) {
            this.showNotification('Image file too large. Maximum size is 5MB.', 'warning');
            return;
        }
        
        const reader = new FileReader();
        reader.onload = (e) => {
            const preview = container.querySelector('#image-preview, .image-preview');
            if (preview) {
                const img = preview.querySelector('img');
                if (img) {
                    img.src = e.target.result;
                    preview.classList.remove('d-none');
                    
                    // Hide upload prompt
                    const uploadContent = container.querySelector('#upload-content, .upload-content');
                    if (uploadContent) {
                        const children = uploadContent.children;
                        for (let i = 0; i < children.length - 1; i++) {
                            if (!children[i].classList.contains('image-preview')) {
                                children[i].classList.add('d-none');
                            }
                        }
                    }
                }
            }
        };
        reader.readAsDataURL(file);
    }
    
    // Sidebar functionality
    setupSidebar() {
        const sidebarToggle = document.querySelector('.navbar-toggler');
        const sidebar = document.querySelector('.sidebar');
        const backdrop = document.querySelector('.sidebar-backdrop');
        
        if (!sidebarToggle || !sidebar) return;
        
        // Create backdrop if it doesn't exist
        if (!backdrop && window.innerWidth <= 768) {
            const newBackdrop = document.createElement('div');
            newBackdrop.className = 'sidebar-backdrop';
            document.body.appendChild(newBackdrop);
            
            newBackdrop.addEventListener('click', () => {
                this.hideSidebar();
            });
        }
        
        sidebarToggle.addEventListener('click', () => {
            this.toggleSidebar();
        });
        
        // Close sidebar on window resize
        window.addEventListener('resize', () => {
            if (window.innerWidth > 768) {
                this.hideSidebar();
            }
        });
    }
    
    toggleSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const backdrop = document.querySelector('.sidebar-backdrop');
        
        if (sidebar.classList.contains('show')) {
            this.hideSidebar();
        } else {
            sidebar.classList.add('show');
            if (backdrop) backdrop.classList.add('show');
            document.body.style.overflow = 'hidden';
        }
    }
    
    hideSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const backdrop = document.querySelector('.sidebar-backdrop');
        
        sidebar.classList.remove('show');
        if (backdrop) backdrop.classList.remove('show');
        document.body.style.overflow = '';
    }
    
    // Navbar scroll effect
    setupNavbarScroll() {
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;
        
        let lastScrollY = window.scrollY;
        
        window.addEventListener('scroll', () => {
            const currentScrollY = window.scrollY;
            
            if (currentScrollY > 100) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
            
            lastScrollY = currentScrollY;
        });
    }
    
    // Notification system
    setupNotifications() {
        // Auto-dismiss alerts
        const alerts = document.querySelectorAll('.alert-success, .alert-info');
        alerts.forEach(alert => {
            const isSuccess = alert.classList.contains('alert-success');
            const delay = isSuccess ? 5000 : 7000;
            
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, delay);
        });
    }
    
    showNotification(message, type = 'info') {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                <i class="bi bi-${this.getAlertIcon(type)} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        let container = document.querySelector('#notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'position-fixed top-0 end-0 p-3';
            container.style.zIndex = '1060';
            document.body.appendChild(container);
        }
        
        container.insertAdjacentHTML('afterbegin', alertHtml);
        
        // Auto-dismiss after delay
        const alert = container.querySelector('.alert');
        setTimeout(() => {
            if (alert && alert.parentNode) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, type === 'success' ? 5000 : 7000);
    }
    
    getAlertIcon(type) {
        const icons = {
            'success': 'check-circle-fill',
            'danger': 'exclamation-triangle-fill',
            'warning': 'exclamation-circle-fill',
            'info': 'info-circle-fill',
            'error': 'exclamation-triangle-fill'
        };
        return icons[type] || 'info-circle-fill';
    }
    
    // Loading spinner utilities
    showLoadingSpinner(container) {
        const spinner = document.createElement('div');
        spinner.className = 'text-center p-4 loading-spinner-container';
        spinner.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2 text-muted">Loading...</p>
        `;
        container.appendChild(spinner);
    }
    
    hideLoadingSpinner(container) {
        const spinner = container.querySelector('.loading-spinner-container');
        if (spinner) {
            spinner.remove();
        }
    }
    
    // Utility methods
    debounce(func, wait) {
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
    
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.cfmp = new CFMP();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CFMP;
}