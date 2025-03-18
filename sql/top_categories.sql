WITH total_revenue_cte AS (
    SELECT SUM(oi.price) AS total_revenue
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.order_purchase_timestamp BETWEEN :start_date AND :end_date
    AND c.customer_state LIKE :state
)
SELECT
    pc.product_category_name_english,
    COUNT(DISTINCT oi.order_id) AS number_of_orders,
    COUNT(oi.order_item_id) AS quantity_sold,
    ROUND(AVG(oi.price), 2) AS average_price,
    ROUND(SUM(oi.price), 2) AS total_revenue,
    ROUND(SUM(oi.price) / t.total_revenue, 2) AS revenue_share
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN product_categories pc ON p.product_category_name = pc.product_category_name
JOIN orders o ON oi.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
CROSS JOIN total_revenue_cte t
WHERE o.order_purchase_timestamp BETWEEN :start_date AND :end_date
AND c.customer_state LIKE :state
GROUP BY pc.product_category_name_english, t.total_revenue
ORDER BY total_revenue DESC
LIMIT 20;