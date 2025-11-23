-- ============================================================================
-- Grocery Store Management System - Complete Database Schema
-- MySQL 8.0+
-- ============================================================================

-- Create database
CREATE DATABASE IF NOT EXISTS grocery_store_db;
USE grocery_store_db;

-- ============================================================================
-- TABLE: users
-- Purpose: Store user accounts with authentication and role management
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('admin', 'cashier') NOT NULL DEFAULT 'cashier',
    email VARCHAR(100),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_role (role),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE: categories
-- Purpose: Product categories for organization
-- ============================================================================
CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category_name (category_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE: products
-- Purpose: Store product information and pricing
-- ============================================================================
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    barcode VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    category_id INT,
    unit_price DECIMAL(10, 2) NOT NULL,
    cost_price DECIMAL(10, 2),
    stock_quantity INT NOT NULL DEFAULT 0,
    reorder_level INT DEFAULT 10,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL,
    INDEX idx_barcode (barcode),
    INDEX idx_product_name (product_name),
    INDEX idx_category (category_id),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE: sales
-- Purpose: Store sales transaction headers
-- ============================================================================
CREATE TABLE IF NOT EXISTS sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_number VARCHAR(50) UNIQUE NOT NULL,
    customer_name VARCHAR(100),
    customer_phone VARCHAR(20),
    subtotal DECIMAL(10, 2) NOT NULL,
    tax_amount DECIMAL(10, 2) DEFAULT 0,
    discount_amount DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2) NOT NULL,
    payment_method ENUM('cash', 'card', 'mobile_money') DEFAULT 'cash',
    cashier_id INT,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cashier_id) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_sale_number (sale_number),
    INDEX idx_sale_date (sale_date),
    INDEX idx_cashier (cashier_id),
    INDEX idx_customer (customer_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE: sale_items
-- Purpose: Store individual items in each sale (line items)
-- ============================================================================
CREATE TABLE IF NOT EXISTS sale_items (
    sale_item_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sales(sale_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT,
    INDEX idx_sale (sale_id),
    INDEX idx_product (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE: inventory_transactions
-- Purpose: Track all stock movements for audit trail
-- ============================================================================
CREATE TABLE IF NOT EXISTS inventory_transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    transaction_type ENUM('restock', 'sale', 'adjustment', 'return') NOT NULL,
    quantity_change INT NOT NULL,
    previous_stock INT NOT NULL,
    new_stock INT NOT NULL,
    reference_id INT COMMENT 'Related sale_id or other reference',
    notes TEXT,
    user_id INT,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_product (product_id),
    INDEX idx_transaction_date (transaction_date),
    INDEX idx_transaction_type (transaction_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE: activity_logs
-- Purpose: Log all user activities for security and auditing
-- ============================================================================
CREATE TABLE IF NOT EXISTS activity_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) COMMENT 'Type: product, sale, user, etc.',
    entity_id INT COMMENT 'ID of affected entity',
    details TEXT,
    ip_address VARCHAR(45),
    log_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_user (user_id),
    INDEX idx_action (action),
    INDEX idx_log_date (log_date),
    INDEX idx_entity (entity_type, entity_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- INSERT DEFAULT DATA
-- ============================================================================

-- Insert default admin user
-- Password: admin123 (hashed with bcrypt)
-- IMPORTANT: Change this password immediately after first login!
INSERT INTO users (username, password_hash, full_name, role, email) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Hn8jHu', 'System Administrator', 'admin', 'admin@grocerystore.com')
ON DUPLICATE KEY UPDATE username = username;

-- Insert default product categories
INSERT INTO categories (category_name, description) VALUES
('Beverages', 'Soft drinks, juices, water, energy drinks'),
('Dairy', 'Milk, cheese, yogurt, butter'),
('Bakery', 'Bread, cakes, pastries, cookies'),
('Snacks', 'Chips, cookies, candy, nuts'),
('Household', 'Cleaning supplies, toiletries, paper products'),
('Fresh Produce', 'Fruits and vegetables'),
('Meat & Seafood', 'Fresh and frozen meats, fish'),
('Frozen Foods', 'Ice cream, frozen meals, frozen vegetables'),
('Canned Goods', 'Canned vegetables, fruits, soups'),
('Personal Care', 'Shampoo, soap, cosmetics, hygiene products')
ON DUPLICATE KEY UPDATE category_name = category_name;

-- ============================================================================
-- CREATE VIEWS FOR REPORTING
-- ============================================================================

-- View: Low stock products that need reordering
CREATE OR REPLACE VIEW low_stock_products AS
SELECT 
    p.product_id,
    p.barcode,
    p.product_name,
    c.category_name,
    p.stock_quantity,
    p.reorder_level,
    p.unit_price,
    (p.reorder_level - p.stock_quantity) as shortage_quantity
FROM products p
LEFT JOIN categories c ON p.category_id = c.category_id
WHERE p.stock_quantity <= p.reorder_level 
  AND p.is_active = TRUE
ORDER BY p.stock_quantity ASC;

-- View: Daily sales summary
CREATE OR REPLACE VIEW daily_sales_summary AS
SELECT 
    DATE(sale_date) as sale_day,
    COUNT(*) as total_orders,
    SUM(total_amount) as total_revenue,
    SUM(subtotal) as total_subtotal,
    SUM(tax_amount) as total_tax,
    SUM(discount_amount) as total_discounts,
    AVG(total_amount) as average_order_value,
    MIN(total_amount) as min_order_value,
    MAX(total_amount) as max_order_value
FROM sales
GROUP BY DATE(sale_date)
ORDER BY sale_day DESC;

-- View: Product sales performance
CREATE OR REPLACE VIEW product_sales_performance AS
SELECT 
    p.product_id,
    p.product_name,
    p.barcode,
    c.category_name,
    COUNT(DISTINCT si.sale_id) as times_sold,
    SUM(si.quantity) as total_quantity_sold,
    SUM(si.subtotal) as total_revenue,
    AVG(si.unit_price) as average_selling_price,
    p.unit_price as current_price,
    p.stock_quantity as current_stock
FROM products p
LEFT JOIN categories c ON p.category_id = c.category_id
LEFT JOIN sale_items si ON p.product_id = si.product_id
WHERE p.is_active = TRUE
GROUP BY p.product_id, p.product_name, p.barcode, c.category_name, 
         p.unit_price, p.stock_quantity
ORDER BY total_quantity_sold DESC;

-- View: User activity summary
CREATE OR REPLACE VIEW user_activity_summary AS
SELECT 
    u.user_id,
    u.username,
    u.full_name,
    u.role,
    COUNT(CASE WHEN al.action LIKE 'login%' THEN 1 END) as login_count,
    COUNT(CASE WHEN al.action = 'sale_completed' THEN 1 END) as sales_made,
    MAX(al.log_date) as last_activity,
    u.is_active
FROM users u
LEFT JOIN activity_logs al ON u.user_id = al.user_id
GROUP BY u.user_id, u.username, u.full_name, u.role, u.is_active
ORDER BY last_activity DESC;

-- ============================================================================
-- CREATE STORED PROCEDURES
-- ============================================================================

DELIMITER //

-- Procedure: Process a complete sale transaction
CREATE PROCEDURE IF NOT EXISTS process_sale(
    IN p_sale_number VARCHAR(50),
    IN p_customer_name VARCHAR(100),
    IN p_subtotal DECIMAL(10,2),
    IN p_tax DECIMAL(10,2),
    IN p_discount DECIMAL(10,2),
    IN p_total DECIMAL(10,2),
    IN p_payment_method VARCHAR(20),
    IN p_cashier_id INT,
    OUT p_sale_id INT
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_sale_id = -1;
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Sale processing failed - transaction rolled back';
    END;
    
    START TRANSACTION;
    
    -- Insert sale header
    INSERT INTO sales (
        sale_number, customer_name, subtotal, tax_amount, 
        discount_amount, total_amount, payment_method, cashier_id
    )
    VALUES (
        p_sale_number, p_customer_name, p_subtotal, p_tax, 
        p_discount, p_total, p_payment_method, p_cashier_id
    );
    
    SET p_sale_id = LAST_INSERT_ID();
    
    COMMIT;
END //

-- Procedure: Get inventory value
CREATE PROCEDURE IF NOT EXISTS get_inventory_value(
    OUT p_total_value DECIMAL(15,2),
    OUT p_total_cost DECIMAL(15,2)
)
BEGIN
    SELECT 
        COALESCE(SUM(stock_quantity * unit_price), 0),
        COALESCE(SUM(stock_quantity * cost_price), 0)
    INTO p_total_value, p_total_cost
    FROM products
    WHERE is_active = TRUE;
END //

-- Procedure: Get sales statistics for date range
CREATE PROCEDURE IF NOT EXISTS get_sales_stats(
    IN p_start_date DATE,
    IN p_end_date DATE
)
BEGIN
    SELECT 
        COUNT(*) as total_sales,
        SUM(total_amount) as total_revenue,
        AVG(total_amount) as average_sale,
        MIN(total_amount) as min_sale,
        MAX(total_amount) as max_sale,
        SUM(discount_amount) as total_discounts,
        SUM(tax_amount) as total_tax
    FROM sales
    WHERE DATE(sale_date) BETWEEN p_start_date AND p_end_date;
END //

DELIMITER ;

-- ============================================================================
-- CREATE TRIGGERS
-- ============================================================================

DELIMITER //

-- Trigger: Update product timestamp on stock change
CREATE TRIGGER IF NOT EXISTS update_product_timestamp
BEFORE UPDATE ON products
FOR EACH ROW
BEGIN
    IF NEW.stock_quantity != OLD.stock_quantity THEN
        SET NEW.updated_at = CURRENT_TIMESTAMP;
    END IF;
END //

-- Trigger: Prevent negative stock
CREATE TRIGGER IF NOT EXISTS prevent_negative_stock
BEFORE UPDATE ON products
FOR EACH ROW
BEGIN
    IF NEW.stock_quantity < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Stock quantity cannot be negative';
    END IF;
END //

DELIMITER ;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Additional composite indexes for common queries
CREATE INDEX idx_sale_date_cashier ON sales(sale_date, cashier_id);
CREATE INDEX idx_product_category_active ON products(category_id, is_active);
CREATE INDEX idx_inventory_product_date ON inventory_transactions(product_id, transaction_date);

-- ============================================================================
-- GRANT PRIVILEGES (Optional - for production use)
-- ============================================================================

-- Uncomment and modify for production deployment
-- CREATE USER IF NOT EXISTS 'grocery_app'@'localhost' IDENTIFIED BY 'your_secure_password';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON grocery_store_db.* TO 'grocery_app'@'localhost';
-- FLUSH PRIVILEGES;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify all tables were created
SELECT 
    TABLE_NAME, 
    TABLE_ROWS,
    CREATE_TIME
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'grocery_store_db'
ORDER BY TABLE_NAME;

-- Verify default admin user exists
SELECT 
    user_id, 
    username, 
    full_name, 
    role,
    is_active,
    created_at
FROM users
WHERE username = 'admin';

-- Verify categories were inserted
SELECT 
    category_id,
    category_name,
    description
FROM categories
ORDER BY category_name;

-- ============================================================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================================================

-- Uncomment to insert sample products for testing
/*
INSERT INTO products (barcode, product_name, category_id, unit_price, cost_price, stock_quantity, reorder_level) VALUES
('8888888001', 'Coca Cola 1.5L', 1, 45.00, 35.00, 100, 20),
('8888888002', 'Pepsi 1.5L', 1, 45.00, 35.00, 80, 20),
('8888888003', 'Fresh Milk 1L', 2, 85.00, 70.00, 50, 15),
('8888888004', 'White Bread Loaf', 3, 55.00, 45.00, 60, 20),
('8888888005', 'Whole Wheat Bread', 3, 65.00, 50.00, 40, 15),
('8888888006', 'Potato Chips 100g', 4, 35.00, 25.00, 120, 30),
('8888888007', 'Chocolate Bar', 4, 25.00, 18.00, 150, 40),
('8888888008', 'Dish Soap 500ml', 5, 45.00, 35.00, 70, 20),
('8888888009', 'Toilet Paper 4-pack', 5, 120.00, 95.00, 50, 15),
('8888888010', 'Fresh Apples 1kg', 6, 120.00, 100.00, 30, 10);
*/

-- ============================================================================
-- DATABASE SETUP COMPLETE
-- ============================================================================

SELECT '✓ Database setup completed successfully!' as Status;
SELECT 'Default login: username=admin, password=admin123' as Note;
SELECT 'IMPORTANT: Change the default admin password immediately!' as Warning;