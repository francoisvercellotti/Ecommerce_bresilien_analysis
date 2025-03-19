WITH order_categories AS (
    SELECT
        od.order_id,
        pc.product_category_name_english AS category_name_english
    FROM vw_order_details od
    JOIN products p ON od.product_id = p.product_id
    JOIN product_categories pc ON p.product_category_name = pc.product_category_name
    WHERE p.product_category_name IS NOT NULL
    GROUP BY od.order_id, pc.product_category_name_english
)
SELECT
    a.category_name_english as category_name_1,
    b.category_name_english as category_name_2,
    COUNT(*) as frequency
FROM order_categories a
JOIN order_categories b ON a.order_id = b.order_id AND a.category_name_english < b.category_name_english
GROUP BY a.category_name_english, b.category_name_english
HAVING COUNT(*) > 5
ORDER BY frequency DESC;