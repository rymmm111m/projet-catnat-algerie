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
# 2. CHARGEMENT CENTRALISÉ DES DONNÉES
# ==========================================
@st.cache_data
# Fonction magique pour nettoyer les accents et les tirets
def clean_name(text):
    if not isinstance(text, str) or text == "nan": return ""
    # Enlève les accents
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    # Remplace les tirets par des espaces et met tout en majuscules
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
    
    # On applique notre nettoyeur intelligent ici !
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

if 'selected_wilaya' not in st.session_state:
    st.session_state.selected_wilaya = "Toutes les Wilayas"

# ==========================================
# 3. MENU DE NAVIGATION & LOGO
# ==========================================
# Ajout du Logo tout en haut de la barre latérale
try:
    # Après (taille contrôlée)
   st.sidebar.image("logo.png", width=150)
except Exception:
    st.sidebar.warning("Logo introuvable. Placez 'logo.png' dans le dossier.")

st.sidebar.title("Menu Principal")
page = st.sidebar.radio(
    "Choisissez un module d'analyse :",
    [
        "Cartographie du Portefeuille", 
        "Souscription de Contrat", 
        "Simulation Monte Carlo"
    ]
)
st.sidebar.markdown("---")
st.sidebar.caption("Système d'évaluation de l'exposition au risque sismique")


