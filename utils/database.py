import os
import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st

def create_db_engine():
    """Crée et retourne une connexion à la base de données PostgreSQL."""
    try:
        # Utilisation des secrets Streamlit en priorité
        user = st.secrets.get("DB_USER") or os.getenv("DB_USER")
        password = st.secrets.get("DB_PASSWORD") or os.getenv("DB_PASSWORD")
        host = st.secrets.get("DB_HOST") or os.getenv("DB_HOST")
        port = st.secrets.get("DB_PORT") or os.getenv("DB_PORT")
        db_name = st.secrets.get("DB_NAME") or os.getenv("DB_NAME")

        if not all([user, password, host, port, db_name]):
            st.error("Informations de connexion incomplètes")
            return None

        connection_string = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
        return create_engine(connection_string)
    except Exception as e:
        st.error(f"Erreur de connexion à la base de données : {e}")
        return None


def clear_table(engine, table_name):
    """Vide une table en utilisant TRUNCATE ... CASCADE."""
    with engine.begin() as connection:
        connection.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;"))
    print(f"Table {table_name} vidée.")

@st.cache_data(ttl=3600)  # Cache les résultats pendant 1 heure
def execute_query(query_file, params=None):
    engine = create_db_engine()
    if engine is None:
        return pd.DataFrame()

    try:
        # Pour le développement, chargez depuis des fichiers SQL
        if os.path.exists(f"sql/{query_file}"):
            with open(f"sql/{query_file}", "r") as file:
                query = file.read()

            # Passer les paramètres directement à read_sql
            return pd.read_sql(text(query), engine, params=params)

        # Pour le déploiement, chargez des données prétraitées
        else:
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
    engine = create_db_engine()
    if engine is None:
        return pd.DataFrame()

    try:
        if params:
            query = query_string.format(**params)
        else:
            query = query_string

        return pd.read_sql(text(query), engine)
    except Exception as e:
        st.error(f"Erreur lors de l'exécution de la requête: {e}")
        return pd.DataFrame()