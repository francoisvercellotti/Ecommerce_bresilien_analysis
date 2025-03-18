import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import streamlit as st

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

@st.cache_data(ttl=3600)  # Cache les résultats pendant 1 heure
def execute_query(query_file, params=None):
    """Exécute une requête SQL depuis un fichier et retourne un DataFrame"""
    try:
        # Pour le développement, chargez depuis des fichiers SQL
        if os.path.exists(f"sql/{query_file}"):
            with open(f"sql/{query_file}", "r") as file:
                query = file.read()

            engine = create_db_engine()
            # Passer les paramètres directement à read_sql
            return pd.read_sql(text(query), engine, params=params)

        # Pour le déploiement, chargez des données prétraitées
        else:
            # Fallback pour le déploiement - charger des datasets prétraités
            data_file = f"data/{query_file.replace('.sql', '.csv')}"
            if os.path.exists(data_file):
                return pd.read_csv(data_file)
            else:
                st.error(f"Fichier non trouvé: {data_file}")
                return pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur lors de l'exécution de la requête: {e}")
        return pd.DataFrame()

@st.cache_data
def execute_raw_query(query_string, params=None):
    """Exécute une requête SQL brute et retourne un DataFrame"""
    try:
        if params:
            query = query_string.format(**params)
        else:
            query = query_string

        engine = create_db_engine()
        return pd.read_sql(text(query), engine)
    except Exception as e:
        st.error(f"Erreur lors de l'exécution de la requête: {e}")
        return pd.DataFrame()