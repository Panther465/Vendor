// Suppliers page functionality
document.addEventListener('DOMContentLoaded', function() {
    // Global variables
    let placesService;
    let searchCenter = { lat: 20.5937, lng: 78.9629 }; // Default: Central India
    let currentSearchQuery = '';
    
    // Indian states data
    const indianStates = {
        "Andhra Pradesh": { lat: 15.9129, lng: 79.7400 },
        "Arunachal Pradesh": { lat: 28.2180, lng: 94.7278 },
        "Assam": { lat: 26.2006, lng: 92.9376 },
        "Bihar": { lat: 25.0961, lng: 85.3131 },
        "Chhattisgarh": { lat: 21.2787, lng: 81.8661 },
        "Goa": { lat: 15.2993, lng: 74.1240 },
        "Gujarat": { lat: 22.2587, lng: 71.1924 },
        "Haryana": { lat: 29.0588, lng: 76.0856 },
        "Himachal Pradesh": { lat: 31.1048, lng: 77.1734 },
        "Jharkhand": { lat: 23.6102, lng: 85.2799 },
        "Karnataka": { lat: 15.3173, lng: 75.7139 },
        "Kerala": { lat: 10.8505, lng: 76.2711 },
        "Madhya Pradesh": { lat: 22.9734, lng: 78.6569 },
        "Maharashtra": { lat: 19.7515, lng: 75.7139 },
        "Manipur": { lat: 24.6637, lng: 93.9063 },
        "Meghalaya": { lat: 25.4670, lng: 91.3662 },
        "Mizoram": { lat: 23.1645, lng: 92.9376 },
        "Nagaland": { lat: 26.1584, lng: 94.5624 },
        "Odisha": { lat: 20.9517, lng: 85.0985 },
        "Punjab": { lat: 31.1471, lng: 75.3412 },
        "Rajasthan": { lat: 27.0238, lng: 74.2179 },
        "Sikkim": { lat: 27.5330, lng: 88.5122 },
        "Tamil Nadu": { lat: 11.1271, lng: 78.6569 },
        "Telangana": { lat: 18.1124, lng: 79.0193 },
        "Tripura": { lat: 23.9408, lng: 91.9882 },
        "Uttar Pradesh": { lat: 26.8467, lng: 80.9462 },
        "Uttarakhand": { lat: 30.0668, lng: 79.0193 },
        "West Bengal": { lat: 22.9868, lng: 87.8550 }
    };
    
    // Category search terms mapping
    const categorySearchTerms = {
        vegetables: 'wholesale vegetable market OR vegetable supplier OR fresh vegetables wholesale',
        fruits: 'wholesale fruit market OR fruit supplier OR fresh fruits wholesale',
        dairy: 'dairy wholesale OR milk supplier OR cheese wholesale OR dairy products',
        spices: 'spice wholesale OR masala supplier OR spices market OR condiments wholesale',
        grains: 'grain wholesale OR rice supplier OR wheat wholesale OR pulses market',
        meat: 'meat wholesale OR chicken supplier OR mutton wholesale OR meat market',
        oil: 'cooking oil wholesale OR ghee supplier OR oil wholesale OR edible oil',
        packaging: 'food packaging supplier OR disposable plates wholesale OR packaging materials OR food containers'
    };
    
    // DOM elements
    const stateSelector = document.getElementById('state-selector');
    const currentLocationBtn = document.getElementById('current-location-btn');
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const categoryBtns = document.querySelectorAll('.category-btn');
    const loadingState = document.getElementById('loading-state');
    const emptyState = document.getElementById('empty-state');
    const noResultsState = document.getElementById('no-results-state');
    const resultsGrid = document.getElementById('results-grid');
    const resultsTitle = document.getElementById('results-title');
    const resultsCount = document.getElementById('results-count');
    const loadingText = document.getElementById('loading-text');
    
    // Initialize the page
    function initializePage() {
        populateStateSelector();
        setupEventListeners();
        showEmptyState();
    }
    
    // Populate state selector
    function populateStateSelector() {
        Object.keys(indianStates).forEach(state => {
            const option = document.createElement('option');
            option.value = state;
            option.textContent = state;
            stateSelector.appendChild(option);
        });
    }
    
    // Setup event listeners
    function setupEventListeners() {
        stateSelector.addEventListener('change', handleStateSelection);
        currentLocationBtn.addEventListener('click', handleCurrentLocation);
        searchBtn.addEventListener('click', handleSearch);
        
        // Add test search button
        const testSearchBtn = document.getElementById('test-search-btn');
        if (testSearchBtn) {
            testSearchBtn.addEventListener('click', function() {
                const searchTerm = searchInput.value.trim() || 'vegetables';
                console.log('Test search initiated');
                useFallbackSearch(searchTerm);
            });
        }
        
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                handleSearch();
            }
        });
        
        categoryBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                handleCategorySelection(this);
            });
        });
    }
    
    // Handle state selection
    function handleStateSelection() {
        const selectedState = stateSelector.value;
        console.log('State selected:', selectedState);
        if (selectedState && indianStates[selectedState]) {
            searchCenter = indianStates[selectedState];
            console.log('Search center updated to:', searchCenter);
            showNotification(`Location set to ${selectedState}. Ready to search!`);
        }
    }
    
    // Handle current location
    function handleCurrentLocation() {
        if (!navigator.geolocation) {
            showNotification('Geolocation is not supported by this browser.', 'error');
            return;
        }
        
        showLoading('Getting your location...');
        
        navigator.geolocation.getCurrentPosition(
            function(position) {
                searchCenter = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                
                // Use reverse geocoding to get location name
                reverseGeocode(position.coords.latitude, position.coords.longitude);
                hideLoading();
            },
            function(error) {
                hideLoading();
                let errorMessage = 'Unable to get your location. ';
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        errorMessage += 'Please allow location access.';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMessage += 'Location information unavailable.';
                        break;
                    case error.TIMEOUT:
                        errorMessage += 'Location request timed out.';
                        break;
                    default:
                        errorMessage += 'An unknown error occurred.';
                        break;
                }
                showNotification(errorMessage, 'error');
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 300000
            }
        );
    }
    
    // Handle category selection
    function handleCategorySelection(button) {
        // Remove active class from all buttons
        categoryBtns.forEach(btn => btn.classList.remove('active'));
        
        // Add active class to clicked button
        button.classList.add('active');
        
        // Get category and set search input
        const category = button.dataset.category;
        const categoryName = button.textContent.trim();
        searchInput.value = categoryName;
        currentSearchQuery = categorySearchTerms[category] || categoryName;
    }
    
    // Handle search
    function handleSearch() {
        const searchTerm = searchInput.value.trim();
        
        if (!searchTerm) {
            showNotification('Please enter a search term or select a category.', 'error');
            return;
        }
        
        console.log('Search initiated with term:', searchTerm);
        console.log('Current search center:', searchCenter);
        
        // Use category search terms if available, otherwise use the search term
        const activeCategory = document.querySelector('.category-btn.active');
        let searchQuery;
        
        if (activeCategory) {
            const category = activeCategory.dataset.category;
            searchQuery = categorySearchTerms[category];
        } else {
            // Create a more specific search query for raw materials
            searchQuery = `${searchTerm} wholesale OR ${searchTerm} supplier OR ${searchTerm} market OR bulk ${searchTerm}`;
        }
        
        console.log('Final search query:', searchQuery);
        performSearch(searchQuery, searchTerm);
    }
    
    // Perform the actual search
    function performSearch(searchQuery, displayTerm) {
        console.log('Starting search with query:', searchQuery);
        console.log('Search center:', searchCenter);
        console.log('Places service:', placesService);
        
        const service = getPlacesService();
        if (!service) {
            console.error('Google Maps service not available, using fallback');
            showNotification('Google Maps service not available. Using demo data.', 'info');
            // Use fallback demo data
            useFallbackSearch(displayTerm);
            return;
        }
        
        showLoading(`Searching for ${displayTerm} suppliers...`);
        hideAllStates();
        
        const searchRequest = {
            location: searchCenter,
            radius: '50000', // 50km radius
            query: searchQuery
        };
        
        console.log('Search request:', searchRequest);
        
        service.textSearch(searchRequest, function(results, status) {
            console.log('Search results:', results);
            console.log('Search status:', status);
            
            if (status === google.maps.places.PlacesServiceStatus.OK && results && results.length > 0) {
                loadingText.textContent = `Found ${results.length} suppliers. Getting details...`;
                
                // Get detailed information for each place
                const detailPromises = results.map(place => getPlaceDetails(place.place_id));
                
                Promise.all(detailPromises).then(detailedResults => {
                    const validResults = detailedResults.filter(result => result !== null);
                    console.log('Valid results:', validResults);
                    hideLoading();
                    
                    if (validResults.length > 0) {
                        displaySuppliersWithProducts(validResults, displayTerm);
                    } else {
                        showNoResults();
                    }
                });
            } else {
                console.error('Search failed with status:', status);
                hideLoading();
                showNoResults();
            }
        });
    }
    
    // Get detailed place information
    function getPlaceDetails(placeId) {
        return new Promise((resolve) => {
            const request = {
                placeId: placeId,
                fields: [
                    'name', 'formatted_address', 'formatted_phone_number', 
                    'rating', 'photos', 'place_id', 'website', 'types',
                    'opening_hours', 'price_level'
                ]
            };
            
            const service = getPlacesService();
            if (!service) {
                resolve(null);
                return;
            }
            service.getDetails(request, function(place, status) {
                if (status === google.maps.places.PlacesServiceStatus.OK) {
                    resolve(place);
                } else {
                    console.error(`Failed to get details for place ${placeId}:`, status);
                    resolve(null);
                }
            });
        });
    }
    
    // Display search results
    function displayResults(results, searchTerm) {
        resultsTitle.textContent = `${searchTerm} Suppliers`;
        resultsCount.textContent = `${results.length} supplier${results.length !== 1 ? 's' : ''} found`;
        
        resultsGrid.innerHTML = '';
        
        results.forEach(supplier => {
            const card = createSupplierCard(supplier);
            resultsGrid.appendChild(card);
        });
        
        showResults();
    }

    // Display suppliers with their products
    function displaySuppliersWithProducts(suppliers, searchTerm) {
        resultsTitle.textContent = `${searchTerm} Suppliers & Products`;
        resultsCount.textContent = `${suppliers.length} supplier${suppliers.length !== 1 ? 's' : ''} found`;
        
        resultsGrid.innerHTML = '';
        
        suppliers.forEach(supplier => {
            const supplierCard = createSupplierWithProductsCard(supplier, searchTerm);
            resultsGrid.appendChild(supplierCard);
        });
        
        showResults();
    }
    
    // Create supplier card
    function createSupplierCard(supplier) {
        const card = document.createElement('div');
        card.className = 'supplier-card';
        
        // Generate placeholder image with supplier type
        const supplierType = getSupplierType(supplier.types);
        const colors = ['3b82f6', '10b981', 'ef4444', 'f97316', '8b5cf6', 'f59e0b'];
        const bgColor = colors[Math.floor(Math.random() * colors.length)];
        const placeholderUrl = `https://placehold.co/400x200/${bgColor}/ffffff?text=${encodeURIComponent(supplierType)}&font=lora`;
        
        // Rating display
        const ratingHtml = supplier.rating ? `
            <div class="supplier-rating">
                <i class="fas fa-star"></i>
                <span>${supplier.rating.toFixed(1)}</span>
            </div>
        ` : '';
        
        // Phone display
        const phoneHtml = supplier.formatted_phone_number ? `
            <div class="supplier-phone">
                <i class="fas fa-phone"></i>
                <a href="tel:${supplier.formatted_phone_number}">${supplier.formatted_phone_number}</a>
            </div>
        ` : `
            <div class="supplier-phone">
                <i class="fas fa-phone"></i>
                <span style="color: var(--text-lighter);">Phone not available</span>
            </div>
        `;
        
        // Types display
        const typesHtml = supplier.types ? 
            supplier.types.slice(0, 3).map(type => 
                `<span class="supplier-type">${type.replace(/_/g, ' ')}</span>`
            ).join('') : '';
        
        // Action buttons
        const websiteBtn = supplier.website ? 
            `<a href="${supplier.website}" target="_blank" class="supplier-btn supplier-btn-primary">
                <i class="fas fa-globe"></i> Website
            </a>` :
            `<a href="https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(supplier.name)}&query_place_id=${supplier.place_id}" target="_blank" class="supplier-btn supplier-btn-primary">
                <i class="fas fa-map-marker-alt"></i> View on Maps
            </a>`;
        
        card.innerHTML = `
            <div class="supplier-card-image">
                <img src="${placeholderUrl}" alt="${supplier.name}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                <div class="supplier-placeholder" style="display: none;">
                    <i class="fas fa-store"></i>
                </div>
            </div>
            <div class="supplier-card-content">
                <div class="supplier-card-header">
                    <h3 class="supplier-name">${supplier.name}</h3>
                    ${ratingHtml}
                </div>
                <div class="supplier-types">
                    ${typesHtml}
                </div>
                <div class="supplier-address">
                    <i class="fas fa-map-marker-alt"></i>
                    <span>${supplier.formatted_address || 'Address not available'}</span>
                </div>
                ${phoneHtml}
                <div class="supplier-actions">
                    ${websiteBtn}
                    <a href="tel:${supplier.formatted_phone_number || ''}" class="supplier-btn supplier-btn-secondary">
                        <i class="fas fa-phone"></i> Call
                    </a>
                </div>
            </div>
        `;
        
        return card;
    }

    // Create supplier card with products section
    function createSupplierWithProductsCard(supplier, searchTerm) {
        const card = document.createElement('div');
        card.className = 'supplier-with-products-card';
        
        // Generate supplier type from Google Places types
        const supplierType = getSupplierType(supplier.types);
        const colors = ['3b82f6', '10b981', 'ef4444', 'f97316', '8b5cf6'];
        const bgColor = colors[Math.floor(Math.random() * colors.length)];
        const illustrationUrl = `https://placehold.co/500x300/${bgColor}/ffffff?text=${encodeURIComponent(supplierType)}&font=lora`;

        // Rating display
        const ratingHtml = supplier.rating ? `
            <div class="supplier-rating">
                <span class="rating-value">${supplier.rating.toFixed(1)}</span>
                <i class="fas fa-star"></i>
            </div>
        ` : '<span class="no-rating">No rating</span>';

        // Phone display
        const phoneHtml = supplier.formatted_phone_number ? `
            <div class="supplier-contact">
                <i class="fas fa-phone"></i>
                <a href="tel:${supplier.formatted_phone_number}">${supplier.formatted_phone_number}</a>
            </div>
        ` : '';

        // Types display
        const typesHtml = supplier.types ? 
            supplier.types.slice(0, 3).map(type => 
                `<span class="supplier-type-tag">${type.replace(/_/g, ' ')}</span>`
            ).join('') : '';

        // Action buttons
        const websiteBtn = supplier.website ? 
            `<a href="${supplier.website}" target="_blank" class="supplier-action-btn supplier-btn-primary">
                <i class="fas fa-globe"></i> Website
            </a>` :
            `<a href="https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(supplier.name)}&query_place_id=${supplier.place_id}" target="_blank" class="supplier-action-btn supplier-btn-primary">
                <i class="fas fa-map-marker-alt"></i> View on Maps
            </a>`;

        // Generate products for this supplier
        const products = generateProductsForSupplier(supplier, searchTerm);
        const productsHtml = products.map(product => createProductTile(product)).join('');

        card.innerHTML = `
            <div class="supplier-main-info">
                <div class="supplier-details-section">
                    <div class="supplier-header">
                        <h3 class="supplier-main-name">${supplier.name}</h3>
                        ${ratingHtml}
                    </div>
                    <div class="supplier-types">
                        ${typesHtml}
                    </div>
                    <div class="supplier-address">
                        <i class="fas fa-map-marker-alt"></i>
                        <span>${supplier.formatted_address || 'Address not available'}</span>
                    </div>
                    ${phoneHtml}
                    <div class="supplier-actions">
                        ${websiteBtn}
                        <button class="supplier-action-btn supplier-btn-secondary" onclick="toggleProducts('${supplier.place_id}')">
                            <i class="fas fa-box"></i> View Products
                        </button>
                    </div>
                </div>
            </div>
            <div class="supplier-products-section" id="products-${supplier.place_id}" style="display: none;">
                <div class="products-header">
                    <h4>Available Products</h4>
                    <span class="products-count">${products.length} products available</span>
                </div>
                <div class="products-grid-inline">
                    ${productsHtml}
                </div>
            </div>
        `;
        
        return card;
    }

    // Generate realistic products for a specific supplier based on search term
    function generateProductsForSupplier(supplier, searchTerm) {
        const products = [];
        const categories = {
            'vegetables': ['Fresh Onions', 'Tomatoes', 'Potatoes', 'Green Chilies', 'Ginger', 'Garlic'],
            'fruits': ['Fresh Apples', 'Bananas', 'Oranges', 'Lemons', 'Seasonal Fruits'],
            'spices': ['Turmeric Powder', 'Red Chili Powder', 'Cumin Seeds', 'Coriander Powder', 'Garam Masala', 'Pani Puri Masala'],
            'dairy': ['Fresh Milk', 'Paneer', 'Butter', 'Pure Ghee', 'Curd'],
            'grains': ['Basmati Rice', 'Wheat Flour', 'Chickpeas', 'Moong Dal', 'Toor Dal'],
            'meat': ['Fresh Chicken', 'Mutton', 'Fish', 'Eggs'],
            'oil': ['Sunflower Oil', 'Mustard Oil', 'Coconut Oil', 'Pure Ghee'],
            'packaging': ['Disposable Plates', 'Food Containers', 'Paper Bags', 'Plastic Cups', 'Aluminum Foil']
        };

        // Determine category from search term
        let category = 'general';
        let productList = [];
        
        for (const [cat, items] of Object.entries(categories)) {
            if (searchTerm.toLowerCase().includes(cat) || 
                items.some(item => item.toLowerCase().includes(searchTerm.toLowerCase()) || 
                searchTerm.toLowerCase().includes(item.toLowerCase()))) {
                category = cat;
                productList = items;
                break;
            }
        }

        // If no specific category found, create products based on search term
        if (productList.length === 0) {
            productList = [
                `Premium ${searchTerm}`,
                `Fresh ${searchTerm}`,
                `Organic ${searchTerm}`,
                `Bulk ${searchTerm}`
            ];
        }

        // Generate 3-6 products per supplier
        const numProducts = Math.floor(Math.random() * 4) + 3;
        const selectedProducts = productList.slice(0, numProducts);

        selectedProducts.forEach((productName, index) => {
            const basePrice = Math.random() * 100 + 20; // Random price between 20-120
            const product = {
                id: `${supplier.place_id}_${index}`,
                name: productName,
                supplierId: supplier.place_id,
                supplierName: supplier.name,
                price: parseFloat(basePrice.toFixed(2)),
                unit: category === 'packaging' ? 'per piece' : 'per kg',
                category: category,
                description: `High quality ${productName.toLowerCase()} from ${supplier.name}`,
                image: `https://placehold.co/200x150/10b981/ffffff?text=${encodeURIComponent(productName)}&font=lora`,
                rating: (Math.random() * 2 + 3).toFixed(1), // Rating between 3-5
                inStock: Math.random() > 0.1, // 90% chance of being in stock
                minOrder: category === 'packaging' ? 100 : 1
            };
            
            products.push(product);
            // Save to database for cart functionality
            database.saveProduct(product);
        });

        return products;
    }

    // Get product icon based on category and name
    function getProductIcon(productName, category) {
        const name = productName.toLowerCase();
        
        // Specific product icons
        if (name.includes('onion')) return 'fas fa-circle';
        if (name.includes('tomato')) return 'fas fa-circle';
        if (name.includes('potato')) return 'fas fa-circle';
        if (name.includes('chili') || name.includes('pepper')) return 'fas fa-pepper-hot';
        if (name.includes('ginger') || name.includes('garlic')) return 'fas fa-seedling';
        if (name.includes('apple')) return 'fas fa-apple-alt';
        if (name.includes('banana')) return 'fas fa-moon';
        if (name.includes('orange') || name.includes('lemon')) return 'fas fa-circle';
        if (name.includes('turmeric') || name.includes('masala') || name.includes('cumin') || name.includes('coriander')) return 'fas fa-mortar-pestle';
        if (name.includes('milk') || name.includes('paneer') || name.includes('butter') || name.includes('ghee') || name.includes('curd')) return 'fas fa-glass-whiskey';
        if (name.includes('rice') || name.includes('wheat') || name.includes('flour') || name.includes('dal')) return 'fas fa-seedling';
        if (name.includes('chicken') || name.includes('mutton') || name.includes('fish') || name.includes('egg')) return 'fas fa-drumstick-bite';
        if (name.includes('oil')) return 'fas fa-tint';
        if (name.includes('plate') || name.includes('container') || name.includes('bag') || name.includes('cup') || name.includes('foil')) return 'fas fa-box';
        
        // Category-based fallback icons
        switch(category) {
            case 'vegetables': return 'fas fa-carrot';
            case 'fruits': return 'fas fa-apple-alt';
            case 'spices': return 'fas fa-pepper-hot';
            case 'dairy': return 'fas fa-cheese';
            case 'grains': return 'fas fa-seedling';
            case 'meat': return 'fas fa-drumstick-bite';
            case 'oil': return 'fas fa-oil-can';
            case 'packaging': return 'fas fa-box';
            default: return 'fas fa-shopping-basket';
        }
    }

    // Create product tile (ultra-compact version)
    function createProductTile(product) {
        const stockClass = product.inStock ? 'in-stock' : 'out-of-stock';
        const stockText = product.inStock ? '✓' : '✗';
        const productIcon = getProductIcon(product.name, product.category);
        
        return `
            <div class="product-tile ${stockClass}">
                <div class="product-tile-header">
                    <div class="product-icon-mini">
                        <i class="${productIcon}"></i>
                    </div>
                    <div class="product-stock-mini ${stockClass}">${stockText}</div>
                </div>
                <div class="product-tile-content">
                    <h5 class="product-tile-name">${product.name}</h5>
                    <div class="product-tile-price">
                        <span class="price">₹${product.price}</span>
                        <span class="unit">${product.unit}</span>
                    </div>
                    <div class="product-tile-rating">
                        <span>${product.rating}</span>
                        <i class="fas fa-star"></i>
                    </div>
                    <div class="product-tile-quantity">
                        <span class="qty-label">Qty:</span>
                        <div class="quantity-controls-mini">
                            <button class="qty-btn" onclick="decreaseQuantity('${product.id}')">-</button>
                            <input type="number" id="qty-${product.id}" value="1" min="1" max="100" class="qty-input">
                            <button class="qty-btn" onclick="increaseQuantity('${product.id}')">+</button>
                        </div>
                    </div>
                    <div class="product-tile-actions">
                        <button class="product-tile-btn view-btn" onclick="openProductModal('${product.id}')">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="product-tile-btn cart-btn" onclick="addToCartWithQuantity('${product.id}')" ${!product.inStock ? 'disabled' : ''}>
                            <i class="fas fa-cart-plus"></i> Add
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Get supplier type from Google Places types
    function getSupplierType(types) {
        if (!types || types.length === 0) return 'Supplier';
        
        const relevantTypes = [
            'grocery_or_supermarket', 'food', 'store', 'supermarket',
            'meal_takeaway', 'restaurant', 'establishment'
        ];
        
        const primaryType = types.find(type => relevantTypes.includes(type)) || types[0];
        return primaryType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
    
    // State management functions
    function showLoading(message) {
        loadingText.textContent = message;
        loadingState.classList.remove('hidden');
        hideOtherStates(['loading']);
    }
    
    function hideLoading() {
        loadingState.classList.add('hidden');
    }
    
    function showEmptyState() {
        emptyState.classList.remove('hidden');
        hideOtherStates(['empty']);
    }
    
    function showNoResults() {
        noResultsState.classList.remove('hidden');
        hideOtherStates(['no-results']);
    }
    
    function showResults() {
        resultsGrid.classList.remove('hidden');
        document.getElementById('products-grid').classList.add('hidden');
        hideOtherStates(['results']);
    }

    function showProducts() {
        document.getElementById('products-grid').classList.remove('hidden');
        resultsGrid.classList.add('hidden');
        hideOtherStates(['products']);
    }
    
    function hideAllStates() {
        loadingState.classList.add('hidden');
        emptyState.classList.add('hidden');
        noResultsState.classList.add('hidden');
        resultsGrid.classList.add('hidden');
    }
    
    function hideOtherStates(except) {
        const states = {
            'loading': loadingState,
            'empty': emptyState,
            'no-results': noResultsState,
            'results': resultsGrid,
            'products': document.getElementById('products-grid')
        };
        
        Object.keys(states).forEach(key => {
            if (!except.includes(key)) {
                states[key].classList.add('hidden');
            }
        });
    }
    
    // Notification system
    function showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
        
        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: ${type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 10px;
            max-width: 400px;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        // Remove after 4 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 4000);
    }
    
    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
    
    // Initialize when page loads
    initializePage();
    
    // Fallback initialization if Google Maps callback doesn't work
    setTimeout(() => {
        if (!placesService && window.google && window.google.maps && window.google.maps.places) {
            console.log('Initializing Places Service via fallback');
            const mapDiv = document.getElementById('map-hidden');
            placesService = new google.maps.places.PlacesService(mapDiv);
        }
    }, 2000);
    
    // Reverse geocoding to get location name
    function reverseGeocode(lat, lng) {
        if (!window.google || !window.google.maps) {
            updateStateSelector('Current Location');
            showNotification('Current location set. Ready to search!');
            return;
        }
        
        const geocoder = new google.maps.Geocoder();
        const latlng = { lat: lat, lng: lng };
        
        geocoder.geocode({ location: latlng }, (results, status) => {
            if (status === 'OK' && results[0]) {
                // Find the most appropriate address component
                let locationName = 'Current Location';
                
                for (let result of results) {
                    for (let component of result.address_components) {
                        if (component.types.includes('administrative_area_level_1')) {
                            locationName = `Current Location (${component.long_name})`;
                            break;
                        }
                    }
                    if (locationName !== 'Current Location') break;
                }
                
                // Update the state selector to show current location
                updateStateSelector(locationName);
                showNotification(`Location set to ${locationName}. Ready to search!`);
            } else {
                updateStateSelector('Current Location');
                showNotification('Current location set. Ready to search!');
            }
        });
    }
    
    // Update state selector with current location
    function updateStateSelector(locationName) {
        // Clear selection first
        stateSelector.value = '';
        
        // Check if current location option already exists
        let currentLocationOption = stateSelector.querySelector('option[value="current-location"]');
        
        if (!currentLocationOption) {
            currentLocationOption = document.createElement('option');
            currentLocationOption.value = 'current-location';
            stateSelector.insertBefore(currentLocationOption, stateSelector.firstChild.nextSibling);
        }
        
        currentLocationOption.textContent = locationName;
        currentLocationOption.selected = true;
    }

    // Check for global placesService
    function getPlacesService() {
        if (window.placesService) {
            return window.placesService;
        }
        if (placesService) {
            return placesService;
        }
        if (window.google && window.google.maps && window.google.maps.places) {
            const mapDiv = document.getElementById('map-hidden');
            placesService = new google.maps.places.PlacesService(mapDiv);
            return placesService;
        }
        return null;
    }

    // Fallback search when Google Maps API is not available
    function useFallbackSearch(searchTerm) {
        console.log('Using fallback search for:', searchTerm);
        
        // Create demo suppliers based on search term
        const demoSuppliers = createDemoSuppliers(searchTerm);
        
        hideLoading();
        if (demoSuppliers.length > 0) {
            displaySuppliersWithProducts(demoSuppliers, searchTerm);
        } else {
            showNoResults();
        }
    }

    // Create demo suppliers for testing
    function createDemoSuppliers(searchTerm) {
        const suppliers = [
            {
                place_id: 'demo_1',
                name: `${searchTerm} Wholesale Market`,
                formatted_address: 'Demo Address, Mumbai, Maharashtra, India',
                formatted_phone_number: '+91 98765 43210',
                rating: 4.2,
                types: ['grocery_or_supermarket', 'food', 'store'],
                website: null
            },
            {
                place_id: 'demo_2',
                name: `Fresh ${searchTerm} Suppliers`,
                formatted_address: 'Demo Address, Delhi, India',
                formatted_phone_number: '+91 98765 43211',
                rating: 4.5,
                types: ['food', 'store'],
                website: null
            },
            {
                place_id: 'demo_3',
                name: `Premium ${searchTerm} Mart`,
                formatted_address: 'Demo Address, Bangalore, Karnataka, India',
                formatted_phone_number: '+91 98765 43212',
                rating: 4.0,
                types: ['grocery_or_supermarket', 'establishment'],
                website: null
            }
        ];
        
        return suppliers;
    }
});
    
// Global functions for product interactions
window.openProductModal = function(productId) {
    console.log('Opening modal for product:', productId);
    const products = database.getProductsFromLocalStorage();
    const product = products.find(p => p.id === productId);
    console.log('Found product:', product);
    console.log('Cart available:', window.cart);
    
    if (product) {
        if (window.cart) {
            window.cart.openProductModal(product);
        } else {
            // Wait for cart to be initialized
            // Fallback: Show product modal directly
            showProductModal(product);
        }
    } else {
        console.error('Product not found:', productId);
    }
};

window.quickAddToCart = function(productId) {
    console.log('Quick add to cart:', productId);
    const products = database.getProductsFromLocalStorage();
    const product = products.find(p => p.id === productId);
    console.log('Found product for cart:', product);
    
    if (product) {
        const cartProduct = {
            id: product.id,
            name: product.name,
            price: product.price,
            unit: product.unit,
            quantity: 1,
            supplierId: product.supplierId,
            supplierName: product.supplierName,
            supplierAddress: product.supplierAddress,
            supplierPhone: product.supplierPhone,
            supplierRating: product.supplierRating,
            supplierLat: product.supplierLat,
            supplierLng: product.supplierLng,
            image: product.image
        };
        
        if (window.cart) {
            window.cart.addItem(cartProduct);
        } else {
            // Fallback: Add directly to cart via API
            addToCartDirectly(cartProduct);
        }
    } else {
        console.error('Product not found for cart:', productId);
    }
};

window.toggleProducts = function(supplierId) {
    const productsSection = document.getElementById(`products-${supplierId}`);
    const button = event.target.closest('button');
    
    if (productsSection) {
        const isVisible = productsSection.style.display !== 'none';
        
        if (isVisible) {
            productsSection.style.display = 'none';
            if (button) button.innerHTML = '<i class="fas fa-box"></i> View Products';
        } else {
            productsSection.style.display = 'block';
            if (button) button.innerHTML = '<i class="fas fa-box"></i> Hide Products';
        }
    }
};

window.increaseQuantity = function(productId) {
    const input = document.getElementById(`qty-${productId}`);
    if (input) {
        const currentValue = parseInt(input.value) || 1;
        input.value = Math.min(currentValue + 1, 100);
    }
};

window.decreaseQuantity = function(productId) {
    const input = document.getElementById(`qty-${productId}`);
    if (input) {
        const currentValue = parseInt(input.value) || 1;
        input.value = Math.max(currentValue - 1, 1);
    }
};

window.addToCartWithQuantity = function(productId) {
    console.log('Add to cart with quantity:', productId);
    const products = database.getProductsFromLocalStorage();
    const product = products.find(p => p.id === productId);
    const quantityInput = document.getElementById(`qty-${productId}`);
    const quantity = quantityInput ? parseInt(quantityInput.value) || 1 : 1;
    
    if (product) {
        const cartProduct = {
            id: product.id,
            name: product.name,
            price: product.price,
            unit: product.unit,
            quantity: quantity,
            supplierId: product.supplierId,
            supplierName: product.supplierName,
            supplierAddress: product.supplierAddress,
            supplierPhone: product.supplierPhone,
            supplierRating: product.supplierRating,
            supplierLat: product.supplierLat,
            supplierLng: product.supplierLng,
            image: product.image
        };
        
        if (window.cart) {
            window.cart.addItem(cartProduct);
        } else {
            // Fallback: Add directly to cart via API
            addToCartDirectly(cartProduct);
        }
    } else {
        console.error('Product not found for cart:', productId);
    }
};
// Add to cart using Django API
function addToCartDirectly(product) {
    console.log('Adding to cart via API:', product);
    
    // Prepare data for Django API
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
    
    // Send AJAX request to Django backend
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
            const navbarCartCount = document.querySelector('.cart-count');
            if (navbarCartCount) {
                navbarCartCount.textContent = data.cart_count;
                navbarCartCount.style.display = data.cart_count > 0 ? 'inline' : 'none';
            }
            
            // Show success notification
            showSupplierNotification(data.message, 'success');
        } else {
            showSupplierNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error adding to cart:', error);
        showSupplierNotification('Error adding item to cart', 'error');
    });
}

// Simple product modal fallback
function showProductModal(product) {
    alert(`Product: ${product.name}\nPrice: ₹${product.price}/${product.unit}\nSupplier: ${product.supplierName}\n\nClick "Add to Cart" button to add this item to your cart.`);
}

// Notification function for suppliers page
function showSupplierNotification(message, type = 'info') {
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
        notification.remove();
    }, 4000);
}