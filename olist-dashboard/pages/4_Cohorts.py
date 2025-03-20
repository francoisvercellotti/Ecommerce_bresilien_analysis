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
    page_title="Olist - Analyse des Cohortes",
    page_icon="📊",
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
    .metric-card-cohort {
        background-color: #1e88e5;
    }
    .metric-card-retention {
        background-color: #43a047;
    }
    .metric-card-revenue {
        background-color: #fb8c00;
    }
    .metric-card-aov {
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

    /* Style pour les légendes des graphiques */
    .js-plotly-plot .legend text {
        fill: black !important;
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
graph_height = 300
heatmap_height = 600

# Titre principal
st.markdown("<h1 class='main-header'>📊 Analyse des Cohortes Olist</h1>", unsafe_allow_html=True)

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

    # Nombre de mois à afficher dans les analyses de cohorte
    months_to_display = st.slider(
        "Nombre de mois à analyser",
        min_value=3,
        max_value=12,
        value=6,
        step=1
    )

    # Choix des cohortes à afficher
    st.markdown("<h3 class='sub-header'>Filtres avancés</h3>", unsafe_allow_html=True)

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
                    <div class='metric-card-cohort' style="background-color: #1e88e5; border-radius: 10px; padding: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); color: white; margin-bottom: 8px;">
                        <h3 style="margin-bottom:2px; font-size:1rem; font-weight:bold;">Total Clients</h3>
                        <h2 style="margin:0; font-size:2rem; font-weight:bold;">{format(int(total_customers), ',')}</h2>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col2:
                st.markdown(
                    f"""
                    <div class='metric-card-retention' style="background-color: #43a047; border-radius: 10px; padding: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); color: white; margin-bottom: 8px;">
                        <h3 style="margin-bottom:2px; font-size:1rem; font-weight:bold;">Rétention M+1</h3>
                        <h2 style="margin:0; font-size:2rem; font-weight:bold;">{avg_retention_1m:.2f}%</h2>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col3:
                st.markdown(
                    f"""
                    <div class='metric-card-retention' style="background-color: #fb8c00; border-radius: 10px; padding: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); color: white; margin-bottom: 8px;">
                        <h3 style="margin-bottom:2px; font-size:1rem; font-weight:bold;">Rétention M+3</h3>
                        <h2 style="margin:0; font-size:2rem; font-weight:bold;">{avg_retention_3m:.2f}%</h2>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col4:
                st.markdown(
                    f"""
                    <div class='metric-card-aov' style="background-color: #8e24aa; border-radius: 10px; padding: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); color: white; margin-bottom: 8px;">
                        <h3 style="margin-bottom:2px; font-size:1rem; font-weight:bold;">Revenu Moyen Initial</h3>
                        <h2 style="margin:0; font-size:2rem; font-weight:bold;">{format_currency(avg_revenue_per_customer)}</h2>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Créer une heatmap de rétention
            st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
            st.markdown("<h3>Heatmap de Rétention par Cohorte (%)</h3>", unsafe_allow_html=True)

            # Préparation des données pour la heatmap
            heatmap_data = cohort_data.pivot_table(
                index='cohort_month_str',
                columns='month_number',
                values='retention_rate',
                aggfunc='mean'
            )

            # Création de la heatmap avec Plotly
            fig_heatmap = px.imshow(
                heatmap_data,
                labels=dict(x="Mois après acquisition", y="Cohorte", color="Taux de rétention (%)"),
                x=heatmap_data.columns,
                y=heatmap_data.index,
                color_continuous_scale="Blues",
                aspect="auto"
            )

            # Ajustement des annotations avec texte en noir pour toutes les valeurs
            annotations = []
            for i in range(len(heatmap_data.index)):
                for j in range(len(heatmap_data.columns)):
                    if not pd.isna(heatmap_data.iloc[i, j]):
                        annotations.append(dict(
                            x=j,
                            y=i,
                            text=f"{heatmap_data.iloc[i, j]:.1f}%",
                            showarrow=False,
                            font=dict(
                                # Fixer la couleur du texte à noir pour toutes les valeurs
                                color="black",
                                size=10
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

            # Créer graphique de rétention par cohorte
            st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
            st.markdown("<h3>Courbes de Rétention par Cohorte</h3>", unsafe_allow_html=True)

            # Création du graphique en ligne
            fig_retention = px.line(
                cohort_data,
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

            # Créer graphique de revenu moyen par client
            st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
            st.markdown("<h3>Revenu Moyen par Client et par Cohorte</h3>", unsafe_allow_html=True)

            fig_revenue = px.line(
                cohort_data,
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
                tickprefix="R$ ",
                tickformat=",.2f",
                tickfont=dict(color="black")
            )

            st.plotly_chart(fig_revenue, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Tableau de synthèse des cohortes
            st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
            st.markdown("<h3>Tableau de Synthèse des Cohortes</h3>", unsafe_allow_html=True)

            # Préparation des données pour le tableau
            cohort_summary = cohort_data.pivot_table(
                index='cohort_month_str',
                columns='month_number',
                values='retention_rate',
                aggfunc='mean'
            ).reset_index()

            # Conserver les données numériques pour le style
            numeric_df = cohort_summary.copy()
            numeric_df.columns = ['Cohorte'] + [f'M+{i}' for i in numeric_df.columns[1:]]

            # Formatage pour l'affichage
            cohort_summary.columns = ['Cohorte'] + [f'M+{i}' for i in cohort_summary.columns[1:]]

            # Appliquer le style au DataFrame avec texte noir
            styled_df = numeric_df.style\
                .background_gradient(subset=numeric_df.columns[1:], cmap="Blues")\
                .format({col: "{:.2f}%" for col in numeric_df.columns[1:]})\
                .set_properties(**{'color': 'black'})  # Assurer que le texte est noir

            # Générer le HTML
            html_table = styled_df.to_html()

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
                color: black;
            }
            .scrollable-table th {
                color: black;
                background-color: white;
            }
            </style>
            """, unsafe_allow_html=True)

            # Envelopper le tableau dans un div avec défilement
            st.markdown(f'<div class="scrollable-table">{html_table}</div>', unsafe_allow_html=True)

            # Option de téléchargement
            cohort_csv = cohort_data.to_csv(index=False)
            st.download_button(
                label="📥 Télécharger les données de cohortes (CSV)",
                data=cohort_csv,
                file_name="olist_cohort_analysis.csv",
                mime="text/csv",
                help="Télécharger les données d'analyse de cohortes au format CSV"
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
                    color='customer_segment',
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
                    paper_bgcolor='white',
                    plot_bgcolor='white',
                    yaxis_gridcolor='lightgray',
                    xaxis=dict(
                        title_font_color="black",
                        tickfont_color="black"
                    ),
                    yaxis=dict(
                        title_font_color="black",
                        tickfont_color="black"
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

                # Formater les colonnes pour l'affichage
                display_rfm = rfm_data.copy()
                display_rfm['avg_monetary_value'] = display_rfm['avg_monetary_value'].apply(lambda x: format_currency(x))
                display_rfm['total_monetary_value'] = display_rfm['total_monetary_value'].apply(lambda x: format_currency(x))
                display_rfm['percentage'] = display_rfm['percentage'].apply(lambda x: f"{x:.2f}%")
                display_rfm['revenue_percentage'] = display_rfm['revenue_percentage'].apply(lambda x: f"{x:.2f}%")

                # Renommer les colonnes pour l'affichage
                display_rfm = display_rfm.rename(columns={
                    'customer_segment': 'Segment',
                    'customer_count': 'Nombre de clients',
                    'percentage': '% des clients',
                    'avg_recency_days': 'Récence moyenne (jours)',
                    'avg_frequency': 'Fréquence moyenne',
                    'avg_monetary_value': 'Valeur moyenne',
                    'total_monetary_value': 'Valeur totale',
                    'revenue_percentage': '% du revenu total'
                })

                # Appliquer le style au DataFrame avec texte noir
                styled_rfm = numeric_rfm.style\
                    .background_gradient(subset=['avg_recency_days'], cmap="Reds_r")\
                    .background_gradient(subset=['avg_frequency'], cmap="Blues")\
                    .background_gradient(subset=['avg_monetary_value'], cmap="Greens")\
                    .background_gradient(subset=['total_monetary_value'], cmap="Purples")\
                    .background_gradient(subset=['revenue_percentage'], cmap="RdYlGn")\
                    .format({
                        'avg_recency_days': "{:.2f}",
                        'avg_frequency': "{:.2f}",
                        'avg_monetary_value': "R$ {:.2f}",
                        'total_monetary_value': "R$ {:.2f}",
                        'percentage': "{:.2f}%",
                        'revenue_percentage': "{:.2f}%"
                    })\
                    .set_properties(**{'color': 'black'})  # Assurer que le texte est noir

                # Générer le HTML
                html_table = styled_rfm.to_html()

                # Remplacer les en-têtes de colonnes avec les noms français
                html_table = html_table.replace('>customer_segment<', '>Segment<')
                html_table = html_table.replace('>customer_count<', '>Nombre de clients<')
                html_table = html_table.replace('>percentage<', '>% des clients<')
                html_table = html_table.replace('>avg_recency_days<', '>Récence moyenne (jours)<')
                html_table = html_table.replace('>avg_frequency<', '>Fréquence moyenne<')
                html_table = html_table.replace('>avg_monetary_value<', '>Valeur moyenne<')
                html_table = html_table.replace('>total_monetary_value<', '>Valeur totale<')
                html_table = html_table.replace('>revenue_percentage<', '>% du revenu total<')

                # Ajouter le CSS pour le défilement et assurer le texte noir
                st.markdown("""
                <style>
                .scrollable-table {
                    height: 400px;
                    overflow-y: auto;
                    display: block;
                }
                .scrollable-table table {
                    width: 100%;
                    color: black;
                }
                .scrollable-table th {
                    color: black;
                    background-color: white;
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

                fig_monetary = px.bar(
                    rfm_data,
                    x='customer_segment',
                    y='avg_monetary_value',
                    color='customer_segment',
                    text='avg_monetary_value',
                    labels={
                        'customer_segment': 'Segment',
                        'avg_monetary_value': 'Valeur moyenne (R$)'
                    },
                    height=graph_height
                )

                fig_monetary.update_traces(
                    texttemplate='R$ %{text:.2f}',
                    textposition='outside',
                    textfont=dict(color="black")
                )

                fig_monetary.update_layout(
                    margin=dict(l=50, r=20, t=20, b=100),
                    font=dict(color="black"),
                    xaxis_tickangle=-45,
                    showlegend=False,
                    yaxis=dict(
                        title="Valeur moyenne (R$)",
                        title_font_color="black",
                        tickfont_color="black",
                        gridcolor='lightgray'
                    ),
                    xaxis=dict(
                        title_font_color="black",
                        tickfont_color="black"
                    ),
                    paper_bgcolor='white',
                    plot_bgcolor='white'
                )

                # Formatage de l'axe y pour afficher les valeurs monétaires
                fig_monetary.update_yaxes(
                    tickprefix="R$ ",
                    tickformat=",.2f",
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
                    height=450,
                    margin=dict(l=50, r=20, t=20, b=50),
                    font=dict(color="black"),
                    legend=dict(
                        orientation='h',
                        yanchor='bottom',
                        y=-0.1,
                        xanchor='center',
                        x=0.5,
                        font=dict(color="black")
                    ),
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

