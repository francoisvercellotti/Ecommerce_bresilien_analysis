SELECT
    pc.product_category_name_english as category_name,
    DATE_TRUNC('month', o.order_purchase_timestamp) as order_month,
    SUM(oi.price) as total_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
JOIN product_categories pc ON p.product_category_name = pc.product_category_name
WHERE o.order_status NOT IN ('canceled', 'unavailable')
AND p.product_category_name IS NOT NULL
AND o.order_purchase_timestamp BETWEEN :start_date AND :end_date
GROUP BY pc.product_category_name_english, DATE_TRUNC('month', o.order_purchase_timestamp)
ORDER BY order_month, total_revenue DESC;