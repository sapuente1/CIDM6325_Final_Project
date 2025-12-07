// Donation Search Component
class DonationSearch {
    constructor() {
        this.searchInput = document.querySelector('#donation-search, input[name="search"]');
        this.filterContainer = document.querySelector('.filter-container, .search-filters');
        this.resultsContainer = document.querySelector('#donations-container, .donations-grid');
        this.viewToggle = document.querySelectorAll('input[name="view"]');
        
        this.currentQuery = '';
        this.currentFilters = {};
        this.searchTimeout = null;
        
        this.init();
    }
    
    init() {
        if (!this.searchInput || !this.resultsContainer) return;
        
        this.setupSearchInput();
        this.setupFilters();
        this.setupViewToggle();
        this.setupSorting();
        this.setupPagination();
        
        // Load initial state from URL
        this.loadFromURL();
    }
    
    setupSearchInput() {
        this.searchInput.addEventListener('input', (e) => {
            this.currentQuery = e.target.value.trim();
            this.debounceSearch();
        });
        
        // Clear search button
        const clearBtn = document.querySelector('#clear-search, .clear-search');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                this.clearSearch();
            });
        }
    }
    
    setupFilters() {
        const filterElements = document.querySelectorAll(
            'select[name="food_type"], select[name="status"], input[name="distance"]'
        );
        
        filterElements.forEach(element => {
            element.addEventListener('change', () => {
                this.updateFilters();
                this.performSearch();
            });
        });
        
        // Advanced filters toggle
        const advancedToggle = document.querySelector('#advanced-filters-toggle');
        const advancedFilters = document.querySelector('#advanced-filters');
        
        if (advancedToggle && advancedFilters) {
            advancedToggle.addEventListener('click', () => {
                advancedFilters.classList.toggle('d-none');
                const icon = advancedToggle.querySelector('i');
                if (icon) {
                    icon.classList.toggle('bi-chevron-down');
                    icon.classList.toggle('bi-chevron-up');
                }
            });
        }
    }
    
    setupViewToggle() {
        this.viewToggle.forEach(toggle => {
            toggle.addEventListener('change', () => {
                if (toggle.checked) {
                    this.switchView(toggle.value);
                }
            });
        });
    }
    
    setupSorting() {
        const sortSelect = document.querySelector('select[name="sort"], #sort-select');
        if (sortSelect) {
            sortSelect.addEventListener('change', () => {
                this.performSearch();
            });
        }
    }
    
    setupPagination() {
        // Handle pagination clicks
        document.addEventListener('click', (e) => {
            if (e.target.matches('.pagination a[href], .page-link[href]')) {
                e.preventDefault();
                const url = new URL(e.target.href);
                const page = url.searchParams.get('page');
                if (page) {
                    this.loadPage(page);
                }
            }
        });
    }
    
    debounceSearch() {
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            this.performSearch();
        }, 300);
    }
    
    updateFilters() {
        this.currentFilters = {};
        
        // Collect all filter values
        const filterElements = document.querySelectorAll(
            'select[name], input[name]:checked, input[name][type="range"]'
        );
        
        filterElements.forEach(element => {
            if (element.value && element.name !== 'search' && element.name !== 'csrfmiddlewaretoken') {
                this.currentFilters[element.name] = element.value;
            }
        });
    }
    
    async performSearch() {
        if (!this.resultsContainer) return;
        
        this.showLoading();
        
        try {
            const url = this.buildSearchURL();
            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'text/html'
                }
            });
            
            if (response.ok) {
                const html = await response.text();
                this.updateResults(html);
                this.updateURL(url);
                this.updateResultsCount();
            } else {
                throw new Error(`Search failed: ${response.status}`);
            }
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Search failed. Please try again.');
        } finally {
            this.hideLoading();
        }
    }
    
    buildSearchURL() {
        const url = new URL(window.location.origin + window.location.pathname);
        
        // Add search query
        if (this.currentQuery) {
            url.searchParams.set('search', this.currentQuery);
        }
        
        // Add filters
        Object.entries(this.currentFilters).forEach(([key, value]) => {
            url.searchParams.set(key, value);
        });
        
        // Add sorting
        const sortSelect = document.querySelector('select[name="sort"]');
        if (sortSelect && sortSelect.value) {
            url.searchParams.set('sort', sortSelect.value);
        }
        
        return url.toString();
    }
    
    updateResults(html) {
        // Parse the HTML response
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        
        // Update main results container
        const newResults = doc.querySelector('#donations-container, .donations-grid');
        if (newResults) {
            this.resultsContainer.innerHTML = newResults.innerHTML;
        }
        
        // Update pagination
        const newPagination = doc.querySelector('.pagination');
        const currentPagination = document.querySelector('.pagination');
        if (newPagination && currentPagination) {
            currentPagination.parentNode.innerHTML = newPagination.parentNode.innerHTML;
        }
        
        // Re-initialize any dynamic components
        this.initializeCards();
    }
    
    updateURL(url) {
        // Update browser URL without page reload
        const urlObj = new URL(url);
        history.pushState({}, '', urlObj.search ? urlObj.pathname + urlObj.search : urlObj.pathname);
    }
    
    updateResultsCount() {
        const cards = this.resultsContainer.querySelectorAll('.donation-card');
        const countElement = document.querySelector('#results-count, .results-count');
        
        if (countElement) {
            const count = cards.length;
            countElement.textContent = `${count} donation${count !== 1 ? 's' : ''} found`;
        }
    }
    
    switchView(viewType) {
        if (viewType === 'list') {
            this.resultsContainer.classList.add('list-view');
        } else {
            this.resultsContainer.classList.remove('list-view');
        }
        
        // Store preference
        localStorage.setItem('donation-view-preference', viewType);
    }
    
    clearSearch() {
        this.searchInput.value = '';
        this.currentQuery = '';
        
        // Reset filters
        const filterElements = document.querySelectorAll('select[name], input[name]:checked');
        filterElements.forEach(element => {
            if (element.type === 'checkbox') {
                element.checked = false;
            } else {
                element.selectedIndex = 0;
            }
        });
        
        this.currentFilters = {};
        this.performSearch();
    }
    
    loadPage(pageNumber) {
        const url = new URL(this.buildSearchURL());
        url.searchParams.set('page', pageNumber);
        
        this.performSearch();
    }
    
    loadFromURL() {
        const params = new URLSearchParams(window.location.search);
        
        // Load search query
        const query = params.get('search');
        if (query) {
            this.searchInput.value = query;
            this.currentQuery = query;
        }
        
        // Load filters
        params.forEach((value, key) => {
            if (key !== 'search' && key !== 'page') {
                const element = document.querySelector(`[name="${key}"]`);
                if (element) {
                    if (element.type === 'checkbox') {
                        element.checked = true;
                    } else {
                        element.value = value;
                    }
                }
            }
        });
        
        this.updateFilters();
        
        // Load view preference
        const viewPreference = localStorage.getItem('donation-view-preference');
        if (viewPreference) {
            const viewToggle = document.querySelector(`input[name="view"][value="${viewPreference}"]`);
            if (viewToggle) {
                viewToggle.checked = true;
                this.switchView(viewPreference);
            }
        }
    }
    
    initializeCards() {
        // Reinitialize any card-specific functionality
        const cards = this.resultsContainer.querySelectorAll('.donation-card');
        cards.forEach(card => {
            // Add hover effects
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-2px)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = '';
            });
        });
        
        // Lazy load images
        const images = this.resultsContainer.querySelectorAll('img[data-src]');
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            images.forEach(img => imageObserver.observe(img));
        } else {
            // Fallback for browsers without IntersectionObserver
            images.forEach(img => {
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
            });
        }
    }
    
    showLoading() {
        const loadingHtml = `
            <div class="text-center p-5 loading-placeholder">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-3 text-muted">Searching donations...</p>
            </div>
        `;
        
        this.resultsContainer.innerHTML = loadingHtml;
    }
    
    hideLoading() {
        const loading = this.resultsContainer.querySelector('.loading-placeholder');
        if (loading) {
            loading.remove();
        }
    }
    
    showError(message) {
        const errorHtml = `
            <div class="alert alert-danger text-center" role="alert">
                <i class="bi bi-exclamation-triangle me-2"></i>
                ${message}
                <button type="button" class="btn btn-outline-danger btn-sm ms-3" onclick="location.reload()">
                    <i class="bi bi-arrow-clockwise me-1"></i>Retry
                </button>
            </div>
        `;
        
        this.resultsContainer.innerHTML = errorHtml;
    }
    
    // Public methods for external use
    addFilter(name, value) {
        this.currentFilters[name] = value;
        this.performSearch();
    }
    
    removeFilter(name) {
        delete this.currentFilters[name];
        this.performSearch();
    }
    
    setQuery(query) {
        this.currentQuery = query;
        this.searchInput.value = query;
        this.performSearch();
    }
    
    refresh() {
        this.performSearch();
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('#donation-search, input[name="search"]')) {
        window.donationSearch = new DonationSearch();
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DonationSearch;
}