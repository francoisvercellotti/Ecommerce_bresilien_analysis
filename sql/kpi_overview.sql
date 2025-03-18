WITH order_metrics AS (
    SELECT
        COUNT(DISTINCT o.order_id) AS total_orders,
        COUNT(DISTINCT c.customer_unique_id) AS total_customers,
        SUM(CASE WHEN o.order_status = 'delivered' THEN 1 ELSE 0 END) AS delivered_orders,
        SUM(CASE WHEN o.order_status = 'canceled' THEN 1 ELSE 0 END) AS canceled_orders
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.order_purchase_timestamp BETWEEN :start_date AND :end_date
    AND c.customer_state LIKE :state
),
revenue_metrics AS (
    SELECT
        SUM(oi.price) AS total_revenue,
        SUM(oi.price) / COUNT(DISTINCT o.order_id) AS average_order_value,
        COUNT(oi.order_item_id) AS total_items_sold,
        COUNT(oi.order_item_id) / COUNT(DISTINCT o.order_id) AS average_items_per_order
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.order_purchase_timestamp BETWEEN :start_date AND :end_date
    AND c.customer_state LIKE :state
),
delivery_metrics AS (
    SELECT
        ROUND(AVG(EXTRACT(EPOCH FROM (o.order_delivered_customer_date - o.order_purchase_timestamp)) / 86400), 1) AS avg_delivery_days
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
    AND o.order_purchase_timestamp BETWEEN :start_date AND :end_date
    AND c.customer_state LIKE :state
)
SELECT
    om.total_orders AS order_count,
    rm.total_revenue,
    ROUND(rm.average_order_value, 2) AS avg_order,
    dm.avg_delivery_days
FROM order_metrics om, revenue_metrics rm, delivery_metrics dm;
