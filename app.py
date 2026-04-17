import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import json
import os
import numpy as np
import matplotlib.pyplot as plt

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
st.set_page_config(
    layout="wide",
    page_title="Système Expert CATNAT Algérie",
    page_icon="🛡️"
)

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }

    /* ── Métriques : fond neutre + texte forcé visible ── */
    div[data-testid="stMetric"] {
        background: #f0f2f6;
        border-radius: 8px;
        padding: 0.75rem 1rem;
    }
    div[data-testid="stMetric"] label {
        color: #444444 !important;
        font-size: 0.85rem !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #111111 !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
    }

    /* ── Titres principaux ── */
    h1 { font-size: 1.8rem !important; font-weight: 700 !important; }
    h2 { font-size: 1.35rem !important; font-weight: 600 !important; color: #333; }
    h3 { font-size: 1.15rem !important; font-weight: 600 !important; color: #444; }

    .stAlert { border-radius: 8px; }
    div[data-testid="stSidebarNav"] { display: none; }

    .score-badge {
        display: inline-block;
        padding: 0.4rem 1.2rem;
        border-radius: 20px;
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    .score-high   { background: #fde8e8; color: #c0392b; }
    .score-medium { background: #fef3cd; color: #856404; }
    .score-low    { background: #d4edda; color: #155724; }
</style>
""", unsafe_allow_html=True)

# Couleurs carte selon zone RPA (Regroupées en 3 couleurs)
RPA_COLORS = {
    "III":  "#e31a1c",  # Rouge (Zone III)
    "IIb":  "#ff7f00",  # Orange (Zone IIb)
    "IIa":  "#ff7f00",  # Orange (Zone IIa)
    "I":    "#33a02c",  # Vert (Zone I)
    "0":    "#33a02c",  # Vert (Zone 0)
}
# ─────────────────────────────────────────────
# CHARGEMENT DES DONNÉES
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('FUSION_TOTALE_CATNAT.csv', low_memory=False)

    df['CAPITAL_ASSURE'] = pd.to_numeric(df['CAPITAL_ASSURE'], errors='coerce').fillna(0)
    df['PRIME_NETTE'] = pd.to_numeric(
        df['PRIME_NETTE'].astype(str).str.replace(',', '.'), errors='coerce'
    ).fillna(0)
    df['COEFF_A'] = pd.to_numeric(df['COEFF_A'], errors='coerce').fillna(0)

    df['RATIO_RISQUE'] = (df['PRIME_NETTE'] / (df['CAPITAL_ASSURE'] + 1)) * 1000
    df['WILAYA_UP']    = df['WILAYA'].str.strip().str.upper()
    df['COMMUNE_UP']   = df['COMMUNE'].str.split('-').str[-1].str.strip().str.upper()
    df['TYPE_CLEAN']   = df['TYPE'].astype(str).str.split('-').str[-1].str.strip()

    # Nettoyage de la colonne ZONE_RPA
    df['ZONE_RPA'] = df['ZONE_RPA'].astype(str).str.strip()

    # Regroupement en 3 catégories
    def zone_label(z):
        mapping = {
            "III":  "Zone 3 — Risque élevé",
            "IIb":  "Zone 2 — Risque moyen",
            "IIa":  "Zone 2 — Risque moyen",
            "I":    "Zone 1/0 — Risque faible",
            "0":    "Zone 1/0 — Risque faible",
        }
        return mapping.get(z, f"Zone {z}")

    # Application de la fonction
    df['ZONE_LABEL'] = df['ZONE_RPA'].apply(zone_label)
    
    return df

@st.cache_data
def load_geojson(level):
    filename = f"dza_admin{level}.geojson"
    if not os.path.exists(filename):
        st.error(f"Fichier GeoJSON manquant : {filename}")
        return None
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_rpa_color_from_wilaya(wilaya_name, df):
    """Détermine la couleur carte à partir du ZONE_RPA du dataset."""
    rows = df[df['WILAYA_UP'] == str(wilaya_name).upper()]
    if rows.empty:
        return RPA_COLORS.get("I", "#33a02c")
    zone = rows['ZONE_RPA'].mode()[0]
    return RPA_COLORS.get(zone, "#33a02c")


df = load_data()
geo_wilayas  = load_geojson(1)
geo_communes = load_geojson(2)

# Table wilaya → zone RPA (mode) pour la carte
wilaya_zone_map = (
    df.groupby('WILAYA_UP')['ZONE_RPA']
      .agg(lambda x: x.mode()[0])
      .to_dict()
)

def get_rpa_color(name):
    zone = wilaya_zone_map.get(str(name).upper(), "I")
    return RPA_COLORS.get(zone, "#33a02c")


# ─────────────────────────────────────────────
# NAVIGATION
# ─────────────────────────────────────────────
st.sidebar.title("Système Expert CATNAT")
st.sidebar.caption("Algérie — RPA 2024")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    ["Carte & Analyse territoriale", "Scoring de risque client", "Simulation séisme"],
    label_visibility="collapsed"
)


# ═════════════════════════════════════════════
# PAGE 1 — CARTE & DASHBOARD
# ═════════════════════════════════════════════
if page == "Carte & Analyse territoriale":
    st.title("Analyse territoriale — Zonage RPA 2024")

    if 'selected_wilaya' not in st.session_state:
        st.session_state.selected_wilaya = None

    if st.session_state.selected_wilaya:
        if st.sidebar.button("Retour — Algérie entière"):
            st.session_state.selected_wilaya = None
            st.rerun()
        st.caption(f"Wilaya sélectionnée : **{st.session_state.selected_wilaya}**")

# Légende RPA (3 Niveaux)
    col_leg1, col_leg2, col_leg3, _ = st.columns([1, 1, 1, 3])
    col_leg1.markdown("🔴 **Zone III** — Élevée")
    col_leg2.markdown("🟠 **Zone II (a/b)** — Moyenne")
    col_leg3.markdown("🟢 **Zone I/0** — Faible/Négligeable")

    # Carte Folium
    if st.session_state.selected_wilaya:
        center, zoom = [36.0, 3.5], 8
        display_data = {
            "type": "FeatureCollection",
            "features": [
                f for f in geo_communes['features']
                if f['properties'].get('adm1_name', '').upper() == st.session_state.selected_wilaya
            ]
        }
        tooltip_fields  = ['adm1_name', 'adm2_name']
        tooltip_aliases = ['Wilaya :', 'Commune :']
    else:
        center, zoom    = [28.0, 2.0], 5
        display_data    = geo_wilayas
        tooltip_fields  = ['adm1_name']
        tooltip_aliases = ['Wilaya :']

    m = folium.Map(location=center, zoom_start=zoom, tiles="cartodbpositron")
    folium.GeoJson(
        display_data,
        style_function=lambda x: {
            'fillColor': get_rpa_color(x['properties'].get('adm1_name', '')),
            'color': 'white',
            'weight': 1,
            'fillOpacity': 0.7
        },
        tooltip=folium.GeoJsonTooltip(fields=tooltip_fields, aliases=tooltip_aliases)
    ).add_to(m)

    map_res = st_folium(m, width="100%", height=550, key="map_algeria")

    if map_res.get("last_active_drawing") and not st.session_state.selected_wilaya:
        clicked_w = map_res["last_active_drawing"]["properties"].get("adm1_name", "").upper()
        if clicked_w:
            st.session_state.selected_wilaya = clicked_w
            st.rerun()

    # ── Dashboard analytique ──
    st.divider()

    if st.session_state.selected_wilaya:
        dashboard_df = df[df['WILAYA_UP'] == st.session_state.selected_wilaya]
        st.subheader(f"Portefeuille — {st.session_state.selected_wilaya}")
    else:
        dashboard_df = df
        st.subheader("Portefeuille — Algérie entière")

    if dashboard_df.empty:
        st.warning("Aucune donnée disponible pour cette sélection.")
        st.stop()

    # KPIs
    c1, c2, c3 = st.columns(3)
    c1.metric("Capital total exposé (DZD)", f"{dashboard_df['CAPITAL_ASSURE'].sum():,.0f}")
    c2.metric("Primes nettes totales (DZD)", f"{dashboard_df['PRIME_NETTE'].sum():,.0f}")
    c3.metric("Ratio de risque moyen", f"{dashboard_df['RATIO_RISQUE'].mean():.4f}")

    st.markdown("---")

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Exposition par zone RPA")
        zone_data = dashboard_df.groupby('ZONE_LABEL')['CAPITAL_ASSURE'].sum()
        st.bar_chart(zone_data)

    with col_g2:
        st.subheader("Exposition par nature du risque")
        type_data = dashboard_df.groupby('TYPE_CLEAN')['CAPITAL_ASSURE'].sum()
        st.bar_chart(type_data)

    st.markdown("---")

    st.subheader("Surconcentrations — Top 5 (capital le plus élevé)")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.caption("Par wilaya")
        top_w = df.groupby('WILAYA_UP')['CAPITAL_ASSURE'].sum().sort_values(ascending=False).head(5)
        st.bar_chart(top_w)
    with col_t2:
        st.caption("Par commune")
        top_c = dashboard_df.groupby('COMMUNE_UP')['CAPITAL_ASSURE'].sum().sort_values(ascending=False).head(5)
        st.dataframe(top_c.reset_index(), use_container_width=True)

    st.markdown("---")

    st.subheader("Sous-concentrations — Top 5 (déserts commerciaux)")
    col_f1, col_f2 = st.columns(2)
    df_active        = df[df['CAPITAL_ASSURE'] > 0]
    dashboard_active = dashboard_df[dashboard_df['CAPITAL_ASSURE'] > 0]

    with col_f1:
        st.caption("Par wilaya")
        flop_w = df_active.groupby('WILAYA_UP')['CAPITAL_ASSURE'].sum().sort_values(ascending=True).head(5)
        st.bar_chart(flop_w)
    with col_f2:
        st.caption("Par commune")
        flop_c = dashboard_active.groupby('COMMUNE_UP')['CAPITAL_ASSURE'].sum().sort_values(ascending=True).head(5)
        st.dataframe(flop_c.reset_index(), use_container_width=True)


# ═════════════════════════════════════════════
# PAGE 2 — SCORING CLIENT
# ═════════════════════════════════════════════
elif page == "Scoring de risque client":
    st.title("Scoring de risque client")
    st.caption("Évaluation automatique de l'acceptabilité d'un dossier — moteur XGBoost (à intégrer)")
    st.divider()

    col_form, col_result = st.columns([1.4, 1])

    with col_form:
        st.subheader("Données du client")

        wilaya_options = sorted(df['WILAYA_UP'].dropna().unique())
        type_options   = sorted(df['TYPE_CLEAN'].dropna().unique())

        wilaya_sel = st.selectbox("Wilaya", wilaya_options)

        # Zone RPA et coeff_A dérivés automatiquement du dataset
        rows_w = df[df['WILAYA_UP'] == wilaya_sel]
        zone_rpa_val = rows_w['ZONE_RPA'].mode()[0]  if not rows_w.empty else "I"
        coeff_a_val  = rows_w['COEFF_A'].mode()[0]   if not rows_w.empty else 0.12

        zone_labels_map = {
            "III":  ("Zone III — Élevée",        "high"),
            "IIb":  ("Zone IIb — Moyenne haute",  "high"),
            "IIa":  ("Zone IIa — Moyenne",         "medium"),
            "I":    ("Zone I — Faible",            "low"),
            "0":    ("Zone 0 — Négligeable",       "low"),
        }
        zone_label, zone_level = zone_labels_map.get(zone_rpa_val, (f"Zone {zone_rpa_val}", "low"))

        badge_colors = {
            "high":   "#fde8e8;color:#c0392b",
            "medium": "#fef3cd;color:#856404",
            "low":    "#d4edda;color:#155724"
        }
        st.markdown(
            f"Zone RPA détectée : "
            f"<span style='background:{badge_colors[zone_level]};padding:2px 10px;border-radius:12px;"
            f"font-size:0.85rem;font-weight:600'>{zone_label}</span> "
            f"&nbsp;|&nbsp; Coefficient A : <strong>{coeff_a_val}</strong>",
            unsafe_allow_html=True
        )
        st.markdown(" ")

        col_a, col_b = st.columns(2)
        with col_a:
            type_sel   = st.selectbox("Type de bien", type_options)
            capital_in = st.number_input("Capital assuré (DZD)", min_value=0, step=100_000, format="%d")
            prime_in   = st.number_input("Prime nette (DZD)",    min_value=0, step=1_000,   format="%d")

        with col_b:
            nb_etages = st.number_input("Nombre d'étages ", min_value=0, max_value=50, value=1)
            surface   = st.number_input("Surface m² ",       min_value=0, step=10)
            st.caption("⚙️ Étages et surface sont recueillis pour information — ils n'influencent pas encore le score.")

        st.markdown(" ")
        submitted = st.button("Calculer le score de risque", type="primary", use_container_width=True)

    with col_result:
        st.subheader("Résultat de l'évaluation")

        if not submitted:
            st.info("Remplissez le formulaire, puis cliquez sur **Calculer le score de risque**.")
            st.markdown("""
            **Variables prises en compte par le modèle :**
            - Zone sismique RPA (wilaya → ZONE_RPA)
            - Coefficient A de la zone
            - Type de bien
            - Capital assuré
            - Prime nette
            """)
        else:
            if capital_in == 0:
                st.warning("Veuillez saisir un capital assuré supérieur à 0.")
            else:
                # ── Placeholder XGBoost ──────────────────────────────────────
                # TODO: features = [zone_rpa_val, coeff_a_val, type_sel, capital_in, prime_in]
                #       score = model.predict_proba([features])[0][1]
                rng  = np.random.default_rng(int(capital_in) % 9999)
                base = {"high": 0.72, "medium": 0.45, "low": 0.22}[zone_level]
                score = float(np.clip(base + rng.normal(0, 0.08), 0.05, 0.98))
                # ─────────────────────────────────────────────────────────────

                score_pct = int(score * 100)
                bar_color = "#e74c3c" if score > 0.6 else ("#f39c12" if score > 0.35 else "#27ae60")

                st.markdown(f"""
                <div style='margin-bottom:1rem'>
                    <div style='display:flex;justify-content:space-between;margin-bottom:4px'>
                        <span style='font-size:0.85rem;color:#666'>Probabilité de sinistre</span>
                        <span style='font-weight:600;color:{bar_color}'>{score_pct}%</span>
                    </div>
                    <div style='background:#eee;border-radius:8px;height:14px;overflow:hidden'>
                        <div style='width:{score_pct}%;background:{bar_color};height:100%;border-radius:8px'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if score > 0.6:
                    decision, badge_cls, motif = "Refus recommandé", "score-high", \
                        "Score de risque élevé. Zone sismique à forte exposition."
                elif score > 0.35:
                    decision, badge_cls, motif = "Acceptation avec surprime", "score-medium", \
                        "Risque modéré. Application d'une surprime sismique conseillée."
                else:
                    decision, badge_cls, motif = "Acceptation standard", "score-low", \
                        "Risque faible. Conditions standard applicables."

                st.markdown(
                    f"**Décision :** <span class='score-badge {badge_cls}'>{decision}</span>",
                    unsafe_allow_html=True
                )
                st.markdown(f"*{motif}*")
                st.divider()

                st.markdown("**Récapitulatif du dossier**")
                recap = {
                    "Wilaya":           wilaya_sel,
                    "Zone RPA":         zone_label,
                    "Coefficient A":    coeff_a_val,
                    "Type de bien":     type_sel,
                    "Capital (DZD)":    f"{capital_in:,}",
                    "Prime nette (DZD)": f"{prime_in:,}",
                    "Étages":           nb_etages,
                    "Surface (m²)":     surface,
                }
                for k, v in recap.items():
                    st.markdown(f"- **{k}** : {v}")

                st.caption("⚠ Score simulé — le modèle XGBoost sera branché ici.")


# ═════════════════════════════════════════════
# PAGE 3 — SIMULATION SÉISME (Monte Carlo)
# ═════════════════════════════════════════════
elif page == "Simulation séisme":
    st.title("Simulation d'impact séismique")
    st.caption("Modélisation probabiliste — Monte Carlo 100 000 itérations (Poisson × Lognormale)")
    st.divider()

    col_params, col_output = st.columns([1, 1.4])

    with col_params:
        st.subheader("Paramètres")

        wilaya_sim = st.selectbox(
            "Zone d'impact (wilaya)",
            sorted(df['WILAYA_UP'].dropna().unique())
        )

        lambda_freq = st.slider(
            "Fréquence annuelle de l'événement",
            min_value=0.0, max_value=0.2, value=0.05, step=0.01,
            format="%.2f",
            help="Probabilité annuelle d'occurrence (ex. 0.05 = 1 événement tous les 20 ans)"
        )

        # Infos de la zone sélectionnée
        df_w_info = df[df['WILAYA_UP'] == wilaya_sim]
        zone_rpa_sim  = df_w_info['ZONE_RPA'].mode()[0] if not df_w_info.empty else "I"
        coeff_a_sim   = df_w_info['COEFF_A'].mode()[0]  if not df_w_info.empty else 0.12
        capital_zone  = df_w_info['CAPITAL_ASSURE'].sum()
        total_primes  = df_w_info['PRIME_NETTE'].sum()

        st.info(
            f"**Zone RPA :** {zone_rpa_sim}  |  **Coeff. A :** {coeff_a_sim}\n\n"
            f"**Capital exposé :** {capital_zone:,.0f} DZD\n\n"
            f"**Primes encaissées :** {total_primes:,.0f} DZD"
        )

        run_sim = st.button("Lancer la simulation", type="primary", use_container_width=True)

    with col_output:
        st.subheader("Résultats financiers")

        if not run_sim:
            st.info("Sélectionnez une wilaya et une fréquence, puis lancez la simulation.")
            st.markdown("""
            **Ce que calcule le modèle :**
            - Distribution des pertes (Poisson × Lognormale)
            - Prime pure / Perte espérée annuelle (PEA)
            - VaR 99,5 % — scénario 1-en-200 ans (standard Solvabilité II)
            - Ratio S/P technique (Loss Ratio)
            - Histogramme de la distribution des sinistres
            """)
        else:
            with st.spinner("Simulation en cours — 100 000 itérations..."):

                N_SIM    = 100_000
                sigma    = 0.8
                mean_mdr = 0.05

                # Facteur de sévérité par type de bien
                def severity_factor(t):
                    t = str(t).lower()
                    if 'industriel' in t: return 0.7
                    if 'commercial' in t: return 0.5
                    return 0.3

                df_w = df[df['WILAYA_UP'] == wilaya_sim].copy()
                df_w['SEV_FACTOR']       = df_w['TYPE_CLEAN'].apply(severity_factor)
                df_w['EXPOSITION_UNIT']  = df_w['CAPITAL_ASSURE'] * df_w['SEV_FACTOR'] * 0.30
                expo_totale = df_w['EXPOSITION_UNIT'].sum()

                # ── Monte Carlo ──────────────────────────────────────────────
                rng = np.random.default_rng(42)
                losses = np.zeros(N_SIM)
                n_events_per_year = rng.poisson(lambda_freq, N_SIM)

                for i in range(N_SIM):
                    n_ev = n_events_per_year[i]
                    if n_ev > 0:
                        year_loss = 0.0
                        for _ in range(n_ev):
                            mu_adj = np.log(mean_mdr) - 0.5 * sigma**2
                            mdr    = min(rng.lognormal(mu_adj, sigma), 0.8)
                            year_loss += expo_totale * mdr
                        losses[i] = year_loss
                # ─────────────────────────────────────────────────────────────

            st.success("Simulation terminée — 100 000 scénarios annuels générés.")
            st.divider()

            pea    = losses.mean()
            var995 = np.percentile(losses, 99.5)
            var99  = np.percentile(losses, 99.0)
            tvar   = losses[losses >= var99].mean()
            lr     = (pea / total_primes * 100) if total_primes > 0 else 0.0

            # ── KPIs ──────────────────────────────────────────────────────
            m1, m2 = st.columns(2)
            m1.metric("Perte espérée annuelle (PEA)", f"{pea:,.0f} DZD")
            m2.metric("VaR 99,5 % — scénario 1/200 ans", f"{var995:,.0f} DZD")

            m3, m4 = st.columns(2)
            m3.metric("TVaR 99 % (queue de distribution)", f"{tvar:,.0f} DZD")
            lr_color = "green" if lr < 50 else ("orange" if lr < 80 else "red")
            m4.metric("Ratio S/P technique (Loss Ratio)", f"{lr:.2f} %")

            st.divider()

            # ── Histogramme ───────────────────────────────────────────────
            st.subheader("Distribution des sinistres simulés")
            pertes_pos = losses[losses > 0]

            if len(pertes_pos) > 100:
                fig, ax = plt.subplots(figsize=(7, 3.5))
                ax.hist(pertes_pos, bins=50, color='royalblue', alpha=0.75, edgecolor='white')
                ax.axvline(pea,    color='green',  linestyle='--', linewidth=1.5, label=f"PEA : {pea:,.0f}")
                ax.axvline(var995, color='red',    linestyle='--', linewidth=1.5, label=f"VaR 99,5% : {var995:,.0f}")
                ax.set_xlabel("Perte annuelle simulée (DZD)")
                ax.set_ylabel("Fréquence")
                ax.legend(fontsize=8)
                ax.set_title(f"Wilaya : {wilaya_sim} — fréquence λ = {lambda_freq:.2f}")
                fig.tight_layout()
                st.pyplot(fig)
            else:
                st.info("Fréquence trop basse pour générer des sinistres significatifs. "
                        "Essayez d'augmenter la fréquence annuelle.")

            st.caption("⚠ Modèle Poisson × Lognormale — paramétrage à calibrer sur données historiques.")