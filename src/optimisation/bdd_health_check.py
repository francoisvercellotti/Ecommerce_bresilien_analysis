import os
import sys

# Ajouter le chemin du projet à PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

import argparse
import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

from src.database_setup import create_db_engine

def configure_logging():
    """
    Configure la journalisation pour le script de maintenance
    """
    # Créer le dossier logs s'il n'existe pas
    os.makedirs('logs', exist_ok=True)

    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler(f'logs/database_maintenance_{datetime.now().strftime("%Y-%m-%d")}.log'),
            logging.StreamHandler()
        ]
    )

def perform_database_maintenance(maintenance_date=None):
    """
    Effectue la maintenance de la base de données PostgreSQL
    """
    try:
        # Configuration du logging
        configure_logging()
        logging.info("Début de la maintenance de la base de données")

        # Créer le moteur de base de données
        engine = create_db_engine()

        # Vérifier si la date de maintenance est fournie, sinon utiliser la date actuelle
        if maintenance_date is None:
            maintenance_date = datetime.now().date()

        # Liste des tables à analyser et réindexer
        tables_to_maintain = [
            'orders',
            'customers',
            'order_items',
            'products',
            'sellers',
            'order_reviews'
        ]

        # Liste des index à réindexer
        indexes_to_reindex = [
            'idx_orders_order_id',
            'idx_orders_customer_id',
            'idx_order_items_product_id',
            'idx_customers_id',
            'idx_order_reviews_order_id',
            'idx_customers_unique_id'
        ]

        # Créer un contexte de connexion
        with engine.connect() as connection:
            # Exécuter ANALYZE pour chaque table
            for table in tables_to_maintain:
                analyze_query = text(f"ANALYZE {table};")
                connection.execute(analyze_query)
                logging.info(f"ANALYZE effectué pour la table {table}")

            # Réindexer les index
            for index in indexes_to_reindex:
                reindex_query = text(f"REINDEX INDEX {index};")
                connection.execute(reindex_query)
                logging.info(f"REINDEX effectué pour l'index {index}")

            # Ajouter une journalisation de fin de maintenance
            log_maintenance_query = text("SELECT NOW() as maintenance_time;")
            result = connection.execute(log_maintenance_query)
            maintenance_time = result.scalar()
            logging.info(f"Maintenance terminée à {maintenance_time}")

        # Créer le dossier docs/maintenance_report si inexistant
        os.makedirs('docs/maintenance_report', exist_ok=True)

        # Générer un nom de fichier avec la date
        report_filename = f'maintenance_report_{maintenance_date}'

        # Créer un rapport markdown de maintenance
        with open(f'docs/maintenance_report/{report_filename}.md', 'w', encoding='utf-8') as f:
            f.write(f"# Rapport de Maintenance de Base de Données\n")
            f.write(f"**Date :** {maintenance_date}\n\n")
            f.write("## Tables Analysées\n")
            f.write("\n".join([f"- {table}" for table in tables_to_maintain]))
            f.write("\n\n## Index Réindexés\n")
            f.write("\n".join([f"- {index}" for index in indexes_to_reindex]))

        logging.info("Maintenance de la base de données terminée avec succès")
        return True

    except Exception as e:
        logging.error(f"Erreur lors de la maintenance de la base de données : {e}")
        return None

def main():
    # Configuration de l'analyseur d'arguments
    parser = argparse.ArgumentParser(description='Effectuer la maintenance de la base de données')
    parser.add_argument('--date', type=str,
                        help='Date de maintenance (format YYYY-MM-DD, optionnel)')

    # Analyser les arguments
    args = parser.parse_args()

    # Convertir la date si fournie
    maintenance_date = datetime.strptime(args.date, '%Y-%m-%d').date() if args.date else None

    # Effectuer la maintenance
    perform_database_maintenance(maintenance_date)

if __name__ == "__main__":
    main()