import os
import sys
import logging
from datetime import datetime
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration des chemins
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from src.database_setup import create_db_engine

def configure_logging():
    """Configuration du système de logging"""
    logs_dir = os.path.join(PROJECT_ROOT, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(logs_dir, f'data_cleaning_{datetime.now().strftime("%Y-%m-%d")}.log')),
            logging.StreamHandler()
        ]
    )

def load_data(engine, table_name):
    """Charger les données depuis la base de données"""
    try:
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, engine)
        logging.info(f"Données chargées pour {table_name}: {len(df)} lignes")
        return df
    except Exception as e:
        logging.error(f"Erreur lors du chargement de {table_name}: {e}")
        return None

def clean_text_columns(df, text_columns):
    """
    Nettoyer les colonnes textuelles
    - Supprimer les espaces en début et fin
    - Mettre en majuscule la première lettre de chaque mot
    - Gérer les valeurs NaN si spécifiées
    """
    cleaned_df = df.copy()

    for col in text_columns:
        if col in cleaned_df.columns:
            # Gérer les NaN en les remplaçant par une chaîne vide
            cleaned_df[col] = cleaned_df[col].fillna('')

            # Supprimer les espaces et mettre en forme
            cleaned_df[col] = (
                cleaned_df[col]
                .astype(str)  # Convertir en chaîne de caractères
                .str.strip()  # Supprimer les espaces avant/après
                .str.title()  # Mettre la première lettre en majuscule
            )

    return cleaned_df

def handle_numeric_nan(df, numeric_columns, method='median'):
    """
    Gérer les valeurs NaN dans les colonnes numériques
    - Remplacement par la médiane ou la moyenne
    """
    cleaned_df = df.copy()

    for col in numeric_columns:
        if col in cleaned_df.columns and pd.api.types.is_numeric_dtype(cleaned_df[col]):
            # Choisir la méthode de remplacement
            if method == 'median':
                replacement_value = cleaned_df[col].median()
            elif method == 'mean':
                replacement_value = cleaned_df[col].mean()
            else:
                logging.warning(f"Méthode non reconnue pour {col}. Utilisation de la médiane.")
                replacement_value = cleaned_df[col].median()

            # Remplacer les NaN
            cleaned_df[col] = cleaned_df[col].fillna(replacement_value)

            logging.info(f"NaN dans {col} remplacés par {replacement_value}")

    return cleaned_df

def save_cleaned_data(engine, df, table_name):
    """Sauvegarder les données nettoyées"""
    try:
        with engine.connect() as conn:
            # Commencer une transaction
            trans = conn.begin()

            try:
                # Supprimer les données existantes
                conn.execute(text(f"DELETE FROM {table_name}"))

                # Sauvegarder les données nettoyées
                df.to_sql(
                    table_name,
                    conn,
                    if_exists='append',
                    index=False,
                    chunksize=1000  # Traiter les données par lots de 1000 lignes
                )

                # Valider la transaction
                trans.commit()

                logging.info(f"Données nettoyées sauvegardées pour {table_name}")
                logging.info(f"Nombre de lignes sauvegardées : {len(df)}")

            except Exception as e:
                # Annuler la transaction en cas d'erreur
                trans.rollback()
                logging.error(f"Erreur lors de la sauvegarde des données pour {table_name}: {e}")
                raise

    except Exception as e:
        logging.error(f"Erreur de connexion ou de sauvegarde pour {table_name}: {e}")

def generate_cleaning_report(df_before, df_after, table_name):
    """Générer un rapport de nettoyage"""
    report_dir = os.path.join(PROJECT_ROOT, 'docs', 'cleaning_report')
    os.makedirs(report_dir, exist_ok=True)
    report_filename = f'cleaning_report_{table_name}_{datetime.now().strftime("%Y-%m-%d")}.md'
    report_path = os.path.join(report_dir, report_filename)

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# Rapport de Nettoyage - {table_name}\n")
        f.write(f"**Date :** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Colonnes nettoyées
        f.write("## Colonnes Nettoyées\n")
        for col in df_before.columns:
            before_null = df_before[col].isnull().sum()
            after_null = df_after[col].isnull().sum()

            f.write(f"### Colonne : {col}\n")
            f.write(f"- Nombre de NaN avant nettoyage : {before_null}\n")
            f.write(f"- Nombre de NaN après nettoyage : {after_null}\n\n")

        logging.info(f"Rapport de nettoyage généré : {report_path}")

def perform_data_cleaning():
    """Fonction principale de nettoyage des données"""
    configure_logging()
    logging.info("Début du nettoyage des données")

    # Créer le moteur de base de données
    engine = create_db_engine()

    # Configuration de nettoyage
    cleaning_config = {
        'order_items': {
            'text_columns': [],
            'numeric_columns': ['price', 'freight_value']
        },
        'customers': {
            'text_columns': ['customer_city', 'customer_state'],
            'numeric_columns': []
        },
        'sellers': {
            'text_columns': ['seller_city', 'seller_state'],
            'numeric_columns': []
        }
    }

    # Parcourir les tables à nettoyer
    for table_name, config in cleaning_config.items():
        logging.info(f"Nettoyage de la table {table_name}")

        # Charger les données originales
        df_original = load_data(engine, table_name)

        if df_original is not None:
            # Nettoyer les colonnes numériques (gestion des NaN)
            df_cleaned = handle_numeric_nan(
                df_original,
                config['numeric_columns'],
                method='median'
            )

            # Nettoyer les colonnes textuelles
            if config['text_columns']:
                df_cleaned = clean_text_columns(df_cleaned, config['text_columns'])

            # Générer un rapport de nettoyage
            generate_cleaning_report(df_original, df_cleaned, table_name)

            # Sauvegarder les données nettoyées
            save_cleaned_data(engine, df_cleaned, table_name)

    logging.info("Nettoyage des données terminé avec succès")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Effectuer le nettoyage des données')
    parser.parse_args()
    perform_data_cleaning()

if __name__ == "__main__":
    main()