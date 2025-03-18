SELECT
    r.review_score,
    COUNT(*) AS count
FROM order_reviews r
JOIN orders o ON r.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_purchase_timestamp BETWEEN :start_date AND :end_date
AND c.customer_state LIKE :state
GROUP BY r.review_score
ORDER BY r.review_score;