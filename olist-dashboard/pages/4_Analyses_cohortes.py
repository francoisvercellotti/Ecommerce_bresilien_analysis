import sys
import os

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.database import execute_query, execute_raw_query
from datetime import datetime, timedelta

# Configuration de la page
st.set_page_config(
    page_title="Olist - Analyse des Cohortes",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"  # Barre latérale visible par défaut
)

st.markdown("""
    <div style="background: linear-gradient(90deg, #4e8df5, #83b3f7); padding:15px; border-radius:10px; margin-bottom:30px">
        <h1 style="color:white; text-align:center; font-size:48px; font-weight:bold">
            ANALYSE DES COHORTES ET SEGMENTATION RFM
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
            font-size: 1.25rem;
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

# Fonction pour charger les dates min et max - version corrigée cohérente avec le deuxième fichier
@st.cache_data(ttl=3600)
def load_date_range():
    return execute_query("date_range.sql")

# Chargement des données de cohortes
@st.cache_data(ttl=3600)
def load_cohort_data(start_date=None, end_date=None, months_limit=6):
    query = """
    WITH first_purchases AS (
        SELECT
            c.customer_unique_id,
            MIN(o.order_purchase_timestamp) AS first_purchase_date,
            DATE_TRUNC('month', MIN(o.order_purchase_timestamp)) AS cohort_month
        FROM orders o
        JOIN customers c
          ON o.customer_id = c.customer_id
        WHERE 1=1
        {date_filter}
        GROUP BY c.customer_unique_id
    ),
    customer_activity AS (
        SELECT
            fp.customer_unique_id,
            fp.cohort_month,
            o.order_purchase_timestamp,
            DATE_TRUNC('month', o.order_purchase_timestamp) AS order_month,
            EXTRACT(YEAR FROM o.order_purchase_timestamp) - EXTRACT(YEAR FROM fp.cohort_month) AS year_diff,
            EXTRACT(MONTH FROM o.order_purchase_timestamp) - EXTRACT(MONTH FROM fp.cohort_month)
              + (EXTRACT(YEAR FROM o.order_purchase_timestamp) - EXTRACT(YEAR FROM fp.cohort_month)) * 12 AS month_number,
            SUM(oi.price) AS order_value
        FROM first_purchases fp
        JOIN customers c
          ON fp.customer_unique_id = c.customer_unique_id
        JOIN orders o
          ON c.customer_id = o.customer_id
        JOIN order_items oi
          ON o.order_id = oi.order_id
        GROUP BY
            fp.customer_unique_id,
            fp.cohort_month,
            o.order_purchase_timestamp,
            DATE_TRUNC('month', o.order_purchase_timestamp)
    ),
    cohort_size AS (
        SELECT
            cohort_month,
            COUNT(DISTINCT customer_unique_id) AS num_customers
        FROM first_purchases
        GROUP BY cohort_month
    ),
    cohort_retention AS (
        SELECT
            ca.cohort_month,
            ca.month_number,
            COUNT(DISTINCT ca.customer_unique_id) AS num_customers,
            SUM(ca.order_value) AS cohort_revenue
        FROM customer_activity ca
        GROUP BY ca.cohort_month, ca.month_number
    )
    SELECT
        cr.cohort_month,
        cs.num_customers AS original_cohort_size,
        cr.month_number,
        cr.num_customers AS active_customers,
        cr.cohort_revenue,
        ROUND(cr.num_customers::numeric / cs.num_customers * 100, 2) AS retention_rate,
        ROUND(cr.cohort_revenue::numeric / NULLIF(cr.num_customers, 0), 2) AS avg_revenue_per_customer
    FROM cohort_retention cr
    JOIN cohort_size cs
      ON cr.cohort_month = cs.cohort_month
    WHERE cr.month_number <= {months_limit}
    ORDER BY cr.cohort_month, cr.month_number
    """

    date_filter = ""
    if start_date and end_date:
        date_filter = f"AND o.order_purchase_timestamp BETWEEN '{start_date}' AND '{end_date}'"

    query = query.format(date_filter=date_filter, months_limit=months_limit)

    return execute_raw_query(query)

# Fonction pour charger les données RFM
@st.cache_data(ttl=3600)
def load_rfm_segments(start_date=None, end_date=None):
    query = """
    WITH customer_rfm AS (
        -- Calcul des métriques RFM de base
        SELECT
            c.customer_unique_id,
            c.customer_city,
            c.customer_state,
            EXTRACT(EPOCH FROM (
                (SELECT MAX(order_purchase_timestamp) FROM orders) -
                MAX(o.order_purchase_timestamp)
            )) / 86400 AS recency_days,
            COUNT(DISTINCT o.order_id) AS frequency,
            SUM(oi.price) AS monetary_value
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE 1=1
        {date_filter}
        GROUP BY c.customer_unique_id, c.customer_city, c.customer_state
    ),
    rfm_scores AS (
        -- Attribution des scores RFM (1-5, 5 étant le meilleur)
        SELECT
            customer_unique_id,
            customer_city,
            customer_state,
            recency_days,
            frequency,
            monetary_value,
            NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score, -- Récence inversée (plus récent = meilleur score)
            NTILE(5) OVER (ORDER BY frequency) AS f_score,
            NTILE(5) OVER (ORDER BY monetary_value) AS m_score
        FROM customer_rfm
    ),
    rfm_segments AS (
        -- Création des segments basés sur les scores combinés
        SELECT
            customer_unique_id,
            customer_city,
            customer_state,
            recency_days,
            frequency,
            monetary_value,
            r_score,
            f_score,
            m_score,
            CONCAT(r_score, f_score, m_score) AS rfm_score,
            CASE
                WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
                WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
                WHEN r_score >= 3 AND f_score >= 1 AND m_score >= 2 THEN 'Potential Loyalists'
                WHEN r_score >= 4 AND f_score <= 2 AND m_score <= 2 THEN 'New Customers'
                WHEN r_score <= 2 AND f_score >= 4 AND m_score >= 4 THEN 'At Risk Customers'
                WHEN r_score <= 2 AND f_score >= 3 AND m_score >= 3 THEN 'Need Attention'
                WHEN r_score <= 1 AND f_score >= 4 AND m_score >= 4 THEN 'Cannot Lose Them'
                WHEN r_score <= 1 AND f_score <= 2 AND m_score >= 3 THEN 'Hibernating'
                WHEN r_score <= 1 AND f_score <= 1 AND m_score <= 1 THEN 'Lost Customers'
                ELSE 'Others'
            END AS customer_segment
        FROM rfm_scores
    )
    SELECT
        customer_segment,
        COUNT(*) AS customer_count,
        ROUND(COUNT(*)::numeric / SUM(COUNT(*)) OVER () * 100, 2) AS percentage,
        ROUND(AVG(recency_days), 2) AS avg_recency_days,
        ROUND(AVG(frequency), 2) AS avg_frequency,
        ROUND(AVG(monetary_value), 2) AS avg_monetary_value,
        ROUND(SUM(monetary_value), 2) AS total_monetary_value,
        ROUND(SUM(monetary_value) / SUM(SUM(monetary_value)) OVER () * 100, 2) AS revenue_percentage
    FROM rfm_segments
    GROUP BY customer_segment
    ORDER BY revenue_percentage DESC
    """

    date_filter = ""
    if start_date and end_date:
        date_filter = f"AND o.order_purchase_timestamp BETWEEN '{start_date}' AND '{end_date}'"

    query = query.format(date_filter=date_filter)

    return execute_raw_query(query)

# Constantes pour les graphiques
graph_height = 400
heatmap_height = 600


# Filtres dans la sidebar
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

    # Nombre de mois à afficher dans les analyses de cohorte
    months_to_display = st.slider(
        "Nombre de mois à analyser",
        min_value=3,
        max_value=24,
        value=6,
        step=1
    )

    # Choix des cohortes à afficher
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown('<div class="filter-section-title">Cohortes</div>', unsafe_allow_html=True)

    show_all_cohorts = st.checkbox("Afficher toutes les cohortes", value=False)

    if not show_all_cohorts:
        cohort_limit = st.slider(
            "Nombre de cohortes à afficher",
            min_value=3,
            max_value=12,
            value=6,
            step=1
        )
    else:
        cohort_limit = None

# Création d'une layout compact pour tout le dashboard
layout_container = st.container()

with layout_container:
    try:
        # Charger les données de cohortes
        cohort_data = load_cohort_data(sql_start_date, sql_end_date, months_to_display)

        if not cohort_data.empty:
            # Préparation des données pour les graphiques et visualisations
            cohort_data['cohort_month'] = pd.to_datetime(cohort_data['cohort_month'])
            cohort_data['cohort_month_str'] = cohort_data['cohort_month'].dt.strftime('%Y-%m')

            # Filtrer les cohortes si nécessaire
            if not show_all_cohorts and cohort_limit:
                # Obtenir les cohortes uniques
                unique_cohorts = cohort_data['cohort_month_str'].unique()
                if len(unique_cohorts) > cohort_limit:
                    # Prendre les N cohortes les plus récentes
                    selected_cohorts = sorted(unique_cohorts, reverse=True)[:cohort_limit]
                    cohort_data = cohort_data[cohort_data['cohort_month_str'].isin(selected_cohorts)]

            # Calculer les métriques globales
            cohort_metrics = cohort_data[cohort_data['month_number'] == 0].copy()
            total_customers = cohort_metrics['original_cohort_size'].sum()
            avg_retention_1m = cohort_data[cohort_data['month_number'] == 1]['retention_rate'].mean()
            avg_retention_3m = cohort_data[cohort_data['month_number'] == 3]['retention_rate'].mean() if 3 in cohort_data['month_number'].values else 0
            avg_revenue_per_customer = cohort_data[cohort_data['month_number'] == 0]['avg_revenue_per_customer'].mean()

            # Affichage des métriques générales
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown(
                    f"""
                    <div class='metric-card metric-card-customers'>
                        <div class='metric-label'>Total Clients</div>
                        <div class='metric-value'>{format(int(total_customers), ',')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col2:
                st.markdown(
                    f"""
                    <div class='metric-card metric-card-spend'>
                        <div class='metric-label'>Rétention M+1</div>
                        <div class='metric-value'>{avg_retention_1m:.2f}%</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col3:
                st.markdown(
                    f"""
                    <div class='metric-card metric-card-frequency'>
                        <div class='metric-label'>Rétention M+3</div>
                        <div class='metric-value'>{avg_retention_3m:.2f}%</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col4:
                st.markdown(
                    f"""
                    <div class='metric-card metric-card-clv'>
                        <div class='metric-label'>Revenu Moyen M+0</div>
                        <div class='metric-value'>{format_currency(avg_revenue_per_customer)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Options d'affichage des cohortes dans la barre latérale
            st.sidebar.markdown("### Options d'affichage des cohortes")
            display_option = st.sidebar.selectbox(
                "Afficher les cohortes par:",
                [
                    "Chronologie (12 dernières cohortes)",
                    "Mêmes mois sur différentes années",
                    "Trimestriel",
                    "Semestriel",
                    "Annuel"
                ],
                index=0,
                key="display_option_key"
            )

            # Formatage des dates pour affichage plus propre
            cohort_data['cohort_month_str'] = pd.to_datetime(cohort_data['cohort_month']).dt.strftime('%b %Y')
            cohort_data['year'] = pd.to_datetime(cohort_data['cohort_month']).dt.year
            cohort_data['month'] = pd.to_datetime(cohort_data['cohort_month']).dt.month
            cohort_data['month_name'] = pd.to_datetime(cohort_data['cohort_month']).dt.strftime('%b')

            # Préparation des données selon l'option sélectionnée
            if display_option == "Chronologie (12 dernières cohortes)":
                # Correction de l'erreur: utiliser np.sort au lieu de sort_values
                unique_dates = pd.to_datetime(cohort_data['cohort_month'].unique())
                unique_dates_sorted = np.sort(unique_dates)
                latest_cohorts = unique_dates_sorted[-12:]
                filtered_data = cohort_data[pd.to_datetime(cohort_data['cohort_month']).isin(latest_cohorts)]
                pivot_index = 'cohort_month_str'

            elif display_option == "Mêmes mois sur différentes années":
                # Sélection du mois à afficher
                selected_month = st.sidebar.selectbox(
                    "Choisir un mois:",
                    sorted(cohort_data['month_name'].unique()),
                    index=0,
                    key="selected_month_key"
                )
                filtered_data = cohort_data[cohort_data['month_name'] == selected_month]
                pivot_index = 'cohort_month_str'

            elif display_option == "Trimestriel":
                # Ajouter trimestre aux données
                cohort_data['quarter'] = pd.to_datetime(cohort_data['cohort_month']).dt.to_period('Q').astype(str)

                # Sélection des trimestres à afficher
                selected_quarters = st.sidebar.multiselect(
                    "Sélectionner les trimestres:",
                    sorted(cohort_data['quarter'].unique()),
                    default=sorted(cohort_data['quarter'].unique())[-4:],  # Derniers 4 trimestres par défaut
                    key="selected_quarters_key"
                )
                filtered_data = cohort_data[cohort_data['quarter'].isin(selected_quarters)]

                # Agréger les données par trimestre
                pivot_index = 'quarter'

            elif display_option == "Semestriel":
                # Ajouter semestre aux données
                cohort_data['semester'] = pd.to_datetime(cohort_data['cohort_month']).dt.year.astype(str) + '-' + \
                                        ((pd.to_datetime(cohort_data['cohort_month']).dt.month - 1) // 6 + 1).astype(str)

                # Sélection des semestres à afficher
                selected_semesters = st.sidebar.multiselect(
                    "Sélectionner les semestres:",
                    sorted(cohort_data['semester'].unique()),
                    default=sorted(cohort_data['semester'].unique())[-4:],  # Derniers 4 semestres par défaut
                    key="selected_semesters_key"
                )
                filtered_data = cohort_data[cohort_data['semester'].isin(selected_semesters)]

                # Agréger les données par semestre
                pivot_index = 'semester'

            elif display_option == "Annuel":
                # Sélection des années à afficher
                selected_years = st.sidebar.multiselect(
                    "Sélectionner les années:",
                    sorted(cohort_data['year'].unique()),
                    default=sorted(cohort_data['year'].unique())[-3:],  # Dernières 3 années par défaut
                    key="selected_years_key"
                )
                filtered_data = cohort_data[cohort_data['year'].isin(selected_years)]

                # Agréger les données par année
                pivot_index = 'year'
            else:
                filtered_data = cohort_data
                pivot_index = 'cohort_month_str'

            # Préparation des données pour la heatmap selon l'option sélectionnée
            if display_option in ["Trimestriel", "Semestriel", "Annuel"]:
                # Pour la heatmap - Agréger les données par la période sélectionnée
                agg_data = filtered_data.groupby([pivot_index, 'month_number'])['retention_rate'].mean().reset_index()

                # Créer la table pivot pour la heatmap
                heatmap_data = agg_data.pivot_table(
                    index=pivot_index,
                    columns='month_number',
                    values='retention_rate',
                    aggfunc='mean'
                )
            else:
                # Utiliser les données filtrées sans agrégation supplémentaire pour la heatmap
                heatmap_data = filtered_data.pivot_table(
                    index='cohort_month_str',
                    columns='month_number',
                    values='retention_rate',
                    aggfunc='mean'
                )

            # Garantir que l'index est toujours trié chronologiquement
            if display_option == "Chronologie (12 dernières cohortes)":
                # Corriger le tri des dates
                cohort_order = pd.to_datetime(filtered_data['cohort_month'].unique())
                cohort_order_sorted = np.sort(cohort_order)
                cohort_order_str = [pd.to_datetime(d).strftime('%b %Y') for d in cohort_order_sorted]
                heatmap_data = heatmap_data.reindex(cohort_order_str)

            # Créer une heatmap de rétention
            st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
            st.markdown("<h3>Heatmap de Rétention par Cohorte (%)</h3>", unsafe_allow_html=True)

            # Création de la heatmap avec Plotly
            fig_heatmap = px.imshow(
                heatmap_data,
                labels=dict(x="Mois après acquisition", y="Cohorte", color="Taux de rétention (%)"),
                x=list(heatmap_data.columns),
                y=heatmap_data.index,
                color_continuous_scale=[
                    [0, "rgb(220, 220, 255)"],
                    [0.2, "rgb(150, 150, 255)"],
                    [0.4, "rgb(100, 100, 255)"],
                    [0.6, "rgb(50, 50, 230)"],
                    [0.8, "rgb(20, 20, 180)"],
                    [1, "rgb(5, 5, 100)"]
                ],
                aspect="auto",
                zmin=0,
                zmax=100
            )

            # Ajustement des annotations avec contraste adaptatif
            annotations = []
            for i in range(len(heatmap_data.index)):
                for j in range(len(heatmap_data.columns)):
                    if not pd.isna(heatmap_data.iloc[i, j]):
                        value = heatmap_data.iloc[i, j]
                        text_color = "white" if value > 30 else "black"
                        annotations.append(dict(
                            x=j,
                            y=i,
                            text=f"{value:.1f}%",
                            showarrow=False,
                            font=dict(
                                color=text_color,
                                size=12
                            )
                        ))

            fig_heatmap.update_layout(
                annotations=annotations,
                height=heatmap_height,
                margin=dict(l=50, r=20, t=20, b=30),
                coloraxis_colorbar=dict(
                    title="Taux de rétention (%)",
                    title_font_color="black",
                    tickfont_color="black"
                ),
                font=dict(color="black"),
                xaxis_title="Mois après acquisition",
                yaxis_title="Cohorte",
                paper_bgcolor='white',
                plot_bgcolor='white',
                xaxis=dict(
                    title_font_color="black",
                    tickfont_color="black",
                    gridcolor='lightgray'
                ),
                yaxis=dict(
                    title_font_color="black",
                    tickfont_color="black",
                    gridcolor='lightgray'
                )
            )

            st.plotly_chart(fig_heatmap, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Création du graphique en ligne
            st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
            st.markdown("<h3>Taux de Rétention par Cohorte</h3>", unsafe_allow_html=True)

            # Création du graphique en ligne avec les données filtrées
            if display_option in ["Trimestriel", "Semestriel", "Annuel"]:
                # Pour les affichages agrégés, créer une colonne de groupe pour la légende
                group_col = 'quarter' if display_option == "Trimestriel" else 'semester' if display_option == "Semestriel" else 'year'
                group_col_name = 'Trimestre' if display_option == "Trimestriel" else 'Semestre' if display_option == "Semestriel" else 'Année'

                # Agréger les données pour le graphique en ligne
                line_data = filtered_data.groupby([group_col, 'month_number']).agg({
                    'retention_rate': 'mean',
                    'avg_revenue_per_customer': 'mean'
                }).reset_index()

                fig_retention = px.line(
                    line_data,
                    x='month_number',
                    y='retention_rate',
                    color=group_col,
                    labels={
                        'month_number': 'Mois après acquisition',
                        'retention_rate': 'Taux de rétention (%)',
                        group_col: group_col_name
                    },
                    markers=True
                )
            else:
                # Pour l'affichage standard par cohorte
                fig_retention = px.line(
                    filtered_data,
                    x='month_number',
                    y='retention_rate',
                    color='cohort_month_str',
                    labels={
                        'month_number': 'Mois après acquisition',
                        'retention_rate': 'Taux de rétention (%)',
                        'cohort_month_str': 'Cohorte'
                    },
                    markers=True
                )

            fig_retention.update_layout(
                height=graph_height,
                margin=dict(l=50, r=20, t=20, b=40),
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1,
                    font=dict(color="black")
                ),
                font=dict(color="black"),
                xaxis=dict(
                    tickmode='array',
                    tickvals=list(range(0, months_to_display + 1)),
                    title_font_color="black",
                    tickfont_color="black",
                    gridcolor='lightgray'
                ),
                yaxis=dict(
                    title_font_color="black",
                    tickfont_color="black",
                    gridcolor='lightgray'
                ),
                paper_bgcolor='white',
                plot_bgcolor='white'
            )

            st.plotly_chart(fig_retention, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Créer graphique de revenu moyen par client avec les données filtrées
            st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
            st.markdown("<h3>Revenu Moyen par Client et par Cohorte</h3>", unsafe_allow_html=True)

            # Création du graphique de revenu moyen
            if display_option in ["Trimestriel", "Semestriel", "Annuel"]:
                # Utiliser les données déjà agrégées
                fig_revenue = px.line(
                    line_data,
                    x='month_number',
                    y='avg_revenue_per_customer',
                    color=group_col,
                    labels={
                        'month_number': 'Mois après acquisition',
                        'avg_revenue_per_customer': 'Revenu moyen par client (R$)',
                        group_col: group_col_name
                    },
                    markers=True
                )
            else:
                # Pour l'affichage standard par cohorte
                fig_revenue = px.line(
                    filtered_data,
                    x='month_number',
                    y='avg_revenue_per_customer',
                    color='cohort_month_str',
                    labels={
                        'month_number': 'Mois après acquisition',
                        'avg_revenue_per_customer': 'Revenu moyen par client (R$)',
                        'cohort_month_str': 'Cohorte'
                    },
                    markers=True
                )

            fig_revenue.update_layout(
                height=graph_height,
                margin=dict(l=50, r=20, t=20, b=40),
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1,
                    font=dict(color="black")
                ),
                font=dict(color="black"),
                xaxis=dict(
                    tickmode='array',
                    tickvals=list(range(0, months_to_display + 1)),
                    title_font_color="black",
                    tickfont_color="black",
                    gridcolor='lightgray'
                ),
                yaxis=dict(
                    title_font_color="black",
                    tickfont_color="black",
                    gridcolor='lightgray'
                ),
                paper_bgcolor='white',
                plot_bgcolor='white'
            )

            # Formatage de l'axe y pour afficher les valeurs monétaires avec texte noir
            fig_revenue.update_yaxes(
                tickprefix=" ",
                tickformat=",.0f",
                tickfont=dict(color="black")
            )

            st.plotly_chart(fig_revenue, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Tableau de synthèse des cohortes
            st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
            st.markdown("<h3>Tableau de Synthèse des Cohortes</h3>", unsafe_allow_html=True)

            # Préparation des données pour le tableau en utilisant les filtres (filtered_data et pivot_index)
            table_data = filtered_data.pivot_table(
                index=pivot_index,  # Utilise la clé d'agrégation définie dans le sidebar
                columns='month_number',
                values='retention_rate',
                aggfunc='mean'
            ).reset_index()

            # Renommer les colonnes pour un affichage plus clair : la première colonne correspond à la période filtrée
            table_data.columns = ["Cohorte"] + [f'M+{int(i)}' for i in table_data.columns[1:]]

            # Dupliquer le DataFrame pour appliquer le style
            numeric_df = table_data.copy()
            # Remplacer d'abord les NaN par 0 dans le DataFrame
            numeric_df = numeric_df.fillna(0)

            # Création du style du tableau
            styled_df = (
                numeric_df.style

                # Définir le style du header (fond bleu, texte blanc, centrage)
                .set_table_styles([
                    {
                        'selector': 'th',
                        'props': [
                            ('background-color', '#1e88e5'),
                            ('color', 'white'),
                            ('text-align', 'center')
                        ]
                    },
                    {
                        'selector': 'td',
                        'props': [
                            ('text-align', 'center')
                        ]
                    }
                ], overwrite=False)
                # Colorer la première colonne (celle des périodes) en gris clair avec texte noir
                .set_properties(subset=[table_data.columns[0]], **{'background-color': '#f0f0f0', 'color': 'black'})
                # Appliquer un gradient sur les colonnes numériques (M+0, M+1, etc.)
                .background_gradient(subset=numeric_df.columns[1:], cmap="YlGnBu")
                # Formater l’affichage en pourcentage avec 2 décimales
                .format({col: "{:.2f}%" for col in numeric_df.columns[1:]})
            )

            # Convertir le style en HTML
            html_table = styled_df.to_html()

            # CSS pour rendre le tableau défilant
            st.markdown("""
            <style>
            .scrollable-table {
                height: 400px;
                overflow-y: auto;
                display: block;
            }
            .scrollable-table table {
                width: 100%;
                color: black; /* Couleur par défaut du texte */
            }
            .scrollable-table th {
                color: white;
                background-color: #1e88e5;
            }
            </style>
            """, unsafe_allow_html=True)

            # Affichage du tableau dans un div scrollable
            st.markdown(f'<div class="scrollable-table">{html_table}</div>', unsafe_allow_html=True)

            # Option de téléchargement : export des données filtrées
            filtered_csv = filtered_data.to_csv(index=False)
            st.download_button(
                label="📥 Télécharger les données de cohortes (CSV)",
                data=filtered_csv,
                file_name="olist_cohort_analysis_filtered.csv",
                mime="text/csv",
                help="Télécharger les données d'analyse de cohortes filtrées au format CSV"
            )

            st.markdown("</div>", unsafe_allow_html=True)


           # Affichage des segments RFM
            st.markdown("<h2 class='sub-header'>Segmentation RFM des Clients</h2>", unsafe_allow_html=True)

            # Charger les données RFM
            rfm_data = load_rfm_segments(sql_start_date, sql_end_date)

            if not rfm_data.empty:
                # Affichage du graphique de répartition des segments
                st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
                st.markdown("<h3>Répartition des Segments RFM</h3>", unsafe_allow_html=True)

                fig_segments = px.bar(
                    rfm_data,
                    x='customer_segment',
                    y='customer_count',
                    color='customer_count',  # Dégradé basé sur le nombre de clients
                    color_continuous_scale=[[0, 'rgb(140,180,255)'], [1, 'rgb(0,50,150)']],  # Bleu plus clair pour min
                    text='percentage',
                    labels={
                        'customer_segment': 'Segment',
                        'customer_count': 'Nombre de clients',
                        'percentage': 'Pourcentage (%)'
                    },
                    height=graph_height
                )

                fig_segments.update_traces(
                    texttemplate='%{text:.1f}%',
                    textposition='outside',
                    textfont=dict(color="black")
                )

                fig_segments.update_layout(
                    margin=dict(l=50, r=20, t=20, b=100),
                    font=dict(color="black"),
                    xaxis_tickangle=-45,
                    showlegend=False,
                    coloraxis_showscale=False,  # Suppression de la colorbar
                    paper_bgcolor='white',
                    plot_bgcolor='white',
                    yaxis_gridcolor='lightgray',
                    xaxis=dict(
                        title_font_color="black",
                        tickfont_color="black"
                    ),
                    yaxis=dict(
                        title_font_color="black",
                        tickfont_color="black",
                        range=[0, max(rfm_data['customer_count']) * 1.2]  # Ajout de 20% d'espace en haut
                    )
                )

                st.plotly_chart(fig_segments, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)


                # Tableau des métriques RFM par segment
                st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
                st.markdown("<h3>Métriques des Segments RFM</h3>", unsafe_allow_html=True)

                # Ajouter un sélecteur pour l'ordre de tri
                sort_options = {
                    "customer_segment": "Segment",
                    "avg_recency_days": "Récence moyenne (jours)",
                    "avg_frequency": "Fréquence moyenne",
                    "avg_monetary_value": "Valeur moyenne",
                    "total_monetary_value": "Valeur totale",
                    "revenue_percentage": "% du revenu total"
                }

                selected_sort = st.selectbox(
                    "Trier par:",
                    options=list(sort_options.keys()),
                    format_func=lambda x: sort_options[x],
                    index=0  # Par défaut, tri par segment
                )

                # Sélectionner l'ordre de tri (croissant/décroissant)
                sort_order = st.radio(
                    "Ordre:",
                    ["Décroissant", "Croissant"],
                    horizontal=True,
                    index=0  # Par défaut, décroissant
                )

                # Appliquer le tri
                ascending = True if sort_order == "Croissant" else False
                rfm_data = rfm_data.sort_values(by=selected_sort, ascending=ascending)

                # Conserver les données numériques pour le style
                numeric_rfm = rfm_data.copy()

                # Formater certaines colonnes pour l'affichage dans le CSV (pour téléchargement)
                display_rfm = rfm_data.copy()
                display_rfm['avg_monetary_value'] = display_rfm['avg_monetary_value'].apply(lambda x: format_currency(x))
                display_rfm['total_monetary_value'] = display_rfm['total_monetary_value'].apply(lambda x: format_currency(x))
                display_rfm['percentage'] = display_rfm['percentage'].apply(lambda x: f"{x:.2f}%")
                display_rfm['revenue_percentage'] = display_rfm['revenue_percentage'].apply(lambda x: f"{x:.2f}%")

                # Appliquer le style au DataFrame sans masquer l'index en utilisant hide_index()
                # On applique un dégradé "Blues" sur toutes les colonnes numériques pour une palette uniforme
                styled_rfm = numeric_rfm.style\
                    .background_gradient(subset=[
                        'customer_count',
                        'percentage',
                        'avg_recency_days',
                        'avg_frequency',
                        'avg_monetary_value',
                        'total_monetary_value',
                        'revenue_percentage'
                    ], cmap="Blues")\
                    .set_properties(**{'color': 'black'})\
                    .set_table_styles([
                        # Style des en-têtes : fond gris clair et texte noir
                        {'selector': 'th', 'props': [('background-color', '#d3d3d3'), ('color', 'black'), ('padding', '8px'), ('text-align', 'center')]},
                        # Style spécifique pour la colonne "Segment" (première colonne) : fond gris léger
                        {'selector': 'td.col0', 'props': [('background-color', '#e6e6e6'), ('color', 'black'), ('padding', '8px'), ('text-align', 'center')]}
                    ])\
                    .format({
                        'avg_recency_days': "{:.2f}",
                        'avg_frequency': "{:.2f}",
                        'avg_monetary_value': "R$ {:.2f}",
                        'total_monetary_value': "R$ {:.2f}",
                        'percentage': "{:.2f}%",
                        'revenue_percentage': "{:.2f}%"
                    })

                # Générer le HTML et renommer les en-têtes pour l'affichage en français
                html_table = styled_rfm.to_html()
                html_table = html_table.replace('>customer_segment<', '>Segment<')
                html_table = html_table.replace('>customer_count<', '>Nombre de clients<')
                html_table = html_table.replace('>percentage<', '>% des clients<')
                html_table = html_table.replace('>avg_recency_days<', '>Récence moyenne (jours)<')
                html_table = html_table.replace('>avg_frequency<', '>Fréquence moyenne<')
                html_table = html_table.replace('>avg_monetary_value<', '>Valeur moyenne<')
                html_table = html_table.replace('>total_monetary_value<', '>Valeur totale<')
                html_table = html_table.replace('>revenue_percentage<', '>% du revenu total<')

                # Ajouter le CSS pour masquer l'index et améliorer la lisibilité du tableau
                st.markdown("""
                <style>
                /* Masquer l'index généré par Pandas (la première colonne d'en-tête et de cellules) */
                table > thead > tr > th:first-child,
                table > tbody > tr > th:first-child {
                    display: none;
                }
                /* Conteneur défilable pour le tableau */
                .scrollable-table {
                    height: 400px;
                    overflow-y: auto;
                    display: block;
                }
                .scrollable-table table {
                    width: 100%;
                    border-collapse: collapse;
                    color: black;
                }
                .scrollable-table th, .scrollable-table td {
                    padding: 8px;
                    text-align: center;
                }
                </style>
                """, unsafe_allow_html=True)

                # Envelopper le tableau dans un div avec défilement
                st.markdown(f'<div class="scrollable-table">{html_table}</div>', unsafe_allow_html=True)

                # Option de téléchargement
                rfm_csv = rfm_data.to_csv(index=False)
                st.download_button(
                    label="📥 Télécharger les données RFM (CSV)",
                    data=rfm_csv,
                    file_name="olist_rfm_segments.csv",
                    mime="text/csv",
                    help="Télécharger les données de segmentation RFM au format CSV"
                )
                st.markdown("</div>", unsafe_allow_html=True)



                # Graphique des valeurs moyennes par segment
                st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
                st.markdown("<h3>Valeur monétaire moyenne par segment</h3>", unsafe_allow_html=True)

                # Calcul de la valeur maximale pour ajuster l'axe y
                max_value = rfm_data['avg_monetary_value'].max()

                fig_monetary = px.bar(
                    rfm_data,
                    x='customer_segment',
                    y='avg_monetary_value',
                    color='avg_monetary_value',  # Couleur basée sur la valeur
                    color_continuous_scale=[[0, 'rgb(140,180,255)'], [1, 'rgb(0,50,150)']],  # Bleu ajusté pour éviter trop de clarté
                    text='avg_monetary_value',
                    labels={
                        'customer_segment': 'Segment',
                        'avg_monetary_value': 'Valeur moyenne (R$)'
                    },
                    height=graph_height
                )

                fig_monetary.update_traces(
                    texttemplate='%{text:.0f}',
                    textposition='outside',
                    textfont=dict(color="black")
                )

                fig_monetary.update_layout(
                    margin=dict(l=50, r=20, t=20, b=100),
                    font=dict(color="black"),
                    xaxis_tickangle=-45,
                    showlegend=False,
                    coloraxis_showscale=False,  # Suppression de la colorbar
                    yaxis=dict(
                        title="Valeur moyenne (R$)",
                        title_font_color="black",
                        tickfont_color="black",
                        gridcolor='lightgray',
                        range=[0, max_value * 1.2]  # Multiplication par 1.2 pour ajouter de l'espace
                    ),
                    xaxis=dict(
                        title_font_color="black",
                        tickfont_color="black"
                    ),
                    paper_bgcolor='white',
                    plot_bgcolor='white'
                )

                # Formatage de l'axe y pour afficher le préfixe monétaire
                fig_monetary.update_yaxes(
                    tickprefix=" ",
                    tickformat=",.0f",
                    tickfont=dict(color="black")
                )

                st.plotly_chart(fig_monetary, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)



                # Graphique des mesures RFM normalisées
                st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
                st.markdown("<h3>Profil RFM par segment</h3>", unsafe_allow_html=True)

                # Préparer les données normalisées pour le radar chart
                radar_data = rfm_data.copy()

                # Normaliser les métriques RFM (inverser la récence où une valeur plus faible est meilleure)
                max_recency = radar_data['avg_recency_days'].max()
                radar_data['recency_normalized'] = 1 - (radar_data['avg_recency_days'] / max_recency)
                radar_data['frequency_normalized'] = radar_data['avg_frequency'] / radar_data['avg_frequency'].max()
                radar_data['monetary_normalized'] = radar_data['avg_monetary_value'] / radar_data['avg_monetary_value'].max()

                # Créer le radar chart
                fig_radar = go.Figure()

                for i, segment in enumerate(radar_data['customer_segment']):
                    fig_radar.add_trace(go.Scatterpolar(
                        r=[
                            radar_data.loc[radar_data['customer_segment'] == segment, 'recency_normalized'].iloc[0],
                            radar_data.loc[radar_data['customer_segment'] == segment, 'frequency_normalized'].iloc[0],
                            radar_data.loc[radar_data['customer_segment'] == segment, 'monetary_normalized'].iloc[0]
                        ],
                        theta=['Récence', 'Fréquence', 'Valeur'],
                        fill='toself',
                        name=segment
                    ))

                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 1],
                            color="black",
                            tickfont=dict(color="black")
                        ),
                        angularaxis=dict(
                            color="black",
                            tickfont=dict(color="black")
                        ),
                        bgcolor="white"
                    ),
                    showlegend=True,
                    height=550,
                    margin=dict(l=50, r=20, t=20, b=50),
                    font=dict(color="black"),
                    legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=-0.1,
                    xanchor='left',
                    x=0,
                    font=dict(color="black")
                )
                ,
                    paper_bgcolor='white'
                )

                st.plotly_chart(fig_radar, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            else:
                st.warning("Aucune donnée RFM disponible pour la période sélectionnée.")

        else:
            st.warning("Aucune donnée de cohorte disponible pour la période sélectionnée.")

    except Exception as e:
        st.error(f"Erreur lors du traitement des données: {e}")
        import traceback
        st.error(traceback.format_exc())

# Footer
st.markdown("<div class='footer'>© 2023 Olist Analytics Dashboard - Développé avec Streamlit</div>", unsafe_allow_html=True)