# ==========================================
# 4. PAGE 1 : CARTOGRAPHIE DU PORTEFEUILLE
# ==========================================
if page == "Cartographie du Portefeuille":
    def get_rpa_color(name):
        w = str(name).upper()
        if w in ["ALGER", "BOUMERDES", "BLIDA", "TIPAZA", "CHLEF", "AIN DEFLA"]: return RPA_COLORS["ROUGE"]
        elif w in ["ORAN", "CONSTANTINE", "SETIF", "BEJAIA", "TIZI OUZOU", "JIJEL", "SKIKDA", "ANNABA", "MEDEA"]: return RPA_COLORS["ORANGE"]
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

    st.title("Cartographie des Risques Sismiques")
    
    col_search, col_btn = st.columns([3, 1])
    liste_wilayas = ["Toutes les Wilayas"] + sorted(df['WILAYA_UP'].dropna().unique().tolist())
    index_actuel = liste_wilayas.index(st.session_state.selected_wilaya) if st.session_state.selected_wilaya in liste_wilayas else 0

    with col_search:
        choix_recherche = st.selectbox("Rechercher ou sélectionner une Wilaya :", options=liste_wilayas, index=index_actuel)

    with col_btn:
        st.write("")
        st.write("")
        if st.button("Réinitialiser la vue", use_container_width=True):
            st.session_state.selected_wilaya = "Toutes les Wilayas"
            st.rerun()

    if choix_recherche != st.session_state.selected_wilaya:
        st.session_state.selected_wilaya = choix_recherche
        st.rerun()

    bounds_to_fit = None
    display_data = None
    tooltip_fields = []
    tooltip_aliases = []
    
    # Construction de la carte avec sécurité anti-crash (Correction du Bug)
    if st.session_state.selected_wilaya != "Toutes les Wilayas" and geo_communes:
        features_wilaya = [f for f in geo_communes['features'] if clean_name(f['properties'].get('adm1_name', '')) == st.session_state.selected_wilaya]
        
        if features_wilaya: # Vérifie si la liste n'est pas vide avant de dessiner
            display_data = {"type": "FeatureCollection", "features": features_wilaya}
            tooltip_fields, tooltip_aliases = ['adm1_name', 'adm2_name'], ['Wilaya:', 'Commune:']
            bounds_to_fit = get_bounds(features_wilaya)
            m = folium.Map(tiles="cartodbpositron")
        else:
            st.warning("Les données géographiques des communes ne sont pas disponibles pour cette Wilaya. Affichage de la carte globale.")
            # Fallback vers la carte nationale si erreur
            if geo_wilayas:
                display_data = geo_wilayas
                tooltip_fields, tooltip_aliases = ['adm1_name'], ['Wilaya:']
                m = folium.Map(location=[28.0, 2.0], zoom_start=5, tiles="cartodbpositron")

    elif geo_wilayas:
        display_data = geo_wilayas
        tooltip_fields, tooltip_aliases = ['adm1_name'], ['Wilaya:']
        m = folium.Map(location=[28.0, 2.0], zoom_start=5, tiles="cartodbpositron")
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
        
        if bounds_to_fit: m.fit_bounds(bounds_to_fit)
        
        map_res = st_folium(m, width="100%", height=450, key="map_algeria")

        if map_res.get("last_active_drawing") and st.session_state.selected_wilaya == "Toutes les Wilayas":
            clicked_w = map_res["last_active_drawing"]["properties"].get("adm1_name", "").upper()
            if clicked_w:
                st.session_state.selected_wilaya = clicked_w
                st.rerun()

    st.divider()
    
    # --- DASHBOARD MIS À JOUR ---
    is_national = (st.session_state.selected_wilaya == "Toutes les Wilayas")
    dashboard_df = df if is_national else df[df['WILAYA_UP'] == st.session_state.selected_wilaya]
    
    st.header(f"Analyse du Portefeuille : {'Algérie Entière' if is_national else st.session_state.selected_wilaya}")

    if not dashboard_df.empty:
        # Métriques principales
        c1, c2, c3 = st.columns(3)
        c1.metric("Capital Total Exposé (DZD)", f"{dashboard_df['CAPITAL_ASSURE'].sum():,.0f}".replace(',', ' '))
        c2.metric("Total Primes Nettes (DZD)", f"{dashboard_df['PRIME_NETTE'].sum():,.0f}".replace(',', ' '))
        c3.metric("Ratio de Risque Moyen", f"{dashboard_df['RATIO_RISQUE'].mean():.2f}")
        
        st.write("---")
        
        # 1. Exposition par Zone RPA (Graphique + Camembert)
        st.subheader("Exposition par Zone RPA")
        col_bar_zone, col_pie_zone = st.columns(2)
        zone_data = dashboard_df.groupby('ZONE_RPA_CAT')['CAPITAL_ASSURE'].sum().reset_index()
        
        with col_bar_zone:
            fig_bar_zone = px.bar(zone_data, x='ZONE_RPA_CAT', y='CAPITAL_ASSURE', text_auto='.2s', labels={'ZONE_RPA_CAT':'Zone RPA', 'CAPITAL_ASSURE':'Capital (DZD)'})
            fig_bar_zone.update_traces(marker_color='#ff4b4b')
            st.plotly_chart(fig_bar_zone, use_container_width=True)
            
        with col_pie_zone:
            fig_pie_zone = px.pie(zone_data, names='ZONE_RPA_CAT', values='CAPITAL_ASSURE', hole=0.4)
            st.plotly_chart(fig_pie_zone, use_container_width=True)
            
        st.write("---")
        
        # 2. Exposition par Nature du Risque (Graphique + Camembert)
        st.subheader("Exposition par Nature du Risque")
        col_bar_type, col_pie_type = st.columns(2)
        type_data = dashboard_df.groupby('TYPE_CLEAN')['CAPITAL_ASSURE'].sum().reset_index()
        
        with col_bar_type:
            fig_bar_type = px.bar(type_data, x='TYPE_CLEAN', y='CAPITAL_ASSURE', text_auto='.2s', labels={'TYPE_CLEAN':'Type de Bien', 'CAPITAL_ASSURE':'Capital (DZD)'})
            fig_bar_type.update_traces(marker_color='#0068c9')
            st.plotly_chart(fig_bar_type, use_container_width=True)
            
        with col_pie_type:
            fig_pie_type = px.pie(type_data, names='TYPE_CLEAN', values='CAPITAL_ASSURE', hole=0.4)
            st.plotly_chart(fig_pie_type, use_container_width=True)
            
        st.write("---")
            
        # 3. Points Chauds & Opportunités (Uniquement Diagrammes)
        group_col = 'WILAYA_UP' if is_national else 'COMMUNE_UP'
        grouped_geo = dashboard_df.groupby(group_col)['CAPITAL_ASSURE'].sum().reset_index()
        grouped_geo_positive = grouped_geo[grouped_geo['CAPITAL_ASSURE'] > 0] # Filtrer pour ignorer les 0
        
        col_hot, col_cold = st.columns(2)
        
        with col_hot:
            st.subheader("🔥 Points Chauds (Top 3 Sur-concentration)")
            top3 = grouped_geo.sort_values(ascending=False, by='CAPITAL_ASSURE').head(3)
            fig_hot = px.bar(top3, x=group_col, y='CAPITAL_ASSURE', text_auto='.2s', labels={group_col: 'Localisation', 'CAPITAL_ASSURE':'Capital (DZD)'})
            fig_hot.update_traces(marker_color='#e31a1c')
            st.plotly_chart(fig_hot, use_container_width=True)
            
        with col_cold:
            st.subheader("💡 Opportunités (Top 3 Sous-concentration)")
            bottom3 = grouped_geo_positive.sort_values(ascending=True, by='CAPITAL_ASSURE').head(3)
            fig_cold = px.bar(bottom3, x=group_col, y='CAPITAL_ASSURE', text_auto='.2s', labels={group_col: 'Localisation', 'CAPITAL_ASSURE':'Capital (DZD)'})
            fig_cold.update_traces(marker_color='#33a02c')
            st.plotly_chart(fig_cold, use_container_width=True)


