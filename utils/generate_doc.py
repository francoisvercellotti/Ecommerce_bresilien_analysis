import os
import sys
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Ajouter le chemin du projet pour importer correctement
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database_setup import create_db_engine

def export_database_documentation():
    """
    Exporte la documentation de la base de données de manière structurée
    """
    try:
        # Créer le moteur de base de données
        engine = create_db_engine()

        # Requête pour récupérer la documentation
        query = """
            SELECT
                object_name,
                object_type,
                description,
                usage_example,
                created_date
            FROM data_dictionary
            ORDER BY object_type, object_name
        """

        # Utiliser pandas pour exécuter la requête
        df = pd.read_sql(query, engine)

        # Créer le dossier docs si inexistant
        os.makedirs('docs', exist_ok=True)

        # Écriture du fichier markdown
        with open('docs/database_documentation.md', 'w', encoding='utf-8') as f:
            f.write("# Documentation Technique de la Base de Données\n\n")

            # Grouper par type d'objet
            grouped = df.groupby('object_type')

            for object_type, group in grouped:
                f.write(f"## {object_type.upper()}\n\n")

                for _, row in group.iterrows():
                    f.write(f"### {row['object_name']}\n\n")
                    f.write(f"**Description :** {row['description']}\n\n")

                    if row['usage_example'] and row['usage_example'] != 'N/A':
                        f.write("**Exemple d'utilisation :**\n")
                        f.write(f"```sql\n{row['usage_example']}\n```\n\n")

                    f.write(f"**Date de création :** {row['created_date']}\n\n")
                    f.write("---\n\n")

        print("Documentation exportée avec succès dans docs/database_documentation.md")

    except Exception as e:
        print(f"Erreur lors de l'export : {e}")

if __name__ == "__main__":
    export_database_documentation()