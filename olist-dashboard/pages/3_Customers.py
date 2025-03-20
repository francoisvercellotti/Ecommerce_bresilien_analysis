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
    page_title="Olist - Analyse des Clients",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"  # Barre latérale visible par défaut
)

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

    /* Carte pour les métriques avec couleurs différentes */
    .metric-card {
        background-color: #1e88e5;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        color: white;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .metric-card .metric-label {
        font-size: 1.25rem;
    }
    .metric-card .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
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
</style>
""", unsafe_allow_html=True)

# Fonction pour formater les valeurs monétaires
def format_currency(value):
    return f"R$ {value:,.2f}"

# Chargement des données avec cache et paramètres de date
@st.cache_data(ttl=3600)
def load_customer_lifetime_value(start_date=None, end_date=None):
    query = """
    WITH customer_orders AS (
        SELECT
            c.customer_unique_id,
            COUNT(DISTINCT o.order_id) AS order_count,
            SUM(oi.price) AS total_spend,
            MIN(o.order_purchase_timestamp) AS first_purchase,
            MAX(o.order_purchase_timestamp) AS last_purchase,
            GREATEST(1, EXTRACT(EPOCH FROM (MAX(o.order_purchase_timestamp) - MIN(o.order_purchase_timestamp))) / 86400) AS customer_lifespan_days
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_status = 'delivered'
        {date_filter}
        GROUP BY c.customer_unique_id
    ),
    customer_value AS (
        SELECT
            customer_unique_id,
            order_count,
            total_spend,
            first_purchase,
            last_purchase,
            customer_lifespan_days,
            total_spend / NULLIF(order_count, 0) AS average_order_value,
            CASE
                WHEN order_count <= 1 THEN 1
                ELSE order_count / (customer_lifespan_days / 30.0)
            END AS purchase_frequency_monthly,
            CASE
                WHEN order_count <= 1 THEN total_spend
                ELSE (total_spend / order_count) * (order_count / (customer_lifespan_days / 30.0)) * 12
            END AS estimated_annual_value
        FROM customer_orders
        WHERE order_count > 0
    )
    SELECT
        customer_unique_id,
        order_count,
        CAST(total_spend AS numeric(10,2)) AS total_spend,
        first_purchase,
        last_purchase,
        CAST(customer_lifespan_days AS numeric(10,2)) AS customer_lifespan_days,
        CAST(average_order_value AS numeric(10,2)) AS average_order_value,
        CAST(purchase_frequency_monthly AS numeric(10,4)) AS purchase_frequency_monthly,
        CAST(estimated_annual_value AS numeric(10,2)) AS estimated_annual_value,
        CASE
            WHEN estimated_annual_value > 500 THEN 'Premium'
            WHEN estimated_annual_value > 200 THEN 'High Value'
            WHEN estimated_annual_value > 100 THEN 'Medium Value'
            ELSE 'Standard'
        END AS customer_segment
    FROM customer_value
    ORDER BY estimated_annual_value DESC
    """

    date_filter = ""
    if start_date and end_date:
        date_filter = f"AND o.order_purchase_timestamp BETWEEN '{start_date}' AND '{end_date}'"

    query = query.format(date_filter=date_filter)

    return execute_raw_query(query)

@st.cache_data(ttl=3600)
def load_customer_segments_summary(start_date=None, end_date=None):
    query = """
    WITH customer_orders AS (
        SELECT
            c.customer_unique_id,
            COUNT(DISTINCT o.order_id) AS order_count,
            SUM(oi.price) AS total_spend,
            MIN(o.order_purchase_timestamp) AS first_purchase,
            MAX(o.order_purchase_timestamp) AS last_purchase,
            GREATEST(1, EXTRACT(EPOCH FROM (MAX(o.order_purchase_timestamp) - MIN(o.order_purchase_timestamp))) / 86400) AS customer_lifespan_days
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_status = 'delivered'
        {date_filter}
        GROUP BY c.customer_unique_id
    ),
    customer_metrics AS (
        SELECT
            customer_unique_id,
            order_count,
            total_spend,
            first_purchase,
            last_purchase,
            customer_lifespan_days,
            total_spend / NULLIF(order_count, 0) AS average_order_value,
            CASE
                WHEN order_count <= 1 THEN 1
                ELSE order_count / (customer_lifespan_days / 30.0)
            END AS purchase_frequency_monthly,
            CASE
                WHEN order_count <= 1 THEN total_spend
                ELSE (total_spend / order_count) * (order_count / (customer_lifespan_days / 30.0)) * 12
            END AS estimated_annual_value
        FROM customer_orders
        WHERE order_count > 0
    ),
    customer_value AS (
        SELECT
            customer_unique_id,
            order_count,
            total_spend,
            first_purchase,
            last_purchase,
            customer_lifespan_days,
            average_order_value,
            purchase_frequency_monthly,
            estimated_annual_value,
            CASE
                WHEN estimated_annual_value > 500 THEN 'Premium'
                WHEN estimated_annual_value > 200 THEN 'High Value'
                WHEN estimated_annual_value > 100 THEN 'Medium Value'
                ELSE 'Standard'
            END AS customer_segment
        FROM customer_metrics
    )
    SELECT
        customer_segment,
        COUNT(*) AS customer_count,
        ROUND(AVG(order_count), 2) AS avg_orders,
        ROUND(AVG(total_spend), 2) AS avg_total_spend,
        ROUND(AVG(customer_lifespan_days), 2) AS avg_lifespan_days,
        ROUND(AVG(average_order_value), 2) AS avg_order_value,
        ROUND(AVG(purchase_frequency_monthly), 4) AS avg_purchase_frequency,
        ROUND(AVG(estimated_annual_value), 2) AS avg_annual_value,
        ROUND(SUM(estimated_annual_value), 2) AS total_annual_value
    FROM customer_value
    GROUP BY customer_segment
    ORDER BY avg_annual_value DESC
    """

    date_filter = ""
    if start_date and end_date:
        date_filter = f"AND o.order_purchase_timestamp BETWEEN '{start_date}' AND '{end_date}'"

    query = query.format(date_filter=date_filter)

    return execute_raw_query(query)

@st.cache_data(ttl=3600)
def load_customer_geography(start_date=None, end_date=None):
    query = """
    WITH customer_locations AS (
        SELECT
            c.customer_unique_id,
            c.customer_city,
            c.customer_state,
            COUNT(DISTINCT o.order_id) AS order_count,
            SUM(oi.price) AS total_spend,
            (SUM(oi.price) / COUNT(DISTINCT o.order_id)) AS avg_order_value
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_status = 'delivered'
        {date_filter}
        GROUP BY c.customer_unique_id, c.customer_city, c.customer_state
    )
    SELECT
        customer_state,
        COUNT(*) AS customer_count,
        ROUND(AVG(order_count), 2) AS avg_orders,
        ROUND(AVG(total_spend), 2) AS avg_total_spend,
        ROUND(AVG(avg_order_value), 2) AS avg_order_value,
        ROUND(SUM(total_spend), 2) AS total_state_spend
    FROM customer_locations
    GROUP BY customer_state
    ORDER BY total_state_spend DESC
    """

    date_filter = ""
    if start_date and end_date:
        date_filter = f"AND o.order_purchase_timestamp BETWEEN '{start_date}' AND '{end_date}'"

    query = query.format(date_filter=date_filter)

    return execute_raw_query(query)

@st.cache_data(ttl=3600)
def load_customer_purchase_frequency(start_date=None, end_date=None):
    query = """
    WITH customer_orders AS (
        SELECT
            c.customer_unique_id,
            COUNT(DISTINCT o.order_id) AS order_count,
            MIN(o.order_purchase_timestamp) AS first_purchase,
            MAX(o.order_purchase_timestamp) AS last_purchase,
            GREATEST(1, EXTRACT(EPOCH FROM (MAX(o.order_purchase_timestamp) - MIN(o.order_purchase_timestamp))) / 86400) AS customer_lifespan_days
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_status = 'delivered'
        {date_filter}
        GROUP BY c.customer_unique_id
    ),
    frequency_data AS (
        SELECT
            CASE
                WHEN order_count = 1 THEN 'One-time'
                WHEN order_count BETWEEN 2 AND 3 THEN '2-3 orders'
                WHEN order_count BETWEEN 4 AND 6 THEN '4-6 orders'
                ELSE '7+ orders'
            END AS purchase_frequency,
            COUNT(*) AS customer_count,
            ROUND(AVG(customer_lifespan_days), 2) AS avg_lifespan_days
        FROM customer_orders
        GROUP BY
            CASE
                WHEN order_count = 1 THEN 'One-time'
                WHEN order_count BETWEEN 2 AND 3 THEN '2-3 orders'
                WHEN order_count BETWEEN 4 AND 6 THEN '4-6 orders'
                ELSE '7+ orders'
            END
    )
    SELECT
        purchase_frequency,
        customer_count,
        avg_lifespan_days
    FROM frequency_data
    ORDER BY
        CASE
            WHEN purchase_frequency = 'One-time' THEN 1
            WHEN purchase_frequency = '2-3 orders' THEN 2
            WHEN purchase_frequency = '4-6 orders' THEN 3
            ELSE 4
        END
    """

    date_filter = ""
    if start_date and end_date:
        date_filter = f"AND o.order_purchase_timestamp BETWEEN '{start_date}' AND '{end_date}'"

    query = query.format(date_filter=date_filter)

    return execute_raw_query(query)

@st.cache_data(ttl=3600)
def load_customer_categories(start_date=None, end_date=None):
    query = """
    WITH customer_category_preferences AS (
        SELECT
            c.customer_unique_id,
            p.product_category_name,
            COUNT(DISTINCT o.order_id) AS category_orders,
            SUM(oi.price) AS category_spend
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_status = 'delivered' AND p.product_category_name IS NOT NULL
        {date_filter}
        GROUP BY c.customer_unique_id, p.product_category_name
    )
    SELECT
        product_category_name,
        COUNT(DISTINCT customer_unique_id) AS customer_count,
        SUM(category_orders) AS total_orders,
        ROUND(AVG(category_orders), 2) AS avg_orders_per_customer,
        ROUND(SUM(category_spend), 2) AS total_spend,
        ROUND(AVG(category_spend), 2) AS avg_spend_per_customer
    FROM customer_category_preferences
    GROUP BY product_category_name
    ORDER BY total_spend DESC
    """

    date_filter = ""
    if start_date and end_date:
        date_filter = f"AND o.order_purchase_timestamp BETWEEN '{start_date}' AND '{end_date}'"

    query = query.format(date_filter=date_filter)

    return execute_raw_query(query)


@st.cache_data(ttl=3600)
def load_date_range():
    return execute_query("date_range.sql")

# Constantes pour les graphiques
graph_height = 300
heatmap_height = 600

# Titre principal
st.markdown("<h1 class='main-header'>👥 Analyse des Clients Olist</h1>", unsafe_allow_html=True)

# Filtres dans la sidebar
with st.sidebar:
    st.markdown("<h2 class='sub-header'>Filtres</h2>", unsafe_allow_html=True)

    # Filtre de période
    st.markdown("<h3 class='sub-header'>Période</h3>", unsafe_allow_html=True)
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

    # Filtre de segment client
    st.markdown("<h3 class='sub-header'>Filtres de segment</h3>", unsafe_allow_html=True)
    customer_segments = ["Premium", "High Value", "Medium Value", "Standard"]
    selected_segments = st.multiselect(
        "Segments clients",
        options=customer_segments,
        default=customer_segments
    )

    # Nombre minimum de commandes
    min_orders = st.slider(
        "Nombre minimum de commandes",
        min_value=1,
        max_value=10,
        value=1,
        step=1
    )

# Création d'une layout compact pour tout le dashboard
layout_container = st.container()

# CSS personnalisé pour les cartes de métriques colorées
st.markdown("""
<style>
.metric-card {
    padding: 15px;
    border-radius: 5px;
    margin-bottom: 10px;
    color: white;
    text-align: center;
}
.metric-card-customers {
    background-color: #5470C6;  /* Bleu */
}
.metric-card-spend {
    background-color: #91CC75;  /* Vert */
}
.metric-card-frequency {
    background-color: #FAC858;  /* Jaune */
}
.metric-card-clv {
    background-color: #EE6666;  /* Rouge */
}
.metric-label {
    font-size: 14px;
    font-weight: bold;
    margin-bottom: 5px;
}
.metric-value {
    font-size: 20px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

with layout_container:
    # Métriques générales
    col1, col2, col3, col4 = st.columns(4)

    try:
        # Charger les données avec les filtres appliqués
        customer_data = load_customer_lifetime_value(sql_start_date, sql_end_date)

        # Filtrer par segment client
        if selected_segments and len(selected_segments) > 0:
            customer_data = customer_data[customer_data["customer_segment"].isin(selected_segments)]

        # Filtrer par nombre minimum de commandes
        customer_data = customer_data[customer_data["order_count"] >= min_orders]

        if not customer_data.empty:
            with col1:
                st.markdown(
                    f"""
                    <div class='metric-card-customers' style="background-color: #1e88e5; border-radius: 10px; padding: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); color: white; margin-bottom: 8px;">
                        <h3 style="margin-bottom:2px; font-size:1rem; font-weight:bold;">Nombre de clients</h3>
                        <h2 style="margin:0; font-size:2rem; font-weight:bold;">{format(len(customer_data), ',')}</h2>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col2:
                avg_spend = customer_data['total_spend'].mean()
                st.markdown(
                    f"""
                    <div class='metric-card-spend' style="background-color: #43a047; border-radius: 10px; padding: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); color: white; margin-bottom: 8px;">
                        <h3 style="margin-bottom:2px; font-size:1rem; font-weight:bold;">Dépense moyenne</h3>
                        <h2 style="margin:0; font-size:2rem; font-weight:bold;">{format_currency(avg_spend)}</h2>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col3:
                avg_frequency = customer_data['purchase_frequency_monthly'].mean()
                st.markdown(
                    f"""
                    <div class='metric-card-frequency' style="background-color: #fb8c00; border-radius: 10px; padding: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); color: white; margin-bottom: 8px;">
                        <h3 style="margin-bottom:2px; font-size:1rem; font-weight:bold;">Fréquence d'achat (mensuelle)</h3>
                        <h2 style="margin:0; font-size:2rem; font-weight:bold;">{avg_frequency:.2f}</h2>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col4:
                avg_clv = customer_data['estimated_annual_value'].mean()
                st.markdown(
                    f"""
                    <div class='metric-card-clv' style="background-color: #8e24aa; border-radius: 10px; padding: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); color: white; margin-bottom: 8px;">
                        <h3 style="margin-bottom:2px; font-size:1rem; font-weight:bold;">Valeur annuelle moyenne</h3>
                        <h2 style="margin:0; font-size:2rem; font-weight:bold;">{format_currency(avg_clv)}</h2>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        else:
            st.warning("Aucune donnée client disponible pour les filtres sélectionnés.")
    except Exception as e:
        st.error(f"Erreur lors du chargement des métriques générales: {e}")

    # Tableau de segments clients
    st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
    st.markdown("<h3>Segments clients</h3>", unsafe_allow_html=True)
    try:
        segments_data = load_customer_segments_summary(sql_start_date, sql_end_date)
        if not segments_data.empty:
            # Filtrer par segments sélectionnés
            if selected_segments and len(selected_segments) > 0:
                segments_data = segments_data[segments_data["customer_segment"].isin(selected_segments)]

            # Duplicata du DataFrame pour conserver les valeurs numériques pour le style
            numeric_segments = segments_data.copy()

            # Vérifier quelles colonnes existent dans le DataFrame
            available_columns = segments_data.columns.tolist()

            # Sélectionner les colonnes pour le gradient de couleur
            gradient_columns = []
            if "count" in available_columns:
                gradient_columns.append(("count", "Blues"))
            if "segment_count" in available_columns:
                gradient_columns.append(("segment_count", "Blues"))
            if "avg_total_spend" in available_columns:
                gradient_columns.append(("avg_total_spend", "Greens"))
            if "avg_order_value" in available_columns:
                gradient_columns.append(("avg_order_value", "RdPu"))
            if "avg_purchase_frequency" in available_columns:
                gradient_columns.append(("avg_purchase_frequency", "Oranges"))
            if "avg_annual_value" in available_columns:
                gradient_columns.append(("avg_annual_value", "RdYlGn"))
            if "total_annual_value" in available_columns:
                gradient_columns.append(("total_annual_value", "Spectral"))

            # Créer le style de base
            styled_segments = numeric_segments.style

            # Appliquer le gradient à chaque colonne disponible
            for col, cmap in gradient_columns:
                styled_segments = styled_segments.background_gradient(subset=[col], cmap=cmap)

            # Appliquer le formatage selon les colonnes disponibles
            format_dict = {}
            if "avg_total_spend" in available_columns:
                format_dict["avg_total_spend"] = "R$ {:.2f}"
            if "avg_order_value" in available_columns:
                format_dict["avg_order_value"] = "R$ {:.2f}"
            if "avg_purchase_frequency" in available_columns:
                format_dict["avg_purchase_frequency"] = "{:.4f}"
            if "avg_annual_value" in available_columns:
                format_dict["avg_annual_value"] = "R$ {:.2f}"
            if "total_annual_value" in available_columns:
                format_dict["total_annual_value"] = "R$ {:.2f}"

            # Appliquer le formatage
            styled_segments = styled_segments.format(format_dict)

            # Générer le HTML
            html_segments = styled_segments.to_html()

            # Dictionnaire de correspondance pour les noms de colonnes
            column_names = {
                "customer_segment": "Segment",
                "count": "Nombre de clients",
                "segment_count": "Taille Segment",
                "avg_total_spend": "Dépense Moyenne",
                "avg_order_value": "Valeur Moy. Commande",
                "avg_purchase_frequency": "Fréq. Moy. Achat",
                "avg_annual_value": "Valeur Annuelle Moy.",
                "total_annual_value": "Valeur Annuelle Totale"
            }

            # Remplacer les en-têtes de colonnes avec les noms français
            for eng_name, fr_name in column_names.items():
                if eng_name in available_columns:
                    html_segments = html_segments.replace(f'>{eng_name}<', f'>{fr_name}<')

            # Ajouter le CSS pour un tableau normal sans défilement avec un padding réduit
            st.markdown("""
            <style>
            .table-container table {
                width: 100%;
                margin-bottom: 10px; /* Réduit l'espace après le tableau */
            }
            </style>
            """, unsafe_allow_html=True)

            # Afficher le tableau sans défilement
            st.markdown(f'<div class="table-container">{html_segments}</div>', unsafe_allow_html=True)

            # Option de téléchargement
            segments_csv = segments_data.to_csv(index=False)
            st.download_button(
                label="📥 Télécharger les données (CSV)",
                data=segments_csv,
                file_name="olist_customer_segments.csv",
                mime="text/csv",
                help="Télécharger les données des segments clients au format CSV"
            )
        else:
            st.warning("Aucune donnée de segment client disponible pour les filtres sélectionnés.")
    except Exception as e:
        st.error(f"Erreur lors de l'affichage du tableau des segments: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

    # Distribution des clients par segment
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
        st.markdown("<h3>Distribution des clients par segment</h3>", unsafe_allow_html=True)
        try:
            if not segments_data.empty:
                # Créer le graphique
                fig = px.pie(
                    segments_data,
                    values="customer_count",
                    names="customer_segment",
                    title="Répartition des clients par segment",
                    color="customer_segment",
                    color_discrete_map={
                        "Premium": "#1a9850",
                        "High Value": "#91cf60",
                        "Medium Value": "#d9ef8b",
                        "Standard": "#fee08b"
                    }
                )

                fig.update_layout(
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    font=dict(family="Arial, sans-serif", size=14, color="black"),  # Taille augmentée et couleur noire
                    height=graph_height,
                    margin=dict(l=10, r=10, t=30, b=10),
                    legend=dict(font=dict(size=14, color="black"))  # Légende en noir et plus grande
                )

                # Texte du titre en noir et plus grand
                fig.update_layout(title_font=dict(size=16, color="black"))

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Aucune donnée disponible pour l'affichage de la distribution.")
        except Exception as e:
            st.error(f"Erreur lors de l'affichage de la distribution des clients: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
        st.markdown("<h3>Valeur annuelle par segment</h3>", unsafe_allow_html=True)
        try:
            if not segments_data.empty:
                # Créer le graphique
                fig = px.bar(
                    segments_data,
                    x="customer_segment",
                    y="total_annual_value",
                    title="Valeur annuelle totale par segment",
                    color="customer_segment",
                    color_discrete_map={
                        "Premium": "#1a9850",
                        "High Value": "#91cf60",
                        "Medium Value": "#d9ef8b",
                        "Standard": "#fee08b"
                    },
                    text_auto='.2s'
                )

                fig.update_layout(
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    font=dict(family="Arial, sans-serif", size=14, color="black"),  # Taille augmentée et couleur noire
                    height=graph_height,
                    margin=dict(l=10, r=10, t=30, b=10),
                    xaxis_title="Segment client",
                    yaxis_title="Valeur annuelle totale (R$)",
                    legend=dict(font=dict(size=14, color="black")),  # Légende en noir et plus grande
                    title_font=dict(size=16, color="black")  # Titre en noir et plus grand
                )

                # Mise à jour des axes avec texte plus grand et noir
                fig.update_xaxes(title_font=dict(size=14, color="black"), tickfont=dict(size=12, color="black"))
                fig.update_yaxes(title_font=dict(size=14, color="black"), tickfont=dict(size=12, color="black"))

                # Formater les montants pour l'affichage
                fig.update_traces(
                    texttemplate='R$ %{y:.2s}',
                    textposition='outside',
                    textfont=dict(size=12, color="black")  # Texte des valeurs en noir et plus grand
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Aucune donnée disponible pour l'affichage de la valeur annuelle.")
        except Exception as e:
            st.error(f"Erreur lors de l'affichage de la valeur annuelle: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

    # Fréquence d'achat et géographie
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
        st.markdown("<h3>Fréquence d'achat des clients</h3>", unsafe_allow_html=True)
        try:
            purchase_frequency_data = load_customer_purchase_frequency(sql_start_date, sql_end_date)

            if not purchase_frequency_data.empty:
                # Créer un ordre personnalisé pour les catégories
                order_mapping = {
                    "One-time": 0,
                    "2-3 orders": 1,
                    "4-6 orders": 2,
                    "7+ orders": 3
                }

                # Ajouter une colonne pour le tri
                purchase_frequency_data["sort_order"] = purchase_frequency_data["purchase_frequency"].map(order_mapping)
                purchase_frequency_data = purchase_frequency_data.sort_values("sort_order")

                # Créer le graphique
                fig = px.bar(
                    purchase_frequency_data,
                    x="purchase_frequency",
                    y="customer_count",
                    title="Distribution de la fréquence d'achat",
                    color="purchase_frequency",
                    color_discrete_map={
                        "One-time": "#fee08b",
                        "2-3 orders": "#d9ef8b",
                        "4-6 orders": "#91cf60",
                        "7+ orders": "#1a9850"
                    },
                    text_auto=True
                )

                fig.update_layout(
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    font=dict(family="Arial, sans-serif", size=14, color="black"),  # Taille augmentée et couleur noire
                    height=graph_height,
                    margin=dict(l=10, r=10, t=30, b=10),
                    xaxis_title="Fréquence d'achat",
                    yaxis_title="Nombre de clients",
                    legend=dict(font=dict(size=14, color="black")),  # Légende en noir et plus grande
                    title_font=dict(size=16, color="black")  # Titre en noir et plus grand
                )

                # Mise à jour des axes avec texte plus grand et noir
                fig.update_xaxes(title_font=dict(size=14, color="black"), tickfont=dict(size=12, color="black"))
                fig.update_yaxes(title_font=dict(size=14, color="black"), tickfont=dict(size=12, color="black"))

                # Texte des valeurs en noir et plus grand
                fig.update_traces(textfont=dict(size=12, color="black"))

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Aucune donnée de fréquence d'achat disponible.")
        except Exception as e:
            st.error(f"Erreur lors de l'affichage de la fréquence d'achat: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
        st.markdown("<h3>Répartition géographique des clients</h3>", unsafe_allow_html=True)
        try:
            geography_data = load_customer_geography(sql_start_date, sql_end_date)

            if not geography_data.empty:
                # Prendre les 10 premiers états par nombre de clients
                top_10_states = geography_data.sort_values("customer_count", ascending=False).head(10)

                # Créer le graphique
                fig = px.bar(
                    top_10_states,
                    x="customer_state",
                    y="customer_count",
                    title="Top 10 États par nombre de clients",
                    color="avg_total_spend",
                    color_continuous_scale="Viridis",
                    text_auto=True
                )

                fig.update_layout(
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    font=dict(family="Arial, sans-serif", size=14, color="black"),  # Taille augmentée et couleur noire
                    height=graph_height,
                    margin=dict(l=10, r=10, t=30, b=10),
                    xaxis_title="État",
                    yaxis_title="Nombre de clients",
                    coloraxis_colorbar=dict(
                        title="Dépense moyenne (R$)",
                        title_font=dict(size=14, color="black"),  # Titre de la barre de couleur en noir et plus grand
                        tickfont=dict(size=12, color="black")  # Texte des graduations en noir et plus grand
                    ),
                    title_font=dict(size=16, color="black")  # Titre en noir et plus grand
                )

                # Mise à jour des axes avec texte plus grand et noir
                fig.update_xaxes(title_font=dict(size=14, color="black"), tickfont=dict(size=12, color="black"))
                fig.update_yaxes(title_font=dict(size=14, color="black"), tickfont=dict(size=12, color="black"))

                # Texte des valeurs en noir et plus grand
                fig.update_traces(textfont=dict(size=12, color="black"))

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Aucune donnée géographique disponible.")
        except Exception as e:
            st.error(f"Erreur lors de l'affichage de la répartition géographique: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

    # Catégories de produits populaires
    st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
    st.markdown("<h3>Catégories de produits populaires</h3>", unsafe_allow_html=True)
    try:
        category_data = load_customer_categories(sql_start_date, sql_end_date)

        if not category_data.empty:
            # Prendre les 10 premières catégories par nombre de clients
            top_10_categories = category_data.sort_values("customer_count", ascending=False).head(10)

            # Créer le graphique
            fig = px.bar(
                top_10_categories,
                x="product_category_name",
                y="customer_count",
                title="Top 10 catégories de produits par nombre de clients",
                color="total_spend",
                color_continuous_scale="Viridis",
                text_auto=True
            )

            fig.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white",
                font=dict(family="Arial, sans-serif", size=14, color="black"),  # Taille augmentée et couleur noire
                height=graph_height,
                margin=dict(l=10, r=10, t=30, b=10),
                xaxis_title="Catégorie de produit",
                yaxis_title="Nombre de clients",
                coloraxis_colorbar=dict(
                    title="Dépense totale (R$)",
                    title_font=dict(size=14, color="black"),  # Titre de la barre de couleur en noir et plus grand
                    tickfont=dict(size=12, color="black")  # Texte des graduations en noir et plus grand
                ),
                xaxis={'categoryorder':'total descending'},
                title_font=dict(size=16, color="black")  # Titre en noir et plus grand
            )

            # Mise à jour des axes avec texte plus grand et noir
            fig.update_xaxes(
                title_font=dict(size=14, color="black"),
                tickfont=dict(size=12, color="black"),
                tickangle=45
            )
            fig.update_yaxes(title_font=dict(size=14, color="black"), tickfont=dict(size=12, color="black"))

            # Texte des valeurs en noir et plus grand
            fig.update_traces(textfont=dict(size=12, color="black"))

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Aucune donnée de catégorie disponible.")
    except Exception as e:
        st.error(f"Erreur lors de l'affichage des catégories de produits: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

    # Table des clients les plus valorisés
    st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
    st.markdown("<h3>Top 20 clients les plus valorisés</h3>", unsafe_allow_html=True)
    try:
        if not customer_data.empty:
            # Ajouter un sélecteur pour l'ordre de tri
            sort_options = {
                "estimated_annual_value": "Valeur annuelle estimée (décroissant)",
                "total_spend": "Dépense totale (décroissant)",
                "order_count": "Nombre de commandes (décroissant)",
                "average_order_value": "Valeur moyenne des commandes (décroissant)",
                "purchase_frequency_monthly": "Fréquence d'achat mensuelle (décroissant)"
            }

            selected_sort = st.selectbox(
                "Trier par:",
                options=list(sort_options.keys()),
                format_func=lambda x: sort_options[x],
                index=0  # Par défaut, tri par valeur annuelle estimée
            )

            # Sélectionner les colonnes pertinentes
            top_customers = customer_data[["customer_unique_id", "order_count", "total_spend",
                                        "average_order_value", "purchase_frequency_monthly",
                                        "estimated_annual_value", "customer_segment"]]

            # Trier selon la colonne sélectionnée
            top_customers = top_customers.sort_values(by=selected_sort, ascending=False)

            # Limiter le nombre de lignes pour l'affichage
            display_limit = st.slider("Nombre de clients à afficher", 5, 100, 20)
            top_customers = top_customers.head(display_limit)

            # Dupliquer le DataFrame pour conserver les valeurs numériques pour le style
            numeric_df = top_customers.copy()

            # Création d'une copie pour l'affichage avec formatage
            top_customers_display = top_customers.copy()
            top_customers_display["total_spend"] = top_customers_display["total_spend"].apply(lambda x: f"R$ {x:,.2f}")
            top_customers_display["average_order_value"] = top_customers_display["average_order_value"].apply(lambda x: f"R$ {x:,.2f}")
            top_customers_display["purchase_frequency_monthly"] = top_customers_display["purchase_frequency_monthly"].apply(lambda x: f"{x:.4f}")
            top_customers_display["estimated_annual_value"] = top_customers_display["estimated_annual_value"].apply(lambda x: f"R$ {x:,.2f}")

            # Renommer les colonnes pour l'affichage
            top_customers_display = top_customers_display.rename(columns={
                "customer_unique_id": "ID Client",
                "order_count": "Nb Commandes",
                "total_spend": "Dépense Totale",
                "average_order_value": "Valeur Moy. Commande",
                "purchase_frequency_monthly": "Fréq. Mensuelle",
                "estimated_annual_value": "Valeur Annuelle",
                "customer_segment": "Segment"
            })

            # Appliquer le style au DataFrame
            styled_df = numeric_df.style\
                .background_gradient(subset=["order_count"], cmap="Blues")\
                .background_gradient(subset=["total_spend"], cmap="Greens")\
                .background_gradient(subset=["average_order_value"], cmap="RdPu")\
                .background_gradient(subset=["purchase_frequency_monthly"], cmap="Oranges")\
                .background_gradient(subset=["estimated_annual_value"], cmap="RdYlGn")\
                .format({
                    "total_spend": "R$ {:.2f}",
                    "average_order_value": "R$ {:.2f}",
                    "purchase_frequency_monthly": "{:.4f}",
                    "estimated_annual_value": "R$ {:.2f}"
                })

            # Générer le HTML
            html_table = styled_df.to_html()

            # Remplacer les en-têtes de colonnes avec les noms français
            html_table = html_table.replace('>customer_unique_id<', '>ID Client<')
            html_table = html_table.replace('>order_count<', '>Nb Commandes<')
            html_table = html_table.replace('>total_spend<', '>Dépense Totale<')
            html_table = html_table.replace('>average_order_value<', '>Valeur Moy. Commande<')
            html_table = html_table.replace('>purchase_frequency_monthly<', '>Fréq. Mensuelle<')
            html_table = html_table.replace('>estimated_annual_value<', '>Valeur Annuelle<')
            html_table = html_table.replace('>customer_segment<', '>Segment<')

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
            csv = top_customers.to_csv(index=False)
            st.download_button(
                label="📥 Télécharger les données (CSV)",
                data=csv,
                file_name="olist_top_customers.csv",
                mime="text/csv",
                help="Télécharger les données des clients les plus valorisés au format CSV"
            )
        else:
            st.warning("Aucune donnée client disponible.")
    except Exception as e:
        st.error(f"Erreur lors de l'affichage des clients les plus valorisés: {e}")
    st.markdown("</div>", unsafe_allow_html=True)
    # Pied de page
    st.markdown("<div class='footer'>© 2023 Olist - Analyse des clients - Dernière mise à jour: {}</div>".format(datetime.now().strftime("%d/%m/%Y %H:%M")), unsafe_allow_html=True)