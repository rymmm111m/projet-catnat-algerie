import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import json
import os

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="RPA 2024 & CATNAT Algérie")

# Couleurs Réglementaires RPA 2024
RPA_COLORS = {
    "ZONE_3": "#e31a1c", # ROUGE
    "ZONE_2": "#ff7f00", # ORANGE
    "ZONE_1": "#33a02c"  # VERT
}

# --- CHARGEMENT DES DONNEES ---
@st.cache_data
def load_csv():
    df = pd.read_csv('FUSION_TOTALE_CATNAT.csv')
    df['CAPITAL_ASSURE'] = pd.to_numeric(df['CAPITAL_ASSURE'], errors='coerce').fillna(0)
    df['PRIME_NETTE'] = pd.to_numeric(df['PRIME_NETTE'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
    df['RATIO_RISQUE'] = (df['PRIME_NETTE'] / (df['CAPITAL_ASSURE'] + 1)) * 1000
    
    # Nettoyage des noms pour la jointure
    df['WILAYA_UP'] = df['WILAYA'].str.split('-').str[-1].str.strip().str.upper()
    df['COMMUNE_UP'] = df['COMMUNE'].str.split('-').str[-1].str.strip().str.upper()
    
    # Nettoyage du Type de risque (Enlève le "1 - " au début)
    df['TYPE_CLEAN'] = df['TYPE'].astype(str).str.split('-').str[-1].str.strip()
    
    # Création de la colonne ZONE_RPA selon la Wilaya
    def assign_zone(w):
        if w in ["ALGER", "BOUMERDES", "BLIDA", "TIPAZA", "CHLEF", "AIN DEFLA"]:
            return "ZONE 3 (Élevée)"
        elif w in ["ORAN", "CONSTANTINE", "SETIF", "BEJAIA", "TIZI OUZOU", "JIJEL", "SKIKDA", "ANNABA", "MEDEA"]:
            return "ZONE 2 (Moyenne)"
        else:
            return "ZONE 1 / 0 (Faible)"
            
    df['ZONE_RPA'] = df['WILAYA_UP'].apply(assign_zone)
    return df

@st.cache_data
def load_geojson(level):
    filename = f"dza_admin{level}.geojson"
    if not os.path.exists(filename):
        st.error(f"Fichier {filename} manquant !")
        return None
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

# --- LOGIQUE RPA 2024 ---
def get_rpa_color(name):
    w = str(name).upper()
    if w in ["ALGER", "BOUMERDES", "BLIDA", "TIPAZA", "CHLEF", "AIN DEFLA"]:
        return RPA_COLORS["ZONE_3"]
    elif w in ["ORAN", "CONSTANTINE", "SETIF", "BEJAIA", "TIZI OUZOU", "JIJEL", "SKIKDA", "ANNABA", "MEDEA"]:
        return RPA_COLORS["ZONE_2"]
    return RPA_COLORS["ZONE_1"]

# --- ETAT ---
if 'selected_wilaya' not in st.session_state:
    st.session_state.selected_wilaya = None

# --- UI ---
df = load_csv()
geo_wilayas = load_geojson(1)
geo_communes = load_geojson(2)

st.title("🛡️ Algérie : Risques Sismiques RPA 2024")

if st.session_state.selected_wilaya:
    if st.sidebar.button("🌍 Retour Algérie Entière"):
        st.session_state.selected_wilaya = None
        st.rerun()

# --- CARTE ---
if st.session_state.selected_wilaya:
    center = [36.0, 3.5]
    zoom = 8
    display_data = {
        "type": "FeatureCollection",
        "features": [f for f in geo_communes['features'] 
                     if f['properties'].get('adm1_name', '').upper() == st.session_state.selected_wilaya]
    }
    tooltip_fields = ['adm1_name', 'adm2_name']
    tooltip_aliases = ['Wilaya:', 'Commune:']
else:
    center = [28.0, 2.0]
    zoom = 5
    display_data = geo_wilayas
    tooltip_fields = ['adm1_name']
    tooltip_aliases = ['Wilaya:']

m = folium.Map(location=center, zoom_start=zoom, tiles="cartodbpositron")

def style_fn(feature):
    w_name = feature['properties'].get('adm1_name', '').upper()
    return {
        'fillColor': get_rpa_color(w_name),
        'color': 'white',
        'weight': 1,
        'fillOpacity': 0.7
    }

folium.GeoJson(
    display_data,
    style_function=style_fn,
    tooltip=folium.GeoJsonTooltip(fields=tooltip_fields, aliases=tooltip_aliases)
).add_to(m)

map_res = st_folium(m, width="100%", height=600, key="map_algeria")

# CLIC DETECTION
if map_res.get("last_active_drawing") and not st.session_state.selected_wilaya:
    clicked_w = map_res["last_active_drawing"]["properties"].get("adm1_name", "").upper()
    if clicked_w:
        st.session_state.selected_wilaya = clicked_w
        st.rerun()

# --- DASHBOARD ANALYTIQUE ---
st.divider()

if st.session_state.selected_wilaya:
    dashboard_df = df[df['WILAYA_UP'] == st.session_state.selected_wilaya]
    st.header(f"📊 Dashboard Portefeuille : {st.session_state.selected_wilaya}")
else:
    dashboard_df = df
    st.header("📊 Dashboard Portefeuille : Algérie Entière")

if not dashboard_df.empty:
    # --- BLOC 1 : KPIs GLOBAUX ---
    st.subheader("1. Chiffres Clés")
    c1, c2, c3 = st.columns(3)
    c1.metric("Capital Total Exposé (DZD)", f"{dashboard_df['CAPITAL_ASSURE'].sum():,.0f}")
    c2.metric("Total Primes Nettes (DZD)", f"{dashboard_df['PRIME_NETTE'].sum():,.0f}")
    c3.metric("Ratio de Risque Moyen", f"{dashboard_df['RATIO_RISQUE'].mean():.2f}")
    
    st.markdown("---")
    
    # --- BLOC 2 & 3 : ANALYSE PAR ZONE ET PAR NATURE ---
    col_graph1, col_graph2 = st.columns(2)
    with col_graph1:
        st.subheader("2. Exposition par Zone RPA")
        zone_data = dashboard_df.groupby('ZONE_RPA')['CAPITAL_ASSURE'].sum()
        st.bar_chart(zone_data)
        
    with col_graph2:
        st.subheader("3. Exposition par Nature du Risque")
        type_data = dashboard_df.groupby('TYPE_CLEAN')['CAPITAL_ASSURE'].sum()
        st.bar_chart(type_data)
        
    st.markdown("---")
    
    # --- BLOC 4 : SUR-CONCENTRATIONS (TOP 5) ---
    st.subheader("4. Points Chauds : Top 5 des Sur-concentrations (Risque)")
    col_top1, col_top2 = st.columns(2)
    with col_top1:
        st.write("**Top 5 Wilayas (Capital le plus élevé)**")
        top_w = df.groupby('WILAYA_UP')['CAPITAL_ASSURE'].sum().sort_values(ascending=False).head(5)
        st.bar_chart(top_w)
        
    with col_top2:
        st.write("**Top 5 Communes (Capital le plus élevé)**")
        top_c = dashboard_df.groupby('COMMUNE_UP')['CAPITAL_ASSURE'].sum().sort_values(ascending=False).head(5)
        st.dataframe(top_c.reset_index(), use_container_width=True)

    st.markdown("---")

    # --- BLOC 5 : SOUS-CONCENTRATIONS (FLOP 5) ---
    st.subheader("5. Opportunités : Top 5 des Sous-concentrations (Désert Commercial)")
    col_flop1, col_flop2 = st.columns(2)
    
    # On filtre les valeurs à > 0 pour éviter d'afficher des zones où l'assureur n'a strictement aucun contrat
    df_active = df[df['CAPITAL_ASSURE'] > 0]
    dashboard_df_active = dashboard_df[dashboard_df['CAPITAL_ASSURE'] > 0]

    with col_flop1:
        st.write("**Bottom 5 Wilayas (Capital le plus bas)**")
        flop_w = df_active.groupby('WILAYA_UP')['CAPITAL_ASSURE'].sum().sort_values(ascending=True).head(5)
        st.bar_chart(flop_w)
        
    with col_flop2:
        st.write("**Bottom 5 Communes (Capital le plus bas)**")
        flop_c = dashboard_df_active.groupby('COMMUNE_UP')['CAPITAL_ASSURE'].sum().sort_values(ascending=True).head(5)
        st.dataframe(flop_c.reset_index(), use_container_width=True)

else:
    st.warning("Aucune donnée disponible pour cette sélection.")