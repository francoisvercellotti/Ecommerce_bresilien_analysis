import os
import sys
import argparse
import pandas as pd
from datetime import datetime, date
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Ajouter le chemin du projet pour importer correctement
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database_setup import create_db_engine

def check_table_columns(engine, table_name):
    """
    Vérifie les colonnes d'une table
    """
    inspector = inspect(engine)
    try:
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        return columns
    except Exception as e:
        print(f"Erreur lors de la vérification de la table {table_name}: {e}")
        return []

def generate_weekly_business_report(start_date=None, end_date=None):
    """
    Génère un rapport hebdomadaire détaillé à partir de la base de données
    et l'exporte en markdown et CSV
    """
    try:
        # Créer le moteur de base de données
        engine = create_db_engine()

        # Vérifier les colonnes des tables
        print("Vérification des colonnes des tables...")
        orders_columns = check_table_columns(engine, 'orders')
        order_items_columns = check_table_columns(engine, 'order_items')
        customers_columns = check_table_columns(engine, 'customers')
        print("Colonnes des tables vérifiées.")

        # Vérifier si la table order_reviews existe
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        has_reviews_table = 'order_reviews' in tables

        # Vérifier et convertir les dates si nécessaire
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        # Requête adaptative basée sur l'existence de la table order_reviews
        customer_satisfaction_query = """
        SELECT
            NULL AS avg_review_score,
            0 AS total_reviews,
            0 AS positive_reviews,
            0 AS negative_reviews
        """ if not has_reviews_table else """
        SELECT
            AVG(review_score) AS avg_review_score,
            COUNT(*) AS total_reviews,
            SUM(CASE WHEN review_score >= 4 THEN 1 ELSE 0 END) AS positive_reviews,
            SUM(CASE WHEN review_score <= 2 THEN 1 ELSE 0 END) AS negative_reviews
        FROM order_reviews r
        JOIN orders o ON r.order_id = o.order_id
        WHERE o.order_purchase_timestamp BETWEEN :start_date AND :end_date
        """

        # Exécuter la requête de génération de rapport
        query = text(f"""
        WITH sales_metrics AS (
            SELECT
                COUNT(DISTINCT o.order_id) AS total_orders,
                SUM(oi.price + oi.freight_value) AS total_revenue,
                COUNT(DISTINCT c.customer_unique_id) AS unique_customers,
                AVG(oi.price + oi.freight_value) AS avg_order_value
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.order_purchase_timestamp BETWEEN :start_date AND :end_date
        ),
        delivery_performance AS (
            SELECT
                COUNT(*) AS total_delivered,
                SUM(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date THEN 1 ELSE 0 END) AS late_deliveries,
                AVG(EXTRACT(EPOCH FROM (order_delivered_customer_date - order_purchase_timestamp))/86400) AS avg_delivery_days
            FROM orders
            WHERE order_status = 'delivered'
            AND order_delivered_customer_date BETWEEN :start_date AND :end_date
        ),
        customer_satisfaction AS (
            {customer_satisfaction_query}
        ),
        new_customers AS (
            SELECT
                COUNT(DISTINCT c.customer_unique_id) AS new_customer_count
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.order_purchase_timestamp BETWEEN :start_date AND :end_date
            AND NOT EXISTS (
                SELECT 1 FROM orders o2
                JOIN customers c2 ON o2.customer_id = c2.customer_id
                WHERE c2.customer_unique_id = c.customer_unique_id
                AND o2.order_purchase_timestamp < :start_date
            )
        )
        SELECT
            :start_date AS report_start_date,
            :end_date AS report_end_date,
            sm.total_orders,
            sm.total_revenue,
            sm.unique_customers,
            sm.avg_order_value,
            nc.new_customer_count,
            dp.total_delivered,
            dp.late_deliveries,
            dp.avg_delivery_days,
            cs.avg_review_score,
            cs.total_reviews,
            cs.positive_reviews,
            cs.negative_reviews
        FROM sales_metrics sm
        CROSS JOIN delivery_performance dp
        CROSS JOIN customer_satisfaction cs
        CROSS JOIN new_customers nc
        """)

        # Exécuter la requête avec les paramètres de date
        with engine.connect() as connection:
            df = pd.read_sql(query, connection, params={
                'start_date': start_date,
                'end_date': end_date
            })

        # Créer le dossier docs/weekly_report si inexistant
        os.makedirs('docs/weekly_report', exist_ok=True)

        # Générer un nom de fichier avec la date
        report_filename = f'weekly_report_{start_date}_to_{end_date}'

        # Exporter en CSV
        df.to_csv(f'docs/weekly_report/{report_filename}.csv', index=False)

        # Créer un rapport markdown détaillé
        with open(f'docs/weekly_report/{report_filename}.md', 'w', encoding='utf-8') as f:
            # En-tête du rapport
            f.write(f"# Rapport Hebdomadaire de Performance\n")
            f.write(f"**Période :** {start_date} au {end_date}\n\n")

            # Métriques de ventes
            f.write("## Métriques de Ventes\n")
            f.write(f"- **Nombre total de commandes :** {df['total_orders'].values[0]}\n")
            f.write(f"- **Revenu total :** {df['total_revenue'].values[0]:.2f} €\n")
            f.write(f"- **Clients uniques :** {df['unique_customers'].values[0]}\n")
            f.write(f"- **Valeur moyenne de commande :** {df['avg_order_value'].values[0]:.2f} €\n")
            f.write(f"- **Nouveaux clients :** {df['new_customer_count'].values[0]}\n\n")

            # Performance de livraison
            f.write("## Performance de Livraison\n")
            f.write(f"- **Total livré :** {df['total_delivered'].values[0]}\n")
            f.write(f"- **Livraisons en retard :** {df['late_deliveries'].values[0]}\n")
            f.write(f"- **Délai moyen de livraison :** {df['avg_delivery_days'].values[0]:.2f} jours\n\n")

            # Satisfaction client
            f.write("## Satisfaction Client\n")
            f.write(f"- **Note moyenne :** {df['avg_review_score'].values[0] or 'N/A'}\n")
            f.write(f"- **Total avis :** {df['total_reviews'].values[0]}\n")
            f.write(f"- **Avis positifs :** {df['positive_reviews'].values[0]}\n")
            f.write(f"- **Avis négatifs :** {df['negative_reviews'].values[0]}\n")

        print(f"Rapport généré avec succès : {report_filename}")
        return df

    except Exception as e:
        print(f"Erreur lors de la génération du rapport : {e}")
        return None

def main():
    # Configuration de l'analyseur d'arguments
    parser = argparse.ArgumentParser(description='Générer un rapport hebdomadaire')
    parser.add_argument('--start', type=str, required=True,
                        help='Date de début (format YYYY-MM-DD)')
    parser.add_argument('--end', type=str, required=True,
                        help='Date de fin (format YYYY-MM-DD)')

    # Analyser les arguments
    args = parser.parse_args()

    # Générer le rapport avec les dates spécifiées
    generate_weekly_business_report(args.start, args.end)

if __name__ == "__main__":
    main()