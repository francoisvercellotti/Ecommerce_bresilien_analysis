import sys
import os

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.database import execute_query, execute_raw_query
from datetime import datetime, timedelta


# Configuration de la page
st.set_page_config(
    page_title="Olist - Analyse des Catégories",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <div style="background: linear-gradient(90deg, #4e8df5, #83b3f7); padding:15px; border-radius:10px; margin-bottom:30px">
        <h1 style="color:white; text-align:center; font-size:48px; font-weight:bold">
            ANALYSE DES CATÉGORIES DE PRODUITS
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

        /* Styles pour les en-têtes */
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

        /* Carte pour les métriques avec couleurs différentes et taille fixe */
        .metric-card {
            background-color: #1e88e5;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
            color: white;
            margin-bottom: 8px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            height: 180px; /* Hauteur fixe */
            width: 100%; /* Largeur complète */
            box-sizing: border-box; /* Pour inclure padding dans la taille totale */
        }

        .metric-card .metric-label {
            font-size: 1.6rem;
            margin-bottom: 10px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 100%;
        }

        .metric-card .metric-value {
            font-size: 1.5rem;
            font-weight: bold;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 100%;
        }

        .metric-card-customers {
            background-color: #1e88e5;
        }
        .metric-card-spend {
            background-color: #43a047;
        }
        .metric-card-frequency {
            background-color: #fb8c00;
        }
        .metric-card-clv {
            background-color: #8e24aa;
        }

        /* Suppression du style par défaut des métriques Streamlit */
        .metric-container {
            margin: 0 !important;
            padding: 0 !important;
        }

        /* Style pour les graphiques */
        .graph-container {
            background-color: white;
            border-radius: 6px;
            padding: 5px;
            margin-bottom: 6px;
            color: black;
            box-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }

        /* Titres des graphiques */
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

        /* Override Streamlit defaults */
        .stApp {
            background-color: #0d2b45;
        }

        /* Ajustez la taille des conteneurs */
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

        /* Style pour les tableaux */
        .dataframe {
            font-size: 0.7rem;
        }
        .dataframe th {
            background-color: #1e3a5f;
            color: white !important;
            padding: 3px !important;
        }
        .dataframe td {
            padding: 3px !important;
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

        /* Responsive Design pour les métriques */
        @media screen and (max-width: 768px) {
            .metric-card {
                height: auto;
                min-height: 120px;
            }

            .metric-card .metric-label {
                font-size: 1rem;
            }

            .metric-card .metric-value {
                font-size: 1.5rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)

# Fonction pour formater les valeurs monétaires
def format_currency(value):
    return f"R$ {value:,.2f}"

# Chargement des données avec cache et paramètres de date
@st.cache_data(ttl=3600)
def load_category_performance(start_date=None, end_date=None):
    query = "category_performance.sql"
    params = {}
    if start_date and end_date:
        # Si la requête SQL contient des paramètres pour les dates
        params = {"start_date": start_date, "end_date": end_date}
    return execute_query(query, params)

@st.cache_data(ttl=3600)
def load_category_trends(start_date=None, end_date=None):
    query = "category_trends.sql"
    params = {}
    if start_date and end_date:
        # Si la requête SQL contient des paramètres pour les dates
        params = {"start_date": start_date, "end_date": end_date}
    return execute_query(query, params)

@st.cache_data(ttl=3600)
def load_cross_selling(start_date=None, end_date=None):
    query = "cross_selling_categories.sql"
    params = {}
    if start_date and end_date:
        # Si la requête SQL contient des paramètres pour les dates
        params = {"start_date": start_date, "end_date": end_date}
    return execute_query(query, params)

@st.cache_data(ttl=3600)
def load_price_distribution(start_date=None, end_date=None, categories=None):
    query = "category_price_distribution.sql"
    params = {}
    if start_date and end_date:
        params = {"start_date": start_date, "end_date": end_date}

    result = execute_query(query, params)

    # Filtrer par catégories si spécifié
    if categories and len(categories) > 0:
        result = result[result["category_name"].isin(categories)]

    return result

@st.cache_data(ttl=3600)
def load_categories_list():
    return execute_query("categories_list.sql")

@st.cache_data(ttl=3600)
def load_date_range():
    return execute_query("date_range.sql")

# Constantes pour les graphiques
# Mode détaillé par défaut
graph_height = 400
heatmap_height = 600




with st.sidebar:
    st.markdown('<h2 style="text-align: center; padding-bottom: 10px;">FILTRES</h2>', unsafe_allow_html=True)

    # Section PÉRIODE
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown('<div class="filter-section-title">PÉRIODE</div>', unsafe_allow_html=True)
    try:
        date_range = load_date_range()
        if not date_range.empty:
            min_date = date_range["min_date"].iloc[0].date()
            max_date = date_range["max_date"].iloc[0].date()

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
                start_date = st.date_input(
                    "Date de début",
                    min_date,
                    min_value=min_date,
                    max_value=max_date
                )

                end_date = st.date_input(
                    "Date de fin",
                    max_date,
                    min_value=min_date,
                    max_value=max_date
                )
            else:
                from datetime import timedelta
                end_date = max_date
                if selected_period == "Derniers 30 jours":
                    start_date = end_date - timedelta(days=30)
                elif selected_period == "Derniers 90 jours":
                    start_date = end_date - timedelta(days=90)
                elif selected_period == "Dernière année":
                    start_date = end_date - timedelta(days=365)
                else:  # Tout l'historique
                    start_date = min_date

                st.write(f"Période: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")
        else:
            st.warning("Impossible de charger les dates. Utilisation de la période complète.")
            start_date = None
            end_date = None
    except Exception as e:
        st.error(f"Erreur lors du chargement des dates: {e}")
        start_date = None
        end_date = None

    # Convertir les dates en format string pour les requêtes SQL si nécessaire
    sql_start_date = start_date.strftime('%Y-%m-%d') if start_date else None
    sql_end_date = end_date.strftime('%Y-%m-%d') if end_date else None

    # Chargement des catégories pour le filtre
    try:
        categories_list = load_categories_list()
        if not categories_list.empty:
            all_categories = categories_list["category_name"].tolist()


            st.markdown('<div class="filter-section">', unsafe_allow_html=True)
            st.markdown('<div class="filter-section-title">Catégories</div>', unsafe_allow_html=True)

            # Option pour sélectionner toutes les catégories ou spécifier des catégories
            select_all_categories = st.checkbox("Toutes les catégories", value=True)

            if not select_all_categories:
                # Multi-sélecteur pour les catégories
                selected_categories = st.multiselect(
                    "Sélectionner des catégories spécifiques",
                    options=all_categories,
                    default=all_categories[:5] if len(all_categories) > 5 else all_categories
                )
            else:
                selected_categories = all_categories

            # Afficher le nombre de catégories sélectionnées
            st.write(f"{len(selected_categories)} catégorie(s) sélectionnée(s)")
    except Exception as e:
        st.error(f"Erreur lors du chargement des catégories: {e}")
        selected_categories = []

# Conteneur pour le dashboard principal
# Création d'une layout compact pour tout le dashboard
layout_container = st.container()

with layout_container:
    # Métriques générales pour les catégories
    col1, col2, col3, col4 = st.columns(4)

    try:
        # Charger les données avec les filtres appliqués
        category_performance = load_category_performance(sql_start_date, sql_end_date)

        # Appliquer le filtre de catégories
        if selected_categories and len(selected_categories) > 0:
            category_performance = category_performance[category_performance["category_name"].isin(selected_categories)]

        if not category_performance.empty:
            with col1:
                st.markdown(
                    f"""
                    <div class='metric-card metric-card-customers'>
                        <div class='metric-label'>Nombre de catégories</div>
                        <div class='metric-value'>{len(category_performance)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col2:
                st.markdown(
                    f"""
                    <div class='metric-card metric-card-spend'>
                        <div class='metric-label'>Revenu total</div>
                        <div class='metric-value'>R$ {category_performance['total_revenue'].sum():,.0f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col3:
                st.markdown(
                    f"""
                    <div class='metric-card metric-card-frequency'>
                        <div class='metric-label'>Commandes totales</div>
                        <div class='metric-value'>{category_performance['order_count'].sum():,}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col4:
                st.markdown(
                    f"""
                    <div class='metric-card metric-card-clv'>
                        <div class='metric-label'>Note moyenne</div>
                        <div class='metric-value'>{category_performance['avg_review_score'].mean():.2f}/5</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.warning("Aucune donnée de catégorie disponible pour les filtres sélectionnés.")
    except Exception as e:
        st.error(f"Erreur lors du chargement des métriques des catégories: {e}")


with layout_container:
    # Tableau de performance des catégories
    st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
    st.markdown("<h3>Performance globale des catégories</h3>", unsafe_allow_html=True)
    try:
        # Charger les données avec les filtres de date appliqués
        category_performance = load_category_performance(sql_start_date, sql_end_date)

        # Appliquer le filtre de catégories
        if selected_categories and len(selected_categories) > 0:
            category_performance = category_performance[category_performance["category_name"].isin(selected_categories)]

        if not category_performance.empty:
            # Ajouter un sélecteur pour la colonne de tri
            sort_options = {
                "category_name": "Catégorie (A-Z)",
                "order_count": "Nombre de commandes",
                "total_revenue": "Revenu total",
                "avg_price": "Prix moyen",
                "avg_review_score": "Note moyenne",
                "avg_freight_value": "Frais de port moyens"
            }

            # Créer deux colonnes pour le tri
            col1, col2 = st.columns([3, 1])

            with col1:
                selected_sort = st.selectbox(
                    "Trier par:",
                    options=list(sort_options.keys()),
                    format_func=lambda x: sort_options[x],
                    index=2  # Par défaut, tri par revenu total
                )

            with col2:
                # Ajouter un sélecteur pour l'ordre de tri
                sort_ascending = st.radio(
                    "Ordre:",
                    options=["Décroissant", "Croissant"],
                    horizontal=True,
                    index=0  # Par défaut, décroissant
                )

                # Convertir le choix en valeur booléenne
                is_ascending = sort_ascending == "Croissant"

            # Trier le DataFrame selon la colonne sélectionnée et l'ordre choisi
            category_performance = category_performance.sort_values(by=selected_sort, ascending=is_ascending)

            # Dupliquer le DataFrame pour conserver les valeurs numériques pour le style
            numeric_df = category_performance.copy()

            # Arrondir les valeurs numériques à 1 chiffre après la virgule
            for col in ["total_revenue", "avg_price", "avg_freight_value", "avg_review_score"]:
                numeric_df[col] = numeric_df[col].round(1)

            # Appliquer le style au DataFrame avec une seule palette de couleur (Bleu)
            styled_df = numeric_df.style\
                .background_gradient(subset=["order_count", "total_revenue", "avg_price", "avg_review_score", "avg_freight_value"], cmap="Blues")\
                .applymap(lambda _: "background-color: lightgrey; color: black;", subset=["category_name"])\
                .format({
                    "total_revenue": "R$ {:.1f}",
                    "avg_price": "R$ {:.1f}",
                    "avg_freight_value": "R$ {:.1f}",
                    "avg_review_score": "{:.1f}"
                })

            # Appliquer un fond bleu clair à l'entête
            styled_df = styled_df.set_table_styles([
                {
                    'selector': 'th',  # Sélectionner la ligne d'entête
                    'props': [
                        ('background-color', '#1e88e5'),  # Bleu clair pour la ligne d'entête
                        ('color', 'white'),  # Texte blanc pour l'entête
                        ('text-align', 'center')  # Centrer le texte de l'entête
                    ]
                }
            ])

            # Générer le HTML sans index
            html_table = styled_df.hide(axis="index").to_html()

            # Remplacer les en-têtes de colonnes avec les noms français
            html_table = html_table.replace('>category_name<', '>Catégorie<')
            html_table = html_table.replace('>order_count<', '>Nombre de commandes<')
            html_table = html_table.replace('>total_revenue<', '>Revenu total<')
            html_table = html_table.replace('>avg_price<', '>Prix moyen<')
            html_table = html_table.replace('>avg_review_score<', '>Note moyenne<')
            html_table = html_table.replace('>avg_freight_value<', '>Frais de port moyens<')

            # Ajouter le CSS pour le défilement
            st.markdown("""
            <style>
            .scrollable-table {
                height: 400px;
                overflow-y: auto;
                display: block;
            }
            .scrollable-table table {
                width: 100%;
            }
            </style>
            """, unsafe_allow_html=True)

            # Envelopper le tableau dans un div avec défilement
            st.markdown(f'<div class="scrollable-table">{html_table}</div>', unsafe_allow_html=True)

            # Option de téléchargement
            csv = category_performance.to_csv(index=False)
            st.download_button(
                label="📥 Télécharger les données (CSV)",
                data=csv,
                file_name="olist_category_performance.csv",
                mime="text/csv",
                help="Télécharger les données de performance des catégories au format CSV"
            )
        else:
            st.warning("Aucune donnée de performance des catégories disponible.")
    except Exception as e:
        st.error(f"Erreur lors du chargement des performances des catégories: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

    # Graphiques de performance des catégories
    col1, col2 = st.columns(2)


    with col1:
        st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: white;'>Top 10 des catégories par Revenu total</h3>", unsafe_allow_html=True)

        # Définir une métrique fixe pour le graphique
        default_metric = "total_revenue"
        metric_label = "Chiffre d'affaires (R$)"

        try:
            if not category_performance.empty:
                # Tri et sélection des 10 meilleures catégories selon la métrique fixe
                top_categories = category_performance.sort_values(by=default_metric, ascending=False).head(10)

                # Création d'un dégradé de bleu personnalisé (commençant par un bleu plus foncé)
                custom_blues = [
                    '#5dade2',
                    '#3498db',
                    '#2980b9',
                    '#2475b0',
                    '#1e3799'
                ]

                fig_cat = px.bar(
                    top_categories,
                    x=default_metric,
                    y="category_name",
                    orientation='h',
                    labels={"category_name": "Catégorie", default_metric: metric_label},
                    color=default_metric,
                    color_continuous_scale=custom_blues
                )

                # Mise à jour du layout
                fig_cat.update_layout(
                    height=graph_height,
                    font_size=14,
                    font_color="black",
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    margin=dict(l=20, r=10, t=5, b=20)
                )

                # Mise à jour des axes
                fig_cat.update_xaxes(
                    tickfont_size=12,
                    title_text=metric_label,
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

            else:
                st.warning("Aucune donnée disponible pour le graphique des catégories.")

        except Exception as e:
            st.error(f"Erreur lors de l'affichage du top des catégories: {e}")

        st.markdown("</div>", unsafe_allow_html=True)


    with col2:
        st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
        st.markdown("<h3>Distribution des prix par catégorie</h3>", unsafe_allow_html=True)
        try:
            # Charger les données avec les filtres appliqués
            price_distribution = load_price_distribution(sql_start_date, sql_end_date, selected_categories)

            if not price_distribution.empty:
                # Sélection des catégories à montrer (si trop nombreuses)
                if len(selected_categories) > 10:
                    # Si trop de catégories, prendre les top catégories par revenu total
                    if not category_performance.empty:
                        top_categories_list = category_performance.sort_values(by="total_revenue", ascending=False).head(10)["category_name"].tolist()
                        price_data = price_distribution[price_distribution["category_name"].isin(top_categories_list)]
                        title = "Distribution des prix (Top 10 catégories par revenu)"
                    else:
                        price_data = price_distribution.sample(min(len(price_distribution), 1000))  # Limiter pour des raisons de performance
                        title = "Distribution des prix (échantillon)"
                else:
                    price_data = price_distribution
                    title = "Distribution des prix par catégorie"

                fig = px.box(
                    price_data,
                    x="category_name",
                    y="price",
                    labels={"category_name": "Catégorie", "price": "Prix (R$)"},
                    color="category_name"
                )
                fig.update_layout(
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    font=dict(family="Arial, sans-serif", size=10, color="black"),
                    xaxis=dict(
                        title=dict(text="", font=dict(color="black", size=10)),
                        tickfont=dict(color="black", size=10),
                        tickangle=-45
                    ),
                    yaxis=dict(
                        title=dict(text="Prix (R$)", font=dict(color="black", size=10)),
                        tickfont=dict(color="black", size=8)
                    ),
                    showlegend=False,
                    height=graph_height,
                    margin=dict(l=10, r=10, t=10, b=30)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Aucune donnée disponible pour la distribution des prix.")
        except Exception as e:
            st.error(f"Erreur lors de l'affichage de la distribution des prix: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

    # Tendance des ventes par catégorie
    st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
    st.markdown("<h3>Évolution des ventes par catégorie</h3>", unsafe_allow_html=True)
    try:
        # Charger les données avec les filtres appliqués
        category_trend = load_category_trends(sql_start_date, sql_end_date)

        if not category_trend.empty:
            # Filtrer par catégories sélectionnées
            if selected_categories and len(selected_categories) > 0:
                category_trend = category_trend[category_trend["category_name"].isin(selected_categories)]

            # Si trop de catégories pour visualisation claire, limiter
            if len(category_trend["category_name"].unique()) > 10:
                # Utiliser les 10 meilleures catégories selon le revenu total
                if not category_performance.empty:
                    top_categories_list = category_performance.sort_values(by="total_revenue", ascending=False).head(10)["category_name"].tolist()
                    trend_data = category_trend[category_trend["category_name"].isin(top_categories_list)]
                else:
                    # Ou prendre les 10 premières par ordre alphabétique
                    unique_categories = sorted(category_trend["category_name"].unique())[:10]
                    trend_data = category_trend[category_trend["category_name"].isin(unique_categories)]
            else:
                trend_data = category_trend

            fig = px.line(
                trend_data,
                x="order_month",
                y="total_revenue",
                color="category_name",
                labels={"order_month": "Mois", "total_revenue": "Revenu total (R$)", "category_name": "Catégorie"}
            )
            fig.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white",
                font=dict(family="Arial, sans-serif", size=10, color="black"),
                xaxis=dict(
                    title=dict(text="Mois", font=dict(color="black", size=1)),
                    tickfont=dict(color="black", size=10),
                    # Ajoutez ces lignes pour adapter l'axe x à la période
                    type="date",  # Spécifier que c'est un axe de date
                    range=[trend_data["order_month"].min(), trend_data["order_month"].max()],  # Définir la plage en fonction des données filtrées
                    tickformat="%b %Y",  # Format d'affichage des dates (mois année)
                    showgrid=False,  # Activer la grille
                    gridcolor='rgba(220, 220, 220, 0.8)'  # Couleur gris clair pour la grille
                ),
                yaxis=dict(
                    title=dict(text="Revenu total (R$)", font=dict(color="black", size=10)),
                    tickfont=dict(color="black", size=10),
                    showgrid=True,  # Activer la grille
                    gridcolor='rgba(220, 220, 220, 0.8)'  # Couleur gris clair pour la grille
                ),
                legend=dict(
                    font=dict(size=12, color="black"),
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                ),
                height=graph_height + 50,  # Un peu plus haut pour la légende
                margin=dict(l=10, r=10, t=30, b=10)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Aucune donnée disponible pour l'évolution des ventes.")
    except Exception as e:
        st.error(f"Erreur lors de l'affichage des tendances: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

    # Analyse des achats croisés entre catégories
    st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
    st.markdown("<h3>Analyse des achats croisés entre catégories</h3>", unsafe_allow_html=True)
    try:
        # Charger les données avec les filtres appliqués
        cross_selling = load_cross_selling(sql_start_date, sql_end_date)

        # Filtrer par catégories sélectionnées si nécessaire
        if selected_categories and len(selected_categories) > 0:
            cross_selling = cross_selling[
                cross_selling["category_name_1"].isin(selected_categories) &
                cross_selling["category_name_2"].isin(selected_categories)
            ]

        # Créer une matrice pour la heatmap
        if not cross_selling.empty:
            pivot_table = cross_selling.pivot(
                index="category_name_1",
                columns="category_name_2",
                values="frequency"
            ).fillna(0)

            # Limiter à un sous-ensemble de catégories pour la clarté
            if len(pivot_table) > 15:
                # Sélectionner les 15 premières catégories par fréquence totale
                top_categories = cross_selling.groupby("category_name_1")["frequency"].sum().nlargest(15).index.tolist()
                pivot_table = pivot_table.loc[top_categories, top_categories]

            fig = px.imshow(
                pivot_table,
                labels={"x": "Catégorie achetée avec", "y": "Catégorie principale", "color": "Fréquence"},
                color_continuous_scale="Viridis",
                aspect="auto"  # Ajustement automatique de l'aspect ratio
            )
            fig.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white",
                font=dict(family="Arial, sans-serif", size=9, color="black"),
                xaxis=dict(
                    tickfont=dict(color="black", size=10),
                    tickangle=-45
                ),
                yaxis=dict(
                    tickfont=dict(color="black", size=10)
                ),
                height=heatmap_height,
                margin=dict(l=10, r=10, t=10, b=50)
            )
            # Modification de la colorbar
            fig.update_coloraxes(
                colorbar=dict(
                    title_font=dict(color='black'),
                    tickfont=dict(color='black')
                )
            )
            st.plotly_chart(fig, use_container_width=True)

            # Explication compacte du graphique
            st.markdown("""
            <p style="font-size:0.8rem; color:black;">
            Cette heatmap montre la fréquence d'achat croisé entre catégories. Les valeurs plus claires indiquent des associations plus fortes.
            </p>
            """, unsafe_allow_html=True)
        else:
            st.info("Pas de données d'achat croisé disponibles.")
    except Exception as e:
        st.error(f"Erreur lors de l'affichage des achats croisés: {e}")
    st.markdown("</div>", unsafe_allow_html=True)


 # Pied de page
st.markdown("<div class='footer'>© 2023 Olist - Analyse Categories - Dernière mise à jour: {}</div>".format(datetime.now().strftime("%d/%m/%Y %H:%M")), unsafe_allow_html=True)

# Ajouter un peu d'espace en bas
st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
