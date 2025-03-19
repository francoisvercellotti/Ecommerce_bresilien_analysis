SELECT DISTINCT pc.product_category_name_english as category_name
FROM products p
JOIN product_categories pc ON p.product_category_name = pc.product_category_name
WHERE p.product_category_name IS NOT NULL
ORDER BY pc.product_category_name_english;