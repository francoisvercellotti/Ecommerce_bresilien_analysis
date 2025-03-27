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
import calendar

# Configuration de la page
st.set_page_config(
    page_title="Olist - Prévisions",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"  # Barre latérale visible par défaut
)

st.markdown("""
    <div style="background: linear-gradient(90deg, #4e8df5, #83b3f7); padding:15px; border-radius:10px; margin-bottom:30px">
        <h1 style="color:white; text-align:center; font-size:48px; font-weight:bold">
            PRÉVISIONS ET ANALYSES PREDICTIVES
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

# Chargement des données avec cache
@st.cache_data(ttl=3600)
def load_date_range():
    return execute_query("date_range.sql")

@st.cache_data(ttl=3600)
def load_sales_prediction_pattern():
    return execute_raw_query("SELECT * FROM vw_prediction_sales_pattern ORDER BY month, day_of_week")

@st.cache_data(ttl=3600)
def load_seasonal_trends():
    return execute_raw_query("SELECT * FROM vw_seasonal_trends ORDER BY month_number")

@st.cache_data(ttl=3600)
def predict_sales_for_date(target_date):
    query = f"""
    SELECT * FROM predict_sales_for_date('{target_date}')
    """
    return execute_raw_query(query)

@st.cache_data(ttl=3600)
def project_sales(target_month, target_year, base_revenue):
    query = f"""
    SELECT * FROM project_sales({target_month}, {target_year}, {base_revenue})
    """
    return execute_raw_query(query)

@st.cache_data(ttl=3600)
def load_customer_churn_risk():
    return execute_raw_query("""
    SELECT
        churn_risk_level,
        COUNT(*) as customer_count,
        ROUND(AVG(churn_risk_score), 2) as avg_risk_score,
        ROUND(AVG(days_since_last_purchase), 0) as avg_days_since_purchase,
        ROUND(AVG(total_orders), 1) as avg_orders,
        ROUND(AVG(avg_review_score), 2) as avg_satisfaction
    FROM vw_customer_churn_risk
    GROUP BY churn_risk_level
    ORDER BY
        CASE
            WHEN churn_risk_level = 'Élevé' THEN 1
            WHEN churn_risk_level = 'Moyen' THEN 2
            WHEN churn_risk_level = 'Faible' THEN 3
        END
    """)

@st.cache_data(ttl=3600)
def load_satisfaction_predictor():
    return execute_raw_query("""
    SELECT * FROM vw_satisfaction_predictor
    ORDER BY corr_delivery_time_review ASC
    LIMIT 20
    """)

# Constantes pour les graphiques
graph_height = 400
heatmap_height = 500


# Filtres dans la sidebar
with st.sidebar:
    st.markdown('<h2 style="text-align: center; padding-bottom: 10px;">FILTRES</h2>', unsafe_allow_html=True)

    # Section
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown('<div class="filter-section-title">Paramètres de Prévision</div>', unsafe_allow_html=True)

    # Date de prévision
    today = datetime.now().date()
    forecast_date = st.date_input(
        "Date de prévision",
        value=today + timedelta(days=1),
        min_value=today,
        max_value=today + timedelta(days=365)
    )

    # Montant de base pour les projections
    base_revenue = st.number_input(
        "Revenu mensuel de base (R$)",
        min_value=10000.0,
        max_value=1000000.0,
        value=100000.0,
        step=10000.0,
        format="%.2f"
    )

    # Année et mois cible pour les projections saisonnières
    target_year = st.number_input("Année cible", min_value=today.year, max_value=today.year + 5, value=today.year)
    target_month = st.slider("Mois cible", min_value=1, max_value=12, value=today.month)

    # Options d'affichage
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown('<div class="filter-section-title">Options d''Affichage</div>', unsafe_allow_html=True)
    show_sales_pattern = st.checkbox("Afficher les tendances de ventes", value=True)
    show_seasonal_trends = st.checkbox("Afficher les tendances saisonnières", value=True)
    show_churn_risk = st.checkbox("Afficher le risque d'attrition", value=True)
    show_satisfaction_predictors = st.checkbox("Afficher les prédicteurs de satisfaction", value=True)

# Création du layout principal
layout_container = st.container()

with layout_container:


    # Carte de métriques pour la prévision de date
    # Section 1: Prévisions pour la date spécifiée
    st.markdown("<h2 class='sub-header'>Prévisions pour la date spécifiée</h2>", unsafe_allow_html=True)
    try:
        sales_prediction = predict_sales_for_date(forecast_date)

        if not sales_prediction.empty:
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(
                    f"""
                    <div class='metric-card metric-card-customers' style='margin-top: 20px;'>
                        <div class='metric-label'>Revenu prévu</div>
                        <div class='metric-value'>{format_currency(sales_prediction['predicted_revenue'].iloc[0])}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col2:
                st.markdown(
                    f"""
                    <div class='metric-card metric-card-frequency' style='margin-top: 20px;'>
                        <div class='metric-label'>Commandes prévues</div>
                        <div class='metric-value'>{sales_prediction['predicted_orders'].iloc[0]:.0f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col3:
                confidence = sales_prediction['confidence_level'].iloc[0]
                confidence_color = "#43a047" if confidence == "Élevé" else "#fb8c00" if confidence == "Moyen" else "#e53935"

                st.markdown(
                    f"""
                    <div class='metric-card metric-card-clv' style='margin-top: 20px; background-color: {confidence_color} !important;'>
                        <div class='metric-label'>Niveau de confiance</div>
                        <div class='metric-value'>{confidence}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Afficher les détails de la prévision
            st.markdown(f"""
            <div style="background-color: #1e3a5f; border-radius: 10px; padding: 20px; margin-top: 15px; margin-top: 20px;margin-bottom: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                <h3 style="color: white; font-size: 24px; margin-bottom: 15px;">Prévision pour le <span style="font-weight: bold;">{forecast_date.strftime('%d/%m/%Y')}</span></h3>
                <p style="color: white; font-size: 18px; margin-bottom: 10px;">Jour {forecast_date.weekday()} de la semaine</p>
                <p style="color: #a8c7ff; font-size: 16px; font-style: italic;">Cette prévision est basée sur les tendances historiques pour des jours similaires.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
                st.warning("Aucune prévision disponible pour la date sélectionnée.")
    except Exception as e:
                st.error(f"Erreur lors du chargement des prévisions: {e}")
    # Section 2: Projection des ventes
    st.markdown("<h2 class='sub-header'>Projection des ventes</h2>", unsafe_allow_html=True)

    try:
        projected_sales = project_sales(target_month, target_year, base_revenue)

        if not projected_sales.empty:
            # Afficher la projection

            month_name = projected_sales['projected_month'].iloc[0].strip()
            projected_revenue = projected_sales['projected_revenue'].iloc[0]

            st.markdown(f"""
            <div style="background-color: #2196f3; border-radius: 10px; padding: 25px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.2); margin: 15px 0;">
                <h3 style="font-size: 22px; color: white; margin-bottom: 15px;">Projection pour {month_name} {target_year}</h3>
                <h1 style="font-size: 3.5rem; color: white; margin: 20px 0; font-weight: bold; text-shadow: 1px 1px 3px rgba(0,0,0,0.3);">{format_currency(projected_revenue)}</h1>
                <p style="font-size: 16px; color: #e3f2fd; margin-top: 15px;">Basée sur un revenu mensuel de base de <span style="font-weight: bold;">{format_currency(base_revenue)}</span> ajusté par les indices saisonniers.</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("Aucune projection disponible pour le mois et l'année sélectionnés.")
    except Exception as e:
        st.error(f"Erreur lors du chargement des projections: {e}")


# Section 3: Tendances de ventes
if show_sales_pattern:
    st.markdown("<h2 class='sub-header'>Tendances de ventes par jour de la semaine</h2>", unsafe_allow_html=True)

    try:
        sales_pattern = load_sales_prediction_pattern()

        if not sales_pattern.empty:
            # Créer un heatmap des tendances de ventes

            st.markdown("<h3 style='color: white;'>Heatmap des tendances de ventes</h3>", unsafe_allow_html=True)

            # Préparer les données pour le heatmap
            pivot_data = sales_pattern.pivot(index='day_of_week', columns='month', values='avg_revenue_by_day')

            # Créer le heatmap
            fig = px.imshow(
                pivot_data,
                labels=dict(x="Mois", y="Jour de la semaine", color="Revenu moyen"),
                x=[f"Mois {i}" for i in range(1, 13)],
                y=[f"Jour {i}" for i in range(0, 7)],
                color_continuous_scale="Blues",
                height=heatmap_height
            )

            fig.update_layout(
            font=dict(color='black'),
            xaxis_title_font=dict(color='black'),
            yaxis_title_font=dict(color='black'),
            legend_font=dict(color='black'),
            margin=dict(l=40, r=40, t=40, b=40),
            coloraxis_colorbar=dict(title="Revenu moyen (R$)"),
            paper_bgcolor='white',
            plot_bgcolor='white'
        )
            # Mise à jour des axes
            fig.update_xaxes(tickfont=dict(color='black'))
            fig.update_yaxes(tickfont=dict(color='black'))
            fig.update_yaxes(
                tickmode='array',
                tickvals=[0, 1, 2, 3, 4, 5, 6],
                ticktext=['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'],
                tickfont=dict(color='black')
            )


            # Mise à jour de la colorbar (associée à la coloraxis)
            fig.update_coloraxes(colorbar=dict(
                tickfont=dict(color='black'),
                title_font=dict(color='black')
            ))



            st.plotly_chart(fig, use_container_width=True)

            # Afficher les statistiques par jour de la semaine
            st.markdown("<h3 style='color: white;'>Statistiques par jour de la semaine</h3>", unsafe_allow_html=True)

            day_stats = sales_pattern.groupby('day_of_week').agg({
                'avg_revenue_by_day': 'mean',
                'avg_orders_by_day': 'mean'
            }).reset_index()

            day_stats['day_name'] = day_stats['day_of_week'].apply(lambda x: ['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'][int(x)])

            # Trier par jour de la semaine
            day_stats = day_stats.sort_values('day_of_week')

            fig2 = go.Figure()

            fig2.add_trace(go.Bar(
                x=day_stats['day_name'],
                y=day_stats['avg_revenue_by_day'],
                name='Revenu moyen',
                marker_color='#1e88e5'
            ))

            fig2.add_trace(go.Scatter(
                x=day_stats['day_name'],
                y=day_stats['avg_orders_by_day'] * 100,  # Multiplier pour l'échelle
                name='Commandes moyennes',
                yaxis='y2',
                mode='lines+markers',
                marker_color='#fb8c00',
                line=dict(width=3)
            ))

            fig2.update_layout(
                title=dict(
                    text=' ',
                    font=dict(color='black')  # Définir la couleur du titre en noir
                ),
                xaxis=dict(title='Jour de la semaine', color='black'),
                yaxis=dict(title='Revenu moyen (R$)', side='left', showgrid=True, color='black'),
                yaxis2=dict(
                    title='Commandes moyennes',
                    side='right',
                    overlaying='y',
                    showgrid=False,
                    color='black',
                    title_font=dict(color='black')  # Définir la couleur du titre de l'axe y de droite en noir
                ),
                legend=dict(x=4.5, y=1.2, bgcolor='rgba(255,255,255,0.8)'),
                font=dict(color='black'),
                xaxis_title_font=dict(color='black'),
                yaxis_title_font=dict(color='black'),
                legend_font=dict(color='black'),
                height=graph_height,
                paper_bgcolor='white',
                plot_bgcolor='white'
            )

            fig2.update_xaxes(tickfont=dict(color='black'))
            fig2.update_yaxes(tickfont=dict(color='black'))

            st.plotly_chart(fig2, use_container_width=True)

            st.markdown("</div>", unsafe_allow_html=True)

        else:
            st.warning("Aucune donnée de tendance de ventes disponible.")
    except Exception as e:
        st.error(f"Erreur lors du chargement des tendances de ventes: {e}")

# Section 4: Tendances saisonnières
if show_seasonal_trends:
    st.markdown("<h2 class='sub-header'>Tendances saisonnières</h2>", unsafe_allow_html=True)

    try:
        seasonal_trends = load_seasonal_trends()

        if not seasonal_trends.empty:

            st.markdown("<h3 style='color: white;'>Indices saisonniers par mois</h3>", unsafe_allow_html=True)

            # Copier et renommer les colonnes
            styled_trends = seasonal_trends.copy()
            styled_trends['month_number'] = styled_trends['month_number'].astype(int)
            styled_trends = styled_trends.rename(columns={
                'month_number': 'Numéro du mois',
                'month_name': 'Nom du mois',
                'avg_monthly_revenue': 'Revenu mensuel moyen',
                'avg_monthly_orders': 'Commandes mensuelles moyennes',
                'revenue_seasonal_index': 'Indice saisonnier (Revenu)',
                'orders_seasonal_index': 'Indice saisonnier (Commandes)'
            })

            # Définir les colonnes numériques pour le dégradé
            numeric_cols = [
                'Revenu mensuel moyen',
                'Commandes mensuelles moyennes',
                'Indice saisonnier (Revenu)',
                'Indice saisonnier (Commandes)'
            ]
            for col in numeric_cols:
                styled_trends[col] = pd.to_numeric(styled_trends[col], errors='coerce')

            # Appliquer le style :
            # - Fond gris pour "Numéro du mois" et "Nom du mois"
            # - Dégradé pour les colonnes numériques
            # - Formatage des valeurs (monétaires et indices)
            styled_df = styled_trends.style \
                .applymap(lambda v: 'background-color: lightgrey; color: black', subset=['Numéro du mois', 'Nom du mois']) \
                .background_gradient(subset=numeric_cols, cmap="Blues") \
                .format({
                    'Revenu mensuel moyen': lambda x: f"R$ {x:,.2f}" if pd.notnull(x) else "N/A",
                    'Commandes mensuelles moyennes': lambda x: f"{x:,.2f}" if pd.notnull(x) else "N/A",
                    'Indice saisonnier (Revenu)': lambda x: f"{x:.2f}" if pd.notnull(x) else "N/A",
                    'Indice saisonnier (Commandes)': lambda x: f"{x:.2f}" if pd.notnull(x) else "N/A"
                }) \
                .set_table_styles([
                    {
                        'selector': 'th',
                        'props': [
                            ('background-color', '#1e88e5'),
                            ('color', 'white'),
                            ('text-align', 'center'),
                            ('font-weight', 'bold'),
                            ('padding', '8px')
                        ]
                    },
                    {
                        'selector': 'td',
                        'props': [
                            ('padding', '8px'),
                            ('text-align', 'right')
                        ]
                    }
                ])

            # Convertir le style en HTML
            html_table = styled_df.hide(axis="index").to_html()

            # Ajouter du CSS pour le style du tableau (optionnel)
            st.markdown("""
            <style>
            .styled-table {
                width: 100%;
                border-collapse: collapse;
                font-size: 0.9em;
            }
            .styled-table thead tr {
                background-color: #1e88e5;
                color: white;
                text-align: center;
            }
            .styled-table tbody tr:nth-of-type(even) {
                background-color: #f3f3f3;
            }
            .styled-table td, .styled-table th {
                padding: 8px 12px;
                border: 1px solid #ddd;
            }
            .scrollable-table {
                max-height: 400px;
                overflow-y: auto;
                display: block;
                margin-top: 15px;
            }
            </style>
            """, unsafe_allow_html=True)

            st.markdown(f'<div class="scrollable-table">{html_table}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("Aucune donnée de tendance saisonnière disponible.")
    except Exception as e:
        st.error(f"Erreur lors du chargement des tendances saisonnières: {e}")


# Section 5: Risque d'attrition des clients
if show_churn_risk:
    st.markdown("<h2 class='sub-header'>Risque d'attrition des clients</h2>", unsafe_allow_html=True)

    try:
        churn_risk = load_customer_churn_risk()

        if not churn_risk.empty:

            st.markdown("<h3 style='color: white;'>Analyse du risque d'attrition</h3>", unsafe_allow_html=True)

            # Créer un graphique du risque d'attrition
            fig = go.Figure()

            # Définir les couleurs en fonction du niveau de risque
            colors = {
                'Élevé': '#e53935',
                'Moyen': '#fb8c00',
                'Faible': '#43a047'
            }

            # Créer un graphique en barres pour le nombre de clients
            fig.add_trace(go.Bar(
                x=churn_risk['churn_risk_level'],
                y=churn_risk['customer_count'],
                name='Nombre de clients',
                marker_color=[colors[level] for level in churn_risk['churn_risk_level']],
                text=churn_risk['customer_count'],
                textposition='auto'
            ))

            fig.update_layout(
                title='Répartition des clients par niveau de risque d\'attrition',
                xaxis=dict(title='Niveau de risque', color='black'),
                yaxis=dict(title='Nombre de clients', color='black'),
                height=graph_height,
                paper_bgcolor='white',
                plot_bgcolor='white',
                font=dict(color='black'),
                xaxis_title_font=dict(color='black'),
                yaxis_title_font=dict(color='black'),
                legend_font=dict(color='black')
            )
            # Masquer la grille verticale et afficher la grille horizontale en gris
            fig.update_xaxes(tickfont=dict(color='black'), showgrid=False)
            fig.update_yaxes(tickfont=dict(color='black'), showgrid=True, gridcolor='grey')
            fig.update_coloraxes(colorbar=dict(tickfont=dict(color='black'), title_font=dict(color='black')))


            st.plotly_chart(fig, use_container_width=True)

            # Afficher les métriques par niveau de risque
            col1, col2, col3 = st.columns(3)

            for i, (_, row) in enumerate(churn_risk.iterrows()):
                risk_level = row['churn_risk_level']
                color = colors[risk_level]

                with [col1, col2, col3][i]:
                    st.markdown(
                        f"""
                        <div style="background-color: {color}; border-radius: 10px; padding: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); color: white; margin-bottom: 8px;">
                            <h3 style="margin-bottom:2px; font-size:1.5rem; font-weight:300;">Risque {risk_level}</h3>
                            <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                                <div>
                                    <p>Clients: <strong>{row['customer_count']}</strong></p>
                                    <p>Score moyen: <strong>{row['avg_risk_score']}</strong></p>
                                </div>
                                <div>
                                    <p>Jours depuis achat: <strong>{row['avg_days_since_purchase']:.0f}</strong></p>
                                    <p>Satisfaction: <strong>{row['avg_satisfaction']}</strong></p>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            # Ajouter une table avec les détails
            st.markdown("<h4 style='color: white; margin-top: 15px;'>Détails par niveau de risque</h4>", unsafe_allow_html=True)

            # Préparer les données pour le tableau
            churn_table = churn_risk.copy()
            churn_table = churn_table.rename(columns={
                'churn_risk_level': 'Niveau de risque',
                'customer_count': 'Nombre de clients',
                'avg_risk_score': 'Score moyen',
                'avg_days_since_purchase': 'Jours depuis achat',
                'avg_orders': 'Commandes moyennes',
                'avg_satisfaction': 'Satisfaction moyenne'
            })

            # Formater les nombres
            churn_table['Jours depuis achat'] = churn_table['Jours depuis achat'].round().astype(int)
            churn_table['Score moyen'] = churn_table['Score moyen'].apply(lambda x: f"{x:.2f}")
            churn_table['Commandes moyennes'] = churn_table['Commandes moyennes'].apply(lambda x: f"{x:.1f}")
            churn_table['Satisfaction moyenne'] = churn_table['Satisfaction moyenne'].apply(lambda x: f"{x:.2f}")

            # Générer le style pour le tableau
            def color_risk_level(value):
                """Applique la couleur en fonction du niveau de risque"""
                if value == "Élevé":
                    return "background-color: #e53935; color: white"
                elif value == "Moyen":
                    return "background-color: #fb8c00; color: white"
                elif value == "Faible":
                    return "background-color: #43a047; color: white"
                return ""

            # Appliquer les styles
            styled_df = churn_table.style \
                .applymap(color_risk_level, subset=['Niveau de risque']) \
                .background_gradient(cmap="Blues", subset=['Nombre de clients', 'Score moyen',
                                                        'Jours depuis achat', 'Commandes moyennes',
                                                        'Satisfaction moyenne']) \
                .set_table_styles([
                    {
                        'selector': 'th',
                        'props': [
                            ('background-color', '#1e88e5'),
                            ('color', 'white'),
                            ('text-align', 'center'),
                            ('font-weight', 'bold'),
                            ('padding', '8px')
                        ]
                    }
                ])


            # Générer HTML et afficher
            html_table = styled_df.hide(axis="index").to_html()
            st.markdown(f'<div class="scrollable-table">{html_table}</div>', unsafe_allow_html=True)


            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("Aucune donnée de risque d'attrition disponible.")
    except Exception as e:
        st.error(f"Erreur lors du chargement du risque d'attrition: {e}")

# Section 6: Prédicteurs de satisfaction
if show_satisfaction_predictors:
    st.markdown("<h2 class='sub-header'>Prédicteurs de satisfaction client</h2>", unsafe_allow_html=True)

    try:
        satisfaction_predictors = load_satisfaction_predictor()

        if not satisfaction_predictors.empty:

            st.markdown("<h3 style='color: white;'>Résumé tabulaire</h3>", unsafe_allow_html=True)

            # Sélectionner les 10 premières lignes et copier le DataFrame
            styled_predictors = satisfaction_predictors.head(10).copy()

            # Renommer les colonnes pour une meilleure lisibilité
            styled_predictors = styled_predictors.rename(columns={
                'product_category_name_english': 'Catégorie de produit',
                'order_count': 'Nombre de commandes',
                'avg_review_score': 'Score moyen',
                'late_delivery_rate': 'Taux de livraison tardive',
                'avg_delivery_time': 'Temps de livraison moyen (jours)',
                'avg_freight_ratio': 'Ratio de fret moyen',
                'corr_delivery_time_review': 'Corrélation temps/satisfaction',
                'corr_freight_ratio_review': 'Corrélation fret/satisfaction',
                'corr_price_review': 'Corrélation prix/satisfaction'
            })

            # Formater certaines colonnes numériques
            for col in ['Taux de livraison tardive', 'Temps de livraison moyen (jours)', 'Ratio de fret moyen']:
                styled_predictors[col] = styled_predictors[col].apply(lambda x: f"{x:.2f}")

            for col in ['Corrélation temps/satisfaction', 'Corrélation fret/satisfaction', 'Corrélation prix/satisfaction']:
                styled_predictors[col] = styled_predictors[col].apply(lambda x: f"{x:.3f}")

            # S'assurer que les colonnes servant au tri sont de type numérique
            styled_predictors['Nombre de commandes'] = pd.to_numeric(styled_predictors['Nombre de commandes'], errors='coerce')
            styled_predictors['Score moyen'] = pd.to_numeric(styled_predictors['Score moyen'], errors='coerce')

            # Ajout d'un sélecteur pour choisir la colonne de tri
            sort_options = {
                'Catégorie de produit': 'Catégorie de produit',
                'Nombre de commandes': 'Nombre de commandes',
                'Score moyen': 'Score moyen',
                'Taux de livraison tardive': 'Taux de livraison tardive',
                'Temps de livraison moyen (jours)': 'Temps de livraison moyen (jours)',
                'Ratio de fret moyen': 'Ratio de fret moyen',
                'Corrélation temps/satisfaction': 'Corrélation temps/satisfaction',
                'Corrélation fret/satisfaction': 'Corrélation fret/satisfaction',
                'Corrélation prix/satisfaction': 'Corrélation prix/satisfaction'
            }

            selected_sort = st.selectbox(
                "Trier par :",
                options=list(sort_options.keys()),
                format_func=lambda x: sort_options[x],
                index=0  # Par défaut, tri par 'Catégorie de produit'
            )

            # Sélection de l'ordre de tri (ascendant ou descendant)
            sort_order = st.radio(
                "Ordre :",
                ["Décroissant", "Croissant"],
                horizontal=True,
                index=0  # Par défaut, décroissant
            )
            ascending = True if sort_order == "Croissant" else False

            # Appliquer le tri sur le DataFrame
            styled_predictors = styled_predictors.sort_values(by=selected_sort, ascending=ascending)

            # Appliquer le style : dégradé sur toutes les colonnes sauf 'Catégorie de produit'
            styled_df = styled_predictors.style \
                .applymap(lambda v: 'background-color: #f0f0f0; color: black', subset=['Catégorie de produit']) \
                .background_gradient(cmap="Blues", subset=styled_predictors.columns.difference(['Catégorie de produit'])) \
                .set_table_styles([
                    {
                        'selector': 'th',
                        'props': [
                            ('background-color', '#1e88e5'),
                            ('color', 'white'),
                            ('text-align', 'center'),
                            ('font-weight', 'bold'),
                            ('padding', '8px')
                        ]
                    },
                    {
                        'selector': 'td',
                        'props': [
                            ('padding', '8px'),
                            ('text-align', 'right')
                        ]
                    }
                ])

            # Convertir le style en HTML pour affichage dans Streamlit
            html_table = styled_df.hide(axis="index").to_html()

            # Créer un conteneur scrollable pour le tableau
            st.markdown("""
                <style>
                .scrollable-table {
                    max-height: 400px;
                    overflow-y: auto;
                    display: block;
                    margin-top: 15px;
                }
                </style>
            """, unsafe_allow_html=True)
            st.markdown(f'<div class="scrollable-table">{html_table}</div>', unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("Aucune donnée de prédicteurs de satisfaction disponible.")
    except Exception as e:
        st.error(f"Erreur lors du chargement des prédicteurs de satisfaction: {e}")




# Pied de page
    st.markdown("<div class='footer'>© 2023 Olist - Analyse des clients - Dernière mise à jour: {}</div>".format(datetime.now().strftime("%d/%m/%Y %H:%M")), unsafe_allow_html=True)

# Ajouter un peu d'espace en bas
st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

# Script JavaScript pour améliorer l'interaction
st.markdown("""
<script>
    // Script pour améliorer le comportement du défilement dans les tableaux
    document.addEventListener('DOMContentLoaded', function() {
        const tables = document.querySelectorAll('.scrollable-table');
        tables.forEach(table => {
            table.addEventListener('wheel', function(e) {
                if (e.deltaY !== 0) {
                    e.preventDefault();
                    this.scrollTop += e.deltaY;
                }
            });
        });
    });
</script>
""", unsafe_allow_html=True)