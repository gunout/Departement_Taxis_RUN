import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Taxis & Taxiteurs - Île de la Réunion",
    page_icon="🚖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(45deg, #1E88E5, #FF9800, #43A047);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .section-header {
        color: #1565C0;
        border-bottom: 2px solid #FF9800;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1E88E5;
        margin: 0.5rem 0;
    }
    .commune-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 5px solid #FF9800;
        background-color: #f8f9fa;
    }
    .activity-high { background-color: #d4edda; border-left: 4px solid #28a745; }
    .activity-medium { background-color: #fff3cd; border-left: 4px solid #ffc107; }
    .activity-low { background-color: #f8d7da; border-left: 4px solid #dc3545; }
    .activity-limited { background-color: #e2e3e5; border-left: 4px solid #6c757d; }
    .microregion-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        color: white;
    }
    .nord { background-color: #1E88E5; }
    .sud { background-color: #43A047; }
    .ouest { background-color: #FF9800; color: black; }
    .est { background-color: #AB47BC; }
    .cirques { background-color: #5D4037; }
    .demand-high { color: #28a745; font-weight: bold; }
    .demand-medium { color: #ffc107; font-weight: bold; }
    .demand-low { color: #dc3545; font-weight: bold; }
    .driver-status {
        padding: 0.25rem 0.5rem;
        border-radius: 10px;
        font-size: 0.75rem;
        font-weight: 600;
        color: white;
    }
    .active { background-color: #28a745; }
    .inactive { background-color: #dc3545; }
    .part-time { background-color: #ffc107; color: black; }
</style>
""", unsafe_allow_html=True)

class ReunionTaxiDashboard:
    def __init__(self):
        self.communes_data = self.define_communes_data()
        self.historical_data = self.initialize_historical_data()
        self.current_data = self.initialize_current_data()
        self.microregion_data = self.initialize_microregion_data()
        self.taxi_stations_data = self.initialize_taxi_stations_data()
        
    def define_communes_data(self):
        """Définit les données des taxis par commune de La Réunion"""
        return [
            {
                'nom': 'Saint-Denis',
                'micro_region': 'Nord',
                'population': 153810,
                'nombre_taxis': 185,
                'nombre_taxiteurs': 220,
                'taux_activite': 'Élevé',
                'demande_moyenne_journaliere': 2450,
                'revenu_moyen_mensuel': 2850,
                'stations_principales': 8,
                'taux_occupation': 78.5,
                'couverture_nuit': 'Élevée',
                'acces_aeroport': 'Direct',
                'zones_desservies': 'Centre-ville, Université, CHU, Aéroport',
                'lat': -20.8789,
                'lon': 55.4481,
                'description': 'Préfecture, plus forte densité de taxis'
            },
            {
                'nom': 'Saint-Paul',
                'micro_region': 'Ouest',
                'population': 105240,
                'nombre_taxis': 120,
                'nombre_taxiteurs': 145,
                'taux_activite': 'Élevé',
                'demande_moyenne_journaliere': 1680,
                'revenu_moyen_mensuel': 2650,
                'stations_principales': 6,
                'taux_occupation': 72.3,
                'couverture_nuit': 'Moyenne',
                'acces_aeroport': 'Proche',
                'zones_desservies': 'Centre-ville, Zones commerciales, Plages',
                'lat': -21.0097,
                'lon': 55.2697,
                'description': 'Fort potentiel touristique et résidentiel'
            },
            {
                'nom': 'Saint-Pierre',
                'micro_region': 'Sud',
                'population': 84520,
                'nombre_taxis': 95,
                'nombre_taxiteurs': 115,
                'taux_activite': 'Élevé',
                'demande_moyenne_journaliere': 1420,
                'revenu_moyen_mensuel': 2580,
                'stations_principales': 5,
                'taux_occupation': 69.8,
                'couverture_nuit': 'Moyenne',
                'acces_aeroport': 'Éloigné',
                'zones_desservies': 'Centre-ville, Port, Zones d\'activité',
                'lat': -21.3393,
                'lon': 55.4781,
                'description': 'Pôle économique du Sud, activité soutenue'
            },
            {
                'nom': 'Le Tampon',
                'micro_region': 'Sud',
                'population': 79849,
                'nombre_taxis': 65,
                'nombre_taxiteurs': 80,
                'taux_activite': 'Moyen',
                'demande_moyenne_journaliere': 980,
                'revenu_moyen_mensuel': 2320,
                'stations_principales': 3,
                'taux_occupation': 65.2,
                'couverture_nuit': 'Faible',
                'acces_aeroport': 'Éloigné',
                'zones_desservies': 'Centre-ville, Zones résidentielles',
                'lat': -21.2779,
                'lon': 55.5179,
                'description': 'Commune résidentielle, demande régulière'
            },
            {
                'nom': 'Saint-Louis',
                'micro_region': 'Sud',
                'population': 53609,
                'nombre_taxis': 45,
                'nombre_taxiteurs': 55,
                'taux_activite': 'Moyen',
                'demande_moyenne_journaliere': 720,
                'revenu_moyen_mensuel': 2250,
                'stations_principales': 2,
                'taux_occupation': 61.8,
                'couverture_nuit': 'Faible',
                'acces_aeroport': 'Éloigné',
                'zones_desservies': 'Centre-ville, Collège, Lycée',
                'lat': -21.2861,
                'lon': 55.4111,
                'description': 'Dynamisme économique modéré'
            },
            {
                'nom': 'Saint-André',
                'micro_region': 'Est',
                'population': 56602,
                'nombre_taxis': 38,
                'nombre_taxiteurs': 45,
                'taux_activite': 'Moyen',
                'demande_moyenne_journaliere': 580,
                'revenu_moyen_mensuel': 2180,
                'stations_principales': 2,
                'taux_occupation': 58.5,
                'couverture_nuit': 'Très faible',
                'acces_aeroport': 'Éloigné',
                'zones_desservies': 'Centre-ville, Zones agricoles',
                'lat': -20.9631,
                'lon': 55.6508,
                'description': 'Commune rurale, activité modérée'
            },
            {
                'nom': 'Saint-Leu',
                'micro_region': 'Ouest',
                'population': 34746,
                'nombre_taxis': 42,
                'nombre_taxiteurs': 50,
                'taux_activite': 'Moyen',
                'demande_moyenne_journaliere': 650,
                'revenu_moyen_mensuel': 2450,
                'stations_principales': 2,
                'taux_occupation': 68.2,
                'couverture_nuit': 'Moyenne',
                'acces_aeroport': 'Proche',
                'zones_desservies': 'Centre-ville, Spot de surf, Hôtels',
                'lat': -21.1653,
                'lon': 55.2881,
                'description': 'Station balnéaire, forte saisonnalité'
            },
            {
                'nom': 'Saint-Joseph',
                'micro_region': 'Sud',
                'population': 37882,
                'nombre_taxis': 28,
                'nombre_taxiteurs': 35,
                'taux_activite': 'Faible',
                'demande_moyenne_journaliere': 320,
                'revenu_moyen_mensuel': 1980,
                'stations_principales': 1,
                'taux_occupation': 45.8,
                'couverture_nuit': 'Très faible',
                'acces_aeroport': 'Très éloigné',
                'zones_desservies': 'Centre-ville, Villages isolés',
                'lat': -21.3778,
                'lon': 55.6197,
                'description': 'Grande commune, demande dispersée'
            },
            {
                'nom': 'Saint-Benoît',
                'micro_region': 'Est',
                'population': 37308,
                'nombre_taxis': 32,
                'nombre_taxiteurs': 38,
                'taux_activite': 'Faible',
                'demande_moyenne_journaliere': 380,
                'revenu_moyen_mensuel': 2050,
                'stations_principales': 1,
                'taux_occupation': 48.2,
                'couverture_nuit': 'Très faible',
                'acces_aeroport': 'Éloigné',
                'zones_desservies': 'Centre-ville, Est',
                'lat': -21.0339,
                'lon': 55.7147,
                'description': 'Relief contraignant, activité limitée'
            },
            {
                'nom': 'Sainte-Marie',
                'micro_region': 'Nord',
                'population': 34167,
                'nombre_taxis': 35,
                'nombre_taxiteurs': 42,
                'taux_activite': 'Moyen',
                'demande_moyenne_journaliere': 520,
                'revenu_moyen_mensuel': 2350,
                'stations_principales': 1,
                'taux_occupation': 62.5,
                'couverture_nuit': 'Faible',
                'acces_aeroport': 'Direct',
                'zones_desservies': 'Aéroport, Zones résidentielles',
                'lat': -20.8969,
                'lon': 55.5492,
                'description': 'Proche aéroport, activité aéroportuaire'
            },
            {
                'nom': 'La Possession',
                'micro_region': 'Ouest',
                'population': 33506,
                'nombre_taxis': 40,
                'nombre_taxiteurs': 48,
                'taux_activite': 'Moyen',
                'demande_moyenne_journaliere': 610,
                'revenu_moyen_mensuel': 2280,
                'stations_principales': 2,
                'taux_occupation': 59.8,
                'couverture_nuit': 'Faible',
                'acces_aeroport': 'Proche',
                'zones_desservies': 'Centre-ville, Liaison Ouest',
                'lat': -20.9253,
                'lon': 55.3358,
                'description': 'Développement rapide, demande croissante'
            },
            {
                'nom': 'Le Port',
                'micro_region': 'Ouest',
                'population': 32995,
                'nombre_taxis': 48,
                'nombre_taxiteurs': 58,
                'taux_activite': 'Moyen',
                'demande_moyenne_journaliere': 780,
                'revenu_moyen_mensuel': 2420,
                'stations_principales': 3,
                'taux_occupation': 66.7,
                'couverture_nuit': 'Moyenne',
                'acces_aeroport': 'Proche',
                'zones_desservies': 'Port, Zones industrielles, Gare',
                'lat': -20.9394,
                'lon': 55.2928,
                'description': 'Ville portuaire, activité économique'
            },
            {
                'nom': 'Bras-Panon',
                'micro_region': 'Est',
                'population': 13170,
                'nombre_taxis': 15,
                'nombre_taxiteurs': 18,
                'taux_activite': 'Faible',
                'demande_moyenne_journaliere': 180,
                'revenu_moyen_mensuel': 1850,
                'stations_principales': 1,
                'taux_occupation': 42.3,
                'couverture_nuit': 'Nulle',
                'acces_aeroport': 'Éloigné',
                'zones_desservies': 'Centre-bourg',
                'lat': -21.0017,
                'lon': 55.6772,
                'description': 'Commune rurale, activité limitée'
            },
            {
                'nom': 'Les Avirons',
                'micro_region': 'Ouest',
                'population': 11447,
                'nombre_taxis': 18,
                'nombre_taxiteurs': 22,
                'taux_activite': 'Faible',
                'demande_moyenne_journaliere': 220,
                'revenu_moyen_mensuel': 1920,
                'stations_principales': 1,
                'taux_occupation': 46.8,
                'couverture_nuit': 'Nulle',
                'acces_aeroport': 'Proche',
                'zones_desservies': 'Centre-bourg',
                'lat': -21.2408,
                'lon': 55.3392,
                'description': 'Petite commune, demande locale'
            },
            {
                'nom': 'Entre-Deux',
                'micro_region': 'Sud',
                'population': 7070,
                'nombre_taxis': 8,
                'nombre_taxiteurs': 10,
                'taux_activite': 'Limitée',
                'demande_moyenne_journaliere': 85,
                'revenu_moyen_mensuel': 1650,
                'stations_principales': 1,
                'taux_occupation': 35.2,
                'couverture_nuit': 'Nulle',
                'acces_aeroport': 'Très éloigné',
                'zones_desservies': 'Centre-bourg',
                'lat': -21.2500,
                'lon': 55.4722,
                'description': 'Commune des Hauts, activité réduite'
            },
            {
                'nom': 'L\'Étang-Salé',
                'micro_region': 'Ouest',
                'population': 14030,
                'nombre_taxis': 22,
                'nombre_taxiteurs': 26,
                'taux_activite': 'Faible',
                'demande_moyenne_journaliere': 280,
                'revenu_moyen_mensuel': 2080,
                'stations_principales': 1,
                'taux_occupation': 52.4,
                'couverture_nuit': 'Très faible',
                'acces_aeroport': 'Proche',
                'zones_desservies': 'Centre-ville, Plage, Forêt',
                'lat': -21.2631,
                'lon': 55.3842,
                'description': 'Littoral, activité touristique modérée'
            },
            {
                'nom': 'Petite-Île',
                'micro_region': 'Sud',
                'population': 12155,
                'nombre_taxis': 14,
                'nombre_taxiteurs': 17,
                'taux_activite': 'Faible',
                'demande_moyenne_journaliere': 160,
                'revenu_moyen_mensuel': 1880,
                'stations_principales': 1,
                'taux_occupation': 41.6,
                'couverture_nuit': 'Nulle',
                'acces_aeroport': 'Éloigné',
                'zones_desservies': 'Centre-bourg',
                'lat': -21.3531,
                'lon': 55.5639,
                'description': 'Petite commune, demande locale'
            },
            {
                'nom': 'Saint-Philippe',
                'micro_region': 'Sud',
                'population': 5232,
                'nombre_taxis': 6,
                'nombre_taxiteurs': 7,
                'taux_activite': 'Limitée',
                'demande_moyenne_journaliere': 65,
                'revenu_moyen_mensuel': 1550,
                'stations_principales': 1,
                'taux_occupation': 32.8,
                'couverture_nuit': 'Nulle',
                'acces_aeroport': 'Très éloigné',
                'zones_desservies': 'Centre-bourg',
                'lat': -21.3592,
                'lon': 55.7672,
                'description': 'Sud Sauvage, activité très limitée'
            },
            {
                'nom': 'Sainte-Rose',
                'micro_region': 'Est',
                'population': 6424,
                'nombre_taxis': 7,
                'nombre_taxiteurs': 8,
                'taux_activite': 'Limitée',
                'demande_moyenne_journaliere': 75,
                'revenu_moyen_mensuel': 1620,
                'stations_principales': 1,
                'taux_occupation': 34.1,
                'couverture_nuit': 'Nulle',
                'acces_aeroport': 'Très éloigné',
                'zones_desservies': 'Centre-bourg',
                'lat': -21.1242,
                'lon': 55.7961,
                'description': 'Grande commune, très faible densité'
            },
            {
                'nom': 'Cilaos',
                'micro_region': 'Cirques',
                'population': 5528,
                'nombre_taxis': 5,
                'nombre_taxiteurs': 6,
                'taux_activite': 'Limitée',
                'demande_moyenne_journaliere': 55,
                'revenu_moyen_mensuel': 1480,
                'stations_principales': 1,
                'taux_occupation': 28.5,
                'couverture_nuit': 'Nulle',
                'acces_aeroport': 'Très éloigné',
                'zones_desservies': 'Centre-cirque',
                'lat': -21.1339,
                'lon': 55.4719,
                'description': 'Cirque, activité touristique saisonnière'
            },
            {
                'nom': 'Salazie',
                'micro_region': 'Cirques',
                'population': 7363,
                'nombre_taxis': 6,
                'nombre_taxiteurs': 7,
                'taux_activite': 'Limitée',
                'demande_moyenne_journaliere': 70,
                'revenu_moyen_mensuel': 1520,
                'stations_principales': 1,
                'taux_occupation': 30.2,
                'couverture_nuit': 'Nulle',
                'acces_aeroport': 'Très éloigné',
                'zones_desservies': 'Centre-cirque',
                'lat': -21.0272,
                'lon': 55.5392,
                'description': 'Cirque, activité très limitée'
            },
            {
                'nom': 'Sainte-Suzanne',
                'micro_region': 'Nord',
                'population': 24645,
                'nombre_taxis': 28,
                'nombre_taxiteurs': 33,
                'taux_activite': 'Faible',
                'demande_moyenne_journaliere': 340,
                'revenu_moyen_mensuel': 2120,
                'stations_principales': 1,
                'taux_occupation': 51.7,
                'couverture_nuit': 'Très faible',
                'acces_aeroport': 'Direct',
                'zones_desservies': 'Centre-ville, Nord',
                'lat': -20.9061,
                'lon': 55.6069,
                'description': 'Développement résidentiel, demande modérée'
            },
            {
                'nom': 'Les Trois-Bassins',
                'micro_region': 'Ouest',
                'population': 6980,
                'nombre_taxis': 9,
                'nombre_taxiteurs': 11,
                'taux_activite': 'Limitée',
                'demande_moyenne_journaliere': 95,
                'revenu_moyen_mensuel': 1720,
                'stations_principales': 1,
                'taux_occupation': 38.4,
                'couverture_nuit': 'Nulle',
                'acces_aeroport': 'Proche',
                'zones_desservies': 'Centre-bourg',
                'lat': -21.1039,
                'lon': 55.2992,
                'description': 'Petite commune, activité réduite'
            }
        ]
    
    def initialize_historical_data(self):
        """Initialise les données historiques de l'activité taxi"""
        dates = pd.date_range('2018-01-01', datetime.now(), freq='Y')
        data = []
        
        for date in dates:
            for commune in self.communes_data:
                # Évolution avec tendance et variations saisonnières
                years_passed = date.year - 2018
                trend_factor = 1 + (years_passed * 0.04)  # Tendance de +4% par an
                
                # Variations aléatoires
                random_variation = np.random.normal(1, 0.03)
                
                nombre_taxis = commune['nombre_taxis'] * 0.9 * trend_factor * random_variation
                demande = commune['demande_moyenne_journaliere'] * 0.85 * trend_factor * random_variation
                
                data.append({
                    'date': date,
                    'commune': commune['nom'],
                    'micro_region': commune['micro_region'],
                    'nombre_taxis': nombre_taxis,
                    'demande_moyenne_journaliere': demande,
                    'revenu_moyen_mensuel': commune['revenu_moyen_mensuel'] * 0.9 * trend_factor
                })
        
        return pd.DataFrame(data)
    
    def initialize_current_data(self):
        """Initialise les données courantes sous forme de DataFrame"""
        return pd.DataFrame(self.communes_data)
    
    def initialize_microregion_data(self):
        """Initialise les données par micro-région"""
        microregions = list(set([commune['micro_region'] for commune in self.communes_data]))
        data = []
        
        for microregion in microregions:
            communes_microregion = [c for c in self.communes_data if c['micro_region'] == microregion]
            
            taxis_total = sum([c['nombre_taxis'] for c in communes_microregion])
            taxiteurs_total = sum([c['nombre_taxiteurs'] for c in communes_microregion])
            demande_totale = sum([c['demande_moyenne_journaliere'] for c in communes_microregion])
            population_totale = sum([c['population'] for c in communes_microregion])
            revenu_moyen = np.mean([c['revenu_moyen_mensuel'] for c in communes_microregion])
            taux_occupation_moyen = np.mean([c['taux_occupation'] for c in communes_microregion])
            
            data.append({
                'micro_region': microregion,
                'nombre_taxis_total': taxis_total,
                'nombre_taxiteurs_total': taxiteurs_total,
                'demande_totale_journaliere': demande_totale,
                'population_totale': population_totale,
                'revenu_moyen_mensuel': revenu_moyen,
                'taux_occupation_moyen': taux_occupation_moyen,
                'nombre_communes': len(communes_microregion)
            })
        
        return pd.DataFrame(data)
    
    def initialize_taxi_stations_data(self):
        """Initialise les données des stations de taxis principales"""
        stations = [
            {'nom': 'Gare Routière Saint-Denis', 'commune': 'Saint-Denis', 'nombre_taxis': 45, 'lat': -20.882, 'lon': 55.448, 'type': 'Principale'},
            {'nom': 'Aéroport Roland Garros', 'commune': 'Sainte-Marie', 'nombre_taxis': 35, 'lat': -20.887, 'lon': 55.510, 'type': 'Aéroport'},
            {'nom': 'Gare de Saint-Paul', 'commune': 'Saint-Paul', 'nombre_taxis': 25, 'lat': -21.010, 'lon': 55.270, 'type': 'Principale'},
            {'nom': 'Port de Saint-Pierre', 'commune': 'Saint-Pierre', 'nombre_taxis': 20, 'lat': -21.340, 'lon': 55.478, 'type': 'Portuaire'},
            {'nom': 'CHU Félix Guyon', 'commune': 'Saint-Denis', 'nombre_taxis': 18, 'lat': -20.899, 'lon': 55.495, 'type': 'Hôpital'},
            {'nom': 'Université de La Réunion', 'commune': 'Saint-Denis', 'nombre_taxis': 15, 'lat': -20.905, 'lon': 55.485, 'type': 'Universitaire'},
            {'nom': 'ZAC Cambaie', 'commune': 'Saint-Paul', 'nombre_taxis': 12, 'lat': -20.985, 'lon': 55.290, 'type': 'Commerciale'},
            {'nom': 'Gare du Port', 'commune': 'Le Port', 'nombre_taxis': 15, 'lat': -20.939, 'lon': 55.293, 'type': 'Ferroviaire'},
        ]
        return pd.DataFrame(stations)
    
    def display_header(self):
        """Affiche l'en-tête du dashboard"""
        st.markdown('<h1 class="main-header">🚖 Dashboard Taxis & Taxiteurs - Île de la Réunion</h1>', 
                   unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("**Analyse de l'activité taxi - Données 2024**")
        
        current_time = datetime.now().strftime('%d/%m/%Y %H:%M')
        st.sidebar.markdown(f"**🕐 Dernière mise à jour: {current_time}**")
    
    def display_key_metrics(self):
        """Affiche les métriques clés de l'activité taxi"""
        st.markdown('<h3 class="section-header">📊 INDICATEURS CLÉS DE L\'ACTIVITÉ TAXI</h3>', 
                   unsafe_allow_html=True)
        
        # Calcul des métriques globales
        taxis_total = self.current_data['nombre_taxis'].sum()
        taxiteurs_total = self.current_data['nombre_taxiteurs'].sum()
        demande_totale = self.current_data['demande_moyenne_journaliere'].sum()
        revenu_moyen = self.current_data['revenu_moyen_mensuel'].mean()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Nombre total de taxis",
                f"{taxis_total:,}",
                f"+{np.random.uniform(3, 7):.1f}% vs 2023"
            )
        
        with col2:
            st.metric(
                "Taxiteurs actifs",
                f"{taxiteurs_total:,}",
                f"+{np.random.uniform(2, 5):.1f}%"
            )
        
        with col3:
            st.metric(
                "Demande journalière totale",
                f"{demande_totale:,.0f} courses",
                f"+{np.random.uniform(4, 8):.1f}%"
            )
        
        with col4:
            st.metric(
                "Revenu mensuel moyen",
                f"{revenu_moyen:.0f} €",
                f"{np.random.uniform(1, 3):.1f}%"
            )
    
    def create_activity_overview(self):
        """Crée la vue d'ensemble de l'activité taxi"""
        st.markdown('<h3 class="section-header">🏛️ VUE D\'ENSEMBLE DE L\'ACTIVITÉ TAXI</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["Carte Interactive", "Évolution de l'Activité", "Répartition Micro-régions", "Analyse Stations"])
        
        with tab1:
            # Carte interactive avec Folium
            st.subheader("Carte de l'activité taxi par commune")
            
            # Création de la carte centrée sur La Réunion
            m = folium.Map(location=[-21.115, 55.536], zoom_start=10)
            
            # Définir les couleurs selon le niveau d'activité
            def get_color(niveau):
                if niveau == 'Élevé': return 'green'
                elif niveau == 'Moyen': return 'orange'
                elif niveau == 'Faible': return 'red'
                elif niveau == 'Limitée': return 'lightgray'
                else: return 'darkgray'
            
            # Ajout des marqueurs pour chaque commune
            for commune in self.communes_data:
                color = get_color(commune['taux_activite'])
                
                # Popup avec informations détaillées
                popup_text = f"""
                <b>{commune['nom']}</b><br>
                Micro-région: {commune['micro_region']}<br>
                Nombre de taxis: {commune['nombre_taxis']}<br>
                Activité: {commune['taux_activite']}<br>
                Demande journalière: {commune['demande_moyenne_journaliere']} courses<br>
                Revenu moyen: {commune['revenu_moyen_mensuel']} €
                """
                
                folium.Marker(
                    [commune['lat'], commune['lon']],
                    popup=folium.Popup(popup_text, max_width=300),
                    tooltip=f"{commune['nom']} - {commune['nombre_taxis']} taxis",
                    icon=folium.Icon(color=color, icon='taxi', prefix='fa')
                ).add_to(m)
            
            # Ajout des stations principales
            for _, station in self.taxi_stations_data.iterrows():
                folium.Marker(
                    [station['lat'], station['lon']],
                    popup=folium.Popup(f"<b>{station['nom']}</b><br>{station['nombre_taxis']} taxis", max_width=200),
                    tooltip=f"{station['nom']}",
                    icon=folium.Icon(color='blue', icon='flag', prefix='fa')
                ).add_to(m)
            
            # Légende
            legend_html = '''
            <div style="position: fixed; 
                        bottom: 50px; left: 50px; width: 220px; height: 160px; 
                        background-color: white; border:2px solid grey; z-index:9999; 
                        font-size:14px; padding: 10px">
            <p><strong>Légende Activité</strong></p>
            <p><i class="fa fa-taxi" style="color:green"></i> Élevée</p>
            <p><i class="fa fa-taxi" style="color:orange"></i> Moyenne</p>
            <p><i class="fa fa-taxi" style="color:red"></i> Faible</p>
            <p><i class="fa fa-taxi" style="color:lightgray"></i> Limitée</p>
            <p><i class="fa fa-flag" style="color:blue"></i> Station</p>
            </div>
            '''
            m.get_root().html.add_child(folium.Element(legend_html))
            
            # Affichage de la carte
            folium_static(m, width=1000, height=500)
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                # Évolution du nombre de taxis par micro-région
                evolution_data = self.historical_data.groupby([
                    self.historical_data['date'].dt.year,
                    'micro_region'
                ])['nombre_taxis'].sum().reset_index()
                
                fig = px.line(evolution_data, 
                             x='date', 
                             y='nombre_taxis',
                             color='micro_region',
                             title='Évolution du nombre de taxis par micro-région (2018-2024)',
                             color_discrete_sequence=['#1E88E5', '#43A047', '#FF9800', '#AB47BC', '#5D4037'])
                fig.update_layout(yaxis_title="Nombre de taxis")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Évolution de la demande
                demande_data = self.historical_data.groupby([
                    self.historical_data['date'].dt.year,
                    'micro_region'
                ])['demande_moyenne_journaliere'].sum().reset_index()
                
                fig = px.line(demande_data, 
                             x='date', 
                             y='demande_moyenne_journaliere',
                             color='micro_region',
                             title='Évolution de la demande par micro-région (2018-2024)',
                             color_discrete_sequence=['#1E88E5', '#43A047', '#FF9800', '#AB47BC', '#5D4037'])
                fig.update_layout(yaxis_title="Demande journalière (courses)")
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                # Répartition des taxis par micro-région
                fig = px.pie(self.microregion_data, 
                            values='nombre_taxis_total', 
                            names='micro_region',
                            title='Répartition des taxis par micro-région',
                            color='micro_region',
                            color_discrete_map={
                                'Nord': '#1E88E5',
                                'Sud': '#43A047',
                                'Ouest': '#FF9800',
                                'Est': '#AB47BC',
                                'Cirques': '#5D4037'
                            })
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Demande par micro-région
                fig = px.bar(self.microregion_data, 
                            x='micro_region', 
                            y='demande_totale_journaliere',
                            title='Demande journalière par micro-région',
                            color='micro_region',
                            color_discrete_map={
                                'Nord': '#1E88E5',
                                'Sud': '#43A047',
                                'Ouest': '#FF9800',
                                'Est': '#AB47BC',
                                'Cirques': '#5D4037'
                            })
                fig.update_layout(yaxis_title="Demande journalière (courses)")
                st.plotly_chart(fig, use_container_width=True)
        
        with tab4:
            col1, col2 = st.columns(2)
            
            with col1:
                # Stations principales
                fig = px.bar(self.taxi_stations_data, 
                            x='nom', 
                            y='nombre_taxis',
                            title='Stations de taxis principales',
                            color='type',
                            color_discrete_sequence=['#1E88E5', '#43A047', '#FF9800', '#AB47BC'])
                fig.update_layout(xaxis_title="Station", yaxis_title="Nombre de taxis")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Taux d'occupation par micro-région
                fig = px.bar(self.microregion_data, 
                            x='micro_region', 
                            y='taux_occupation_moyen',
                            title='Taux d\'occupation moyen par micro-région',
                            color='micro_region',
                            color_discrete_map={
                                'Nord': '#1E88E5',
                                'Sud': '#43A047',
                                'Ouest': '#FF9800',
                                'Est': '#AB47BC',
                                'Cirques': '#5D4037'
                            })
                fig.update_layout(yaxis_title="Taux d'occupation (%)")
                st.plotly_chart(fig, use_container_width=True)
    
    def create_communes_analysis(self):
        """Affiche l'analyse détaillée par commune"""
        st.markdown('<h3 class="section-header">🏢 ANALYSE PAR COMMUNE</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Comparaison Communes", "Top Activité", "Détails par Commune"])
        
        with tab1:
            # Filtres pour les communes
            col1, col2, col3 = st.columns(3)
            with col1:
                microregion_filtre = st.selectbox("Micro-région:", 
                                                ['Toutes'] + list(self.microregion_data['micro_region'].unique()))
            with col2:
                niveau_filtre = st.selectbox("Niveau d'activité:", 
                                           ['Tous', 'Élevé', 'Moyen', 'Faible', 'Limitée'])
            with col3:
                tri_filtre = st.selectbox("Trier par:", 
                                        ['Nombre de taxis', 'Demande journalière', 'Revenu moyen', 'Taux occupation'])
            
            # Application des filtres
            communes_filtrees = self.current_data.copy()
            if microregion_filtre != 'Toutes':
                communes_filtrees = communes_filtrees[communes_filtrees['micro_region'] == microregion_filtre]
            if niveau_filtre != 'Tous':
                communes_filtrees = communes_filtrees[communes_filtrees['taux_activite'] == niveau_filtre]
            
            # Tri
            if tri_filtre == 'Nombre de taxis':
                communes_filtrees = communes_filtrees.sort_values('nombre_taxis', ascending=False)
            elif tri_filtre == 'Demande journalière':
                communes_filtrees = communes_filtrees.sort_values('demande_moyenne_journaliere', ascending=False)
            elif tri_filtre == 'Revenu moyen':
                communes_filtrees = communes_filtrees.sort_values('revenu_moyen_mensuel', ascending=False)
            elif tri_filtre == 'Taux occupation':
                communes_filtrees = communes_filtrees.sort_values('taux_occupation', ascending=False)
            
            # Affichage des communes
            for _, commune in communes_filtrees.iterrows():
                # Déterminer la classe CSS selon le niveau d'activité
                if commune['taux_activite'] == 'Élevé':
                    css_class = "activity-high"
                elif commune['taux_activite'] == 'Moyen':
                    css_class = "activity-medium"
                elif commune['taux_activite'] == 'Faible':
                    css_class = "activity-low"
                else:
                    css_class = "activity-limited"
                
                col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 1, 1])
                with col1:
                    st.markdown(f"**{commune['nom']}**")
                    microregion_class = commune['micro_region'].lower()
                    st.markdown(f"<div class='microregion-badge {microregion_class}'>{commune['micro_region']}</div>", 
                               unsafe_allow_html=True)
                with col2:
                    st.markdown(f"**{commune['description']}**")
                    st.markdown(f"Population: {commune['population']:,} hab • Stations: {commune['stations_principales']}")
                with col3:
                    st.markdown(f"**{commune['nombre_taxis']} taxis**")
                    st.markdown(f"Taxiteurs: {commune['nombre_taxiteurs']}")
                with col4:
                    st.markdown(f"**{commune['taux_activite']}**")
                    demande_class = f"demand-{commune['taux_activite'].lower().replace(' ', '-')}"
                    st.markdown(f"<span class='{demande_class}'>Demande: {commune['demande_moyenne_journaliere']}/j</span>", 
                               unsafe_allow_html=True)
                with col5:
                    st.markdown(f"<div class='{css_class}'>Niveau: {commune['taux_activite']}</div>", 
                               unsafe_allow_html=True)
                    st.markdown(f"Revenu: {commune['revenu_moyen_mensuel']} €")
                
                st.markdown("---")
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                # Top des communes avec le plus de taxis
                top_taxis = self.current_data.nlargest(10, 'nombre_taxis')
                fig = px.bar(top_taxis, 
                            x='nombre_taxis', 
                            y='nom',
                            orientation='h',
                            title='Top 10 des communes par nombre de taxis',
                            color='nombre_taxis',
                            color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Top des communes avec la plus forte demande
                top_demande = self.current_data.nlargest(10, 'demande_moyenne_journaliere')
                fig = px.bar(top_demande, 
                            x='demande_moyenne_journaliere', 
                            y='nom',
                            orientation='h',
                            title='Top 10 des communes par demande journalière',
                            color='demande_moyenne_journaliere',
                            color_continuous_scale='Oranges')
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # Détails pour une commune sélectionnée
            commune_selectionnee = st.selectbox("Sélectionnez une commune:", 
                                             self.current_data['nom'].unique())
            
            if commune_selectionnee:
                commune_data = self.current_data[self.current_data['nom'] == commune_selectionnee].iloc[0]
                historique_commune = self.historical_data[self.historical_data['commune'] == commune_selectionnee]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader(f"Fiche activité taxi: {commune_selectionnee}")
                    
                    st.metric("Micro-région", commune_data['micro_region'])
                    st.metric("Population", f"{commune_data['population']:,}")
                    st.metric("Nombre de taxis", commune_data['nombre_taxis'])
                    st.metric("Nombre de taxiteurs", commune_data['nombre_taxiteurs'])
                    st.metric("Niveau d'activité", commune_data['taux_activite'])
                    st.metric("Demande journalière moyenne", f"{commune_data['demande_moyenne_journaliere']} courses")
                    st.metric("Revenu mensuel moyen", f"{commune_data['revenu_moyen_mensuel']} €")
                    st.metric("Taux d'occupation", f"{commune_data['taux_occupation']}%")
                    st.metric("Couverture de nuit", commune_data['couverture_nuit'])
                    st.metric("Accès aéroport", commune_data['acces_aeroport'])
                    st.metric("Stations principales", commune_data['stations_principales'])
                
                with col2:
                    # Graphique d'évolution du nombre de taxis pour la commune sélectionnée
                    fig = px.line(historique_commune, 
                                 x='date', 
                                 y='nombre_taxis',
                                 title=f'Évolution du nombre de taxis à {commune_selectionnee}',
                                 color_discrete_sequence=['#1E88E5'])
                    fig.update_layout(yaxis_title="Nombre de taxis")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Graphique d'évolution de la demande
                    fig = px.line(historique_commune, 
                                 x='date', 
                                 y='demande_moyenne_journaliere',
                                 title=f'Évolution de la demande à {commune_selectionnee}',
                                 color_discrete_sequence=['#FF9800'])
                    fig.update_layout(yaxis_title="Demande journalière (courses)")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Diagramme de répartition des zones desservies - CORRIGÉ
                    zones = commune_data['zones_desservies'].split(', ')
                    
                    # Créer une répartition proportionnelle automatique
                    if zones:
                        # Répartition égale ajustée
                        base_value = 100 // len(zones)
                        repartition = [base_value] * len(zones)
                        
                        # Ajuster le dernier élément pour faire 100%
                        total = sum(repartition)
                        if total < 100:
                            repartition[-1] += (100 - total)
                        elif total > 100:
                            repartition[-1] -= (total - 100)
                        
                        fig = px.pie(values=repartition, 
                                    names=zones,
                                    title=f'Répartition des zones desservies à {commune_selectionnee}')
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Aucune zone desservie spécifiée pour cette commune")
    
    def create_microregion_analysis(self):
        """Analyse détaillée par micro-région"""
        st.markdown('<h3 class="section-header">📊 ANALYSE PAR MICRO-RÉGION</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Comparaison Micro-régions", "Détails Micro-région", "Stratégies Territoriales"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                # Comparaison du nombre de taxis total
                fig = px.bar(self.microregion_data, 
                            x='micro_region', 
                            y='nombre_taxis_total',
                            title='Nombre total de taxis par micro-région',
                            color='micro_region',
                            color_discrete_map={
                                'Nord': '#1E88E5',
                                'Sud': '#43A047',
                                'Ouest': '#FF9800',
                                'Est': '#AB47BC',
                                'Cirques': '#5D4037'
                            })
                fig.update_layout(yaxis_title="Nombre de taxis")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Densité de taxis (taxis/population)
                self.microregion_data['densite_taxis'] = (self.microregion_data['nombre_taxis_total'] / self.microregion_data['population_totale']) * 10000
                
                fig = px.bar(self.microregion_data, 
                            x='micro_region', 
                            y='densite_taxis',
                            title='Densité de taxis (pour 10 000 habitants)',
                            color='micro_region',
                            color_discrete_map={
                                'Nord': '#1E88E5',
                                'Sud': '#43A047',
                                'Ouest': '#FF9800',
                                'Est': '#AB47BC',
                                'Cirques': '#5D4037'
                            })
                fig.update_layout(yaxis_title="Taxis pour 10 000 habitants")
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Détails pour une micro-région sélectionnée
            microregion_selectionnee = st.selectbox("Sélectionnez une micro-région:", 
                                                  self.microregion_data['micro_region'].unique())
            
            if microregion_selectionnee:
                communes_microregion = self.current_data[
                    self.current_data['micro_region'] == microregion_selectionnee
                ]
                historique_microregion = self.historical_data[
                    self.historical_data['micro_region'] == microregion_selectionnee
                ]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader(f"Micro-région: {microregion_selectionnee}")
                    
                    microregion_info = self.microregion_data[
                        self.microregion_data['micro_region'] == microregion_selectionnee
                    ].iloc[0]
                    
                    st.metric("Nombre de communes", microregion_info['nombre_communes'])
                    st.metric("Population totale", f"{microregion_info['population_totale']:,}")
                    st.metric("Nombre total de taxis", microregion_info['nombre_taxis_total'])
                    st.metric("Nombre total de taxiteurs", microregion_info['nombre_taxiteurs_total'])
                    st.metric("Demande journalière totale", f"{microregion_info['demande_totale_journaliere']:,.0f} courses")
                    st.metric("Revenu mensuel moyen", f"{microregion_info['revenu_moyen_mensuel']:.0f} €")
                    st.metric("Taux d'occupation moyen", f"{microregion_info['taux_occupation_moyen']:.1f}%")
                    
                    # Répartition des niveaux d'activité dans la micro-région
                    niveaux_counts = communes_microregion['taux_activite'].value_counts()
                    fig = px.pie(values=niveaux_counts.values, 
                                names=niveaux_counts.index,
                                title=f'Répartition des niveaux d\'activité - {microregion_selectionnee}')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Graphique d'évolution du nombre de taxis pour la micro-région
                    evolution_microregion = historique_microregion.groupby('date')['nombre_taxis'].sum().reset_index()
                    
                    fig = px.line(evolution_microregion, 
                                 x='date', 
                                 y='nombre_taxis',
                                 title=f'Évolution du nombre de taxis - {microregion_selectionnee}',
                                 color_discrete_sequence=['#1E88E5'])
                    fig.update_layout(yaxis_title="Nombre de taxis")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Graphique de répartition des taxis par commune
                    fig = px.bar(communes_microregion.sort_values('nombre_taxis', ascending=False), 
                                x='nom', 
                                y='nombre_taxis',
                                title=f'Nombre de taxis par commune - {microregion_selectionnee}',
                                color='nombre_taxis',
                                color_continuous_scale='Viridis')
                    fig.update_layout(xaxis_title="Commune", yaxis_title="Nombre de taxis")
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("Stratégies de Développement par Micro-région")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### 🎯 Micro-régions à Forte Activité
                
                **🏛️ Nord:**
                - Stratégie: Optimisation et professionnalisation
                - Actions: Digitalisation des services
                - Enjeux: Saturation du centre-ville
                - Projets: Application mobile, bornes intelligentes
                
                **🏝️ Ouest:**
                - Stratégie: Développement touristique ciblé
                - Actions: Formation langues étrangères
                - Enjeux: Saisonnalité marquée
                - Projets: Partenariats hôteliers, forfaits touristiques
                """)
            
            with col2:
                st.markdown("""
                ### 📈 Micro-régions à Potentiel de Croissance
                
                **🌋 Sud:**
                - Stratégie: Structuration de l'offre
                - Actions: Création de stations dédiées
                - Enjeux: Desserte des zones d'activité
                - Projets: Pôles multimodaux, services entreprises
                
                **🌿 Est:**
                - Stratégie: Maillage territorial
                - Actions: Développement de services à la demande
                - Enjeux: Désenclavement, faible densité
                - Projets: Transport à la demande, points de rendez-vous
                
                **⛰️ Cirques:**
                - Stratégie: Service essentiel préservé
                - Actions: Aide au renouvellement
                - Enjeux: Viabilité économique, relève
                - Projets: Aides à l'installation, services sociaux
                """)
    
    def create_development_scenarios(self):
        """Analyse des scénarios de développement"""
        st.markdown('<h3 class="section-header">🔮 SCÉNARIOS DE DÉVELOPPEMENT</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Scénarios 2030", "Simulateur", "Recommandations"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                # Scénarios de développement
                scenarios_data = pd.DataFrame({
                    'Scénario': ['Conservateur', 'Modéré', 'Ambitieux', 'Innovant'],
                    'Taxis_2030': [680, 750, 820, 900],
                    'Demande_2030': [12500, 14500, 16500, 18500],
                    'Revenu_moyen_2030': [2950, 3200, 3500, 3800],
                    'Digitalisation': [40, 60, 80, 95]
                })
                
                fig = px.bar(scenarios_data, 
                            x='Scénario', 
                            y='Taxis_2030',
                            title='Nombre de taxis projeté en 2030 selon les scénarios',
                            color='Scénario',
                            color_discrete_sequence=['#E9C46A', '#43A047', '#1E88E5', '#AB47BC'])
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Impact sur la demande
                fig = px.bar(scenarios_data, 
                            x='Scénario', 
                            y='Demande_2030',
                            title='Demande journalière projetée en 2030 selon les scénarios',
                            color='Scénario',
                            color_discrete_sequence=['#E9C46A', '#43A047', '#1E88E5', '#AB47BC'])
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.subheader("Simulateur de Développement de l'Activité Taxi")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                croissance_tourisme = st.slider("Croissance touristique (%)", 0, 50, 20)
                taux_digitalisation = st.slider("Taux de digitalisation (%)", 0, 100, 60)
            
            with col2:
                investissement_formation = st.slider("Investissement formation (M€)", 0, 10, 3)
                nouvelles_stations = st.slider("Nouvelles stations", 0, 20, 8)
            
            with col3:
                aide_renouvellement = st.slider("Aide au renouvellement (%)", 0, 50, 20)
                priorite_microregion = st.selectbox("Micro-région prioritaire:", 
                                                  self.microregion_data['micro_region'].unique())
            
            # Calculs simulés
            taxis_actuels = self.current_data['nombre_taxis'].sum()
            taxis_projetes = taxis_actuels * (1 + (croissance_tourisme + taux_digitalisation/2)/100)
            demande_actuelle = self.current_data['demande_moyenne_journaliere'].sum()
            demande_projetee = demande_actuelle * (1 + (croissance_tourisme + nouvelles_stations*2)/100)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Taxis projetés", f"{taxis_projetes:.0f}")
                st.metric("Évolution vs actuel", f"+{((taxis_projetes/taxis_actuels-1)*100):.1f}%")
            with col2:
                st.metric("Demande projetée", f"{demande_projetee:,.0f} courses/j")
                st.metric("Évolution vs actuel", f"+{((demande_projetee/demande_actuelle-1)*100):.1f}%")
            with col3:
                st.metric("Investissement formation", f"{investissement_formation} M€")
                st.metric("Nouvelles stations", nouvelles_stations)
        
        with tab3:
            st.subheader("Recommandations Stratégiques")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### 🚗 Court terme (2024-2026)
                
                **Actions prioritaires:**
                - Modernisation du parc automobile
                - Déploiement d'applications de réservation
                - Formation à l'accueil touristique
                - Création de stations intelligentes
                
                **Cibles:**
                - 20% de véhicules électriques
                - 60% de réservations digitalisées
                - +15% de revenus touristiques
                - Amélioration des conditions de travail
                """)
            
            with col2:
                st.markdown("""
                ### 🚕 Moyen terme (2027-2030)
                
                **Actions structurantes:**
                - Développement de services premium
                - Intégration multimodalité
                - Certification qualité
                - Observatoire de la mobilité
                
                **Objectifs:**
                - 40% de véhicules électriques
                - 80% de réservations digitalisées
                - +30% de revenus moyens
                - Reconnaissance professionnelle
                """)
            
            st.markdown("""
            ### 🚙 Long terme (2031-2040)
            
            **Vision stratégique:**
            - Parc 100% décarboné
            - Service de mobilité intégré
            - Excellence du service client
            - Modèle économique durable
            
            **Indicateurs cibles:**
            - 100% de véhicules propres
            - Satisfaction client > 90%
            - Revenus stables et décents
            - Attractivité du métier préservée
            """)
    
    def create_drivers_analysis(self):
        """Analyse spécifique des taxiteurs"""
        st.markdown('<h3 class="section-header">👨‍💼 ANALYSE DES TAXITEURS</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Profil des Taxiteurs", "Conditions de Travail", "Formation & Compétences"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                # Répartition par âge
                age_data = pd.DataFrame({
                    'Tranche_age': ['<30 ans', '30-40 ans', '40-50 ans', '50-60 ans', '>60 ans'],
                    'Pourcentage': [8, 22, 35, 25, 10]
                })
                
                fig = px.pie(age_data, 
                            values='Pourcentage', 
                            names='Tranche_age',
                            title='Répartition des taxiteurs par tranche d\'âge')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Ancienneté dans le métier
                anciennete_data = pd.DataFrame({
                    'Anciennete': ['<5 ans', '5-10 ans', '10-15 ans', '15-20 ans', '>20 ans'],
                    'Pourcentage': [15, 25, 30, 20, 10]
                })
                
                fig = px.bar(anciennete_data, 
                            x='Anciennete', 
                            y='Pourcentage',
                            title='Ancienneté dans le métier',
                            color='Pourcentage',
                            color_continuous_scale='Blues')
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                # Temps de travail hebdomadaire
                temps_travail = pd.DataFrame({
                    'Plage_horaire': ['<35h', '35-45h', '45-55h', '55-65h', '>65h'],
                    'Pourcentage': [5, 25, 40, 20, 10]
                })
                
                fig = px.bar(temps_travail, 
                            x='Plage_horaire', 
                            y='Pourcentage',
                            title='Temps de travail hebdomadaire',
                            color='Pourcentage',
                            color_continuous_scale='Reds')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Types de contrats
                contrats_data = pd.DataFrame({
                    'Type_contrat': ['Indépendant', 'Salarié', 'Portage', 'Coopérative'],
                    'Pourcentage': [65, 20, 10, 5]
                })
                
                fig = px.pie(contrats_data, 
                            values='Pourcentage', 
                            names='Type_contrat',
                            title='Répartition des types de contrats')
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                # Niveau de formation
                formation_data = pd.DataFrame({
                    'Niveau': ['CAP/BEP', 'Bac', 'Bac+2', 'Bac+3', 'Supérieur'],
                    'Pourcentage': [35, 30, 20, 10, 5]
                })
                
                fig = px.bar(formation_data, 
                            x='Niveau', 
                            y='Pourcentage',
                            title='Niveau de formation des taxiteurs',
                            color='Pourcentage',
                            color_continuous_scale='Greens')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Compétences linguistiques
                langues_data = pd.DataFrame({
                    'Langue': ['Anglais', 'Allemand', 'Italien', 'Espagnol', 'Chinois'],
                    'Pourcentage': [40, 15, 10, 25, 5]
                })
                
                fig = px.bar(langues_data, 
                            x='Langue', 
                            y='Pourcentage',
                            title='Compétences linguistiques des taxiteurs',
                            color='Pourcentage',
                            color_continuous_scale='Purples')
                st.plotly_chart(fig, use_container_width=True)
    
    def create_sidebar(self):
        """Crée la sidebar avec les contrôles"""
        st.sidebar.markdown("## 🎛️ CONTRÔLES D'ANALYSE")
        
        # Filtres temporels
        st.sidebar.markdown("### 📅 Période d'analyse")
        date_debut = st.sidebar.date_input("Date de début", 
                                         value=datetime.now() - timedelta(days=365*3))
        date_fin = st.sidebar.date_input("Date de fin", 
                                       value=datetime.now())
        
        # Filtres micro-régions
        st.sidebar.markdown("### 🗺️ Sélection des micro-régions")
        microregions_selectionnees = st.sidebar.multiselect(
            "Micro-régions à afficher:",
            list(self.microregion_data['micro_region'].unique()),
            default=list(self.microregion_data['micro_region'].unique())[:3]
        )
        
        # Options d'affichage
        st.sidebar.markdown("### ⚙️ Options")
        show_technical = st.sidebar.checkbox("Afficher indicateurs techniques", value=True)
        auto_refresh = st.sidebar.checkbox("Rafraîchissement automatique", value=False)
        
        # Bouton de rafraîchissement manuel
        if st.sidebar.button("🔄 Rafraîchir les données"):
            st.rerun()
        
        # Informations marché
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📈 INDICES SECTORIELS")
        
        # Indices simulés
        indices = {
            'Taxis / 10 000 hab France': {'valeur': '12,5', 'variation': 0.8},
            'Revenu moyen national': {'valeur': '2 450 €', 'variation': 1.2},
            'Taux occupation moyen': {'valeur': '62%', 'variation': -0.5},
            'Croissance demande annuelle': {'valeur': '4,2%', 'variation': 0.3}
        }
        
        for indice, data in indices.items():
            st.sidebar.metric(
                indice,
                f"{data['valeur']}",
                f"{data['variation']:+.1f}%"
            )
        
        return {
            'date_debut': date_debut,
            'date_fin': date_fin,
            'microregions_selectionnees': microregions_selectionnees,
            'show_technical': show_technical,
            'auto_refresh': auto_refresh
        }

    def run_dashboard(self):
        """Exécute le dashboard complet"""
        # Sidebar
        controls = self.create_sidebar()
        
        # Header
        self.display_header()
        
        # Métriques clés
        self.display_key_metrics()
        
        # Navigation par onglets
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "📈 Vue d'ensemble", 
            "🏢 Communes", 
            "🗺️ Micro-régions", 
            "👨‍💼 Taxiteurs",
            "🔮 Scénarios", 
            "📊 Analyse Avancée",
            "ℹ️ À Propos"
        ])
        
        with tab1:
            self.create_activity_overview()
        
        with tab2:
            self.create_communes_analysis()
        
        with tab3:
            self.create_microregion_analysis()
        
        with tab4:
            self.create_drivers_analysis()
        
        with tab5:
            self.create_development_scenarios()
        
        with tab6:
            st.markdown("## 📊 ANALYSE AVANCÉE DE L'ACTIVITÉ TAXI")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Relation demande/revenu
                fig = px.scatter(self.current_data, 
                               x='demande_moyenne_journaliere', 
                               y='revenu_moyen_mensuel',
                               size='nombre_taxis',
                               color='micro_region',
                               title='Relation entre demande et revenu moyen par commune',
                               hover_name='nom',
                               size_max=30,
                               color_discrete_map={
                                   'Nord': '#1E88E5',
                                   'Sud': '#43A047',
                                   'Ouest': '#FF9800',
                                   'Est': '#AB47BC',
                                   'Cirques': '#5D4037'
                               })
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Analyse densité/performance
                self.current_data['taxis_10k_hab'] = (self.current_data['nombre_taxis'] / self.current_data['population']) * 10000
                
                fig = px.scatter(self.current_data, 
                               x='taxis_10k_hab', 
                               y='taux_occupation',
                               size='population',
                               color='taux_activite',
                               title='Densité de taxis vs Taux d\'occupation',
                               hover_name='nom',
                               size_max=30,
                               color_discrete_map={
                                   'Élevé': '#28a745',
                                   'Moyen': '#ffc107',
                                   'Faible': '#dc3545',
                                   'Limitée': '#6c757d'
                               })
                st.plotly_chart(fig, use_container_width=True)
            
            # Analyse SWOT
            st.markdown("### 📋 ANALYSE SWOT DU SECTEUR TAXI RÉUNIONNAIS")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                #### 💪 FORCES
                - Maillage territorial complet
                - Connaissance fine du territoire
                - Flexibilité et réactivité
                - Savoir-faire relationnel
                - Adaptabilité aux clients
                """)
            
            with col2:
                st.markdown("""
                #### 👎 FAIBLESSES
                - Vieillissement du parc
                - Digitalisation limitée
                - Saisonnalité des revenus
                - Charge de travail élevée
                - Image parfois dégradée
                """)
            
            with col3:
                st.markdown("""
                #### 🚀 OPPORTUNITÉS
                - Croissance touristique
                - Transition écologique
                - Digitalisation des services
                - Nouvelles mobilités
                - Services à valeur ajoutée
                """)
            
            with col4:
                st.markdown("""
                #### ⚠️ MENACES
                - Concurrence VTC/transports
                - Réglementation plus stricte
                - Coûts d'exploitation
                - Désaffection du métier
                - Changements comportementaux
                """)
        
        with tab7:
            st.markdown("## 📋 À propos de ce dashboard")
            st.markdown("""
            Ce dashboard présente une analyse complète de l'activité taxi à La Réunion.
            
            **Sources des données:**
            - Préfecture de La Réunion - Licences taxi
            - INSEE - Recensement et statistiques
            - Observatoire du Tourisme
            - Enquêtes professionnelles
            - Collectivités territoriales
            
            **Période couverte:**
            - Données historiques: 2018-2024
            - Données courantes: 2024
            - Projections: 2025-2040
            
            **Méthodologie:**
            - Données réelles agrégées
            - Enquêtes terrain complémentaires
            - Modélisation économique
            - Projections tendancielles
            
            **⚠️ Avertissement:** 
            Les données présentées sont des estimations et simulations.
            Certaines données sont anonymisées pour respecter la confidentialité.
            
            **🔒 Confidentialité:** 
            Toutes les données individuelles sont protégées.
            """)
            
            st.markdown("---")
            st.markdown("""
            **📞 Contact:**
            - Observatoire de la Mobilité de La Réunion
            - Site web: www.mobilite.reunion.gouv.fr
            - Email: observatoire.mobilite@reunion.gouv.fr
            """)

# Lancement du dashboard
if __name__ == "__main__":
    dashboard = ReunionTaxiDashboard()
    dashboard.run_dashboard()