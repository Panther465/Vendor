// Database functionality using Web SQL (SQLite in browser)
class Database {
    constructor() {
        this.db = null;
        this.init();
    }

    init() {
        try {
            // Initialize Web SQL database (SQLite in browser)
            this.db = openDatabase('StreetEatsDB', '1.0', 'StreetEats Connect Database', 5 * 1024 * 1024);
            this.createTables();
        } catch (error) {
            console.error('Database initialization failed:', error);
            // Fallback to localStorage if Web SQL is not supported
            this.useLocalStorageFallback = true;
        }
    }

    createTables() {
        if (!this.db) return;

        this.db.transaction((tx) => {
            // Orders table
            tx.executeSql(`
                CREATE TABLE IF NOT EXISTS orders (
                    id TEXT PRIMARY KEY,
                    vendor_name TEXT,
                    vendor_phone TEXT,
                    vendor_address TEXT,
                    subtotal REAL,
                    delivery_charge REAL,
                    total REAL,
                    status TEXT,
                    created_at TEXT
                )
            `);

            // Order items table
            tx.executeSql(`
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT,
                    product_id TEXT,
                    product_name TEXT,
                    supplier_id TEXT,
                    supplier_name TEXT,
                    price REAL,
                    quantity INTEGER,
                    unit TEXT,
                    FOREIGN KEY (order_id) REFERENCES orders (id)
                )
            `);

            // Products table (for caching product data)
            tx.executeSql(`
                CREATE TABLE IF NOT EXISTS products (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    supplier_id TEXT,
                    supplier_name TEXT,
                    price REAL,
                    unit TEXT,
                    category TEXT,
                    description TEXT,
                    image_url TEXT,
                    rating REAL,
                    created_at TEXT
                )
            `);

            // Suppliers table
            tx.executeSql(`
                CREATE TABLE IF NOT EXISTS suppliers (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    address TEXT,
                    phone TEXT,
                    rating REAL,
                    category TEXT,
                    latitude REAL,
                    longitude REAL,
                    created_at TEXT
                )
            `);

            console.log('Database tables created successfully');
        });
    }