# ==========================================
# 5. PAGE 2 : SOUSCRIPTION DE CONTRAT
# ==========================================
elif page == "Souscription de Contrat":
    
    def determiner_zone_depuis_data(wilaya_nom):
        try:
            zone_detectee = df[df['WILAYA_UP'] == wilaya_nom]['ZONE_RPA'].mode()[0]
            return zone_detectee
        except:
            return "IIa"

    def evaluer_risque_avance(zone_rpa, type_bien, capital):
        taux_base = {"0": 0.0001, "I": 0.0003, "IIa": 0.0007, "IIb": 0.0012, "III": 0.0020, "IV": 0.0030}
        coeffs_type = {"Immobilier (Habitation)": 1.0, "Commercial (Bureaux/Magasins)": 1.4, "Industriel (Usines/Dépôts)": 2.2}
        
        base_rate = taux_base.get(zone_rpa, 0.0010)
        mult_type = coeffs_type.get(type_bien, 1.0)
        
        score_zone = {"0": 10, "I": 25, "IIa": 45, "IIb": 65, "III": 85, "IV": 100}.get(zone_rpa, 50)
        score_bien = {"Immobilier (Habitation)": 20, "Commercial (Bureaux/Magasins)": 50, "Industriel (Usines/Dépôts)": 90}.get(type_bien, 50)
        
        score_final = (score_zone * 0.6) + (score_bien * 0.4)
        if capital > 1_000_000_000: score_final += 10
            
        return min(score_final, 100.0), capital * base_rate * mult_type

    st.title("Module de Souscription Intelligent")
    st.markdown("Détection automatique de l'aléa sismique et ajustement tarifaire selon l'activité.")

    with st.container(border=True):
        st.subheader("Informations du Prospect")
        col_w, col_c = st.columns(2)
        
        wilayas_list = sorted(df['WILAYA_UP'].dropna().unique())
        selected_wilaya = col_w.selectbox("Wilaya du projet", wilayas_list)
        zone_auto = determiner_zone_depuis_data(selected_wilaya)
        
        communes_list = sorted(df[df['WILAYA_UP'] == selected_wilaya]['COMMUNE_UP'].dropna().unique())
        selected_commune = col_c.selectbox("Commune", communes_list)

        col_type, col_cap = st.columns(2)
        type_bien = col_type.selectbox("Nature du Bien", ["Immobilier (Habitation)", "Commercial (Bureaux/Magasins)", "Industriel (Usines/Dépôts)"])
        capital_assure = col_cap.number_input("Capital total à assurer (DZD)", min_value=0.0, value=50_000_000.0, step=10_000_000.0)

    st.caption(f"Zone RPA détectée pour {selected_wilaya} : **Zone {zone_auto}**")

    if st.button("Générer le Diagnostic de Souscription", type="primary", use_container_width=True):
        score, prime = evaluer_risque_avance(zone_auto, type_bien, capital_assure)
        st.divider()
        
        c1, c2 = st.columns([1, 1.2])
        with c1:
            fig = go.Figure(go.Indicator(
                mode = "gauge+number", value = score, number = {'suffix': "%", 'font': {'size': 40}},
                gauge = {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#222"},
                    'steps': [{'range': [0, 40], 'color': "#33a02c"}, {'range': [40, 75], 'color': "#ff7f00"}, {'range': [75, 100], 'color': "#e31a1c"}]
                }
            ))
            fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.subheader("Analyse Technique")
            st.metric("Prime Nette Annuelle", f"{prime:,.2f} DZD".replace(',', ' '))
            
            if score < 40: st.success("🟢 **RISQUE ACCEPTABLE**\n\nProfil standard. Aucune mesure particulière requise.")
            elif score < 75: st.warning("🟠 **SURVEILLANCE REQUISE**\n\nExposition modérée. Application d'une franchise recommandée.")
            else: st.error("🔴 **RISQUE ÉLEVÉ**\n\nActivité vulnérable en zone sismique. Étude de vulnérabilité obligatoire.")


