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
    page_title="Olist - Analyse des Vendeurs",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"  # Barre latérale visible par défaut
)

st.markdown("""
    <div style="background: linear-gradient(90deg, #4e8df5, #83b3f7); padding:15px; border-radius:10px; margin-bottom:30px">
        <h1 style="color:white; text-align:center; font-size:48px; font-weight:bold">
            ANALYSE DES VENDEURS
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
    return f"R$ {value:,.0f}"

# Chargement des données avec cache et paramètres de date
@st.cache_data(ttl=3600)
def load_seller_performance(start_date=None, end_date=None):
    query = """
    WITH seller_metrics AS (
        SELECT
            seller_id,
            COUNT(DISTINCT order_id) AS total_orders,
            COUNT(DISTINCT product_id) AS unique_products,
            COUNT(DISTINCT product_category_name_english) AS product_categories,
            SUM(price) AS total_revenue,
            AVG(price) AS average_price,
            AVG(delivery_time_days) AS avg_delivery_time,
            AVG(review_score) AS avg_review,
            COUNT(CASE WHEN delivered_on_time THEN 1 END)::numeric / NULLIF(COUNT(*), 0) * 100 AS on_time_delivery_percentage,
            COUNT(CASE WHEN review_score >= 4 THEN 1 END)::numeric / NULLIF(COUNT(CASE WHEN review_score IS NOT NULL THEN 1 END), 0) * 100 AS positive_review_percentage,
            COUNT(CASE WHEN review_score <= 2 THEN 1 END)::numeric / NULLIF(COUNT(CASE WHEN review_score IS NOT NULL THEN 1 END), 0) * 100 AS negative_review_percentage
        FROM vw_order_details
        WHERE seller_id IS NOT NULL
        {date_filter}
        GROUP BY seller_id
    ),
    seller_rankings AS (
        SELECT
            seller_id,
            total_orders,
            unique_products,
            product_categories,
            total_revenue,
            average_price,
            avg_delivery_time,
            avg_review,
            on_time_delivery_percentage,
            positive_review_percentage,
            negative_review_percentage,
            PERCENT_RANK() OVER (ORDER BY total_revenue DESC) AS revenue_percentile,
            PERCENT_RANK() OVER (ORDER BY avg_review DESC) AS review_percentile,
            PERCENT_RANK() OVER (ORDER BY on_time_delivery_percentage DESC) AS delivery_percentile
        FROM seller_metrics
        WHERE total_orders >= 5
    )
    SELECT
        seller_id,
        total_orders,
        unique_products,
        product_categories,
        CAST(total_revenue AS numeric(10,2)) AS total_revenue,
        CAST(average_price AS numeric(10,2)) AS average_price,
        CAST(avg_delivery_time AS numeric(10,2)) AS avg_delivery_time,
        CAST(avg_review AS numeric(10,2)) AS avg_review,
        CAST(on_time_delivery_percentage AS numeric(10,2)) AS on_time_delivery_percentage,
        CAST(positive_review_percentage AS numeric(10,2)) AS positive_review_percentage,
        CAST(negative_review_percentage AS numeric(10,2)) AS negative_review_percentage,
        CAST((revenue_percentile * 100) AS numeric(10,2)) AS revenue_percentile,
        CAST((review_percentile * 100) AS numeric(10,2)) AS review_percentile,
        CAST((delivery_percentile * 100) AS numeric(10,2)) AS delivery_percentile,
        CASE
            WHEN revenue_percentile <= 0.2 AND review_percentile <= 0.2 AND delivery_percentile <= 0.2 THEN 'Elite'
            WHEN revenue_percentile <= 0.4 AND review_percentile <= 0.4 AND delivery_percentile <= 0.4 THEN 'High Performer'
            WHEN revenue_percentile <= 0.6 AND review_percentile <= 0.6 AND delivery_percentile <= 0.6 THEN 'Good'
            WHEN revenue_percentile <= 0.8 AND review_percentile <= 0.8 AND delivery_percentile <= 0.8 THEN 'Average'
            ELSE 'Needs Improvement'
        END AS performance_category
    FROM seller_rankings
    ORDER BY (revenue_percentile + review_percentile + delivery_percentile) / 3
    """

    date_filter = ""
    if start_date and end_date:
        date_filter = f"AND order_purchase_timestamp BETWEEN '{start_date}' AND '{end_date}'"

    query = query.format(date_filter=date_filter)

    return execute_raw_query(query)

@st.cache_data(ttl=3600)
def load_seller_trends(start_date=None, end_date=None):
    query = """
    SELECT
        seller_id,
        DATE_TRUNC('month', order_purchase_timestamp) AS order_month,
        COUNT(DISTINCT order_id) AS monthly_orders,
        SUM(price) AS monthly_revenue,
        AVG(review_score) AS monthly_avg_review
    FROM vw_order_details
    WHERE seller_id IS NOT NULL
    {date_filter}
    GROUP BY seller_id, DATE_TRUNC('month', order_purchase_timestamp)
    ORDER BY seller_id, order_month
    """

    date_filter = ""
    if start_date and end_date:
        date_filter = f"AND order_purchase_timestamp BETWEEN '{start_date}' AND '{end_date}'"

    query = query.format(date_filter=date_filter)

    return execute_raw_query(query)

@st.cache_data(ttl=3600)
def load_seller_categories(start_date=None, end_date=None):
    query = """
    SELECT
        seller_id,
        product_category_name_english,
        COUNT(DISTINCT order_id) AS order_count,
        SUM(price) AS total_revenue,
        AVG(review_score) AS avg_review
    FROM vw_order_details
    WHERE seller_id IS NOT NULL AND product_category_name_english IS NOT NULL
    {date_filter}
    GROUP BY seller_id, product_category_name_english
    ORDER BY seller_id, SUM(price) DESC
    """

    date_filter = ""
    if start_date and end_date:
        date_filter = f"AND order_purchase_timestamp BETWEEN '{start_date}' AND '{end_date}'"

    query = query.format(date_filter=date_filter)

    return execute_raw_query(query)

@st.cache_data(ttl=3600)
def load_seller_geolocation(start_date=None, end_date=None):
    query = """
    SELECT
        s.seller_id,
        s.seller_city,
        s.seller_state,
        COUNT(DISTINCT od.order_id) AS total_orders,
        SUM(od.price) AS total_revenue,
        AVG(od.review_score) AS avg_review
    FROM vw_order_details od
    JOIN sellers s ON od.seller_id = s.seller_id
    WHERE s.seller_state IS NOT NULL
    {date_filter}
    GROUP BY s.seller_id, s.seller_city, s.seller_state
    ORDER BY SUM(od.price) DESC
    """

    date_filter = ""
    if start_date and end_date:
        date_filter = f"AND od.order_purchase_timestamp BETWEEN '{start_date}' AND '{end_date}'"

    query = query.format(date_filter=date_filter)

    return execute_raw_query(query)

@st.cache_data(ttl=3600)
def load_date_range():
    return execute_query("date_range.sql")

# Constantes pour les graphiques
graph_height = 400
heatmap_height = 600


with st.sidebar:
    st.markdown('<h2 style="text-align: center; padding-bottom: 10px;">FILTRES</h2>', unsafe_allow_html=True)

    # Section PÉRIODE
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown('<div class="filter-section-title">PÉRIODE</div>', unsafe_allow_html=True)

    # Votre code existant pour les dates
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

    # Fermer la div de la section période
    st.markdown('</div>', unsafe_allow_html=True)

    # Convertir les dates en format string pour les requêtes SQL si nécessaire
    sql_start_date = start_date.strftime('%Y-%m-%d') if start_date else None
    sql_end_date = end_date.strftime('%Y-%m-%d') if end_date else None

    # Filtre de performance
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown('<div class="filter-section-title">Performances</div>', unsafe_allow_html=True)
    performance_categories = ["Elite", "High Performer", "Good", "Average", "Needs Improvement"]
    selected_performance = st.multiselect(
        "Catégories de performance",
        options=performance_categories,
        default=performance_categories
    )
    # Fermer la div de la section performance
    st.markdown('</div>', unsafe_allow_html=True)

    # Nombre minimum de commandes
    min_orders = st.slider(
        "Nombre minimum de commandes",
        min_value=5,
        max_value=100,
        value=10,
        step=5
    )

# Création d'une layout compact pour tout le dashboard
layout_container = st.container()



with layout_container:
    # Métriques générales
    col1, col2, col3, col4 = st.columns(4)

    try:
        # Charger les données avec les filtres appliqués
        seller_data = load_seller_performance(sql_start_date, sql_end_date)

        # Filtrer par catégorie de performance
        if selected_performance and len(selected_performance) > 0:
            seller_data = seller_data[seller_data["performance_category"].isin(selected_performance)]

        # Filtrer par nombre minimum de commandes
        seller_data = seller_data[seller_data["total_orders"] >= min_orders]


        if not seller_data.empty:
            with col1:
                st.markdown(
                    f"""
                    <div class='metric-card metric-card-customers'>
                        <div class='metric-label'>Nombre de vendeurs</div>
                        <div class='metric-value'>{format(len(seller_data), ',')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col2:
                st.markdown(
                    f"""
                    <div class='metric-card metric-card-spend'>
                        <div class='metric-label'>Revenu total</div>
                        <div class='metric-value'>{format_currency(seller_data['total_revenue'].sum())}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col3:
                st.markdown(
                    f"""
                    <div class='metric-card metric-card-frequency'>
                        <div class='metric-label'>Note moyenne</div>
                        <div class='metric-value'>{seller_data['avg_review'].mean():.2f}/5</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col4:
                st.markdown(
                    f"""
                    <div class='metric-card metric-card-clv'>
                        <div class='metric-label'>Livraison à temps</div>
                        <div class='metric-value'>{seller_data['on_time_delivery_percentage'].mean():.1f}%</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.warning("Aucune donnée de vendeur disponible pour les filtres sélectionnés.")
    except Exception as e:
        st.error(f"Erreur lors du chargement des métriques générales: {e}")


   # Tableau de performance des vendeurs
    st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
    st.markdown("<h3>Performance des vendeurs</h3>", unsafe_allow_html=True)
    try:
        if not seller_data.empty:
            # Ajouter un sélecteur pour l'ordre de tri
            sort_options = {
                "total_orders": "Nombre de commandes",
                "total_revenue": "Revenu total",
                "avg_review": "Note moyenne",
                "on_time_delivery_percentage": "% Livraison à temps",
                "positive_review_percentage": "% Avis positifs"
            }

            # Créer deux colonnes pour les options de tri
            col1, col2 = st.columns([3, 1])

            with col1:
                selected_sort = st.selectbox(
                    "Trier par:",
                    options=list(sort_options.keys()),
                    format_func=lambda x: sort_options[x],
                    index=1  # Par défaut, tri par revenu total
                )

            with col2:
                sort_order = st.radio(
                    "Ordre:",
                    options=["Décroissant", "Croissant"],
                    horizontal=True,
                    index=0  # Par défaut, tri décroissant
                )

            # Définir l'ordre de tri (True pour croissant, False pour décroissant)
            ascending = sort_order == "Croissant"

            # Trier le DataFrame selon la colonne sélectionnée et l'ordre choisi
            seller_data = seller_data.sort_values(by=selected_sort, ascending=ascending)

            # Limiter le nombre de lignes pour l'affichage
            display_limit = st.slider("Nombre de vendeurs à afficher", 10, 100, 20)
            display_df = seller_data.head(display_limit)

            # Dupliquer le DataFrame pour conserver les valeurs numériques pour le style
            numeric_df = display_df.copy()

            # Sélectionner les colonnes à afficher
            columns_to_display = [
                "seller_id", "total_orders", "total_revenue", "unique_products",
                "avg_review", "on_time_delivery_percentage", "positive_review_percentage",
                "performance_category"
            ]

            numeric_df = numeric_df[columns_to_display]

            # Appliquer le style au DataFrame avec une seule palette de couleur (Bleu)
            styled_df = numeric_df.style\
                .background_gradient(subset=["total_orders", "total_revenue", "avg_review",
                                            "on_time_delivery_percentage", "positive_review_percentage"], cmap="Blues")\
                .applymap(lambda _: "background-color: lightgrey;", subset=["seller_id", "unique_products", "performance_category"])\
                .applymap(lambda _: "color: black;", subset=["seller_id", "unique_products", "performance_category"])\
                .format({
                    "total_revenue": "R$ {:.2f}",
                    "avg_review": "{:.2f}",
                    "on_time_delivery_percentage": "{:.1f}%",
                    "positive_review_percentage": "{:.1f}%"
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
            html_table = html_table.replace('>seller_id<', '>ID Vendeur<')
            html_table = html_table.replace('>total_orders<', '>Commandes<')
            html_table = html_table.replace('>total_revenue<', '>Revenu total<')
            html_table = html_table.replace('>unique_products<', '>Produits uniques<')
            html_table = html_table.replace('>avg_review<', '>Note moyenne<')
            html_table = html_table.replace('>on_time_delivery_percentage<', '>% Livraison à temps<')
            html_table = html_table.replace('>positive_review_percentage<', '>% Avis positifs<')
            html_table = html_table.replace('>performance_category<', '>Catégorie<')

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
            csv = seller_data.to_csv(index=False)
            st.download_button(
                label="📥 Télécharger les données (CSV)",
                data=csv,
                file_name="olist_seller_performance.csv",
                mime="text/csv",
                help="Télécharger les données de performance des vendeurs au format CSV"
            )
        else:
            st.warning("Aucune donnée de vendeur disponible pour les filtres sélectionnés.")
    except Exception as e:
        st.error(f"Erreur lors de l'affichage du tableau de performance: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

    # Distribution des vendeurs par catégorie de performance
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
        st.markdown("<h3>Distribution des vendeurs par catégorie de performance</h3>", unsafe_allow_html=True)
        st.markdown("<div style='height: 84px;'></div>", unsafe_allow_html=True)
        try:
            if not seller_data.empty:
                # Compter les vendeurs par catégorie
                performance_counts = seller_data["performance_category"].value_counts().reset_index()
                performance_counts.columns = ["performance_category", "count"]

                # Définir l'ordre des catégories
                category_order = ["Elite", "High Performer", "Good", "Average", "Needs Improvement"]

                # Créer un DataFrame avec toutes les catégories (même celles sans vendeurs)
                all_categories = pd.DataFrame({"performance_category": category_order})
                performance_counts = pd.merge(all_categories, performance_counts, on="performance_category", how="left").fillna(0)

                # Ordonner selon l'ordre défini
                performance_counts["performance_category"] = pd.Categorical(
                    performance_counts["performance_category"],
                    categories=category_order,
                    ordered=True
                )
                performance_counts = performance_counts.sort_values("performance_category")

                # Définir une palette de couleurs
                colors = {
                    "Elite": "#1a9850",
                    "High Performer": "#91cf60",
                    "Good": "#d9ef8b",
                    "Average": "#fee08b",
                    "Needs Improvement": "#fc4e2a"
                }

                # Créer le graphique
                fig = px.bar(
                    performance_counts,
                    x="performance_category",
                    y="count",
                    color="performance_category",
                    labels={"performance_category": "Catégorie de performance", "count": "Nombre de vendeurs"},
                    color_discrete_map=colors,
                    text='count'  # Afficher le texte des valeurs sur les barres
                )

                # Mettre à jour la mise en page
                fig.update_layout(
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    font=dict(family="Arial, sans-serif", size=12, color="black"),
                    xaxis=dict(
                        title=dict(text="Catégorie de performance", font=dict(color="black", size=12)),
                        tickfont=dict(color="black", size=12)
                    ),
                    yaxis=dict(
                        title=dict(text="Nombre de vendeurs", font=dict(color="black", size=12)),
                        tickfont=dict(color="black", size=12),
                        showticklabels=False,  # Cacher les étiquettes des ticks pour l'axe Y
                        gridcolor='lightgray',  # Couleur de la grille horizontale
                    ),
                    showlegend=False,
                    height=graph_height,
                    margin=dict(l=10, r=10, t=30, b=10)
                )

                # Configurer l'apparence des barres pour mettre le texte à l'intérieur
                fig.update_traces(
                    texttemplate='%{text}',  # Format du texte
                    textposition='inside',    # Position du texte à l'intérieur des barres
                    textfont=dict(size=12, color='black'),  # Police pour le texte
                )


                # Configurer les axes pour n'avoir que des lignes de grille horizontales
                fig.update_xaxes(showgrid=False)  # Désactiver la grille verticale
                fig.update_yaxes(showgrid=True)   # Activer la grille horizontale

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Aucune donnée disponible pour l'affichage de la distribution.")
        except Exception as e:
            st.error(f"Erreur lors de l'affichage de la distribution des vendeurs: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
        st.markdown("<h3>Distribution des métriques selon les performances</h3>", unsafe_allow_html=True)
        try:
            if not seller_data.empty:
                # Sélectionner les colonnes pour le box plot
                metrics_to_plot = st.selectbox(
                    "Sélectionner une métrique",
                    options=["avg_review", "on_time_delivery_percentage", "positive_review_percentage"],
                    format_func=lambda x: {
                        "avg_review": "Note moyenne",
                        "on_time_delivery_percentage": "% Livraison à temps",
                        "positive_review_percentage": "% Avis positifs"
                    }[x]
                )

                # Créer un DataFrame pour le box plot
                plot_data = seller_data[["performance_category", metrics_to_plot]].copy()

                # Définir l'ordre des catégories
                category_order = ["Elite", "High Performer", "Good", "Average", "Needs Improvement"]
                plot_data["performance_category"] = pd.Categorical(
                    plot_data["performance_category"],
                    categories=category_order,
                    ordered=True
                )

                # Créer le box plot
                fig = px.box(
                    plot_data.sort_values("performance_category"),
                    x="performance_category",
                    y=metrics_to_plot,
                    color="performance_category",
                    labels={
                        "performance_category": "Catégorie de performance",
                        metrics_to_plot: {
                            "avg_review": "Note moyenne",
                            "on_time_delivery_percentage": "% Livraison à temps",
                            "positive_review_percentage": "% Avis positifs"
                        }[metrics_to_plot]
                    },
                    color_discrete_sequence=px.colors.sequential.Blues_r
                )

                fig.update_layout(
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    font=dict(family="Arial, sans-serif", size=12, color="black"),
                    xaxis=dict(
                        title=dict(text="Catégorie de performance", font=dict(color="black", size=12)),
                        tickfont=dict(color="black", size=12)
                    ),
                    yaxis=dict(
                        title=dict(text={
                            "avg_review": "Note moyenne",
                            "on_time_delivery_percentage": "% Livraison à temps",
                            "positive_review_percentage": "% Avis positifs"
                        }[metrics_to_plot], font=dict(color="black", size=12)),
                        tickfont=dict(color="black", size=12),
                        gridcolor='lightgray',
                    ),
                    showlegend=False,
                    height=graph_height,
                    margin=dict(l=10, r=10, t=30, b=10)
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Aucune donnée disponible pour l'affichage du box plot.")
        except Exception as e:
            st.error(f"Erreur lors de l'affichage du box plot: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

   # Graphiques de tendances et distribution
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
        st.markdown("<h3>Distribution des vendeurs par métrique</h3>", unsafe_allow_html=True)
        st.markdown("<div style='height: 84px;'></div>", unsafe_allow_html=True)
        try:
            if not seller_data.empty:
                # Sélection de la métrique à afficher
                hist_metric = st.selectbox(
                    "Sélectionner une métrique pour l'histogramme",
                    options=["total_revenue", "avg_review", "on_time_delivery_percentage"],
                    format_func=lambda x: {
                        "total_revenue": "Revenu total",
                        "avg_review": "Note moyenne",
                        "on_time_delivery_percentage": "% Livraison à temps"
                    }[x]
                )

                # Créer l'histogramme
                fig = px.histogram(
                    seller_data,
                    x=hist_metric,
                    color="performance_category",
                    labels={
                        hist_metric: {
                            "total_revenue": "Revenu total (R$)",
                            "avg_review": "Note moyenne",
                            "on_time_delivery_percentage": "% Livraison à temps"
                        }[hist_metric],
                        "performance_category": "Catégorie de performance"
                    },
                    color_discrete_sequence=px.colors.qualitative.Set1
                )

                fig.update_layout(
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    font=dict(family="Arial, sans-serif", size=12, color="black"),
                    xaxis=dict(
                        title=dict(text={
                            "total_revenue": "Revenu total (R$)",
                            "avg_review": "Note moyenne",
                            "on_time_delivery_percentage": "% Livraison à temps"
                        }[hist_metric], font=dict(color="black", size=12)),
                        tickfont=dict(color="black", size=12)
                    ),
                    yaxis=dict(
                        title=dict(text="Nombre de vendeurs", font=dict(color="black", size=12)),
                        tickfont=dict(color="black", size=12),
                        gridcolor='lightgray',
                    ),
                    legend=dict(
                        font=dict(color="black", size=12),
                        title=dict(text="Catégorie de performance", font=dict(color="black", size=12))
                    ),
                    height=graph_height,
                    margin=dict(l=10, r=10, t=30, b=10),
                    bargap=0.1
                )

                # Assurer que les annotations et textes à l'intérieur du graphique sont en noir
                for annotation in fig.layout.annotations:
                    annotation.font.color = "black"

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Aucune donnée disponible pour l'affichage de l'histogramme.")
        except Exception as e:
            st.error(f"Erreur lors de l'affichage de l'histogramme: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
        st.markdown("<h3>Corrélation entre les métriques de performance</h3>", unsafe_allow_html=True)
        try:
            if not seller_data.empty:
                # Sélection des métriques pour le scatter plot
                scatter_x = st.selectbox(
                    "Axe X",
                    options=["total_revenue", "avg_review", "on_time_delivery_percentage"],
                    format_func=lambda x: {
                        "total_revenue": "Revenu total",
                        "avg_review": "Note moyenne",
                        "on_time_delivery_percentage": "% Livraison à temps"
                    }[x],
                    index=0
                )

                scatter_y = st.selectbox(
                    "Axe Y",
                    options=["total_revenue", "avg_review", "on_time_delivery_percentage"],
                    format_func=lambda x: {
                        "total_revenue": "Revenu total",
                        "avg_review": "Note moyenne",
                        "on_time_delivery_percentage": "% Livraison à temps"
                    }[x],
                    index=1
                )

                # Création du scatter plot
                fig = px.scatter(
                    seller_data,
                    x=scatter_x,
                    y=scatter_y,
                    color="performance_category",
                    size="total_orders",
                    hover_data=["seller_id", "total_orders", "avg_review"],
                    labels={
                        scatter_x: {
                            "total_revenue": "Revenu total (R$)",
                            "avg_review": "Note moyenne",
                            "on_time_delivery_percentage": "% Livraison à temps"
                        }[scatter_x],
                        scatter_y: {
                            "total_revenue": "Revenu total (R$)",
                            "avg_review": "Note moyenne",
                            "on_time_delivery_percentage": "% Livraison à temps"
                        }[scatter_y],
                        "performance_category": "Catégorie de performance",
                        "total_orders": "Nombre de commandes"
                    },
                    color_discrete_sequence=px.colors.qualitative.Set1
                )

                fig.update_layout(
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    font=dict(family="Arial, sans-serif", size=12, color="black"),
                    xaxis=dict(
                        title=dict(text={
                            "total_revenue": "Revenu total (R$)",
                            "avg_review": "Note moyenne",
                            "on_time_delivery_percentage": "% Livraison à temps"
                        }[scatter_x], font=dict(color="black", size=12)),
                        tickfont=dict(color="black", size=12)
                    ),
                    yaxis=dict(
                        title=dict(text={
                            "total_revenue": "Revenu total (R$)",
                            "avg_review": "Note moyenne",
                            "on_time_delivery_percentage": "% Livraison à temps"
                        }[scatter_y], font=dict(color="black", size=12)),
                        tickfont=dict(color="black", size=12),
                        gridcolor='lightgray',
                    ),
                    legend=dict(
                        font=dict(color="black", size=12),
                        title=dict(text="Catégorie de performance", font=dict(color="black", size=12))
                    ),
                    height=graph_height,
                    margin=dict(l=10, r=10, t=30, b=10)
                )

                # Assurer que les annotations et textes à l'intérieur du graphique sont en noir
                for annotation in fig.layout.annotations:
                    annotation.font.color = "black"

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Aucune donnée disponible pour l'affichage du scatter plot.")
        except Exception as e:
            st.error(f"Erreur lors de l'affichage du scatter plot: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

    # Analyse géographique
    st.markdown("<h2>Analyse géographique</h2>", unsafe_allow_html=True)
    st.markdown("<h3>Répartition géographique des vendeurs</h3>", unsafe_allow_html=True)

    try:
        # Charger les données géographiques
        seller_geo = load_seller_geolocation(sql_start_date, sql_end_date)

        if not seller_geo.empty:
            # Ajouter un sélecteur de métriques avant la création de la carte
            selected_metric = st.selectbox(
                "Choisissez la métrique à visualiser sur la carte:",
                ["total_orders", "total_revenue", "avg_review", "seller_count"],
                format_func=lambda x: {
                    "total_orders": "Total des commandes",
                    "total_revenue": "Revenu total (R$)",
                    "avg_review": "Note moyenne des vendeurs",
                    "seller_count": "Nombre de vendeurs"
                }[x]
            )

            # Agrégation par état
            state_data = seller_geo.groupby("seller_state").agg({
                "total_orders": "sum",
                "total_revenue": "sum",
                "avg_review": "mean",
                "seller_id": "nunique"
            }).reset_index()

            state_data = state_data.rename(columns={
                "seller_id": "seller_count"
            })

            # Coordonnées approximatives des états brésiliens
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
            state_data["lat"] = state_data["seller_state"].apply(lambda x: state_coordinates.get(x, [0, 0])[0])
            state_data["lon"] = state_data["seller_state"].apply(lambda x: state_coordinates.get(x, [0, 0])[1])

            # Créer une carte avec des marqueurs de taille proportionnelle
            fig = px.scatter_mapbox(
                state_data,
                lat="lat",
                lon="lon",
                size=selected_metric,
                color=selected_metric,
                hover_name="seller_state",
                hover_data=["seller_count", "total_orders", "total_revenue", "avg_review"],
                zoom=3,
                height=heatmap_height,
                size_max=50,
                color_continuous_scale=px.colors.sequential.Viridis,
                mapbox_style="carto-positron",
                labels={
                    "seller_state": "État",
                    "seller_count": "Nombre de vendeurs",
                    "total_orders": "Total des commandes",
                    "total_revenue": "Revenu total (R$)",
                    "avg_review": "Note moyenne"
                }
            )

            # Définir une taille minimale pour tous les marqueurs
            fig.update_traces(marker=dict(sizemin=10))

            fig.update_layout(
                margin={"r":0,"t":0,"l":0,"b":0},
                mapbox=dict(
                    center=dict(lat=-15, lon=-55),  # Centre de la carte sur le Brésil
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

            # Ajouter un tableau des top états
            st.markdown("<h4>Top 5 états par performance</h4>", unsafe_allow_html=True)
            try:
                if not state_data.empty:
                    # Ajouter des options de tri pour le tableau
                    sort_options = {
                        "seller_count": "Nombre de vendeurs",
                        "total_orders": "Nombre de commandes",
                        "total_revenue": "Revenu total",
                        "avg_review": "Note moyenne"
                    }

                    # Créer deux colonnes pour les options de tri
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        selected_sort = st.selectbox(
                            "Trier par:",
                            options=list(sort_options.keys()),
                            format_func=lambda x: sort_options[x],
                            index=2,  # Par défaut, tri par revenu total
                            key="state_sort_column"
                        )

                    with col2:
                        sort_order = st.radio(
                            "Ordre:",
                            options=["Décroissant", "Croissant"],
                            horizontal=True,
                            index=0,  # Par défaut, tri décroissant
                            key="state_sort_order"
                        )

                    # Définir l'ordre de tri (True pour croissant, False pour décroissant)
                    ascending = sort_order == "Croissant"

                    # Trier selon la colonne et l'ordre choisis
                    top_states = state_data.sort_values(by=selected_sort, ascending=ascending).head(5)

                    # Supprimer les colonnes lat et lon du DataFrame affiché
                    if "lat" in top_states.columns:
                        top_states = top_states.drop(columns=["lat", "lon"])

                    # Dupliquer le DataFrame pour conserver les valeurs numériques pour le style
                    numeric_df = top_states.copy()

                    # Sélectionner les colonnes à afficher
                    columns_to_display = [
                        "seller_state", "seller_count", "total_orders",
                        "total_revenue", "avg_review"
                    ]

                    numeric_df = numeric_df[columns_to_display]

                    # Appliquer le style au DataFrame avec une seule palette de couleur (Bleu)
                    styled_df = numeric_df.style\
                        .background_gradient(subset=["seller_count", "total_orders", "total_revenue", "avg_review"], cmap="Blues")\
                        .applymap(lambda _: "background-color: lightgrey;", subset=["seller_state"])\
                        .applymap(lambda _: "color: black;", subset=["seller_state"])\
                        .format({
                            "total_revenue": "R$ {:.2f}",
                            "avg_review": "{:.2f}"
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
                    html_table = html_table.replace('>seller_state<', '>État<')
                    html_table = html_table.replace('>seller_count<', '>Nb. vendeurs<')
                    html_table = html_table.replace('>total_orders<', '>Commandes<')
                    html_table = html_table.replace('>total_revenue<', '>Revenu total<')
                    html_table = html_table.replace('>avg_review<', '>Note moyenne<')

                    # Ajouter le CSS pour le style du tableau
                    st.markdown("""
                    <style>
                    .states-table {
                        max-height: 300px;
                        overflow-y: auto;
                        display: block;
                    }
                    .states-table table {
                        width: 100%;
                    }
                    </style>
                    """, unsafe_allow_html=True)

                    # Envelopper le tableau dans un div avec défilement
                    st.markdown(f'<div class="states-table">{html_table}</div>', unsafe_allow_html=True)
                else:
                    st.warning("Aucune donnée d'états disponible pour les filtres sélectionnés.")
            except Exception as e:
                st.error(f"Erreur lors de l'affichage du tableau des top états: {e}")
        else:
            st.warning("Aucune donnée géographique disponible pour la période sélectionnée.")

    except Exception as e:
        st.error(f"Erreur lors du chargement des données géographiques: {e}")

    # Tendances temporelles
    st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
    st.markdown("<h3>Tendances de performance dans le temps</h3>", unsafe_allow_html=True)
    try:
        # Charger les données de tendances
        trends_data = load_seller_trends(sql_start_date, sql_end_date)

        if not trends_data.empty:
            # Filtrer pour n'inclure que les vendeurs dans notre sélection
            trends_data = trends_data[trends_data["seller_id"].isin(seller_data["seller_id"])]

            # Agréger par mois
            monthly_trends = trends_data.groupby("order_month").agg({
                "monthly_orders": "sum",
                "monthly_revenue": "sum",
                "monthly_avg_review": "mean",
                "seller_id": "nunique"
            }).reset_index()

            monthly_trends = monthly_trends.rename(columns={
                "seller_id": "active_sellers"
            })

            # Créer des onglets pour différents graphiques de tendances
            trend_tabs = st.tabs(["Revenu", "Commandes", "Notes", "Vendeurs actifs"])

            with trend_tabs[0]:
                # Graphique de revenu mensuel
                fig = px.line(
                    monthly_trends,
                    x="order_month",
                    y="monthly_revenue",
                    markers=True,
                    labels={
                        "order_month": "Mois",
                        "monthly_revenue": "Revenu mensuel (R$)"
                    }
                )

                fig.update_layout(
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    font=dict(family="Arial, sans-serif", size=12, color="black"),
                    xaxis=dict(
                        title=dict(text="Mois", font=dict(color="black", size=12)),
                        tickfont=dict(color="black", size=12)
                    ),
                    yaxis=dict(
                        title=dict(text="Revenu mensuel (R$)", font=dict(color="black", size=12)),
                        tickfont=dict(color="black", size=12),
                        gridcolor='lightgray',
                    ),
                    height=graph_height,
                    margin=dict(l=10, r=10, t=30, b=10)
                )

                st.plotly_chart(fig, use_container_width=True)

            with trend_tabs[1]:
                # Graphique de commandes mensuelles
                fig = px.line(
                    monthly_trends,
                    x="order_month",
                    y="monthly_orders",
                    markers=True,
                    labels={
                        "order_month": "Mois",
                        "monthly_orders": "Nombre de commandes"
                    }
                )

                fig.update_layout(
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    font=dict(family="Arial, sans-serif", size=12, color="black"),
                    xaxis=dict(
                        title=dict(text=" ", font=dict(color="black", size=10)),
                        tickfont=dict(color="black", size=12)
                    ),
                    yaxis=dict(
                        title=dict(text="Nombre de commandes", font=dict(color="black", size=12)),
                        tickfont=dict(color="black", size=12),
                        gridcolor='lightgray',
                    ),
                    height=graph_height,
                    margin=dict(l=10, r=10, t=30, b=10)
                )

                st.plotly_chart(fig, use_container_width=True)

            with trend_tabs[2]:
                # Graphique de notes moyennes mensuelles
                fig = px.line(
                    monthly_trends,
                    x="order_month",
                    y="monthly_avg_review",
                    markers=True,
                    labels={
                        "order_month": "Mois",
                        "monthly_avg_review": "Note moyenne"
                    }
                )

                fig.update_layout(
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    font=dict(family="Arial, sans-serif", size=12, color="black"),
                    xaxis=dict(
                        title=dict(text=" ", font=dict(color="black", size=12)),
                        tickfont=dict(color="black", size=12)
                    ),
                    yaxis=dict(
                        title=dict(text="Note moyenne", font=dict(color="black", size=12)),
                        tickfont=dict(color="black", size=12),
                        gridcolor='lightgray',
                        range=[1, 5]
                    ),
                    height=graph_height,
                    margin=dict(l=10, r=10, t=30, b=10)
                )

                st.plotly_chart(fig, use_container_width=True)

            with trend_tabs[3]:
                # Graphique de vendeurs actifs par mois
                fig = px.line(
                    monthly_trends,
                    x="order_month",
                    y="active_sellers",
                    markers=True,
                    labels={
                        "order_month": "Mois",
                        "active_sellers": "Vendeurs actifs"
                    }
                )

                fig.update_layout(
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    font=dict(family="Arial, sans-serif", size=12, color="black"),
                    xaxis=dict(
                        title=dict(text=" ", font=dict(color="black", size=12)),
                        tickfont=dict(color="black", size=12),
                        gridcolor='lightgray',
                    ),
                    yaxis=dict(
                        title=dict(text="Vendeurs actifs", font=dict(color="black", size=12)),
                        tickfont=dict(color="black", size=12),
                        gridcolor='lightgray',
                    ),
                    height=graph_height,
                    margin=dict(l=10, r=10, t=30, b=10)
                )

                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Aucune donnée de tendance disponible pour les filtres sélectionnés.")
    except Exception as e:
        st.error(f"Erreur lors de l'affichage des tendances temporelles: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

    # Analyse par catégorie de produit
    st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
    st.markdown("<h3>Performance par Catégorie de Produit</h3>", unsafe_allow_html=True)
    try:
        # Charger les données de catégories
        category_data = load_seller_categories(sql_start_date, sql_end_date)

        if not category_data.empty:
            # Filtrer pour n'inclure que les vendeurs dans notre sélection
            category_data = category_data[category_data["seller_id"].isin(seller_data["seller_id"])]

            # Dictionnaire de traduction français-anglais pour les catégories
            category_translations = {
                "produits_pour_maison": "home_products",
                "meubles_decoration": "furniture_decor",
                "informatique_accessoires": "computers_accessories",
                "telephonie": "telephony",
                "electromenager": "appliances",
                "sport_loisirs": "sports_leisure",
                "sante_beaute": "health_beauty",
                "cuisine_arts_table": "kitchen_dining",
                "outils_bricolage": "tools_home_improvement",
                "jouets": "toys",
                "mode_accessoires": "fashion_accessories",
                "articles_bebes": "baby_products",
                "livres_papeterie": "books_stationery",
                "jardin_exterieur": "garden_outdoor",
                "animalerie": "pet_supplies"
                # Ajoutez d'autres catégories au besoin
            }

            # Traduire les noms de catégories
            category_data["product_category_name_english"] = category_data["product_category_name_english"]

            # Agréger par catégorie
            category_agg = category_data.groupby("product_category_name_english").agg({
                "order_count": "sum",
                "total_revenue": "sum",
                "avg_review": "mean",
                "seller_id": pd.Series.nunique
            }).reset_index()

            category_agg = category_agg.rename(columns={
                "seller_id": "seller_count"
            })

            # Trier par revenu total
            category_agg = category_agg.sort_values("total_revenue", ascending=False)

            # Limiter aux 15 principales catégories
            top_categories = category_agg.head(15)

            # Créer deux onglets pour les graphiques de catégories
            cat_tabs = st.tabs(["Revenu par catégorie", "Nombre de vendeurs par catégorie"])


            with cat_tabs[0]:
                # Graphique de revenu par catégorie
                fig = px.bar(
                    top_categories,
                    x="product_category_name_english",  # Gardé tel quel pour utiliser les noms de catégories en anglais
                    y="total_revenue",
                    color="avg_review",
                    color_continuous_scale="RdYlGn",
                    hover_data=["order_count", "seller_count", "avg_review"],
                    labels={
                        "product_category_name_english": "Catégorie de produit",
                        "total_revenue": "Revenu total (R$)",
                        "order_count": "Nombre de commandes",
                        "seller_count": "Nombre de vendeurs",
                        "avg_review": "Note moyenne"
                    }
                )

                fig.update_layout(
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    font=dict(family="Arial, sans-serif", size=12, color="black"),
                    xaxis=dict(
                        title=dict(text="Catégorie de produit", font=dict(color="black", size=12)),
                        tickfont=dict(color="black", size=12),
                        tickangle=45
                    ),
                    yaxis=dict(
                        title=dict(text="Revenu total (R$)", font=dict(color="black", size=12)),
                        tickfont=dict(color="black", size=12),
                        gridcolor='lightgray',
                    ),
                    height=graph_height,
                    margin=dict(l=10, r=10, t=30, b=30),
                    legend=dict(font=dict(color="black", size=12))
                )
                # Supprimer la barre de couleur
                fig.update_layout(coloraxis_showscale=False)

                # S'assurer que toutes les annotations et textes sont en noir
                for annotation in fig.layout.annotations:
                    annotation.font.color = "black"

                st.plotly_chart(fig, use_container_width=True)

            with cat_tabs[1]:
                # Graphique du nombre de vendeurs par catégorie
                fig = px.bar(
                    top_categories,
                    x="product_category_name_english",  # Gardé tel quel pour utiliser les noms de catégories en anglais
                    y="seller_count",
                    color="avg_review",
                    color_continuous_scale="RdYlGn",
                    hover_data=["order_count", "total_revenue", "avg_review"],
                    labels={
                        "product_category_name_english": "Catégorie de produit",
                        "seller_count": "Nombre de vendeurs",
                        "order_count": "Nombre de commandes",
                        "total_revenue": "Revenu total (R$)",
                        "avg_review": "Note moyenne"
                    }
                )

                fig.update_layout(
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    font=dict(family="Arial, sans-serif", size=12, color="black"),
                    xaxis=dict(
                        title=dict(text="Catégorie de produit", font=dict(color="black", size=12)),
                        tickfont=dict(color="black", size=12),
                        tickangle=45
                    ),
                    yaxis=dict(
                        title=dict(text="Nombre de vendeurs", font=dict(color="black", size=12)),
                        tickfont=dict(color="black", size=12),
                        gridcolor='lightgray',
                    ),
                    height=graph_height,
                    margin=dict(l=10, r=10, t=30, b=30),
                    legend=dict(font=dict(color="black", size=12))
                )
                # Supprimer la barre de couleur
                fig.update_layout(coloraxis_showscale=False)

                # S'assurer que toutes les annotations et textes sont en noir
                for annotation in fig.layout.annotations:
                    annotation.font.color = "black"

                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No category data available for the selected filters.")
    except Exception as e:
        st.error(f"Error while displaying category data: {e}")
st.markdown("</div>", unsafe_allow_html=True)

# Footer avec information sur les données
st.markdown("""
<div class="footer">
    <p>Dashboard d'analyse des vendeurs Olist - Données issues de la base de données Olist</p>
    <p>Période analysée: {start} - {end}</p>
</div>
""".format(
    start=start_date.strftime('%d/%m/%Y') if start_date else "Début des données",
    end=end_date.strftime('%d/%m/%Y') if end_date else "Fin des données"
), unsafe_allow_html=True)
