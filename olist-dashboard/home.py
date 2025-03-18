import sys
import os

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.database import execute_query

# Configuration de la page
st.set_page_config(
    page_title="Olist E-commerce Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ajout de CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Fonction pour formater les valeurs monétaires
def format_currency(value):
    return f"R$ {value:,.2f}"

# En-tête
st.markdown("<h1 class='main-header'>🛒 Dashboard Olist E-commerce</h1>", unsafe_allow_html=True)

# Introduction
st.markdown("""
Ce tableau de bord présente une analyse complète du dataset Olist, un marketplace brésilien.
Naviguez entre les différentes pages pour explorer les analyses détaillées.
""")

# Filtres dans la barre latérale
st.sidebar.title("Filtres")

# Date range filter - déterminé depuis les données
date_min = datetime(2016, 9, 1)
date_max = datetime(2018, 10, 31)

# Filtre de date
date_range = st.sidebar.date_input(
    "Période d'analyse",
    value=(date_min.date(), date_max.date()),
    min_value=date_min.date(),
    max_value=date_max.date(),
)

# Filtre d'état (Brésil)
states = ["Tous"] + ["SP", "RJ", "MG", "RS", "PR", "SC", "BA", "DF", "GO", "ES"]
selected_state = st.sidebar.selectbox("État", states)

# Paramètres pour les requêtes SQL
params = {
    "start_date": date_range[0].strftime("%Y-%m-%d"),
    "end_date": date_range[1].strftime("%Y-%m-%d"),
    "state": "%" if selected_state == "Tous" else selected_state
}

# Métriques clés
st.markdown("<h2 class='sub-header'>📌 Vue d'ensemble</h2>", unsafe_allow_html=True)

# Chargement des KPIs
kpi_data = execute_query("kpi_overview.sql", params)

# Vérifier si les données sont bien chargées
if not kpi_data.empty:
    metrics = kpi_data.iloc[0]

    # Affichage des métriques principales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Commandes", f"{int(metrics['order_count']):,}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Chiffre d'affaires", format_currency(metrics['total_revenue']))
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Panier moyen", format_currency(metrics['avg_order']))
        st.markdown("</div>", unsafe_allow_html=True)

    with col4:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Délai moyen (jours)", f"{metrics['avg_delivery_days']:.1f}")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    st.error("Impossible de charger les KPIs. Vérifiez votre connexion à la base de données.")

# Graphiques principaux
st.markdown("<h2 class='sub-header'>📊 Analyses principales</h2>", unsafe_allow_html=True)

# Tendance des ventes
sales_trend = execute_query("sales_trend.sql", params)
if not sales_trend.empty:
    st.subheader("Évolution des ventes")
    fig_trend = px.line(
        sales_trend,
        x="month",  # Modifié de "date" à "month"
        y="number_of_orders",  # Ou "delivered_orders" selon ce que tu veux visualiser
        title="Évolution des ventes mensuelles",
        labels={"month": "Date", "number_of_orders": "Nombre de commandes"}
    )
    fig_trend.update_layout(
        xaxis_title="Date",
        yaxis_title="Nombre de commandes",
        height=400
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# Row avec deux graphiques
col1, col2 = st.columns(2)

with col1:
    # Top 10 catégories
    top_categories = execute_query("top_categories.sql", params)
    if not top_categories.empty:
        fig_cat = px.bar(
            top_categories.head(10),
            x="total_revenue",  # Modifié de "revenue" à "total_revenue"
            y="product_category_name_english",  # Modifié de "category_name" à "product_category_name_english"
            orientation='h',
            title="Top 10 Catégories par Revenu",
            labels={"total_revenue": "Chiffre d'affaires (R$)", "product_category_name_english": "Catégorie"}
        )
        fig_cat.update_layout(yaxis={'categoryorder':'total ascending'}, height=400)
        st.plotly_chart(fig_cat, use_container_width=True)

with col2:
    # Distribution géographique
    geo_data = execute_query("geo_distribution.sql", params)
    if not geo_data.empty:
        st.subheader("Distribution des commandes par état")

        # Coordonnées approximatives des états brésiliens pour centrer les marqueurs
        state_coordinates = {
            "SP": [-23.5505, -46.6333], "RJ": [-22.9068, -43.1729],
            "MG": [-19.9167, -43.9345], "RS": [-30.0346, -51.2177],
            "PR": [-25.4297, -49.2719], "SC": [-27.5969, -48.5495],
            "BA": [-12.9716, -38.5016], "DF": [-15.7801, -47.9292],
            "GO": [-16.6799, -49.2550], "ES": [-20.3155, -40.3128],
            "PE": [-8.0476, -34.8770], "CE": [-3.7327, -38.5270],
            "PA": [-1.4558, -48.4902], "MT": [-15.6014, -56.0979],
            "MA": [-2.5307, -44.3068], "MS": [-20.4428, -54.6464],
            "PB": [-7.1195, -34.8450], "RN": [-5.7945, -35.2120],
            "PI": [-5.0920, -42.8038], "AL": [-9.6660, -35.7350],
            "SE": [-10.9472, -37.0731], "RO": [-8.7619, -63.9039],
            "AM": [-3.1190, -60.0217], "TO": [-10.1689, -48.3326],
            "AC": [-9.9754, -67.8249], "AP": [0.0356, -51.0705],
            "RR": [2.8199, -60.6714]
        }

        # Ajouter les coordonnées aux données
        geo_data["lat"] = geo_data["customer_state"].apply(lambda x: state_coordinates.get(x, [0, 0])[0])
        geo_data["lon"] = geo_data["customer_state"].apply(lambda x: state_coordinates.get(x, [0, 0])[1])

        # Créer une carte avec des marqueurs de taille proportionnelle
        fig = px.scatter_mapbox(
            geo_data,
            lat="lat",
            lon="lon",
            size="number_of_orders",  # Taille proportionnelle au nombre de commandes
            color="number_of_orders",  # Couleur basée sur le nombre de commandes
            hover_name="customer_state",
            hover_data=["number_of_orders", "total_revenue"],
            zoom=3,  # Réduire le zoom
            height=600,  # Augmenter la hauteur de la carte
            size_max=50,  # Augmenter la taille maximale des marqueurs
            color_continuous_scale=px.colors.sequential.Viridis,  # Changer la palette de couleurs
            mapbox_style="carto-positron"
        )

        # Ajouter des étiquettes pour chaque état
        for i, row in geo_data.iterrows():
            fig.add_trace(
                go.Scattermapbox(
                    lat=[row["lat"]],
                    lon=[row["lon"]],
                    mode="markers+text",
                    text=[f"Commandes: {row['number_of_orders']}<br>Revenu: {format_currency(row['total_revenue'])}"],
                    textfont=dict(size=12, color="black"),
                    hoverinfo="text",
                    marker=dict(size=10, color="rgba(0, 0, 0, 0)")  # Marqueurs invisibles
                )
            )

        fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            mapbox=dict(
                center=dict(lat=-15, lon=-55),  # Centre de la carte sur le Brésil
            )
        )

        st.plotly_chart(fig, use_container_width=True)

# Ajout du graphique des avis clients
review_data = execute_query("reviews_distribution.sql", params)

if not review_data.empty:
    st.subheader("Répartition des avis clients")
    fig_review = px.bar(
        review_data,
        x="review_score",
        y="count",
        title="Répartition des avis clients",
        labels={"review_score": "Note", "count": "Nombre d'avis"}
    )
    fig_review.update_layout(height=400)
    st.plotly_chart(fig_review, use_container_width=True)

# Note finale pour diriger vers d'autres pages
st.info("""
Explorez les onglets à gauche pour des analyses plus approfondies sur :
- Les catégories de produits
- La performance des vendeurs
- La segmentation client
- L'analyse de cohortes
- Les prévisions de ventes
""")

# Pied de page
st.markdown("---")
st.markdown("*Dashboard créé avec Streamlit et SQLAlchemy - Basé sur le dataset Olist*")
