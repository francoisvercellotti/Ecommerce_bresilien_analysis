# Documentation Technique de la Base de Données

## FUNCTION

### get_avg_order_value

**Description :** Fonction qui calcule la valeur moyenne des commandes sur une période donnée. Retourne également le nombre total de commandes, le revenu total et le nombre moyen d'articles par commande.

**Exemple d'utilisation :**
```sql
SELECT * FROM get_avg_order_value('2018-01-01'::timestamp, '2018-03-31'::timestamp);
```

**Date de création :** 2025-03-14 15:47:10.590196

---

### predict_sales_for_date

**Description :** Fonction qui prédit les ventes pour une date future basée sur les tendances historiques de ventes.

**Exemple d'utilisation :**
```sql
SELECT * FROM predict_sales_for_date('2023-12-25');
```

**Date de création :** 2025-03-14 15:36:57.823444

---

### product_category_report

**Description :** Génère un rapport d'analyse détaillé pour une catégorie de produit spécifique. La fonction prend en paramètre le nom de la catégorie en anglais et retourne un rapport au format texte avec les sections suivantes

**Exemple d'utilisation :**
```sql
SELECT * FROM product_category_report('furniture');
```

**Date de création :** 2025-03-14 16:01:36.449583

---

### project_sales

**Description :** Fonction qui projette les ventes futures en utilisant les indices saisonniers.

**Exemple d'utilisation :**
```sql
SELECT * FROM project_sales(12, 2023, 500000);
```

**Date de création :** 2025-03-14 15:37:19.877026

---

## INDEX

### idx_reviews_score

**Description :** Index sur la colonne review_score de la table order_reviews pour optimiser les requêtes de filtrage et d'agrégation sur les scores d'évaluation.

**Exemple d'utilisation :**
```sql
EXPLAIN ANALYZE SELECT * FROM order_reviews WHERE review_score >= 4;
```

**Date de création :** 2025-03-14 15:23:44.102679

---

## KPI

### average_order_value

**Description :** Valeur moyenne d'une commande. Calculé en divisant le revenu total par le nombre de commandes.

**Exemple d'utilisation :**
```sql
SELECT AVG(order_total) FROM (SELECT o.order_id, SUM(oi.price + oi.freight_value) as order_total FROM orders o JOIN order_items oi ON o.order_id = oi.order_id GROUP BY o.order_id) subq;
```

**Date de création :** 2025-03-14 16:16:25.211143

---

### customer_acquisition_cost

**Description :** Coût moyen d'acquisition d'un nouveau client. Cette métrique n'est pas calculable directement avec les données disponibles, mais pourrait être estimée en utilisant des données externes de marketing.

**Date de création :** 2025-03-14 16:16:25.211143

---

### customer_lifetime_value

**Description :** Valeur totale générée par un client unique sur toute sa période d'activité. Calculé en additionnant tous les achats réalisés par le même customer_unique_id.

**Exemple d'utilisation :**
```sql
SELECT c.customer_unique_id, SUM(oi.price + oi.freight_value) as lifetime_value FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN order_items oi ON o.order_id = oi.order_id GROUP BY c.customer_unique_id;
```

**Date de création :** 2025-03-14 16:16:25.211143

---

### customer_retention_rate

**Description :** Pourcentage de clients qui effectuent des achats répétés. Calculé en divisant le nombre de clients avec plus d'une commande par le nombre total de clients uniques.

**Exemple d'utilisation :**
```sql
WITH repeat_customers AS (SELECT c.customer_unique_id, COUNT(DISTINCT o.order_id) as order_count FROM customers c JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.customer_unique_id HAVING COUNT(DISTINCT o.order_id) > 1) SELECT COUNT(*) * 100.0 / (SELECT COUNT(DISTINCT customer_unique_id) FROM customers) FROM repeat_customers;
```

**Date de création :** 2025-03-14 16:16:25.211143

---

### customer_satisfaction_score

**Description :** Score moyen de satisfaction client basé sur les évaluations. Calculé en faisant la moyenne des scores de revue.

**Exemple d'utilisation :**
```sql
SELECT AVG(review_score) FROM order_reviews;
```

**Date de création :** 2025-03-14 16:16:25.211143

---

### on_time_delivery_rate

**Description :** Pourcentage de commandes livrées avant ou à la date estimée. Calculé en divisant le nombre de commandes livrées à temps par le nombre total de commandes livrées.

**Exemple d'utilisation :**
```sql
SELECT (1 - SUM(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date THEN 1 ELSE 0 END)::FLOAT / COUNT(*)) * 100 FROM orders WHERE order_status = 'delivered';
```

**Date de création :** 2025-03-14 16:16:25.211143

---

### repurchase_rate

**Description :** Taux de rachat sur une période donnée. Calculé en divisant le nombre de commandes répétées par le nombre total de commandes.

**Exemple d'utilisation :**
```sql
WITH customer_orders AS (SELECT c.customer_unique_id, COUNT(o.order_id) as order_count FROM customers c JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.customer_unique_id) SELECT SUM(CASE WHEN order_count > 1 THEN order_count - 1 ELSE 0 END)::FLOAT / SUM(order_count) * 100 FROM customer_orders;
```

**Date de création :** 2025-03-14 16:16:25.211143

---

## VIEW

### vw_customer_churn_risk

**Description :** Vue qui calcule un score de risque d'attrition pour chaque client unique en fonction de la récence, fréquence et satisfaction.

**Exemple d'utilisation :**
```sql
SELECT * FROM vw_customer_churn_risk WHERE churn_risk_level = 'Élevé' ORDER BY churn_risk_score;
```

**Date de création :** 2025-03-14 15:37:07.137748

---

### vw_order_details

**Description :** Vue consolidée qui regroupe les informations de commandes, clients, produits, vendeurs et évaluations en une seule table. Facilite les requêtes analytiques complexes en évitant de multiples jointures.

**Exemple d'utilisation :**
```sql
SELECT * FROM vw_order_details WHERE delivered_on_time = false AND customer_state = 'SP' ORDER BY delivery_time_days DESC LIMIT 10;
```

**Date de création :** 2025-03-14 15:36:48.620077

---

### vw_prediction_sales_pattern

**Description :** Vue qui analyse les tendances de ventes par jour de semaine et mois. Utilisée pour les prédictions de ventes.

**Exemple d'utilisation :**
```sql
SELECT * FROM vw_prediction_sales_pattern WHERE month = 12 ORDER BY avg_revenue_by_day DESC;
```

**Date de création :** 2025-03-14 15:36:51.785624

---

### vw_satisfaction_predictors

**Description :** Vue qui identifie les facteurs corrélés avec la satisfaction client par catégorie de produit.

**Exemple d'utilisation :**
```sql
SELECT * FROM vw_satisfaction_predictors ORDER BY corr_delivery_time_review ASC LIMIT 10;
```

**Date de création :** 2025-03-14 15:37:10.269867

---

### vw_satisfaction_predictors_optimized

**Description :** Version optimisée de vw_satisfaction_predictors qui utilise la vue consolidée vw_order_details au lieu de jointures multiples pour une meilleure performance.

**Exemple d'utilisation :**
```sql
SELECT * FROM vw_satisfaction_predictors_optimized ORDER BY corr_delivery_time_review ASC LIMIT 10;
```

**Date de création :** 2025-03-14 15:37:24.276871

---

### vw_seasonal_trends

**Description :** Vue qui calcule les indices saisonniers pour les ventes mensuelles.

**Exemple d'utilisation :**
```sql
SELECT * FROM vw_seasonal_trends ORDER BY month_number;
```

**Date de création :** 2025-03-14 15:37:15.125343

---

