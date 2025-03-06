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

def create_table_schemas(engine):
    """Crée les schémas des tables avec les contraintes de clé étrangère."""
    schema_sql = """
    -- Table clients
    CREATE TABLE customers (
        customer_id VARCHAR(50) PRIMARY KEY,
        customer_unique_id VARCHAR(50) NOT NULL,
        customer_zip_code_prefix VARCHAR(10),
        customer_city VARCHAR(100),
        customer_state VARCHAR(2)
    );
    -- Table catégories de produits
    CREATE TABLE product_categories (
        product_category_name VARCHAR(100) PRIMARY KEY,
        product_category_name_english VARCHAR(100)
    );
    -- Table vendeurs
    CREATE TABLE sellers (
        seller_id VARCHAR(50) PRIMARY KEY,
        seller_zip_code_prefix VARCHAR(10),
        seller_city VARCHAR(100),
        seller_state VARCHAR(2)
    );
    -- Table localisation géographique des codes postaux
    CREATE TABLE geolocation (
        geolocation_zip_code_prefix VARCHAR(10),
        geolocation_lat DECIMAL(10,6),
        geolocation_lng DECIMAL(10,6),
        geolocation_city VARCHAR(100),
        geolocation_state VARCHAR(2),
        PRIMARY KEY (geolocation_zip_code_prefix, geolocation_lat, geolocation_lng)
    );
    -- Table commandes
    CREATE TABLE orders (
        order_id VARCHAR(50) PRIMARY KEY,
        customer_id VARCHAR(50),
        order_status VARCHAR(20),
        order_purchase_timestamp TIMESTAMP,
        order_approved_at TIMESTAMP,
        order_delivered_carrier_date TIMESTAMP,
        order_delivered_customer_date TIMESTAMP,
        order_estimated_delivery_date TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );
    -- Table produits
    CREATE TABLE products (
        product_id VARCHAR(50) PRIMARY KEY,
        product_category_name VARCHAR(100),
        product_name_length INT,
        product_description_length INT,
        product_photos_qty INT,
        product_weight_g INT,
        product_length_cm INT,
        product_height_cm INT,
        product_width_cm INT,
        FOREIGN KEY (product_category_name) REFERENCES product_categories(product_category_name)
    );
    -- Table items des commandes
    CREATE TABLE order_items (
        order_id VARCHAR(50),
        order_item_id INT,
        product_id VARCHAR(50),
        seller_id VARCHAR(50),
        shipping_limit_date TIMESTAMP,
        price DECIMAL(10,2),
        freight_value DECIMAL(10,2),
        PRIMARY KEY (order_id, order_item_id),
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id),
        FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
    );
    -- Table paiements des commandes
    CREATE TABLE order_payments (
        order_id VARCHAR(50),
        payment_sequential INT,
        payment_type VARCHAR(20),
        payment_installments INT,
        payment_value DECIMAL(10,2),
        PRIMARY KEY (order_id, payment_sequential),
        FOREIGN KEY (order_id) REFERENCES orders(order_id)
    );
    -- Table des avis clients
    CREATE TABLE order_reviews (
        review_id VARCHAR(50),
        order_id VARCHAR(50),
        review_score INT,
        review_comment_title VARCHAR(100),
        review_comment_message TEXT,
        review_creation_date TIMESTAMP,
        review_answer_timestamp TIMESTAMP,
        PRIMARY KEY (review_id),
        FOREIGN KEY (order_id) REFERENCES orders(order_id)
    );
    """

    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        # Suppression des tables dans l'ordre inverse
        tables = ['order_reviews', 'order_payments', 'order_items', 'products',
                 'orders', 'geolocation', 'sellers', 'product_categories', 'customers']
        for table in tables:
            conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))

        # Création des tables avec les contraintes
        for statement in schema_sql.split(';'):
            if statement.strip():
                conn.execute(text(statement))

def import_data(data_dir):
    """Importe les données CSV dans PostgreSQL."""
    engine = create_db_engine()

    # Créer d'abord le schéma avec toutes les contraintes
    create_table_schemas(engine)

    # Définir l'ordre d'importation des tables en respectant les dépendances
    import_order = [
        # Tables sans dépendances d'abord
        ('olist_customers_dataset.csv', 'customers'),
        ('product_category_name_translation.csv', 'product_categories'),
        ('olist_sellers_dataset.csv', 'sellers'),
        ('olist_geolocation_dataset.csv', 'geolocation'),
        # Tables avec dépendances simples
        ('olist_orders_dataset.csv', 'orders'),
        ('olist_products_dataset.csv', 'products'),
        # Tables avec dépendances multiples
        ('olist_order_items_dataset.csv', 'order_items'),
        ('olist_order_payments_dataset.csv', 'order_payments'),
        ('olist_order_reviews_dataset.csv', 'order_reviews')
    ]

    # Importation des données
    for file, table_name in import_order:
        file_path = os.path.join(data_dir, file)
        if os.path.exists(file_path):
            print(f"Importation de {file} vers la table {table_name}...")

            # Utilisation d'une approche par chunks pour tous les fichiers
            chunk_size = 100000
            chunks = pd.read_csv(file_path, chunksize=chunk_size)

            for i, chunk in enumerate(chunks):
                # Pour l'import des données, nous utilisons if_exists='append' car les tables sont déjà créées
                chunk.to_sql(table_name, engine, if_exists='append', index=False, method='multi')
                print(f"  Importé chunk {i+1} de {file}")

            print(f"Importation de {file} terminée.")
        else:
            print(f"Fichier {file_path} introuvable.")

if __name__ == "__main__":
    data_dir = os.getenv("DATA_DIR", "./data")
    import_data(data_dir)
    print("Importation des données terminée.")