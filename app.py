import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import json
import os
import unicodedata

# ==========================================
# 1. CONFIGURATION DE LA PAGE
# ==========================================
st.set_page_config(layout="wide", page_title="Expert CATNAT", page_icon="🛡️")

# ==========================================
# 2. GESTION DU THEME (CLAIR / SOMBRE)
# ==========================================
dark_mode = st.sidebar.toggle("🌙 Activer le Mode Sombre", value=False)

if dark_mode:
    # CSS MODE SOMBRE
    st.markdown("""
        <style>
        .stApp { background-color: #0e1117; color: #fafafa; }
        div[data-testid="stVerticalBlock"] > div:has(div.element-container) {
            background-color: #1e1e1e; border: 1px solid #333; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #333; }
        h1, h2, h3, p, span { color: #ffffff !important; }
        div[data-testid="stMetricValue"] { color: #2ea043 !important; }
        </style>
        """, unsafe_allow_html=True)
else:
    # CSS MODE CLAIR (Inspiré du Logo : Blanc & Vert Foncé)
    st.markdown("""
        <style>
        .stApp { background-color: #f4f6f9; color: #1e1e1e; }
        div[data-testid="stVerticalBlock"] > div:has(div.element-container) {
            background-color: #ffffff; border: 1px solid #e9ecef; padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        }
        [data-testid="stSidebar"] { background-color: #ffffff; border-right: 2px solid #0f5132; }
        h1, h2, h3 { color: #0f5132 !important; font-family: 'Helvetica', sans-serif; font-weight: 700; }
        div[data-testid="stMetricValue"] { color: #0f5132 !important; font-weight: 800;}
        </style>
        """, unsafe_allow_html=True)

# Couleurs RPA (Fixes)
RPA_COLORS = {"ROUGE": "#e31a1c", "ORANGE": "#ff7f00", "VERT": "#33a02c"}

# ==========================================
# 3. CHARGEMENT ET NETTOYAGE DES DONNÉES
# ==========================================
def clean_name(text):
    if not isinstance(text, str) or text == "nan": return ""
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    return text.replace('-', ' ').strip().upper()

@st.cache_data
def load_data():
    df = pd.read_csv('FUSION_TOTALE_CATNAT.csv', low_memory=False)
    df['CAPITAL_ASSURE'] = pd.to_numeric(df['CAPITAL_ASSURE'], errors='coerce').fillna(0)
    df['PRIME_NETTE'] = df['PRIME_NETTE'].astype(str).str.replace('"', '').str.replace(',', '.')
    df['PRIME_NETTE'] = pd.to_numeric(df['PRIME_NETTE'], errors='coerce').fillna(0)
    df['WILAYA_UP'] = df['WILAYA'].apply(clean_name)
    df['COMMUNE_UP'] = df['COMMUNE'].apply(clean_name)
    df['TYPE_CLEAN'] = df['TYPE'].astype(str).str.split('-').str[-1].str.strip()
    
    def map_zone_colors(z):
        z_str = str(z).strip()
        if z_str == 'III': return "ZONE III (Rouge)"
        elif z_str in ['IIa', 'IIb']: return "ZONE II (Orange)"
        else: return "ZONE 0/I (Vert)"
    df['ZONE_RPA_CAT'] = df['ZONE_RPA'].apply(map_zone_colors)
    return df

@st.cache_data
def load_geojson(level):
    filename = f"dza_admin{level}.geojson"
    if not os.path.exists(filename): return None
    with open(filename, 'r', encoding='utf-8') as f: return json.load(f)

df = load_data()
geo_wilayas = load_geojson(1)
geo_communes = load_geojson(2)

if 'selected_wilaya' not in st.session_state:
    st.session_state.selected_wilaya = "Toutes les Wilayas"

# ==========================================
# 4. MENU LATÉRAL
# ==========================================
try:
    st.sidebar.image("logo.png", width=180)
except:
    st.sidebar.markdown("### 🛡️ EXPERT CATNAT")

st.sidebar.divider()
page = st.sidebar.radio(
    "Modules d'analyse :",
    ["🗺️ Cartographie & Dashboard", "📝 Souscription de Contrat", "🎲 Simulation Monte Carlo", "📜 Historique des Séismes"]
)
st.sidebar.divider()
st.sidebar.caption("Système d'évaluation de l'exposition au risque sismique")


