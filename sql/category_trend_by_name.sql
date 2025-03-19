SELECT
    DATE_TRUNC('month', od.order_purchase_timestamp) as order_month,
    SUM(od.price) as total_revenue,
    COUNT(DISTINCT od.order_id) as order_count
FROM vw_order_details od
JOIN products p ON od.product_id = p.product_id
JOIN product_categories pc ON p.product_category_name = pc.product_category_name
WHERE pc.product_category_name_english = $1
GROUP BY DATE_TRUNC('month', od.order_purchase_timestamp)
ORDER BY order_month;
