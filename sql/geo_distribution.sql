SELECT
    c.customer_state,
    COUNT(DISTINCT c.customer_unique_id) AS number_of_customers,
    COUNT(DISTINCT o.order_id) AS number_of_orders,
    ROUND(SUM(oi.price), 2) AS total_revenue,
    ROUND(AVG(oi.price), 2) AS average_order_value,
    ROUND(COUNT(DISTINCT o.order_id)::numeric / COUNT(DISTINCT c.customer_unique_id), 2) AS orders_per_customer,
    ROUND(COUNT(DISTINCT c.customer_unique_id)::numeric / SUM(COUNT(DISTINCT c.customer_unique_id)) OVER () * 100, 2) AS customer_percentage
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_state
ORDER BY number_of_customers DESC;
