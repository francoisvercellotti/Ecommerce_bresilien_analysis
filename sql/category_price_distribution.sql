SELECT
    pc.product_category_name_english as category_name,
    od.price
FROM vw_order_details od
JOIN products p ON od.product_id = p.product_id
JOIN product_categories pc ON p.product_category_name = pc.product_category_name
WHERE p.product_category_name IS NOT NULL
ORDER BY category_name;