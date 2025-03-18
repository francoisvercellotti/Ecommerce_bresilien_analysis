WITH monthly_data AS (
    SELECT
        DATE_TRUNC('month', o.order_purchase_timestamp) AS month,
        COUNT(o.order_id) AS number_of_orders,
        COUNT(DISTINCT c.customer_unique_id) AS unique_customers,
        SUM(p.payment_value) AS total_revenue
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_payments p ON o.order_id = p.order_id
    WHERE o.order_purchase_timestamp BETWEEN :start_date AND :end_date
    AND c.customer_state LIKE :state
    GROUP BY DATE_TRUNC('month', o.order_purchase_timestamp)
    ORDER BY month
)
SELECT
    month,
    number_of_orders,
    unique_customers,
    total_revenue,
    number_of_orders - LAG(number_of_orders) OVER (ORDER BY month) AS order_growth,
    ROUND(
        (number_of_orders::numeric - LAG(number_of_orders) OVER (ORDER BY month)) /
        NULLIF(LAG(number_of_orders) OVER (ORDER BY month), 0) * 100,
        2
    ) AS growth_percentage
FROM monthly_data;