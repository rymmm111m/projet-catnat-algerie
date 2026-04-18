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
# 1. CONFIGURATION GÉNÉRALE
# ==========================================
st.set_page_config(layout="wide", page_title="Système Expert CATNAT", page_icon="🛡️")

RPA_COLORS = {
    "ROUGE": "#e31a1c",
    "ORANGE": "#ff7f00",
    "VERT": "#33a02c"
}

# ==========================================
# 2. THEME TOGGLE & CSS
# ==========================================
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

def inject_css(dark_mode):
    if dark_mode:
        bg_app = "#0f1117"
        bg_card = "#1a1d27"
        bg_card2 = "#1e2130"
        text_primary = "#e8eaf0"
        text_secondary = "#9ba3b8"
        border_color = "#2e3347"
        metric_bg = "#1e2130"
        metric_border = "#2e3347"
        sidebar_bg = "#111318"
        sidebar_text = "#e8eaf0"
        sidebar_accent = "#b5e61d"
        sidebar_border = "#1f6f3a"
        btn_bg = "#1f6f3a"
        btn_hover = "#28924e"
        input_bg = "#1e2130"
        divider = "#2e3347"
        plotly_paper = "rgba(26,29,39,0)"
        plotly_plot = "rgba(30,33,48,0)"
        plotly_font = "#e8eaf0"
        header_gradient = "linear-gradient(135deg, #1a1d27 0%, #0f1117 100%)"
        shadow = "0 4px 24px rgba(0,0,0,0.5)"
        tag_bg = "#1f6f3a22"
        tag_border = "#1f6f3a"
    else:
        bg_app = "#f4f6f3"
        bg_card = "#ffffff"
        bg_card2 = "#f9fafb"
        text_primary = "#1a2e1c"
        text_secondary = "#5a6b5c"
        border_color = "#dce8dc"
        metric_bg = "#ffffff"
        metric_border = "#c8deca"
        sidebar_bg = "#1a4d2e"
        sidebar_text = "#f0f7f1"
        sidebar_accent = "#b5e61d"
        sidebar_border = "#2d6e43"
        btn_bg = "#1a4d2e"
        btn_hover = "#226038"
        input_bg = "#f0f7f1"
        divider = "#dce8dc"
        plotly_paper = "rgba(255,255,255,0)"
        plotly_plot = "rgba(249,250,251,0)"
        plotly_font = "#1a2e1c"
        header_gradient = "linear-gradient(135deg, #1a4d2e 0%, #236b3e 100%)"
        shadow = "0 2px 16px rgba(26,77,46,0.10)"
        tag_bg = "#1a4d2e15"
        tag_border = "#1a4d2e"

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    /* ---- BASE ---- */
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}
    .stApp {{
        background-color: {bg_app};
        color: {text_primary};
    }}
    
    /* ---- SIDEBAR ---- */
    [data-testid="stSidebar"] {{
        background: {sidebar_bg} !important;
        border-right: 3px solid {sidebar_border};
        box-shadow: 4px 0 24px rgba(0,0,0,0.18);
    }}
    [data-testid="stSidebar"] * {{
        color: {sidebar_text} !important;
    }}
    [data-testid="stSidebar"] .stRadio label {{
        background: rgba(255,255,255,0.06);
        border: 1px solid {sidebar_border};
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 6px;
        font-size: 0.93rem;
        font-weight: 500;
        transition: all 0.2s;
        display: flex;
        align-items: center;
    }}
    [data-testid="stSidebar"] .stRadio label:hover {{
        background: rgba(181,230,29,0.15);
        border-color: {sidebar_accent};
        transform: translateX(3px);
    }}
    [data-testid="stSidebar"] [data-baseweb="radio"] input:checked + div + label,
    [data-testid="stSidebar"] .stRadio [aria-checked="true"] label {{
        background: rgba(181,230,29,0.2) !important;
        border-color: {sidebar_accent} !important;
    }}
    [data-testid="stSidebar"] .stToggle label {{
        color: {sidebar_text} !important;
    }}
    [data-testid="stSidebarContent"] {{
        padding-top: 1rem;
    }}

    /* ---- MAIN CONTENT PADDING ---- */
    .main .block-container {{
        padding: 2rem 2.5rem 2rem 2.5rem;
        max-width: 1400px;
    }}

    /* ---- PAGE HEADER ---- */
    .page-header {{
        background: {header_gradient};
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        box-shadow: {shadow};
        position: relative;
        overflow: hidden;
    }}
    .page-header::before {{
        content: '';
        position: absolute;
        top: -40px; right: -40px;
        width: 180px; height: 180px;
        border-radius: 50%;
        background: rgba(181,230,29,0.08);
    }}
    .page-header h1 {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff !important;
        margin: 0 0 0.3rem 0;
        letter-spacing: -0.02em;
    }}
    .page-header p {{
        color: rgba(255,255,255,0.72) !important;
        font-size: 0.97rem;
        margin: 0;
    }}
    .page-header .header-badge {{
        display: inline-block;
        background: rgba(181,230,29,0.22);
        border: 1px solid rgba(181,230,29,0.4);
        color: #b5e61d !important;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        border-radius: 20px;
        padding: 3px 12px;
        margin-bottom: 0.7rem;
    }}

    /* ---- METRIC CARDS ---- */
    [data-testid="stMetric"] {{
        background: {metric_bg};
        border: 1.5px solid {metric_border};
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        box-shadow: {shadow};
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    [data-testid="stMetric"]:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 28px rgba(26,77,46,0.13);
    }}
    [data-testid="stMetricLabel"] {{
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: {text_secondary} !important;
    }}
    [data-testid="stMetricValue"] {{
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: {text_primary} !important;
    }}

    /* ---- CONTAINERS / CARDS ---- */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] {{
        background: {bg_card};
        border: 1.5px solid {border_color};
        border-radius: 16px;
        box-shadow: {shadow};
        overflow: hidden;
    }}

    /* ---- INPUTS ---- */
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stNumberInput"] input,
    [data-testid="stSlider"] {{
        background: {input_bg} !important;
        border-color: {border_color} !important;
        color: {text_primary} !important;
        border-radius: 10px !important;
    }}

    /* ---- BUTTONS ---- */
    .stButton > button {{
        background: {btn_bg} !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 0.55rem 1.2rem !important;
        transition: all 0.2s !important;
        box-shadow: 0 2px 8px rgba(26,77,46,0.18) !important;
    }}
    .stButton > button:hover {{
        background: {btn_hover} !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 16px rgba(26,77,46,0.28) !important;
    }}
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, {btn_bg}, {btn_hover}) !important;
        padding: 0.7rem 1.5rem !important;
        font-size: 1rem !important;
    }}

    /* ---- DIVIDERS ---- */
    hr {{
        border-color: {divider} !important;
        margin: 1.5rem 0;
    }}

    /* ---- HEADERS ---- */
    h1, h2, h3, h4 {{
        font-family: 'Space Grotesk', sans-serif;
        color: {text_primary};
        font-weight: 700;
        letter-spacing: -0.01em;
    }}

    /* ---- SUBHEADER STYLE ---- */
    .section-header {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid {divider};
    }}
    .section-header h3 {{
        margin: 0;
        font-size: 1.1rem;
    }}
    .section-dot {{
        width: 10px; height: 10px;
        border-radius: 50%;
        background: {sidebar_accent if not dark_mode else "#b5e61d"};
        flex-shrink: 0;
    }}

    /* ---- ZONE TAG ---- */
    .zone-tag {{
        display: inline-block;
        background: {tag_bg};
        border: 1px solid {tag_border};
        color: {text_primary};
        border-radius: 20px;
        padding: 3px 14px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-top: 0.3rem;
    }}

    /* ---- DATAFRAME ---- */
    [data-testid="stDataFrame"] {{
        border-radius: 12px;
        overflow: hidden;
        border: 1.5px solid {border_color};
    }}

    /* ---- ALERTS — couleurs forcées pour lisibilité en mode clair ---- */
    [data-testid="stAlert"] {{
        border-radius: 12px !important;
        font-size: 0.92rem !important;
    }}
    /* Success */
    [data-testid="stAlert"][kind="success"],
    div[data-testid="stAlert"] > div[class*="success"] {{
        background-color: {'rgba(51,160,44,0.15)' if not dark_mode else 'rgba(51,160,44,0.2)'} !important;
        border: 1.5px solid #33a02c !important;
        color: {'#1a4a1b' if not dark_mode else '#7dd87d'} !important;
    }}
    [data-testid="stAlert"][kind="success"] p,
    [data-testid="stAlert"][kind="success"] strong,
    [data-testid="stAlert"][kind="success"] * {{
        color: {'#1a4a1b' if not dark_mode else '#7dd87d'} !important;
    }}
    /* Warning */
    [data-testid="stAlert"][kind="warning"],
    div[data-testid="stAlert"] > div[class*="warning"] {{
        background-color: {'rgba(255,127,0,0.12)' if not dark_mode else 'rgba(255,127,0,0.2)'} !important;
        border: 1.5px solid #ff7f00 !important;
        color: {'#7a3c00' if not dark_mode else '#ffb347'} !important;
    }}
    [data-testid="stAlert"][kind="warning"] p,
    [data-testid="stAlert"][kind="warning"] strong,
    [data-testid="stAlert"][kind="warning"] * {{
        color: {'#7a3c00' if not dark_mode else '#ffb347'} !important;
    }}
    /* Error */
    [data-testid="stAlert"][kind="error"],
    div[data-testid="stAlert"] > div[class*="error"] {{
        background-color: {'rgba(227,26,28,0.10)' if not dark_mode else 'rgba(227,26,28,0.2)'} !important;
        border: 1.5px solid #e31a1c !important;
        color: {'#7a0a0a' if not dark_mode else '#f87171'} !important;
    }}
    [data-testid="stAlert"][kind="error"] p,
    [data-testid="stAlert"][kind="error"] strong,
    [data-testid="stAlert"][kind="error"] * {{
        color: {'#7a0a0a' if not dark_mode else '#f87171'} !important;
    }}
    /* Fallback large selector for Streamlit alert internals */
    div[class*="stSuccess"] > div, div[class*="stSuccess"] p {{ color: {'#1a4a1b' if not dark_mode else '#7dd87d'} !important; }}
    div[class*="stWarning"] > div, div[class*="stWarning"] p {{ color: {'#7a3c00' if not dark_mode else '#ffb347'} !important; }}
    div[class*="stError"] > div, div[class*="stError"] p {{ color: {'#7a0a0a' if not dark_mode else '#f87171'} !important; }}

    /* ---- SIDEBAR LOGO CONTAINER ---- */
    .sidebar-logo-wrap {{
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 1.2rem 0.8rem 1rem 0.8rem;
        border-bottom: 1px solid {sidebar_border};
        margin-bottom: 0.5rem;
    }}
    .sidebar-app-name {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: {sidebar_accent} !important;
        margin-top: 0.5rem;
    }}

    /* ---- TIMELINE (Page 4) ---- */
    .timeline-container {{
        position: relative;
        padding-left: 2.5rem;
    }}
    .timeline-container::before {{
        content: '';
        position: absolute;
        left: 12px; top: 0; bottom: 0;
        width: 3px;
        background: linear-gradient(to bottom, {sidebar_border}, transparent);
        border-radius: 2px;
    }}
    .timeline-event {{
        position: relative;
        background: {bg_card};
        border: 1.5px solid {border_color};
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.5rem;
        box-shadow: {shadow};
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    .timeline-event:hover {{
        transform: translateX(4px);
        box-shadow: 0 6px 28px rgba(0,0,0,0.12);
    }}
    .timeline-event::before {{
        content: '';
        position: absolute;
        left: -2.08rem; top: 1.6rem;
        width: 14px; height: 14px;
        border-radius: 50%;
        background: {sidebar_accent if not dark_mode else "#b5e61d"};
        border: 3px solid {bg_app};
        box-shadow: 0 0 0 2px {sidebar_border};
    }}
    .timeline-year {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: {'#b5e61d' if dark_mode else '#1a4d2e'};
        line-height: 1;
    }}
    .timeline-title {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.05rem;
        font-weight: 700;
        color: {text_primary};
        margin: 0.25rem 0 0.1rem 0;
    }}
    .timeline-location {{
        font-size: 0.82rem;
        font-weight: 600;
        color: {text_secondary};
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }}
    .timeline-desc {{
        font-size: 0.91rem;
        color: {text_secondary};
        line-height: 1.6;
        margin-top: 0.6rem;
    }}
    .timeline-stats {{
        display: flex;
        gap: 1.5rem;
        margin-top: 1rem;
        padding-top: 0.8rem;
        border-top: 1px solid {divider};
    }}
    .timeline-stat {{
        text-align: center;
    }}
    .timeline-stat-value {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: {text_primary};
    }}
    .timeline-stat-label {{
        font-size: 0.72rem;
        color: {text_secondary};
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    .severity-badge {{
        display: inline-block;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }}
    .severity-catastrophique {{ background: #e31a1c22; color: #e31a1c; border: 1px solid #e31a1c55; }}
    .severity-majeur {{ background: #ff7f0022; color: #ff7f00; border: 1px solid #ff7f0055; }}
    .severity-fort {{ background: #f5a62322; color: #f5a623; border: 1px solid #f5a62355; }}

    /* ---- SPINNER ---- */
    .stSpinner > div {{
        border-top-color: {'#b5e61d' if dark_mode else '#1a4d2e'} !important;
    }}

    /* Hide default Streamlit elements */
    #MainMenu, footer, header {{ visibility: hidden; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# ==========================================
# 3. CHARGEMENT DES DONNÉES
# ==========================================
@st.cache_data
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
    df['RATIO_RISQUE'] = (df['PRIME_NETTE'] / (df['CAPITAL_ASSURE'] + 1)) * 1000
    if 'Source_Annee' in df.columns:
        df['Source_Annee'] = pd.to_numeric(df['Source_Annee'], errors='coerce')
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
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

df = load_data()
geo_wilayas = load_geojson(1)
geo_communes = load_geojson(2)

# ==========================================
# 4. SESSION STATE
# ==========================================
if 'selected_wilaya' not in st.session_state:
    st.session_state.selected_wilaya = "Toutes les Wilayas"

# ==========================================
# 5. SIDEBAR
# ==========================================
inject_css(st.session_state.dark_mode)

with st.sidebar:
    # Logo
    st.markdown('<div class="sidebar-logo-wrap">', unsafe_allow_html=True)
    try:
        st.image("logo.png", width=140)
    except Exception:
        st.markdown("🛡️", unsafe_allow_html=True)
    st.markdown('<div class="sidebar-app-name">Système Expert CATNAT</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Dark mode toggle
    dark_toggle = st.toggle("🌙 Mode Sombre", value=st.session_state.dark_mode)
    if dark_toggle != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_toggle
        st.rerun()

    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "Cartographie & Dashboard",
            "Souscription de Contrat",
            "Simulation Monte Carlo",
            "Historique Sismique"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown(
        f"""<div style="font-size:0.74rem; color: rgba(255,255,255,0.45); text-align:center; padding: 0 0.5rem;">
        Évaluation de l'exposition au<br>risque sismique · Algérie<br><br>
        v2.0 · GAM Assurances
        </div>""",
        unsafe_allow_html=True
    )

# ==========================================
# 6. PAGE 1 : CARTOGRAPHIE & DASHBOARD
# ==========================================
if page == "Cartographie & Dashboard":

    def get_rpa_color(name):
        w = str(name).upper()
        if w in ["ALGER", "BOUMERDES", "BLIDA", "TIPAZA", "CHLEF", "AIN DEFLA"]:
            return RPA_COLORS["ROUGE"]
        elif w in ["ORAN", "CONSTANTINE", "SETIF", "BEJAIA", "TIZI OUZOU", "JIJEL", "SKIKDA", "ANNABA", "MEDEA"]:
            return RPA_COLORS["ORANGE"]
        return RPA_COLORS["VERT"]

    def get_bounds(features):
        lats, lons = [], []
        def extract_coords(c):
            if isinstance(c[0], (int, float)):
                lons.append(c[0]); lats.append(c[1])
            else:
                for item in c: extract_coords(item)
        for f in features:
            geom = f.get('geometry', {})
            if geom: extract_coords(geom.get('coordinates', []))
        if lats and lons: return [[min(lats), min(lons)], [max(lats), max(lons)]]
        return None

    # Page Header
    is_national = (st.session_state.selected_wilaya == "Toutes les Wilayas")
    scope_label = "Algérie Entière" if is_national else st.session_state.selected_wilaya
    st.markdown(f"""
    <div class="page-header">
        <div class="header-badge">Cartographie & Dashboard</div>
        <h1>📍 Risques Sismiques</h1>
        <p>Visualisation géospatiale du portefeuille CATNAT · Vue : <strong>{scope_label}</strong></p>
    </div>
    """, unsafe_allow_html=True)

    # --- Métriques en haut ---
    is_national = (st.session_state.selected_wilaya == "Toutes les Wilayas")
    dashboard_df = df if is_national else df[df['WILAYA_UP'] == st.session_state.selected_wilaya]

    if not dashboard_df.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Capital Exposé (DZD)", f"{dashboard_df['CAPITAL_ASSURE'].sum()/1e9:.2f} Mrd")
        c2.metric("Primes Nettes (DZD)", f"{dashboard_df['PRIME_NETTE'].sum()/1e6:.1f} M")
        c3.metric("Ratio de Risque Moyen", f"{dashboard_df['RATIO_RISQUE'].mean():.3f}")
        c4.metric("Nombre de Polices", f"{len(dashboard_df):,}".replace(',', ' '))

    st.markdown("")

    # --- Sélection wilaya + carte ---
    col_search, col_btn = st.columns([3, 1])
    liste_wilayas = ["Toutes les Wilayas"] + sorted(df['WILAYA_UP'].dropna().unique().tolist())
    index_actuel = liste_wilayas.index(st.session_state.selected_wilaya) if st.session_state.selected_wilaya in liste_wilayas else 0

    with col_search:
        choix_recherche = st.selectbox("Rechercher ou sélectionner une Wilaya :", options=liste_wilayas, index=index_actuel)
    with col_btn:
        st.write(""); st.write("")
        if st.button("Réinitialiser", use_container_width=True):
            st.session_state.selected_wilaya = "Toutes les Wilayas"
            st.rerun()

    if choix_recherche != st.session_state.selected_wilaya:
        st.session_state.selected_wilaya = choix_recherche
        st.rerun()

    bounds_to_fit = None
    display_data = None
    tooltip_fields = []
    tooltip_aliases = []

    dark = st.session_state.dark_mode
    map_tiles = "CartoDB dark_matter" if dark else "cartodbpositron"

    if st.session_state.selected_wilaya != "Toutes les Wilayas" and geo_communes:
        features_wilaya = [f for f in geo_communes['features']
                           if clean_name(f['properties'].get('adm1_name', '')) == st.session_state.selected_wilaya]
        if features_wilaya:
            display_data = {"type": "FeatureCollection", "features": features_wilaya}
            tooltip_fields, tooltip_aliases = ['adm1_name', 'adm2_name'], ['Wilaya:', 'Commune:']
            bounds_to_fit = get_bounds(features_wilaya)
            m = folium.Map(tiles=map_tiles)
        else:
            st.warning("Données géographiques des communes indisponibles. Vue nationale affichée.")
            if geo_wilayas:
                display_data = geo_wilayas
                tooltip_fields, tooltip_aliases = ['adm1_name'], ['Wilaya:']
                m = folium.Map(location=[28.0, 2.0], zoom_start=5, tiles=map_tiles)
    elif geo_wilayas:
        display_data = geo_wilayas
        tooltip_fields, tooltip_aliases = ['adm1_name'], ['Wilaya:']
        m = folium.Map(location=[28.0, 2.0], zoom_start=5, tiles=map_tiles)
    else:
        st.error("Fichiers GeoJSON introuvables.")

    if display_data:
        def style_fn(feature):
            w_name = feature['properties'].get('adm1_name', '').upper()
            return {'fillColor': get_rpa_color(w_name), 'color': 'white', 'weight': 1, 'fillOpacity': 0.7}

        folium.GeoJson(
            display_data,
            style_function=style_fn,
            tooltip=folium.GeoJsonTooltip(fields=tooltip_fields, aliases=tooltip_aliases)
        ).add_to(m)

        # Légende
        legend_html = """
        <div style="position:fixed;bottom:30px;right:30px;z-index:9999;background:rgba(255,255,255,0.95);
                    border-radius:12px;padding:12px 16px;box-shadow:0 4px 20px rgba(0,0,0,0.2);font-size:13px;font-family:Inter,sans-serif;">
          <b style="display:block;margin-bottom:8px;font-size:12px;letter-spacing:0.05em;text-transform:uppercase;color:#555;">Zones RPA</b>
          <div><span style="display:inline-block;width:14px;height:14px;border-radius:3px;background:#e31a1c;margin-right:8px;vertical-align:middle;"></span>Zone III – Élevée</div>
          <div style="margin-top:4px;"><span style="display:inline-block;width:14px;height:14px;border-radius:3px;background:#ff7f00;margin-right:8px;vertical-align:middle;"></span>Zone II – Modérée</div>
          <div style="margin-top:4px;"><span style="display:inline-block;width:14px;height:14px;border-radius:3px;background:#33a02c;margin-right:8px;vertical-align:middle;"></span>Zone 0/I – Faible</div>
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend_html))

        if bounds_to_fit:
            m.fit_bounds(bounds_to_fit)

        map_res = st_folium(m, width="100%", height=480, key="map_algeria")

        if map_res.get("last_active_drawing") and st.session_state.selected_wilaya == "Toutes les Wilayas":
            clicked_w = map_res["last_active_drawing"]["properties"].get("adm1_name", "").upper()
            if clicked_w:
                st.session_state.selected_wilaya = clicked_w
                st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # --- DASHBOARD ---
    is_national = (st.session_state.selected_wilaya == "Toutes les Wilayas")
    dashboard_df = df if is_national else df[df['WILAYA_UP'] == st.session_state.selected_wilaya]

    plotly_layout = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#1a2e1c" if not dark else "#e8eaf0"),
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)")
    )

    if not dashboard_df.empty:
        # --- Pie Charts côte à côte ---
        col_pie1, col_pie2 = st.columns(2)

        with col_pie1:
            st.markdown('<div class="section-header"><div class="section-dot"></div><h3>Exposition par Zone RPA</h3></div>', unsafe_allow_html=True)
            zone_data = dashboard_df.groupby('ZONE_RPA_CAT')['CAPITAL_ASSURE'].sum().reset_index()
            color_map = {
                "ZONE III (Rouge)": "#e31a1c",
                "ZONE II (Orange)": "#ff7f00",
                "ZONE 0/I (Vert)": "#33a02c"
            }
            fig_pie_zone = px.pie(
                zone_data, names='ZONE_RPA_CAT', values='CAPITAL_ASSURE',
                hole=0.5,
                color='ZONE_RPA_CAT',
                color_discrete_map=color_map
            )
            fig_pie_zone.update_traces(textposition='outside', textinfo='percent+label')
            fig_pie_zone.update_layout(**plotly_layout, height=320, showlegend=False)
            st.plotly_chart(fig_pie_zone, use_container_width=True)

        with col_pie2:
            st.markdown('<div class="section-header"><div class="section-dot"></div><h3>Exposition par Type de Risque</h3></div>', unsafe_allow_html=True)
            type_data = dashboard_df.groupby('TYPE_CLEAN')['CAPITAL_ASSURE'].sum().reset_index()
            fig_pie_type = px.pie(
                type_data, names='TYPE_CLEAN', values='CAPITAL_ASSURE',
                hole=0.5,
                color_discrete_sequence=["#1a4d2e", "#b5e61d", "#33a02c", "#2d9e5f", "#84c97b"]
            )
            fig_pie_type.update_traces(textposition='outside', textinfo='percent+label')
            fig_pie_type.update_layout(**plotly_layout, height=320, showlegend=False)
            st.plotly_chart(fig_pie_type, use_container_width=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # --- Top 3 / Flop 3 ---
        group_col = 'WILAYA_UP' if is_national else 'COMMUNE_UP'
        label_geo = "Wilaya" if is_national else "Commune"
        grouped_geo = dashboard_df.groupby(group_col)['CAPITAL_ASSURE'].sum().reset_index()
        grouped_geo_positive = grouped_geo[grouped_geo['CAPITAL_ASSURE'] > 0]

        col_hot, col_cold = st.columns(2)

        with col_hot:
            st.markdown(f'<div class="section-header"><div class="section-dot" style="background:#e31a1c;"></div><h3>🔥 Top 3 Sur-concentration ({label_geo})</h3></div>', unsafe_allow_html=True)
            top3 = grouped_geo.sort_values(ascending=False, by='CAPITAL_ASSURE').head(3)
            fig_hot = px.bar(top3, x=group_col, y='CAPITAL_ASSURE', text_auto='.2s',
                             labels={group_col: label_geo, 'CAPITAL_ASSURE': 'Capital (DZD)'})
            fig_hot.update_traces(marker_color='#e31a1c', marker_line_color='white', marker_line_width=1.5)
            fig_hot.update_layout(**plotly_layout, height=280)
            st.plotly_chart(fig_hot, use_container_width=True)

        with col_cold:
            st.markdown(f'<div class="section-header"><div class="section-dot" style="background:#33a02c;"></div><h3>💡 Top 3 Sous-concentration ({label_geo})</h3></div>', unsafe_allow_html=True)
            bottom3 = grouped_geo_positive.sort_values(ascending=True, by='CAPITAL_ASSURE').head(3)
            fig_cold = px.bar(bottom3, x=group_col, y='CAPITAL_ASSURE', text_auto='.2s',
                              labels={group_col: label_geo, 'CAPITAL_ASSURE': 'Capital (DZD)'})
            fig_cold.update_traces(marker_color='#33a02c', marker_line_color='white', marker_line_width=1.5)
            fig_cold.update_layout(**plotly_layout, height=280)
            st.plotly_chart(fig_cold, use_container_width=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # --- Tableau interactif ---
        st.markdown('<div class="section-header"><div class="section-dot"></div><h3>Tableau Détaillé par Zone RPA</h3></div>', unsafe_allow_html=True)
        table_df = dashboard_df.groupby(['WILAYA_UP', 'ZONE_RPA_CAT']).agg(
            Capital_Total=('CAPITAL_ASSURE', 'sum'),
            Primes_Nettes=('PRIME_NETTE', 'sum'),
            Nb_Polices=('CAPITAL_ASSURE', 'count')
        ).reset_index().sort_values('Capital_Total', ascending=False)
        table_df.columns = ['Wilaya', 'Zone RPA', 'Capital Total (DZD)', 'Primes Nettes (DZD)', 'Nb Polices']
        st.dataframe(table_df, use_container_width=True, height=320)


# ==========================================
# 7. PAGE 2 : SOUSCRIPTION
# ==========================================
elif page == "Souscription de Contrat":

    def determiner_zone_depuis_data(wilaya_nom):
        try:
            return df[df['WILAYA_UP'] == wilaya_nom]['ZONE_RPA'].mode()[0]
        except:
            return "IIa"

    def evaluer_risque_avance(zone_rpa, type_bien, capital):
        taux_base = {"0": 0.0001, "I": 0.0003, "IIa": 0.0007, "IIb": 0.0012, "III": 0.0020, "IV": 0.0030}
        coeffs_type = {
            "Immobilier (Habitation)": 1.0,
            "Commercial (Bureaux/Magasins)": 1.4,
            "Industriel (Usines/Dépôts)": 2.2
        }
        base_rate = taux_base.get(zone_rpa, 0.0010)
        mult_type = coeffs_type.get(type_bien, 1.0)
        score_zone = {"0": 10, "I": 25, "IIa": 45, "IIb": 65, "III": 85, "IV": 100}.get(zone_rpa, 50)
        score_bien = {"Immobilier (Habitation)": 20, "Commercial (Bureaux/Magasins)": 50, "Industriel (Usines/Dépôts)": 90}.get(type_bien, 50)
        score_final = (score_zone * 0.6) + (score_bien * 0.4)
        if capital > 1_000_000_000: score_final += 10
        return min(score_final, 100.0), capital * base_rate * mult_type

    dark = st.session_state.dark_mode
    plotly_layout = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#1a2e1c" if not dark else "#e8eaf0"),
        margin=dict(l=10, r=10, t=30, b=10)
    )

    st.markdown("""
    <div class="page-header">
        <div class="header-badge">Module Tarifaire</div>
        <h1>📋 Souscription de Contrat</h1>
        <p>Détection automatique de l'aléa sismique · Ajustement tarifaire selon zone RPA et activité</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("#### Informations du Prospect")
        col_w, col_c = st.columns(2)

        wilayas_list = sorted(df['WILAYA_UP'].dropna().unique())
        selected_wilaya_sous = col_w.selectbox("Wilaya du projet", wilayas_list, key="sous_wilaya")
        zone_auto = determiner_zone_depuis_data(selected_wilaya_sous)

        communes_list = sorted(df[df['WILAYA_UP'] == selected_wilaya_sous]['COMMUNE_UP'].dropna().unique())
        selected_commune = col_c.selectbox("Commune", communes_list, key="sous_commune")

        col_type, col_cap = st.columns(2)
        type_bien = col_type.selectbox(
            "Nature du Bien",
            ["Immobilier (Habitation)", "Commercial (Bureaux/Magasins)", "Industriel (Usines/Dépôts)"]
        )
        capital_assure = col_cap.number_input(
            "Capital à assurer (DZD)",
            min_value=0.0, value=50_000_000.0, step=10_000_000.0,
            format="%.0f"
        )

        # Zone détectée
        zone_colors = {"III": "#e31a1c", "IIa": "#ff7f00", "IIb": "#ff7f00", "I": "#33a02c", "0": "#33a02c"}
        zone_color = zone_colors.get(zone_auto, "#888")
        st.markdown(
            f'<div style="margin-top:0.5rem;">Zone RPA détectée pour <strong>{selected_wilaya_sous}</strong> : '
            f'<span class="zone-tag" style="border-color:{zone_color};color:{zone_color};background:{zone_color}22;">Zone {zone_auto}</span></div>',
            unsafe_allow_html=True
        )

    st.markdown("")
    if st.button("Générer le Diagnostic de Souscription", type="primary", use_container_width=True):
        score, prime = evaluer_risque_avance(zone_auto, type_bien, capital_assure)
        st.markdown("<hr>", unsafe_allow_html=True)

        col_gauge, col_result = st.columns([1, 1.3])

        with col_gauge:
            st.markdown("##### Score de Risque Global")
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                number={'suffix': "%", 'font': {'size': 44, 'family': 'Space Grotesk', 'color': '#1a2e1c' if not dark else '#e8eaf0'}},
                gauge={
                    'axis': {
                        'range': [0, 100],
                        'tickcolor': '#888',
                        'tickwidth': 1,
                        'tickvals': [0, 25, 40, 50, 75, 100],
                        'ticktext': ['0', '25', '40', '50', '75', '100'],
                    },
                    'bar': {'color': "#1a4d2e" if not dark else "#b5e61d", 'thickness': 0.28},
                    'bgcolor': "rgba(0,0,0,0)",
                    'borderwidth': 0,
                    'steps': [
                        {'range': [0, 40], 'color': "rgba(51,160,44,0.18)"},
                        {'range': [40, 75], 'color': "rgba(255,127,0,0.18)"},
                        {'range': [75, 100], 'color': "rgba(227,26,28,0.18)"}
                    ],
                    'threshold': {
                        'line': {'color': "#e31a1c", 'width': 3},
                        'thickness': 0.75,
                        'value': 75
                    }
                }
            ))
            fig_gauge.update_layout(**plotly_layout, height=290)
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col_result:
            st.markdown("##### Analyse Technique")
            st.metric("Prime Nette Annuelle", f"{prime:,.0f} DZD".replace(',', ' '))
            st.metric("Taux Technique", f"{(prime/capital_assure*100):.4f} %" if capital_assure > 0 else "N/A")
            st.markdown("")

            if score < 40:
                st.success(
                    "**RISQUE ACCEPTABLE**\n\n"
                    f"Score de risque : {score:.1f} / 100\n\n"
                    "Profil standard. Aucune mesure particulière requise. Souscription recommandée."
                )
            elif score < 75:
                st.warning(
                    "**SURVEILLANCE REQUISE**\n\n"
                    f"Score de risque : {score:.1f} / 100\n\n"
                    "Exposition modérée. Application d'une franchise recommandée. Conditions particulières à étudier."
                )
            else:
                st.error(
                    "**RISQUE ÉLEVÉ — SOUSCRIPTION SOUS CONDITIONS**\n\n"
                    f"Score de risque : {score:.1f} / 100\n\n"
                    "Activité vulnérable en zone sismique forte. Étude de vulnérabilité structurelle obligatoire avant souscription."
                )

            st.markdown("")
            with st.expander("Détails du calcul tarifaire"):
                st.markdown(f"""
                | Paramètre | Valeur |
                |---|---|
                | Wilaya | {selected_wilaya_sous} |
                | Commune | {selected_commune} |
                | Zone RPA | Zone {zone_auto} |
                | Type de bien | {type_bien} |
                | Capital assuré | {capital_assure:,.0f} DZD |
                | Prime calculée | {prime:,.2f} DZD |
                | Score global | {score:.1f} / 100 |
                """)


# ==========================================
# 8. PAGE 3 : MONTE CARLO
# ==========================================
elif page == "Simulation Monte Carlo":

    dark = st.session_state.dark_mode
    plotly_layout = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#1a2e1c" if not dark else "#e8eaf0"),
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)")
    )

    st.markdown("""
    <div class="page-header">
        <div class="header-badge">Actuariat Stochastique</div>
        <h1>🎲 Simulation Monte Carlo</h1>
        <p>Évaluation probabiliste des pertes maximales selon des scénarios sismiques simulés · 100 000 itérations</p>
    </div>
    """, unsafe_allow_html=True)

    if 'Source_Annee' not in df.columns:
        st.error("La colonne 'Source_Annee' est manquante dans les données.")
    else:
        df_2024 = df[df['Source_Annee'] == 2024].copy()

        if df_2024.empty:
            st.warning("Aucune donnée trouvée pour l'année 2024 dans le dataset.")
        else:
            def get_severity(row):
                t = str(row['TYPE_CLEAN']).lower()
                if 'industrielle' in t: return 0.7
                if 'commercial' in t: return 0.5
                return 0.3

            df_2024['SEVERITY_FACTOR'] = df_2024.apply(get_severity, axis=1)

            # Paramétrage
            col_params, col_preview = st.columns([1, 1.2])

            with col_params:
                with st.container(border=True):
                    st.markdown("#### Paramétrage du Scénario")
                    wilayas_disponibles = sorted(df_2024['WILAYA_UP'].unique())
                    selected_mc_wilaya = st.selectbox("Wilaya cible de la simulation", wilayas_disponibles)

                    lambda_freq = st.slider(
                        "Fréquence annuelle d'occurrence CATNAT",
                        min_value=0.0,
                        max_value=0.20,
                        value=0.05,
                        step=0.001,
                        help="Probabilité annuelle d'un événement CATNAT. De 0% à 20%, pas de 0,1%."
                    )
                    st.caption(f"Fréquence sélectionnée : **{lambda_freq*100:.1f}%** par an")

            df_w = df_2024[df_2024['WILAYA_UP'] == selected_mc_wilaya].copy()
            df_w['EXPOSITION_UNITAIRE'] = df_w['CAPITAL_ASSURE'] * df_w['SEVERITY_FACTOR'] * 0.30
            expo_totale_wilaya = df_w['EXPOSITION_UNITAIRE'].sum()
            total_primes = df_w['PRIME_NETTE'].sum()

            with col_preview:
                with st.container(border=True):
                    st.markdown(f"#### Portefeuille Ciblé 2024 — {selected_mc_wilaya}")
                    p1, p2, p3 = st.columns(3)
                    p1.metric("Polices Actives", f"{len(df_w):,}".replace(',', ' '))
                    p2.metric("PML Modélisé (M DZD)", f"{expo_totale_wilaya/1e6:.1f}")
                    p3.metric("Primes Nettes (M DZD)", f"{total_primes/1e6:.1f}")

            st.markdown("<hr>", unsafe_allow_html=True)

            if expo_totale_wilaya > 0:
                with st.spinner("Génération de 100 000 scénarios sismiques en cours..."):
                    n_sim = 100000
                    freq = lambda_freq
                    sigma = 0.8
                    mean_mdr = 0.05

                    losses = np.zeros(n_sim)
                    n_events_per_year = np.random.poisson(freq, n_sim)

                    for i in range(n_sim):
                        n_events = n_events_per_year[i]
                        if n_events > 0:
                            total_loss_year = 0
                            for _ in range(n_events):
                                mu_adj = np.log(mean_mdr) - 0.5 * (sigma**2)
                                mdr_event = min(np.random.lognormal(mu_adj, sigma), 0.8)
                                total_loss_year += expo_totale_wilaya * mdr_event
                            losses[i] = total_loss_year

                col_kpi, col_chart = st.columns([1, 1.5])

                with col_kpi:
                    with st.container(border=True):
                        st.markdown("#### Indicateurs de Solvabilité")

                        pml_995 = np.percentile(losses, 99.5)
                        pml_99 = np.percentile(losses, 99.0)
                        mean_loss = losses.mean()
                        lr = (mean_loss / total_primes * 100) if total_primes > 0 else 0

                        st.metric("Charge Moyenne Annuelle", f"{mean_loss/1e6:.2f} M DZD")
                        st.metric("VaR 99% — 1-en-100 ans", f"{pml_99/1e6:.2f} M DZD")
                        st.markdown("")
                        st.error(f"**VaR 99,5% — Solvabilité II**\n\n{pml_995/1e6:.2f} M DZD\n\n*Perte maximale 1-en-200 ans*")
                        st.markdown("<hr>", unsafe_allow_html=True)

                        if lr < 50:
                            st.success(f"**S/P Technique : {lr:.2f}%**\n\nPortefeuille rentable")
                        elif lr < 80:
                            st.warning(f"**S/P Technique : {lr:.2f}%**\n\nSous tension — surveillance requise")
                        else:
                            st.error(f"**S/P Technique : {lr:.2f}%**\n\nDéficitaire — mesures correctives requises")

                with col_chart:
                    st.markdown("#### Distribution des Pertes Simulées")
                    pertes_positives = losses[losses > 0]
                    if len(pertes_positives) > 0:
                        bar_color = "#1a4d2e" if not dark else "#b5e61d"
                        font_color = "#1a2e1c" if not dark else "#e8eaf0"
                        grid_color = "rgba(180,200,180,0.18)" if not dark else "rgba(80,100,80,0.25)"

                        # Calcul manuel des bins pour un histogramme soigné
                        counts, bin_edges = np.histogram(pertes_positives / 1e6, bins=50)
                        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

                        fig_hist = go.Figure()

                        # Barres de l'histogramme
                        fig_hist.add_trace(go.Bar(
                            x=bin_centers,
                            y=counts,
                            width=(bin_edges[1] - bin_edges[0]) * 0.88,
                            marker=dict(
                                color=bar_color,
                                opacity=0.85,
                                line=dict(color="rgba(255,255,255,0.15)", width=0.5)
                            ),
                            name="Fréquence des pertes",
                            hovertemplate="<b>Perte :</b> %{x:.1f} M DZD<br><b>Occurrences :</b> %{y:,}<extra></extra>"
                        ))

                        # Ligne VaR 99,5%
                        fig_hist.add_vline(
                            x=pml_995 / 1e6,
                            line_dash="dash",
                            line_color="#e31a1c",
                            line_width=2,
                            annotation=dict(
                                text=f"VaR 99,5%<br><b>{pml_995/1e6:.1f} M DZD</b>",
                                font=dict(size=11, color="#e31a1c", family="Inter"),
                                bgcolor="rgba(227,26,28,0.08)",
                                bordercolor="#e31a1c",
                                borderwidth=1,
                                borderpad=4,
                                showarrow=False,
                                xanchor="left",
                                yanchor="top"
                            )
                        )

                        # Ligne VaR 99%
                        fig_hist.add_vline(
                            x=pml_99 / 1e6,
                            line_dash="dot",
                            line_color="#ff7f00",
                            line_width=1.5,
                            annotation=dict(
                                text=f"VaR 99%",
                                font=dict(size=10, color="#ff7f00", family="Inter"),
                                showarrow=False,
                                xanchor="right",
                                yanchor="top"
                            )
                        )

                        fig_hist.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            font=dict(family="Inter", color=font_color, size=12),
                            margin=dict(l=20, r=20, t=20, b=60),
                            height=400,
                            xaxis=dict(
                                title=dict(text="Montant des pertes annuelles (M DZD)", font=dict(size=12)),
                                showgrid=True,
                                gridcolor=grid_color,
                                gridwidth=1,
                                zeroline=False,
                                tickfont=dict(size=11),
                            ),
                            yaxis=dict(
                                title=dict(text="Nombre de scénarios", font=dict(size=12)),
                                showgrid=True,
                                gridcolor=grid_color,
                                gridwidth=1,
                                zeroline=False,
                                tickfont=dict(size=11),
                            ),
                            bargap=0.05,
                            showlegend=False,
                        )
                        st.plotly_chart(fig_hist, use_container_width=True)
                    else:
                        st.info("Fréquence trop faible pour générer des événements significatifs sur 100 000 itérations.")
            else:
                st.warning("L'exposition est nulle pour cette Wilaya. Impossible de lancer la simulation.")


# ==========================================
# 9. PAGE 4 : HISTORIQUE SISMIQUE
# ==========================================
elif page == "Historique Sismique":

    st.markdown("""
    <div class="page-header">
        <div class="header-badge">Mémoire Sismique</div>
        <h1>🗓️ Historique des Séismes Majeurs</h1>
        <p>Les événements qui ont façonné la réglementation parasismique algérienne (RPA)</p>
    </div>
    """, unsafe_allow_html=True)

    # Intro
    col_intro, col_stats = st.columns([1.6, 1])
    with col_intro:
        st.markdown("""
        L'Algérie se situe sur la convergence des plaques tectoniques eurasienne et africaine, faisant du nord 
        du pays l'une des zones sismiques les plus actives du pourtour méditerranéen. Chaque séisme majeur 
        a conduit à une révision et un renforcement du **Règlement Parasismique Algérien (RPA)**, 
        première version publiée en 1981, puis révisée en 1988, 1999 et 2003.
        """)
    with col_stats:
        with st.container(border=True):
            s1, s2 = st.columns(2)
            s1.metric("Séismes > M5.0 (20e siècle)", "~120")
            s2.metric("Révisions RPA", "4")
            s3, s4 = st.columns(2)
            s3.metric("Zone III (Très élevée)", "6 Wilayas")
            s4.metric("Wilaya à risque nul", "0")

    st.markdown("<hr>", unsafe_allow_html=True)

    # Timeline data
    seismes = [
        {
            "annee": "2003",
            "titre": "Séisme de Boumerdès",
            "lieu": "Boumerdès / Alger, Algérie",
            "magnitude": "6.8 Mw",
            "victimes": "2 278",
            "blesses": "10 261",
            "degats": "≈ 5 Mrd USD",
            "severity": "catastrophique",
            "zone": "III",
            "description": (
                "Le séisme du 21 mai 2003, à 18h44 heure locale, est le plus dévastateur qu'ait connu l'Algérie depuis El Asnam en 1980. "
                "L'épicentre se situe en mer, à 7 km au nord de Zemmouri. Les dégâts sont massifs dans les wilayas d'Alger, Boumerdès, Tizi Ouzou et Boumerdès. "
                "Plus de 200 000 personnes se retrouvent sans abri. Cet événement entraîne une révision majeure du RPA (version 2003), "
                "reclassant plusieurs zones et renforçant les normes de construction parasismique."
            ),
            "impact_rpa": "Publication du RPA 2003 · Reclassification de zones · Obligation de diagnostic pour le bâti existant"
        },
        {
            "annee": "1996",
            "titre": "Séisme d'Aïn Témouchent",
            "lieu": "Aïn Témouchent, Algérie Occidentale",
            "magnitude": "5.8 Mw",
            "victimes": "16",
            "blesses": "500+",
            "degats": "Modérés",
            "severity": "fort",
            "zone": "II",
            "description": (
                "Le 22 décembre 1999, un séisme de magnitude 5.8 frappe la région d'Aïn Témouchent, dans l'ouest algérien. "
                "Bien que les pertes humaines soient limitées, les dégâts matériels révèlent la vulnérabilité du bâti dans des zones "
                "considérées à risque modéré. Cet événement renforce la prise de conscience sur la nécessité d'étendre la cartographie "
                "sismique à l'ensemble du territoire national et d'appliquer strictement les normes RPA 99."
            ),
            "impact_rpa": "Confirmation du RPA 99 · Extension de la surveillance sismique à l'ouest algérien"
        },
        {
            "annee": "1994",
            "titre": "Séisme de Mascara",
            "lieu": "Mascara, Algérie Occidentale",
            "magnitude": "5.6 Mw",
            "victimes": "171",
            "blesses": "1 000+",
            "degats": "Importants",
            "severity": "majeur",
            "zone": "II",
            "description": (
                "Le 18 août 1994, un séisme secoue la région de Mascara. La destruction de nombreux bâtiments en pisé et en maçonnerie "
                "non renforcée met en lumière la non-conformité d'une grande partie du parc immobilier aux normes parasismiques. "
                "Cet événement accélère les travaux de révision du RPA 88 et conduit à l'élaboration du RPA 99, "
                "avec une attention particulière portée aux constructions en zone sismique modérée."
            ),
            "impact_rpa": "Accélération de la révision vers RPA 99 · Focus sur la maçonnerie non renforcée"
        },
        {
            "annee": "1980",
            "titre": "Séisme d'El Asnam (Chlef)",
            "lieu": "El Asnam (Chlef), Algérie Centrale",
            "magnitude": "7.3 Mw",
            "victimes": "2 633",
            "blesses": "8 369",
            "degats": "≈ 3,5 Mrd USD",
            "severity": "catastrophique",
            "zone": "III",
            "description": (
                "Le 10 octobre 1980, à 13h25 heure locale, un séisme de magnitude 7.3 dévaste la ville d'El Asnam (aujourd'hui Chlef). "
                "Il s'agit de l'un des séismes les plus puissants jamais enregistrés en Algérie et dans tout le Maghreb. "
                "La ville est rasée à 80%, avec l'effondrement de milliers d'immeubles, dont beaucoup de construction récente. "
                "Ce drame fondateur entraîne la création du premier Règlement Parasismique Algérien (RPA 81), "
                "pierre angulaire de toute la réglementation sismique nationale ultérieure. La ville d'El Asnam avait déjà été "
                "détruite par un séisme de magnitude 6.7 en 1954."
            ),
            "impact_rpa": "Création du premier RPA 81 · Naissance de la réglementation parasismique algérienne · Reclassification nationale"
        },
        {
            "annee": "1954",
            "titre": "Séisme d'Orléansville (El Asnam)",
            "lieu": "Orléansville (El Asnam / Chlef)",
            "magnitude": "6.7 Mw",
            "victimes": "1 243",
            "blesses": "5 000+",
            "degats": "Destruction totale du centre-ville",
            "severity": "catastrophique",
            "zone": "III",
            "description": (
                "Le 9 septembre 1954, un puissant séisme frappe Orléansville (aujourd'hui Chlef), détruisant massivement la ville "
                "et faisant plus de 1 200 morts. La zone est reconstruite, mais sans réglementation parasismique adaptée — "
                "ce qui expliquera la catastrophe encore plus meurtrière de 1980. Cet événement est le premier grand séisme "
                "algérien documenté à avoir suscité une réflexion sur la vulnérabilité du bâti en zone sismique."
            ),
            "impact_rpa": "Première prise de conscience · Précurseur de la réflexion parasismique nationale"
        },
    ]

    severity_labels = {
        "catastrophique": ("CATASTROPHIQUE", "severity-catastrophique"),
        "majeur": ("MAJEUR", "severity-majeur"),
        "fort": ("FORT", "severity-fort")
    }

    # Render timeline
    st.markdown('<div class="timeline-container">', unsafe_allow_html=True)

    for s in seismes:
        label, badge_class = severity_labels.get(s["severity"], ("FORT", "severity-fort"))
        st.markdown(f"""
        <div class="timeline-event">
            <div style="display:flex; align-items:flex-start; justify-content:space-between; flex-wrap:wrap; gap:0.5rem;">
                <div>
                    <div class="timeline-year">{s["annee"]}</div>
                    <div class="timeline-title">{s["titre"]}</div>
                    <div class="timeline-location">📍 {s["lieu"]}</div>
                </div>
                <div style="display:flex; flex-direction:column; gap:0.4rem; align-items:flex-end;">
                    <span class="severity-badge {badge_class}">{label}</span>
                    <span class="zone-tag">Zone RPA {s["zone"]}</span>
                </div>
            </div>
            <div class="timeline-desc">{s["description"]}</div>
            <div class="timeline-stats">
                <div class="timeline-stat">
                    <div class="timeline-stat-value">{s["magnitude"]}</div>
                    <div class="timeline-stat-label">Magnitude</div>
                </div>
                <div class="timeline-stat">
                    <div class="timeline-stat-value">{s["victimes"]}</div>
                    <div class="timeline-stat-label">Victimes</div>
                </div>
                <div class="timeline-stat">
                    <div class="timeline-stat-value">{s["blesses"]}</div>
                    <div class="timeline-stat-label">Blessés</div>
                </div>
                <div class="timeline-stat">
                    <div class="timeline-stat-value" style="font-size:0.9rem;">{s["degats"]}</div>
                    <div class="timeline-stat-label">Dégâts</div>
                </div>
            </div>
            <div style="margin-top:0.8rem; padding: 0.6rem 1rem; border-radius:8px; background:rgba(26,77,46,0.1); border-left:3px solid #1a4d2e; font-size:0.84rem;">
                <strong>Impact RPA :</strong> {s["impact_rpa"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Note de bas de page
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center; font-size:0.82rem; opacity:0.6; padding: 1rem;">
        Sources : CRAAG (Centre de Recherche en Astronomie, Astrophysique et Géophysique) · 
        CGS (Centre National de Recherche Appliquée en Génie Parasismique) · 
        USGS Earthquake Hazards Program · DTU (Documents Techniques Unifiés) Algérie
    </div>
    """, unsafe_allow_html=True)