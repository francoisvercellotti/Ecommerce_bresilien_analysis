SELECT
    pc.product_category_name_english as category_name,
    COUNT(DISTINCT od.order_id) as order_count,
    ROUND(SUM(od.price), 2) as total_revenue,
    ROUND(AVG(od.price), 2) as avg_price,
    ROUND(AVG(od.review_score), 2) as avg_review_score,
    ROUND(AVG(od.freight_value), 2) as avg_freight_value
FROM vw_order_details od
JOIN products p ON od.product_id = p.product_id
JOIN product_categories pc ON p.product_category_name = pc.product_category_name
WHERE p.product_category_name IS NOT NULL
AND od.order_purchase_timestamp BETWEEN :start_date AND :end_date
GROUP BY pc.product_category_name_english
ORDER BY total_revenue DESC;