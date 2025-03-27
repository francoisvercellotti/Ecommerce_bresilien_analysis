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
    page_title="Olist - Génération de rapport",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <div style="background: linear-gradient(90deg, #4e8df5, #83b3f7); padding:15px; border-radius:10px; margin-bottom:30px">
        <h1 style="color:white; text-align:center; font-size:48px; font-weight:bold">
            RAPPORT PERIODIQUE
        </h1>
    </div>
    """, unsafe_allow_html=True)

# Ajout du CSS personnalisé
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
    .metric-card-sales {
        background-color: #1e88e5;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        color: white;
        margin-bottom: 8px;
    }
    .metric-card-revenue {
        background-color: #43a047;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        color: white;
        margin-bottom: 8px;
    }
    .metric-card-average {
        background-color: #fb8c00;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        color: white;
        margin-bottom: 8px;
    }
    .metric-card-delivery {
        background-color: #8e24aa;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        color: white;
        margin-bottom: 8px;
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
</style>
""", unsafe_allow_html=True)

# Fonction pour générer le rapport
@st.cache_data(ttl=3600)
def generate_report(start_date, end_date):
    report_query = f"""
    WITH sales_metrics AS (
        SELECT
            COUNT(DISTINCT o.order_id) AS total_orders,
            SUM(oi.price + oi.freight_value) AS total_revenue,
            COUNT(DISTINCT c.customer_unique_id) AS unique_customers,
            AVG(oi.price + oi.freight_value) AS avg_order_value
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_purchase_timestamp BETWEEN '{start_date}' AND '{end_date}'
    ),
    delivery_performance AS (
        SELECT
            COUNT(*) AS total_delivered,
            SUM(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date THEN 1 ELSE 0 END) AS late_deliveries,
            AVG(EXTRACT(EPOCH FROM (order_delivered_customer_date - order_purchase_timestamp))/86400) AS avg_delivery_days
        FROM orders
        WHERE order_status = 'delivered'
          AND order_delivered_customer_date BETWEEN '{start_date}' AND '{end_date}'
    ),
    customer_satisfaction AS (
        SELECT
            AVG(review_score) AS avg_review_score,
            COUNT(*) AS total_reviews,
            SUM(CASE WHEN review_score >= 4 THEN 1 ELSE 0 END) AS positive_reviews,
            SUM(CASE WHEN review_score <= 2 THEN 1 ELSE 0 END) AS negative_reviews
        FROM order_reviews r
        JOIN orders o ON r.order_id = o.order_id
        WHERE o.order_purchase_timestamp BETWEEN '{start_date}' AND '{end_date}'
    ),
    new_customers AS (
        SELECT
            COUNT(DISTINCT c.customer_unique_id) AS new_customer_count
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_purchase_timestamp BETWEEN '{start_date}' AND '{end_date}'
          AND NOT EXISTS (
              SELECT 1
              FROM orders o2
              JOIN customers c2 ON o2.customer_id = c2.customer_id
              WHERE c2.customer_unique_id = c.customer_unique_id
                AND o2.order_purchase_timestamp < '{start_date}'
          )
    )
    SELECT
        '{start_date}' AS report_start_date,
        '{end_date}' AS report_end_date,
        sm.total_orders,
        sm.total_revenue,
        sm.unique_customers,
        sm.avg_order_value,
        nc.new_customer_count,
        dp.total_delivered,
        dp.late_deliveries,
        dp.avg_delivery_days,
        cs.avg_review_score,
        cs.positive_reviews,
        cs.negative_reviews
    FROM sales_metrics sm
    CROSS JOIN delivery_performance dp
    CROSS JOIN customer_satisfaction cs
    CROSS JOIN new_customers nc
    """
    return execute_raw_query(report_query)

