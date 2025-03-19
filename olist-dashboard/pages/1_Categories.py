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
graph_height = 300
heatmap_height = 600

# Titre principal
st.markdown("<h1 class='main-header'>📊 Analyse des Catégories de Produits</h1>", unsafe_allow_html=True)


# Filtres dans la sidebar
with st.sidebar:
    st.markdown("<h2 class='sub-header'>Filtres</h2>", unsafe_allow_html=True)

    # Filtre de métrique
    metric_options = {
        "total_revenue": "Revenu total",
        "order_count": "Nombre de commandes",
        "avg_price": "Prix moyen",
        "avg_review_score": "Note moyenne",
        "avg_freight_value": "Frais de port moyens"
    }

    selected_metric = st.selectbox(
        "Métrique à analyser",
        options=list(metric_options.keys()),
        format_func=lambda x: metric_options[x]
    )

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

    # Chargement des catégories pour le filtre
    try:
        categories_list = load_categories_list()
        if not categories_list.empty:
            all_categories = categories_list["category_name"].tolist()

            # Filtre de catégories avec une option "Toutes les catégories"
            st.markdown("<h3 class='sub-header'>Filtres de catégories</h3>", unsafe_allow_html=True)

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

# Création d'une layout compact pour tout le dashboard
layout_container = st.container()

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
            # Ajouter un sélecteur pour l'ordre de tri
            sort_options = {
                "category_name": "Catégorie (A-Z)",
                "order_count": "Nombre de commandes (décroissant)",
                "total_revenue": "Revenu total (décroissant)",
                "avg_price": "Prix moyen (décroissant)",
                "avg_review_score": "Note moyenne (décroissant)",
                "avg_freight_value": "Frais de port moyens (décroissant)"
            }

            selected_sort = st.selectbox(
                "Trier par:",
                options=list(sort_options.keys()),
                format_func=lambda x: sort_options[x],
                index=2  # Par défaut, tri par revenu total
            )

            # Trier le DataFrame selon la colonne sélectionnée (ordre décroissant par défaut, sauf pour category_name)
            if selected_sort == "category_name":
                category_performance = category_performance.sort_values(by=selected_sort, ascending=True)
            else:
                category_performance = category_performance.sort_values(by=selected_sort, ascending=False)

            # Dupliquer le DataFrame pour conserver les valeurs numériques pour le style
            numeric_df = category_performance.copy()

            # Arrondir les valeurs numériques à 1 chiffre après la virgule
            for col in ["total_revenue", "avg_price", "avg_freight_value", "avg_review_score"]:
                numeric_df[col] = numeric_df[col].round(1)

            # Création d'une copie pour l'affichage avec formatage
            display_df = numeric_df.copy()
            display_df["total_revenue"] = display_df["total_revenue"].apply(lambda x: f"R$ {x:.1f}")
            display_df["avg_price"] = display_df["avg_price"].apply(lambda x: f"R$ {x:.1f}")
            display_df["avg_freight_value"] = display_df["avg_freight_value"].apply(lambda x: f"R$ {x:.1f}")

            # Renommage des colonnes pour l'affichage
            display_df = display_df.rename(columns={
                "category_name": "Catégorie",
                "order_count": "Nombre de commandes",
                "total_revenue": "Revenu total",
                "avg_price": "Prix moyen",
                "avg_review_score": "Note moyenne",
                "avg_freight_value": "Frais de port moyens"
            })

            # Appliquer le style au DataFrame numérique
            styled_df = numeric_df.style\
                .background_gradient(subset=["order_count"], cmap="Greens")\
                .background_gradient(subset=["total_revenue"], cmap="Blues")\
                .background_gradient(subset=["avg_price"], cmap="Purples")\
                .background_gradient(subset=["avg_review_score"], cmap="RdYlGn")\
                .background_gradient(subset=["avg_freight_value"], cmap="RdYlGn_r")\
                .format({
                    "total_revenue": "R$ {:.1f}",
                    "avg_price": "R$ {:.1f}",
                    "avg_freight_value": "R$ {:.1f}",
                    "avg_review_score": "{:.1f}"
                })\
                .set_properties(**{'font-weight': 'bold'})

            # Générer le HTML
            html_table = styled_df.to_html()

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

        # Créer un placeholder pour le titre
        title_placeholder = st.empty()

        # Sélecteur pour choisir la métrique
        graph_metric = st.selectbox(
            "Choisir la métrique pour le Top 10",
            options=list(metric_options.keys()),
            format_func=lambda x: metric_options[x],
            key="graph_metric_selector"
        )

        # Mettre à jour le placeholder avec le titre calculé en fonction de la sélection
        title_placeholder.markdown(
            f"<h3>Top 10 des catégories par {metric_options[graph_metric]}</h3>",
            unsafe_allow_html=True
        )

        try:
            if not category_performance.empty:
                # Tri et sélection des 10 meilleures catégories selon la métrique choisie par l'utilisateur
                top_categories = category_performance.sort_values(by=graph_metric, ascending=False).head(10)

                fig_cat = px.bar(
                    top_categories,
                    x=graph_metric,
                    y="category_name",
                    orientation='h',
                    labels={"category_name": "Catégorie", graph_metric: metric_options[graph_metric]},
                    color=graph_metric,
                    color_continuous_scale="Viridis"
                )

                # Configuration du graphique
                fig_cat.update_layout(
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    font=dict(family="Arial, sans-serif", size=10, color="black"),
                    xaxis=dict(
                        title=dict(text=metric_options[graph_metric], font=dict(color="black", size=10)),
                        tickfont=dict(color="black", size=10)
                    ),
                    yaxis=dict(
                        categoryorder='total ascending',
                        title=dict(text="", font=dict(color="black", size=10)),
                        tickfont=dict(color="black", size=10)
                    ),
                    height=graph_height,
                    margin=dict(l=10, r=10, t=10, b=10)
                )

                # Modification de la colorbar
                fig_cat.update_coloraxes(
                    colorbar=dict(
                        title_font=dict(color='black'),
                        tickfont=dict(color='black')
                    )
                )

                st.plotly_chart(fig_cat, use_container_width=True)

            else:
                st.warning("Aucune donnée disponible pour le graphique des catégories.")

        except Exception as e:
            st.error(f"Erreur lors de l'affichage du top des catégories: {e}")

        st.markdown("</div>", unsafe_allow_html=True)


    with col2:
        st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
        st.markdown("<h3>Distribution des prix par catégorie</h3>", unsafe_allow_html=True)
        st.markdown('<div style="height: 84px;"></div>', unsafe_allow_html=True)
        try:
            # Charger les données avec les filtres appliqués
            price_distribution = load_price_distribution(sql_start_date, sql_end_date, selected_categories)

            if not price_distribution.empty:
                # Sélection des catégories à montrer (si trop nombreuses)
                if len(selected_categories) > 10:
                    # Si trop de catégories, prendre les top catégories par performance
                    if not category_performance.empty:
                        top_categories_list = category_performance.sort_values(by=selected_metric, ascending=False).head(10)["category_name"].tolist()
                        price_data = price_distribution[price_distribution["category_name"].isin(top_categories_list)]
                        title = f"Distribution des prix (Top 10 catégories par {metric_options[selected_metric]})"
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
                # Utiliser les 10 meilleures catégories selon la métrique sélectionnée
                if not category_performance.empty:
                    top_categories_list = category_performance.sort_values(by=selected_metric, ascending=False).head(10)["category_name"].tolist()
                    trend_data = category_trend[category_trend["category_name"].isin(top_categories_list)]
                else:
                    # Ou prendre les 10 premières par ordre alphabétique
                    unique_categories = sorted(category_trend["category_name"].unique())[:10]
                    trend_data = category_trend[category_trend["category_name"].isin(unique_categories)]
            else:
                trend_data = category_trend

            # Dans la section où vous créez le graphique d'évolution des ventes
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
                    tickformat="%b %Y"  # Format d'affichage des dates (mois année)
                ),
                yaxis=dict(
                    title=dict(text="Revenu total (R$)", font=dict(color="black", size=10)),
                    tickfont=dict(color="black", size=8)
                ),
                legend=dict(
                    font=dict(size=10, color="black"),
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
            Cette heatmap montre la fréquence d'achat croisé entre catégories. Les valeurs plus foncées indiquent des associations plus fortes.
            </p>
            """, unsafe_allow_html=True)
        else:
            st.info("Pas de données d'achat croisé disponibles.")
    except Exception as e:
        st.error(f"Erreur lors de l'affichage des achats croisés: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

    # Section des insights
    st.markdown("<h2 class='sub-header'>💡 Insights et opportunités</h2>", unsafe_allow_html=True)

    try:
        # Insights généraux sur les catégories
        st.markdown("""
        ### Insights généraux sur les catégories

        - Les catégories avec les prix moyens les plus élevés ne sont pas nécessairement celles qui génèrent le plus de revenus.
        - Certaines catégories présentent une forte saisonnalité dans les ventes.
        - Des opportunités d'achat croisé existent entre certaines catégories complémentaires.
        - Analysez les catégories ayant une faible note moyenne pour identifier des opportunités d'amélioration.
        """)

        # Insights dynamiques basés sur les données filtrées
        if not category_performance.empty:
            top_category = category_performance.sort_values(by="total_revenue", ascending=False).iloc[0]
            worst_review = category_performance.sort_values(by="avg_review_score").iloc[0]

            st.markdown(f"""
            ### Insights spécifiques à la période sélectionnée

            - La catégorie **{top_category['category_name']}** est la plus performante avec un revenu total de {format_currency(top_category['total_revenue'])}.
            - La catégorie **{worst_review['category_name']}** a la note moyenne la plus basse ({worst_review['avg_review_score']:.1f}/5), ce qui pourrait indiquer des problèmes de qualité à résoudre.
            """)

            # Recommandations basées sur les données
            if len(selected_categories) > 1:
                st.markdown("""
                ### Recommandations

                - Concentrez vos efforts marketing sur les catégories à forte marge et volume de ventes.
                - Envisagez des promotions croisées entre catégories fortement associées.
                - Examinez les catégories à faible satisfaction client pour améliorer la qualité des produits ou les descriptions.
                """)
    except Exception as e:
        st.error(f"Erreur lors de l'affichage des insights: {e}")

    # Pied de page
    st.markdown("<div class='footer'>", unsafe_allow_html=True)
    st.markdown("*Dashboard créé avec Streamlit et SQLAlchemy - Basé sur le dataset Olist*")
    st.markdown("</div>", unsafe_allow_html=True)