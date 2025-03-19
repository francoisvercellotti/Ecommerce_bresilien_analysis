SELECT
    MIN(order_purchase_timestamp) as min_date,
    MAX(order_purchase_timestamp) as max_date
FROM vw_order_details;