# ==========================================
# PAGE 1 : CARTOGRAPHIE & DASHBOARD
# ==========================================
if page == "🗺️ Cartographie & Dashboard":
    st.title("Cartographie des Risques Sismiques")
    
    def get_rpa_color(name):
        w = str(name).upper()
        if w in ["ALGER", "BOUMERDES", "BLIDA", "TIPAZA", "CHLEF", "AIN DEFLA"]: return RPA_COLORS["ROUGE"]
        elif w in ["ORAN", "CONSTANTINE", "SETIF", "BEJAIA", "TIZI OUZOU", "JIJEL", "SKIKDA", "ANNABA", "MEDEA"]: return RPA_COLORS["ORANGE"]
        return RPA_COLORS["VERT"]

    def get_bounds(features):
        lats, lons = [], []
        def extract_coords(c):
            if isinstance(c[0], (int, float)): lons.append(c[0]); lats.append(c[1])
            else:
                for item in c: extract_coords(item)
        for f in features:
            geom = f.get('geometry', {})
            if geom: extract_coords(geom.get('coordinates', []))
        if lats and lons: return [[min(lats), min(lons)], [max(lats), max(lons)]]
        return None

    # Barre de recherche
    col_search, col_reset = st.columns([3, 1])
    liste_w = ["Toutes les Wilayas"] + sorted(df['WILAYA_UP'].dropna().unique().tolist())
    index_actuel = liste_w.index(st.session_state.selected_wilaya) if st.session_state.selected_wilaya in liste_w else 0
    
    choix = col_search.selectbox("Rechercher / Sélectionner une Wilaya :", options=liste_w, index=index_actuel)
    if col_reset.button("🔄 Vue Globale Algérie", use_container_width=True):
        st.session_state.selected_wilaya = "Toutes les Wilayas"
        st.rerun()

    if choix != st.session_state.selected_wilaya:
        st.session_state.selected_wilaya = choix
        st.rerun()

    is_national = (st.session_state.selected_wilaya == "Toutes les Wilayas")
    
    # ---------------- LA CARTE ----------------
    bounds_to_fit, display_data, tooltip_fields, tooltip_aliases = None, None, [], []
    
    if not is_national and geo_communes:
        features_wilaya = [f for f in geo_communes['features'] if clean_name(f['properties'].get('adm1_name', '')) == st.session_state.selected_wilaya]
        if features_wilaya:
            display_data = {"type": "FeatureCollection", "features": features_wilaya}
            tooltip_fields, tooltip_aliases = ['adm1_name', 'adm2_name'], ['Wilaya:', 'Commune:']
            bounds_to_fit = get_bounds(features_wilaya)
            m = folium.Map(tiles="cartodbdark_matter" if dark_mode else "cartodbpositron")
        else:
            st.warning("Bordures des communes non disponibles pour cette Wilaya.")
            m = folium.Map(location=[28.0, 2.0], zoom_start=5, tiles="cartodbdark_matter" if dark_mode else "cartodbpositron")
    elif geo_wilayas:
        display_data = geo_wilayas
        tooltip_fields, tooltip_aliases = ['adm1_name'], ['Wilaya:']
        m = folium.Map(location=[28.0, 2.0], zoom_start=5, tiles="cartodbdark_matter" if dark_mode else "cartodbpositron")

    if display_data:
        folium.GeoJson(
            display_data, 
            style_function=lambda f: {'fillColor': get_rpa_color(f['properties'].get('adm1_name', '').upper()), 'color': 'white', 'weight': 1, 'fillOpacity': 0.6}, 
            tooltip=folium.GeoJsonTooltip(fields=tooltip_fields, aliases=tooltip_aliases)
        ).add_to(m)
        if bounds_to_fit: m.fit_bounds(bounds_to_fit)
        st_folium(m, width="100%", height=400)

    # ---------------- LE DASHBOARD ----------------
    dash_df = df if is_national else df[df['WILAYA_UP'] == st.session_state.selected_wilaya]
    st.header(f"Analyse : {'Algérie Entière' if is_national else st.session_state.selected_wilaya}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Capital Total Exposé", f"{dash_df['CAPITAL_ASSURE'].sum():,.0f} DA".replace(',', ' '))
    c2.metric("Total Primes Nettes", f"{dash_df['PRIME_NETTE'].sum():,.0f} DA".replace(',', ' '))
    c3.metric("Contrats Actifs", f"{len(dash_df):,}".replace(',', ' '))

    st.divider()

    col_pie, col_bar = st.columns(2)
    bg_chart = "rgba(0,0,0,0)"
    text_color = "#ffffff" if dark_mode else "#1e1e1e"

    with col_pie:
        st.subheader("Exposition par Zone RPA")
        zone_data = dash_df.groupby('ZONE_RPA_CAT')['CAPITAL_ASSURE'].sum().reset_index()
        fig_pie = px.pie(zone_data, names='ZONE_RPA_CAT', values='CAPITAL_ASSURE', hole=0.4, 
                         color='ZONE_RPA_CAT', color_discrete_map={"ZONE III (Rouge)": RPA_COLORS["ROUGE"], "ZONE II (Orange)": RPA_COLORS["ORANGE"], "ZONE 0/I (Vert)": RPA_COLORS["VERT"]})
        fig_pie.update_layout(paper_bgcolor=bg_chart, font_color=text_color)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_bar:
        st.subheader("Exposition par Type de Bien")
        type_data = dash_df.groupby('TYPE_CLEAN')['CAPITAL_ASSURE'].sum().reset_index()
        fig_bar = px.bar(type_data, x='TYPE_CLEAN', y='CAPITAL_ASSURE', text_auto='.2s')
        fig_bar.update_traces(marker_color='#0f5132' if not dark_mode else '#2ea043')
        fig_bar.update_layout(paper_bgcolor=bg_chart, plot_bgcolor=bg_chart, font_color=text_color)
        st.plotly_chart(fig_bar, use_container_width=True)

    # ---------------- POINTS CHAUDS & CLASSEMENT ----------------
    group_col = 'WILAYA_UP' if is_national else 'COMMUNE_UP'
    grouped_geo = dash_df.groupby(group_col)['CAPITAL_ASSURE'].sum().reset_index()
    grouped_geo_positive = grouped_geo[grouped_geo['CAPITAL_ASSURE'] > 0]

    st.divider()
    o1, o2 = st.columns(2)
    with o1:
        st.subheader(f"🔥 Points Chauds (Top 3 {'Wilayas' if is_national else 'Communes'})")
        top3 = grouped_geo.sort_values(ascending=False, by='CAPITAL_ASSURE').head(3)
        fig_hot = px.bar(top3, x=group_col, y='CAPITAL_ASSURE', text_auto='.2s')
        fig_hot.update_traces(marker_color=RPA_COLORS["ROUGE"])
        fig_hot.update_layout(paper_bgcolor=bg_chart, plot_bgcolor=bg_chart, font_color=text_color)
        st.plotly_chart(fig_hot, use_container_width=True)
    with o2:
        st.subheader(f"💡 Opportunités (Top 3 {'Wilayas' if is_national else 'Communes'})")
        bot3 = grouped_geo_positive.sort_values(ascending=True, by='CAPITAL_ASSURE').head(3)
        fig_cold = px.bar(bot3, x=group_col, y='CAPITAL_ASSURE', text_auto='.2s')
        fig_cold.update_traces(marker_color=RPA_COLORS["VERT"])
        fig_cold.update_layout(paper_bgcolor=bg_chart, plot_bgcolor=bg_chart, font_color=text_color)
        st.plotly_chart(fig_cold, use_container_width=True)

    # Tableau du classement des Wilayas
    if is_national:
        st.divider()
        st.subheader("📋 Classement des Wilayas par Zone RPA")
        table_df = df.groupby('WILAYA_UP').agg({'ZONE_RPA_CAT': lambda x: x.mode()[0] if not x.empty else 'Inconnu', 'CAPITAL_ASSURE': 'sum'}).reset_index()
        table_df = table_df.sort_values(by=['ZONE_RPA_CAT', 'CAPITAL_ASSURE'], ascending=[False, False])
        table_df.columns = ["Wilaya", "Zone Principale", "Capital Exposé (DA)"]
        st.dataframe(table_df, use_container_width=True, hide_index=True)


