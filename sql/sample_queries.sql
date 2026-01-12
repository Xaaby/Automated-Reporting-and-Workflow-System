-- Sample SQL queries for testing the Automated Reporting and Workflow System
-- These queries demonstrate various use cases and can be used as templates

-- 1. Simple aggregation query
-- Daily active user count
SELECT 
    CURRENT_DATE as report_date,
    COUNT(DISTINCT user_id) as active_users
FROM users
WHERE last_active >= CURRENT_DATE;

-- 2. Time-based aggregation
-- Weekly revenue summary
SELECT 
    DATE_TRUNC('week', order_date) as week,
    SUM(amount) as total_revenue,
    COUNT(*) as order_count,
    AVG(amount) as average_order_value
FROM orders
GROUP BY DATE_TRUNC('week', order_date)
ORDER BY week DESC;

-- 3. Product sales breakdown
-- Monthly product sales
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    SUM(oi.quantity) as total_quantity,
    SUM(oi.amount) as total_amount,
    COUNT(DISTINCT oi.order_id) as order_count
FROM order_items oi
JOIN products p ON oi.product_id = p.id
WHERE DATE_TRUNC('month', oi.created_at) = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_amount DESC;

-- 4. Customer segmentation
-- Top customers by revenue
SELECT 
    c.customer_id,
    c.customer_name,
    c.email,
    COUNT(DISTINCT o.order_id) as total_orders,
    SUM(o.amount) as total_spent,
    AVG(o.amount) as average_order_value
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY c.customer_id, c.customer_name, c.email
ORDER BY total_spent DESC
LIMIT 100;

-- 5. Regional performance
-- Sales by region
SELECT 
    r.region_name,
    r.country,
    COUNT(DISTINCT o.order_id) as order_count,
    SUM(o.amount) as total_revenue,
    COUNT(DISTINCT o.customer_id) as unique_customers
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN regions r ON c.region_id = r.region_id
WHERE o.order_date >= DATE_TRUNC('month', CURRENT_DATE)
GROUP BY r.region_name, r.country
ORDER BY total_revenue DESC;

-- 6. Inventory status
-- Low stock alert
SELECT 
    p.product_id,
    p.product_name,
    p.current_stock,
    p.min_stock_level,
    (p.current_stock - p.min_stock_level) as stock_difference,
    CASE 
        WHEN p.current_stock <= p.min_stock_level THEN 'CRITICAL'
        WHEN p.current_stock <= p.min_stock_level * 1.5 THEN 'LOW'
        ELSE 'OK'
    END as stock_status
FROM products p
WHERE p.current_stock <= p.min_stock_level * 1.5
ORDER BY stock_difference ASC;

-- 7. Time series data
-- Daily metrics trend
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_records,
    COUNT(DISTINCT user_id) as unique_users,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_count
FROM transactions
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- 8. Cross-table analysis
-- Order fulfillment performance
SELECT 
    o.order_id,
    o.order_date,
    o.status,
    o.amount,
    s.shipping_date,
    s.delivery_date,
    (s.delivery_date - o.order_date) as days_to_deliver,
    CASE 
        WHEN s.delivery_date IS NULL THEN 'Pending'
        WHEN (s.delivery_date - o.order_date) <= 3 THEN 'Fast'
        WHEN (s.delivery_date - o.order_date) <= 7 THEN 'Normal'
        ELSE 'Slow'
    END as delivery_performance
FROM orders o
LEFT JOIN shipments s ON o.order_id = s.order_id
WHERE o.order_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY o.order_date DESC;