    // Save order to database
    async saveOrder(order) {
        return new Promise((resolve, reject) => {
            if (this.useLocalStorageFallback) {
                this.saveOrderToLocalStorage(order);
                resolve(order);
                return;
            }

            if (!this.db) {
                reject(new Error('Database not initialized'));
                return;
            }

            this.db.transaction((tx) => {
                // Insert order
                tx.executeSql(
                    `INSERT INTO orders (id, vendor_name, vendor_phone, vendor_address, subtotal, delivery_charge, total, status, created_at) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
                    [
                        order.id,
                        order.vendorInfo.name,
                        order.vendorInfo.phone,
                        order.vendorInfo.address,
                        order.subtotal,
                        order.deliveryCharge,
                        order.total,
                        order.status,
                        order.createdAt
                    ]
                );

                // Insert order items
                order.items.forEach(item => {
                    tx.executeSql(
                        `INSERT INTO order_items (order_id, product_id, product_name, supplier_id, supplier_name, price, quantity, unit) 
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
                        [
                            order.id,
                            item.id,
                            item.name,
                            item.supplierId,
                            item.supplierName,
                            item.price,
                            item.quantity,
                            item.unit
                        ]
                    );
                });
            }, 
            (error) => {
                console.error('Transaction error:', error);
                reject(error);
            },
            () => {
                console.log('Order saved successfully:', order.id);
                resolve(order);
            });
        });
    }

    // Get all orders
    async getOrders() {
        return new Promise((resolve, reject) => {
            if (this.useLocalStorageFallback) {
                const orders = this.getOrdersFromLocalStorage();
                resolve(orders);
                return;
            }

            if (!this.db) {
                reject(new Error('Database not initialized'));
                return;
            }

            this.db.transaction((tx) => {
                tx.executeSql(
                    `SELECT o.*, 
                     GROUP_CONCAT(oi.product_name || ' x ' || oi.quantity) as items_summary
                     FROM orders o 
                     LEFT JOIN order_items oi ON o.id = oi.order_id 
                     GROUP BY o.id 
                     ORDER BY o.created_at DESC`,
                    [],
                    (tx, results) => {
                        const orders = [];
                        for (let i = 0; i < results.rows.length; i++) {
                            orders.push(results.rows.item(i));
                        }
                        resolve(orders);
                    },
                    (tx, error) => {
                        reject(error);
                    }
                );
            });
        });
    }

    // Get order details with items
    async getOrderDetails(orderId) {
        return new Promise((resolve, reject) => {
            if (this.useLocalStorageFallback) {
                const order = this.getOrderFromLocalStorage(orderId);
                resolve(order);
                return;
            }

            if (!this.db) {
                reject(new Error('Database not initialized'));
                return;
            }

            this.db.transaction((tx) => {
                // Get order
                tx.executeSql(
                    'SELECT * FROM orders WHERE id = ?',
                    [orderId],
                    (tx, results) => {
                        if (results.rows.length === 0) {
                            reject(new Error('Order not found'));
                            return;
                        }

                        const order = results.rows.item(0);

                        // Get order items
                        tx.executeSql(
                            'SELECT * FROM order_items WHERE order_id = ?',
                            [orderId],
                            (tx, itemResults) => {
                                const items = [];
                                for (let i = 0; i < itemResults.rows.length; i++) {
                                    items.push(itemResults.rows.item(i));
                                }
                                order.items = items;
                                resolve(order);
                            }
                        );
                    }
                );
            });
        });
    }

    // Save product to database
    async saveProduct(product) {
        return new Promise((resolve, reject) => {
            if (this.useLocalStorageFallback) {
                this.saveProductToLocalStorage(product);
                resolve(product);
                return;
            }

            if (!this.db) {
                reject(new Error('Database not initialized'));
                return;
            }

            this.db.transaction((tx) => {
                tx.executeSql(
                    `INSERT OR REPLACE INTO products (id, name, supplier_id, supplier_name, price, unit, category, description, image_url, rating, created_at) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
                    [
                        product.id,
                        product.name,
                        product.supplierId,
                        product.supplierName,
                        product.price,
                        product.unit,
                        product.category,
                        product.description,
                        product.image,
                        product.rating,
                        new Date().toISOString()
                    ],
                    () => resolve(product),
                    (tx, error) => reject(error)
                );
            });
        });
    }

    // Get products by category
    async getProductsByCategory(category) {
        return new Promise((resolve, reject) => {
            if (this.useLocalStorageFallback) {
                const products = this.getProductsFromLocalStorage(category);
                resolve(products);
                return;
            }

            if (!this.db) {
                reject(new Error('Database not initialized'));
                return;
            }

            this.db.transaction((tx) => {
                tx.executeSql(
                    'SELECT * FROM products WHERE category = ? ORDER BY rating DESC, price ASC',
                    [category],
                    (tx, results) => {
                        const products = [];
                        for (let i = 0; i < results.rows.length; i++) {
                            products.push(results.rows.item(i));
                        }
                        resolve(products);
                    },
                    (tx, error) => reject(error)
                );
            });
        });
    }

    // LocalStorage fallback methods
    saveOrderToLocalStorage(order) {
        const orders = JSON.parse(localStorage.getItem('streetEatsOrders') || '[]');
        orders.push(order);
        localStorage.setItem('streetEatsOrders', JSON.stringify(orders));
    }

    getOrdersFromLocalStorage() {
        return JSON.parse(localStorage.getItem('streetEatsOrders') || '[]');
    }

    getOrderFromLocalStorage(orderId) {
        const orders = this.getOrdersFromLocalStorage();
        return orders.find(order => order.id === orderId);
    }

    saveProductToLocalStorage(product) {
        const products = JSON.parse(localStorage.getItem('streetEatsProducts') || '[]');
        const existingIndex = products.findIndex(p => p.id === product.id);
        
        if (existingIndex >= 0) {
            products[existingIndex] = product;
        } else {
            products.push(product);
        }
        
        localStorage.setItem('streetEatsProducts', JSON.stringify(products));
    }

    getProductsFromLocalStorage(category) {
        const products = JSON.parse(localStorage.getItem('streetEatsProducts') || '[]');
        return category ? products.filter(p => p.category === category) : products;
    }

    // Generate sample products for testing
    generateSampleProducts(searchTerm, suppliers) {
        const sampleProducts = [];
        const categories = {
            'vegetables': ['Onions', 'Tomatoes', 'Potatoes', 'Carrots', 'Cabbage', 'Spinach'],
            'fruits': ['Apples', 'Bananas', 'Oranges', 'Mangoes', 'Grapes', 'Lemons'],
            'spices': ['Turmeric Powder', 'Red Chili Powder', 'Cumin Seeds', 'Coriander Seeds', 'Garam Masala', 'Black Pepper'],
            'dairy': ['Fresh Milk', 'Paneer', 'Butter', 'Ghee', 'Yogurt', 'Cheese'],
            'grains': ['Basmati Rice', 'Wheat Flour', 'Chickpeas', 'Lentils', 'Quinoa', 'Oats'],
            'meat': ['Chicken', 'Mutton', 'Fish', 'Prawns', 'Eggs'],
            'oil': ['Sunflower Oil', 'Mustard Oil', 'Coconut Oil', 'Olive Oil', 'Ghee'],
            'packaging': ['Disposable Plates', 'Food Containers', 'Paper Bags', 'Aluminum Foil', 'Plastic Cups']
        };

        // Determine category from search term
        let category = 'general';
        let products = [];
        
        for (const [cat, items] of Object.entries(categories)) {
            if (searchTerm.toLowerCase().includes(cat) || items.some(item => 
                item.toLowerCase().includes(searchTerm.toLowerCase()) || 
                searchTerm.toLowerCase().includes(item.toLowerCase())
            )) {
                category = cat;
                products = items;
                break;
            }
        }

        // If no specific category found, use a general list
        if (products.length === 0) {
            products = ['Premium Quality ' + searchTerm, 'Fresh ' + searchTerm, 'Organic ' + searchTerm];
        }

        suppliers.forEach((supplier, supplierIndex) => {
            products.forEach((productName, productIndex) => {
                const basePrice = Math.random() * 100 + 20; // Random price between 20-120
                const product = {
                    id: `${supplier.place_id}_${productIndex}`,
                    name: productName,
                    supplierId: supplier.place_id,
                    supplierName: supplier.name,
                    price: parseFloat(basePrice.toFixed(2)),
                    unit: category === 'packaging' ? 'per piece' : 'per kg',
                    category: category,
                    description: `High quality ${productName.toLowerCase()} from ${supplier.name}. Fresh and verified supplier.`,
                    image: `https://placehold.co/300x200/10b981/ffffff?text=${encodeURIComponent(productName)}&font=lora`,
                    rating: (Math.random() * 2 + 3).toFixed(1), // Rating between 3-5
                    inStock: Math.random() > 0.1, // 90% chance of being in stock
                    minOrder: category === 'packaging' ? 100 : 1
                };
                
                sampleProducts.push(product);
                this.saveProduct(product); // Save to database
            });
        });

        return sampleProducts;
    }
}

// Initialize database
const database = new Database();

// Make database available globally
window.database = database;