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

# Configuration de la page - affichage de la sidebar par défaut
st.set_page_config(
    page_title="Olist E-commerce Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"  # Sidebar affichée par défaut
)

st.markdown("""
    <div style="background: linear-gradient(90deg, #4e8df5, #83b3f7); padding:15px; border-radius:10px; margin-bottom:30px">
        <h1 style="color:white; text-align:center; font-size:48px; font-weight:bold">
            DASHBOARD E-COMMERCE OLIST
        </h1>
    </div>
    """, unsafe_allow_html=True)

# Ajout de CSS personnalisé
st.markdown("""
<style>
    /* Fond bleu marine et texte blanc pour le corps principal */
    .main {
        background-color: #0d2b45;
        color: white !important;
    }

    /* Styles pour les en-têtes - assurez-vous qu'ils sont bien en blanc */
    .main-header {
        font-size: 2rem;
        color: white !important;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.25rem;
        color: white !important;
        margin-bottom: 0.3rem;
    }

    /* Carte pour les métriques avec couleurs différentes */
    .metric-card-sales, .metric-card-revenue, .metric-card-average, .metric-card-delivery {
        border-radius: 10px;
        padding: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        color: white;
        margin-bottom: 8px;
    }
    .metric-card-sales { background-color: #1e88e5; }
    .metric-card-revenue { background-color: #43a047; }
    .metric-card-average { background-color: #fb8c00; }
    .metric-card-delivery { background-color: #8e24aa; }

    /* Suppression du style par défaut des métriques Streamlit */
    .metric-container {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Style pour les graphiques - AFFINÉ pour réduire les "boudins blancs" */
    .graph-container {
        background-color: white;
        border-radius: 6px;
        padding: 5px;
        margin-bottom: 6px;
        color: black;
        box-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }

    /* Titres des graphiques rendus plus petits et compacts */
    .graph-container h3 {
        color: black !important;
        margin-top: 0;
        margin-bottom: 2px;
        font-size: 0.85rem;
        padding: 0;
        line-height: 1.2;
    }

    /* Footer */
    .footer {
        color: #b0bec5;
        text-align: center;
        margin-top: 8px;
        font-size: 0.7rem;
    }

    /* Override Streamlit defaults pour affichage compact */
    .stApp {
        background-color: #0d2b45;
    }

    /* Ajustez la taille des conteneurs pour éviter le défilement */
    .main .block-container {
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
    }

    /* Réduisez l'espace entre les éléments */
    .main .element-container {
        margin-bottom: 0.25rem;
    }

    /* Rendre les textes blancs dans le tableau de bord principal */
    .stMarkdown, .stText, .stMarkdown p, .stMarkdown h1, .stMarkdown h2 {
        color: white !important;
    }

    /* Info boxes */
    .stAlert {
        background-color: #1e3a5f;
        color: white;
    }

    /* Assurer que les textes dans les conteneurs graphiques sont noirs */
    .graph-container p, .graph-container h1, .graph-container h2, .graph-container h3, .graph-container .stMarkdown {
        color: black !important;
    }

    /* Réduire la taille des radio buttons */
    .stRadio > div {
        flex-direction: row;
        gap: 0.3rem;
    }
    .stRadio label {
        font-size: 0.8rem;
        padding: 0.1rem 0.3rem;
    }

    /* Réduire l'espace dans les colonnes */
    .row-widget.stButton, .row-widget.stDownloadButton {
        padding: 0 !important;
    }

    /* Réduire l'espace au-dessus des graphiques */
    .plotly-graph-div {
        margin-top: 0 !important;
    }

    /* Réduire la hauteur des séparateurs */
    hr {
        margin: 0.3rem 0;
    }

    /* Forcer tous les textes en blanc dans la main */
    .main h1, .main h2, .main h3:not(.graph-container h3), .main p:not(.graph-container p), .main span:not(.graph-container span) {
        color: white !important;
    }

    /* Réduire la distance entre les éléments streamlit */
    .e1tzin5v2, .e1tzin5v3, .e1tzin5v4 {
        gap: 0.3rem !important;
    }

    /* Réduction de la taille du placeholder */
    .st-emotion-cache-1y4p8pa {
        padding: 0.5rem !important;
    }

    /* Stylisation de la sidebar avec fond blanc et texte bleu */
    .css-1d391kg, .css-1wrcr25, .css-12oz5g7, [data-testid="stSidebar"] {
        background-color: white !important;
    }

    /* Texte et éléments de la sidebar en bleu */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stDateInput label,
    [data-testid="stSidebar"] span {
        color: #0d2b45 !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
    }

    /* Police plus grande pour les éléments de la sidebar */
    [data-testid="stSidebar"] .stSelectbox,
    [data-testid="stSidebar"] .stMultiSelect,
    [data-testid="stSidebar"] .stDateInput {
        font-size: 1.1rem !important;
    }

    /* Nouveau style pour les titres de section - plus élégant */
    .filter-section-title {
        color: #0d2b45 !important;
        font-weight: bold;
        font-size: 1.2rem;
        padding-bottom: 5px;
        margin-bottom: 10px;
        border-bottom: 2px solid #0d2b45;
        text-transform: uppercase;
    }

    /* Style pour les sections de filtres */
    .filter-section {
        margin-bottom: 25px;
        padding-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Fonction pour formater les valeurs monétaires
def format_currency(value):
    return f"R$ {value:,.2f}"


with st.sidebar:
    st.markdown('<h2 style="text-align: center; padding-bottom: 10px;">FILTRES</h2>', unsafe_allow_html=True)

    # Section PÉRIODE
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown('<div class="filter-section-title">PÉRIODE</div>', unsafe_allow_html=True)

    # Date range filter - amélioré dans la sidebar
    date_min = datetime(2016, 9, 1)
    date_max = datetime(2018, 10, 31)

    # Options prédéfinies pour la sélection de la période
    period_options = [
        "Période personnalisée",
        "Derniers 30 jours",
        "Derniers 90 jours",
        "Dernière année",
        "Tout l'historique"
    ]
    selected_period = st.selectbox("Choisir une période", period_options)

    if selected_period == "Période personnalisée":
        # Deux sélecteurs de date distincts
        start_date = st.date_input(
            "Date de début",
            value=date_min.date(),
            min_value=date_min.date(),
            max_value=date_max.date(),
        )

        end_date = st.date_input(
            "Date de fin",
            value=date_max.date(),
            min_value=date_min.date(),
            max_value=date_max.date(),
        )

        # Vérification que la date de fin est postérieure à la date de début
        if start_date > end_date:
            st.warning("La date de fin doit être postérieure à la date de début.")
            end_date = start_date

        date_range = (start_date, end_date)
    else:
        end_date = date_max.date()
        if selected_period == "Derniers 30 jours":
            start_date = end_date - timedelta(days=30)
        elif selected_period == "Derniers 90 jours":
            start_date = end_date - timedelta(days=90)
        elif selected_period == "Dernière année":
            start_date = end_date - timedelta(days=365)
        else:  # Tout l'historique
            start_date = date_min.date()

        date_range = (start_date, end_date)
        st.markdown(f"<p>Période: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}</p>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Section LOCALISATION
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown('<div class="filter-section-title">Zone Géographique</div>', unsafe_allow_html=True)

    # Filtre d'état (Brésil)
    states = ["Tous"] + ["SP", "RJ", "MG", "RS", "PR", "SC", "BA", "DF", "GO", "ES"]
    selected_state = st.selectbox("État", states)

    st.markdown('</div>', unsafe_allow_html=True)

# Pour ce dashboard, la densité d'affichage est désormais en mode "précis" par défaut
graph_height = 400
map_height = 400

# Paramètres pour les requêtes SQL
params = {
    "start_date": date_range[0].strftime("%Y-%m-%d"),
    "end_date": date_range[1].strftime("%Y-%m-%d"),
    "state": "%" if selected_state == "Tous" else selected_state
}

# Création d'un layout compact pour toute la dashboard
layout_container = st.container()

with layout_container:
    # Métriques clés - plus compactes
    st.markdown("<h2 class='sub-header'>📌 Vue d'ensemble</h2>", unsafe_allow_html=True)

    # Chargement des KPIs
    kpi_data = execute_query("kpi_overview.sql", params)

    # Vérifier si les données sont bien chargées
    if not kpi_data.empty:
        metrics = kpi_data.iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div style="background-color: #1e88e5; border-radius: 10px; padding: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); color: white; margin-bottom: 8px;">
                <h3 style="margin-bottom:2px; font-size:2rem; font-weight:300;">Commandes</h3>
                <h2 style="margin:0; font-size:3rem; font-weight:300;">{int(metrics['order_count']):,}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div style="background-color: #43a047; border-radius: 10px; padding: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); color: white; margin-bottom: 8px;">
                <h3 style="margin-bottom:2px; font-size:2rem; font-weight:300;">Chiffre d'affaires</h3>
                <h2 style="margin:0; font-size:3rem; font-weight:300;">{int(metrics['total_revenue']):,}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )


    with col3:
        st.markdown(
            f"""
            <div style="background-color: #fb8c00; border-radius: 10px; padding: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); color: white; margin-bottom: 8px;">
                <h3 style="margin-bottom:2px; font-size:2rem; font-weight:300;">Panier moyen</h3>
                <h2 style="margin:0; font-size:3rem; font-weight:300;">{format_currency(metrics['avg_order'])}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f"""
            <div style="background-color: #8e24aa; border-radius: 10px; padding: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); color: white; margin-bottom: 8px;">
                <h3 style="margin-bottom:2px; font-size:2rem; font-weight:300;">Délai moyen (jours)</h3>
                <h2 style="margin:0; font-size:3rem; font-weight:300;">{metrics['avg_delivery_days']:.1f}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )


    # Organisation des graphiques dans un layout compact
    st.markdown("<h2 class='sub-header'>📊 Analyses principales</h2>", unsafe_allow_html=True)

    # Conteneur pour le graphique en courbe avec sélecteur d'onglets
    st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: white;'>Évolution des indicateurs de performance</h3>", unsafe_allow_html=True)

    # Sélecteur d'onglets pour choisir la métrique à afficher
    trend_tabs = ["Nombre de commandes", "CA total", "Nombre de clients"]
    trend_tab = st.radio("Métrique à afficher", trend_tabs, horizontal=True)

    # Chargement des données pour le graphique en courbe
    sales_trend = execute_query("sales_trend.sql", params)

    if not sales_trend.empty:
        # Définir le titre et les colonnes en fonction de l'onglet sélectionné
        if trend_tab == "Nombre de commandes":
            y_column = "number_of_orders"
            title = "Évolution mensuelle du nombre de commandes"
            y_title = "Nombre de commandes"
        elif trend_tab == "CA total":
            if "total_revenue" not in sales_trend.columns:
                average_order_value = 150  # Valeur fictive - à remplacer par données réelles
                sales_trend["total_revenue"] = sales_trend["number_of_orders"] * average_order_value
            y_column = "total_revenue"
            title = "Évolution mensuelle du chiffre d'affaires"
            y_title = "Chiffre d'affaires (R$)"
        else:  # Nombre de clients
            y_column = "unique_customers"
            title = "Évolution mensuelle du nombre de clients"
            y_title = "Nombre de clients"

        # Créer le graphique avec marges par défaut
        fig_trend = px.line(
            sales_trend,
            x="month",
            y=y_column,
            labels={"month": "Date", y_column: y_title}
        )

        fig_trend.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(
                family="Arial, sans-serif",
                size=11,
                color="black"
            ),
            xaxis=dict(
                title=dict(
                    text=" ",
                    font=dict(color="black", size=9)
                ),
                tickfont=dict(color="black", size=11),
                showgrid=False  # Désactiver la grille verticale
            ),
            yaxis=dict(
                title=dict(
                    text=y_title,
                    font=dict(color="black", size=11)
                ),
                tickfont=dict(color="black", size=11),
                showgrid=True,  # Activer la grille horizontale
                gridcolor='lightgray'  # Couleur grise pour la grille horizontale
            ),
            legend=dict(font=dict(color="black", size=8)),
            height=graph_height,
            margin=dict(l=20, r=20, t=10, b=20)
        )

        st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Row avec deux graphiques côte à côte
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: white;'>Top 10 Catégories par Revenu</h3>", unsafe_allow_html=True)
        top_categories = execute_query("top_categories.sql", params)
        if not top_categories.empty:
            # Création d'un dégradé de bleu personnalisé (commençant par un bleu plus foncé)
            custom_blues = [
                '#5dade2',
                '#3498db',
                '#2980b9',
                '#2475b0',
                '#1e3799'

            ]

            fig_cat = px.bar(
                top_categories.head(10),
                x="total_revenue",
                y="product_category_name_english",
                orientation='h',
                labels={"total_revenue": "Chiffre d'affaires (R$)", "product_category_name_english": "Catégorie"},
                color="total_revenue",
                color_continuous_scale=custom_blues
            )

            # Mise à jour du layout
            fig_cat.update_layout(
                height=graph_height,
                font_size=14,
                font_color="black",  # Toutes les écritures en noir
                plot_bgcolor="white",
                paper_bgcolor="white",
                margin=dict(l=20, r=10, t=5, b=20)
            )

            # Mise à jour des axes
            fig_cat.update_xaxes(
                tickfont_size=12,
                title_text="Chiffre d'affaires (R$)",
                title_font_size=14,
                title_font_color="black",
                tickfont_color="black"
            )

            fig_cat.update_yaxes(
                tickfont_size=12,
                categoryorder='total ascending',
                title_text="",  # Pas de titre pour l'axe Y
                tickfont_color="black"
            )

            # Masquer la barre de couleur
            fig_cat.update_coloraxes(showscale=False)

            st.plotly_chart(fig_cat, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: white;'>Répartition des avis clients</h3>", unsafe_allow_html=True)
        review_data = execute_query("reviews_distribution.sql", params)
        if not review_data.empty:
            # Créer une copie du dataframe avec un nouvel ordre pour le mapping des couleurs
            color_mapping_df = review_data.copy()

            # Trier par count pour avoir une correspondance entre hauteur de barre et couleur
            color_mapping_df = color_mapping_df.sort_values(by="count", ascending=False)

            # Créer une palette de couleurs basée sur l'ordre des valeurs de count
            n_colors = len(color_mapping_df)
            colors_list = ["#1a9850", "#91cf60", "#d9ef8b", "#fee08b"]
            # S'assurer d'avoir suffisamment de couleurs, répéter la dernière si nécessaire
            if n_colors > len(colors_list):
                colors_list.extend([colors_list[-1]] * (n_colors - len(colors_list)))
            elif n_colors < len(colors_list):
                colors_list = colors_list[:n_colors]

            # Créer un dictionnaire de correspondance note -> couleur basé sur la hauteur
            color_dict = {row["review_score"]: colors_list[i] for i, (_, row) in enumerate(color_mapping_df.iterrows())}

            fig_review = px.bar(
                review_data,
                x="review_score",
                y="count",
                labels={"review_score": "Note", "count": "Nombre d'avis"},
                color="review_score",
                color_discrete_map=color_dict
            )

            # Ajout des valeurs à l'intérieur des barres
            fig_review.update_traces(
                texttemplate='%{y}',
                textposition='inside',
                textfont=dict(color="black", size=12)
            )

            # Modifications avec grille horizontale uniquement
            fig_review.update_layout(
                height=graph_height,
                plot_bgcolor="white",
                paper_bgcolor="white",
                font=dict(
                    family="Arial, sans-serif",
                    size=9,
                    color="black"
                ),
                xaxis=dict(
                    title=dict(
                        text="Note",
                        font=dict(color="black", size=10)
                    ),
                    showticklabels=True,
                    tickfont=dict(color="black", size=12),
                    showgrid=False  # Pas de grille verticale
                ),
                yaxis=dict(
                    title=dict(
                        text="Nombre d'avis",
                        font=dict(color="black", size=9)
                    ),
                    showgrid=True,  # Grille horizontale uniquement
                    gridcolor='lightgrey',
                    tickfont=dict(color="black", size=8)
                ),
                showlegend=False,
                coloraxis_showscale=False,
                margin=dict(l=20, r=10, t=5, b=20)
            )

            st.plotly_chart(fig_review, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Carte dans un conteneur séparé
    st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: white;'>Distribution des commandes par état</h3>", unsafe_allow_html=True)

    geo_data = execute_query("geo_distribution.sql", params)
    if not geo_data.empty:
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

        geo_data["lat"] = geo_data["customer_state"].apply(lambda x: state_coordinates.get(x, [0, 0])[0])
        geo_data["lon"] = geo_data["customer_state"].apply(lambda x: state_coordinates.get(x, [0, 0])[1])

        fig = px.scatter_mapbox(
            geo_data,
            lat="lat",
            lon="lon",
            size="number_of_orders",
            color="number_of_orders",
            hover_name="customer_state",
            hover_data=["number_of_orders", "total_revenue"],
            zoom=3,
            height=map_height,
            size_max=40,
            color_continuous_scale=px.colors.sequential.Viridis,
            mapbox_style="carto-positron"
        )

        fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            mapbox=dict(
                center=dict(lat=-15, lon=-55),
            ),
            font=dict(
                color="black",
                size=8
            ),
            hoverlabel=dict(
                font_color="white",
                font_size=9
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Note finale avec un style adapté - plus compact
    st.markdown("""
    <div style="background-color:#1e3a5f; padding:8px; border-radius:8px; margin-top:8px;">
    <h3 style="color:white; font-size:0.85rem; margin:0 0 4px 0;">Explorez les onglets à gauche pour des analyses plus approfondies</h3>
    <div style="display:flex; flex-wrap:wrap; gap:6px;">
        <span style="color:white; background-color:#0d2b45; padding:3px 8px; border-radius:12px; font-size:0.75rem;">Catégories de produits</span>
        <span style="color:white; background-color:#0d2b45; padding:3px 8px; border-radius:12px; font-size:0.75rem;">Performance des vendeurs</span>
        <span style="color:white; background-color:#0d2b45; padding:3px 8px; border-radius:12px; font-size:0.75rem;">Segmentation client</span>
        <span style="color:white; background-color:#0d2b45; padding:3px 8px; border-radius:12px; font-size:0.75rem;">Analyse de cohortes</span>
        <span style="color:white; background-color:#0d2b45; padding:3px 8px; border-radius:12px; font-size:0.75rem;">Prévisions de ventes</span>
    </div>
    </div>
    """, unsafe_allow_html=True)

# Pied de page - plus compact
st.markdown("<div class='footer'>", unsafe_allow_html=True)
st.markdown("*Dashboard créé avec Streamlit et SQLAlchemy - Basé sur le dataset Olist*")
st.markdown("</div>", unsafe_allow_html=True)