# ==========================================
# PAGE 2 : SOUSCRIPTION DE CONTRAT
# ==========================================
elif page == "📝 Souscription de Contrat":
    st.title("Module de Souscription Intelligent")
    
    with st.container():
        c_w, c_c = st.columns(2)
        liste_wilayas = sorted(df['WILAYA_UP'].dropna().unique())
        sub_wilaya = c_w.selectbox("Wilaya du projet", liste_wilayas)
        
        # Le dropdown des communes s'adapte à la wilaya choisie
        communes_list = sorted(df[df['WILAYA_UP'] == sub_wilaya]['COMMUNE_UP'].dropna().unique())
        sub_commune = c_c.selectbox("Commune", communes_list)

        c_t, c_cap = st.columns(2)
        type_bien = c_t.selectbox("Nature du Bien", ["Immobilier (Habitation)", "Commercial (Bureaux/Magasins)", "Industriel (Usines/Dépôts)"])
        capital = c_cap.number_input("Capital total à assurer (DZD)", min_value=0.0, value=50000000.0, step=10000000.0)

    try:
        zone_auto = df[df['WILAYA_UP'] == sub_wilaya]['ZONE_RPA'].mode()[0]
    except:
        zone_auto = "IIa"
    st.caption(f"📍 Zone RPA détectée : **Zone {zone_auto}**")

    if st.button("🚀 Générer le Diagnostic", use_container_width=True):
        taux_base = {"0": 0.0001, "I": 0.0003, "IIa": 0.0007, "IIb": 0.0012, "III": 0.0020, "IV": 0.0030}
        coeffs_type = {"Immobilier (Habitation)": 1.0, "Commercial (Bureaux/Magasins)": 1.4, "Industriel (Usines/Dépôts)": 2.2}
        
        score_zone = {"0": 10, "I": 25, "IIa": 45, "IIb": 65, "III": 85, "IV": 100}.get(zone_auto, 50)
        score_bien = {"Immobilier (Habitation)": 20, "Commercial (Bureaux/Magasins)": 50, "Industriel (Usines/Dépôts)": 90}.get(type_bien, 50)
        score_final = min((score_zone * 0.6) + (score_bien * 0.4), 100.0)
        prime = capital * taux_base.get(zone_auto, 0.0010) * coeffs_type.get(type_bien, 1.0)

        st.divider()
        g1, g2 = st.columns([1, 1.5])
        with g1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=score_final, number={'suffix': "%"},
                gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#1e1e1e" if not dark_mode else "#fafafa"},
                       'steps': [{'range': [0, 40], 'color': RPA_COLORS["VERT"]}, {'range': [40, 75], 'color': RPA_COLORS["ORANGE"]}, {'range': [75, 100], 'color': RPA_COLORS["ROUGE"]}]}
            ))
            fig.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)", font_color="#fff" if dark_mode else "#000")
            st.plotly_chart(fig, use_container_width=True)

        with g2:
            st.metric("Prime Nette Annuelle Estimée", f"{prime:,.2f} DZD".replace(',', ' '))
            if score_final < 40: st.success("🟢 **RISQUE ACCEPTABLE** : Profil standard.")
            elif score_final < 75: st.warning("🟠 **SURVEILLANCE** : Application d'une franchise recommandée.")
            else: st.error("🔴 **RISQUE ÉLEVÉ** : Étude de vulnérabilité obligatoire.")