# Partie Sidebar pour la sélection de la période
with st.sidebar:
    st.markdown('<h2 style="text-align: center; padding-bottom: 10px;">FILTRES</h2>', unsafe_allow_html=True)
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown('<div class="filter-section-title">PÉRIODE</div>', unsafe_allow_html=True)
    try:
        date_range = execute_query("date_range.sql")
        if not date_range.empty:
            min_date = date_range["min_date"].iloc[0].date()
            max_date = date_range["max_date"].iloc[0].date()
            period_options = [
                "Période personnalisée",
                "Derniers 30 jours",
                "Derniers 90 jours",
                "Dernière année",
                "Tout l'historique"
            ]
            selected_period = st.selectbox("Choisir une période", period_options)
            if selected_period == "Période personnalisée":
                start_date = st.date_input("Date de début", min_date, min_value=min_date, max_value=max_date)
                end_date = st.date_input("Date de fin", max_date, min_value=min_date, max_value=max_date)
            else:
                end_date = max_date
                if selected_period == "Derniers 30 jours":
                    start_date = end_date - timedelta(days=30)
                elif selected_period == "Derniers 90 jours":
                    start_date = end_date - timedelta(days=90)
                elif selected_period == "Dernière année":
                    start_date = end_date - timedelta(days=365)
                else:  # Tout l'historique
                    start_date = min_date
                st.write(f"Période sélectionnée : {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")
        else:
            st.warning("Impossible de charger la plage de dates. Utilisation de la période complète.")
            start_date = None
            end_date = None
    except Exception as e:
        st.error(f"Erreur lors du chargement des dates: {e}")
        start_date = None
        end_date = None

# Conversion des dates au format SQL si nécessaire
sql_start_date = start_date.strftime('%Y-%m-%d') if start_date else None
sql_end_date = end_date.strftime('%Y-%m-%d') if end_date else None

# Zone principale : Bouton pour générer le rapport
st.markdown('<h2 style="text-align: center;">Génération du rapport</h2>', unsafe_allow_html=True)

if st.button("Générer le rapport"):
    if sql_start_date and sql_end_date:
        with st.spinner("Génération du rapport en cours..."):
            try:
                # Génération du rapport
                report_df = generate_report(sql_start_date, sql_end_date)
                st.success("Le rapport a été généré avec succès !")

                # On supprime l'affichage par défaut pour éviter le doublon
                # st.dataframe(report_df)

                # Mise en forme du DataFrame sans gradient
                styled_df = report_df.style\
                    .format({
                        "total_revenue": "{:,.0f}",
                        "avg_review_score": "{:.2f}",
                        "avg_order_value": "{:.2f}",
                        "avg_delivery_days": "{:.1f}",
                    })

                # Appliquer un fond bleu clair à l'entête
                styled_df = styled_df.set_table_styles([
                    {
                        'selector': 'th',
                        'props': [
                            ('background-color', '#1e88e5'),
                            ('color', 'white'),
                            ('text-align', 'center')
                        ]
                    }
                ])

                # Générer le HTML sans index
                html_table = styled_df.hide(axis="index").to_html()

                # Remplacer les en-têtes de colonnes par des noms en français
                html_table = html_table.replace('>total_orders<', '>Commandes<')
                html_table = html_table.replace('>total_revenue<', '>Revenu total<')
                html_table = html_table.replace('>unique_customers<', '>Clients uniques<')
                html_table = html_table.replace('>avg_order_value<', '>Valeur moyenne commande<')
                html_table = html_table.replace('>new_customer_count<', '>Nouveaux clients<')
                html_table = html_table.replace('>total_delivered<', '>Livraisons totales<')
                html_table = html_table.replace('>avg_review_score<', '>Note moyenne<')
                html_table = html_table.replace('>late_deliveries<', '>Retards de livraison<')
                html_table = html_table.replace('>avg_delivery_days<', '>Jours moyens livraison<')
                html_table = html_table.replace('>positive_reviews<', '>Avis positifs<')
                html_table = html_table.replace('>negative_reviews<', '>Avis négatifs<')

                # Afficher le rapport stylisé dans Streamlit (une seule fois)
                st.markdown(html_table, unsafe_allow_html=True)

                # Option pour télécharger le rapport en CSV
                csv_data = report_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Télécharger le rapport en CSV",
                    data=csv_data,
                    file_name=f"rapport_{sql_start_date}_to_{sql_end_date}.csv",
                    mime='text/csv'
                )
            except Exception as e:
                st.error(f"Erreur lors de la génération du rapport : {e}")
    else:
        st.error("Les dates sélectionnées ne sont pas valides.")

# Pied de page
st.markdown("<div class='footer'>© 2023 Olist - Rapport periodique - Dernière mise à jour: {}</div>".format(datetime.now().strftime("%d/%m/%Y %H:%M")), unsafe_allow_html=True)

# Ajouter un peu d'espace en bas
st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)