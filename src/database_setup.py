import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

def create_db_engine():
    """Crée et retourne une connexion à la base de données PostgreSQL."""
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")

    connection_string = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    return create_engine(connection_string)

def clear_table(engine, table_name):
    """Vide une table en utilisant TRUNCATE ... CASCADE."""
    with engine.begin() as connection:
        connection.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;"))
    print(f"Table {table_name} vidée.")

from sqlalchemy import create_engine
import pandas as pd
import os

def import_data(data_dir):
    """Importe les données CSV dans PostgreSQL en évitant les doublons."""
    engine = create_db_engine()

    files = {
        'olist_customers_dataset.csv': 'customers',
        'product_category_name_translation.csv': 'product_categories',
        'olist_sellers_dataset.csv': 'sellers',
        'olist_orders_dataset.csv': 'orders',
        'olist_products_dataset.csv': 'products',
        'olist_order_items_dataset.csv': 'order_items',
        'olist_order_payments_dataset.csv': 'order_payments',
        'olist_order_reviews_dataset.csv': 'order_reviews'
    }

    for file, table_name in files.items():
        file_path = os.path.join(data_dir, file)
        if os.path.exists(file_path):
            print(f"Importation de {file} vers la table {table_name}...")

            # Vider la table avant insertion
            clear_table(engine, table_name)

            # Charger le fichier CSV
            df = pd.read_csv(file_path)

            # Vérification des doublons dans 'review_id' avant l'insertion
            if table_name == 'order_reviews':
                # Récupérer les review_id déjà existants dans la base de données
                existing_ids = pd.read_sql('SELECT review_id FROM order_reviews', engine)
                df = df[~df['review_id'].isin(existing_ids['review_id'])]

            # Importer le DataFrame dans la table PostgreSQL
            df.to_sql(table_name, engine, if_exists='append', index=False)
            print(f"Importation de {file} terminée.")
        else:
            print(f"Fichier {file_path} introuvable.")


if __name__ == "__main__":
    try:
        data_dir = os.getenv("DATA_DIR", "./data")
        import_data(data_dir)
        print("Importation des données terminée.")
    except Exception as e:
        print("Une erreur est survenue :", e)