# ==========================================
# 6. PAGE 3 : SIMULATION MONTE CARLO
# ==========================================
elif page == "Simulation Monte Carlo":
    st.title("Simulation Stochastique de Portefeuille (Monte Carlo)")
    st.markdown("Évaluation probabiliste des pertes maximales selon des scénarios sismiques simulés.")

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

            with st.container(border=True):
                st.subheader("Paramétrage du Scénario")
                col_param1, col_param2 = st.columns(2)
                wilayas_disponibles = sorted(df_2024['WILAYA_UP'].unique())
                
                with col_param1:
                    selected_mc_wilaya = st.selectbox("Cible de la simulation (Wilaya)", wilayas_disponibles)
                with col_param2:
                    lambda_freq = st.slider("Fréquence annuelle d'occurrence (CATNAT)", 0.0, 0.2, 0.05, step=0.01)

            df_w = df_2024[df_2024['WILAYA_UP'] == selected_mc_wilaya].copy()
            df_w['EXPOSITION_UNITAIRE'] = df_w['CAPITAL_ASSURE'] * df_w['SEVERITY_FACTOR'] * 0.30
            
            expo_totale_wilaya = df_w['EXPOSITION_UNITAIRE'].sum()
            total_primes = df_w['PRIME_NETTE'].sum()

            st.markdown("### Profil du Portefeuille Ciblé (2024)")
            c1, c2, c3 = st.columns(3)
            c1.metric("Nombre de Polices Actives", len(df_w))
            c2.metric("Exposition Modélisée (PML)", f"{expo_totale_wilaya:,.0f} DZD".replace(',', ' '))
            c3.metric("Volume de Primes Nettes", f"{total_primes:,.0f} DZD".replace(',', ' '))

            st.divider()

            if expo_totale_wilaya > 0:
                with st.spinner("Génération de 100,000 scénarios sismiques en cours..."):
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

                res1, res2 = st.columns([1, 1.5])
                
                with res1:
                    st.subheader("Indicateurs de Solvabilité")
                    st.write(f"**Charge moyenne annuelle :**\n{losses.mean():,.0f} DZD")
                    
                    pml_995 = np.percentile(losses, 99.5)
                    st.error(f"**Value at Risk (VaR 99.5%) :**\n{pml_995:,.0f} DZD")
                    st.caption("Perte maximale attendue avec une probabilité de 1-en-200 ans (Standard Solvabilité II).")
                    
                    lr = (losses.mean() / total_primes * 100) if total_primes > 0 else 0
                    st.write("---")
                    if lr < 50:
                        st.success(f"**S/P Technique : {lr:.2f}%**\n(Rentable)")
                    elif lr < 80:
                        st.warning(f"**S/P Technique : {lr:.2f}%**\n(Sous tension)")
                    else:
                        st.error(f"**S/P Technique : {lr:.2f}%**\n(Déficitaire)")

                with res2:
                    st.subheader("Distribution des Pertes Modélisées")
                    pertes_positives = losses[losses > 0]
                    if len(pertes_positives) > 0:
                        fig_hist = px.histogram(
                            x=pertes_positives, 
                            nbins=40,
                            labels={'x': 'Montant des dommages (DZD)', 'y': "Nombre d'occurrences"},
                            color_discrete_sequence=['#1f77b4']
                        )
                        fig_hist.update_layout(margin=dict(l=0, r=0, t=20, b=0), plot_bgcolor="rgba(0,0,0,0)")
                        st.plotly_chart(fig_hist, use_container_width=True)
                    else:
                        st.info("La probabilité définie est trop faible pour générer des événements significatifs sur 100 000 itérations.")
            else:
                st.warning("L'exposition est nulle pour cette Wilaya. Impossible de lancer la simulation.")