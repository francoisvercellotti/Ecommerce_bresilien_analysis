import pandas as pd

# Charger le fichier CSV dans un DataFrame
df = pd.read_csv('data/olist_order_reviews_dataset.csv')

# Supprimer les doublons basés sur 'review_id'
df = df.drop_duplicates(subset='review_id', keep='first')

# Enregistrer le DataFrame modifié dans un nouveau fichier CSV
df.to_csv('data/olist_order_reviews_dataset.csv', index=False)

print("Les doublons ont été supprimés et le fichier a été réécrit.")