# ==========================================
# PAGE 3 : MONTE CARLO
# ==========================================
elif page == "🎲 Simulation Monte Carlo":
    st.title("Simulation de Portefeuille (Monte Carlo)")
    
    if 'Source_Annee' in df.columns:
        df_2024 = df[df['Source_Annee'] == 2024].copy()
        if not df_2024.empty:
            df_2024['SEVERITY_FACTOR'] = df_2024['TYPE_CLEAN'].apply(lambda t: 0.7 if 'industrielle' in str(t).lower() else (0.5 if 'commercial' in str(t).lower() else 0.3))
            
            with st.container():
                c1, c2 = st.columns(2)
                mc_wilaya = c1.selectbox("Cible de la simulation", sorted(df_2024['WILAYA_UP'].unique()))
                # Curseur de fréquence ajusté (0 à 20% avec step 0.1%)
                lambda_freq = c2.slider("Fréquence annuelle d'occurrence", min_value=0.0, max_value=0.20, value=0.05, step=0.001, format="%.3f")

            df_w = df_2024[df_2024['WILAYA_UP'] == mc_wilaya].copy()
            expo_totale = (df_w['CAPITAL_ASSURE'] * df_w['SEVERITY_FACTOR'] * 0.30).sum()
            total_primes = df_w['PRIME_NETTE'].sum()

            col1, col2, col3 = st.columns(3)
            col1.metric("Polices Actives", len(df_w))
            col2.metric("Exposition (PML)", f"{expo_totale:,.0f} DA".replace(',', ' '))
            col3.metric("Primes Nettes", f"{total_primes:,.0f} DA".replace(',', ' '))

            if expo_totale > 0 and st.button("Lancer la Simulation (100k Itérations)", use_container_width=True):
                with st.spinner("Calcul des scénarios..."):
                    n_sim = 100000
                    losses = np.zeros(n_sim)
                    n_events = np.random.poisson(lambda_freq, n_sim)
                    for i in range(n_sim):
                        if n_events[i] > 0:
                            total = 0
                            for _ in range(n_events[i]):
                                mdr = min(np.random.lognormal(np.log(0.05) - 0.5 * (0.8**2), 0.8), 0.8)
                                total += expo_totale * mdr
                            losses[i] = total
                            
                st.divider()
                r1, r2 = st.columns([1, 1.5])
                with r1:
                    st.write(f"**Charge moyenne :** {losses.mean():,.0f} DA")
                    st.error(f"**VaR 99.5% :** {np.percentile(losses, 99.5):,.0f} DA")
                    lr = (losses.mean() / total_primes * 100) if total_primes > 0 else 0
                    if lr < 50: st.success(f"**S/P Technique : {lr:.2f}%** (Rentable)")
                    elif lr < 80: st.warning(f"**S/P Technique : {lr:.2f}%** (Tendu)")
                    else: st.error(f"**S/P Technique : {lr:.2f}%** (Déficitaire)")
                with r2:
                    pertes = losses[losses > 0]
                    if len(pertes) > 0:
                        fig = px.histogram(x=pertes, nbins=40, color_discrete_sequence=['#0f5132' if not dark_mode else '#2ea043'])
                        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#fff" if dark_mode else "#000")
                        st.plotly_chart(fig, use_container_width=True)


# ==========================================
# PAGE 4 : HISTORIQUE DES SÉISMES
# ==========================================
elif page == "📜 Historique des Séismes":
    st.title("Historique des Séismes Majeurs en Algérie")
    st.markdown("L'Algérie, située à la frontière des plaques tectoniques eurasienne et africaine, possède une longue histoire sismique. Voici les événements ayant façonné les règles parasismiques (RPA).")
    
    st.divider()
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.error("### 2003\n**Magnitude : 6.8**")
    with col2:
        st.markdown("#### Séisme de Boumerdès (Zemmouri)")
        st.write("Le séisme le plus destructeur de l'histoire récente. Il a touché Alger et Boumerdès, causant plus de 2 200 morts et d'immenses dégâts matériels. Il a entraîné la **révision majeure du RPA en 2003**.")
    
    st.write("---")
    
    col3, col4 = st.columns([1, 3])
    with col3:
        st.warning("### 1980\n**Magnitude : 7.1**")
    with col4:
        st.markdown("#### Séisme d'El Asnam (Chlef)")
        st.write("Le séisme le plus puissant enregistré en Algérie. Il a détruit la ville à 80% et fait plus de 2 600 victimes. Cet événement a donné naissance au **tout premier code parasismique algérien (RPA 81)**.")
        
    st.write("---")
    
    col5, col6 = st.columns([1, 3])
    with col5:
        st.warning("### 1954\n**Magnitude : 6.7**")
    with col6:
        st.markdown("#### Séisme d'Orléansville (Ancien nom de Chlef)")
        st.write("Un séisme majeur qui avait déjà ravagé la même région avant 1980, prouvant la forte sismicité cyclique de cette zone de faille.")