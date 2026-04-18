# projet-catnat-algerie
Outil d'analyse des risques CATNAT et zonage RPA 2024.
# 🛡️ Outil d'Analyse CATNAT & Zonage RPA 2024 (Algérie)

### 📋 Présentation du Projet
Cette application interactive est un **Dashboard de Gestion des Risques** conçu pour les compagnies d'assurance opérant en Algérie. Elle permet de croiser les données réelles du portefeuille (Assurances Catastrophes Naturelles - CATNAT) avec les nouvelles réglementations sismiques du **RPA 2024**.

L'objectif principal est d'offrir une aide à la décision pour identifier les zones de **surconcentration de capitaux** et optimiser la stratégie de souscription.

---

### 🚀 Fonctionnalités Clés
* **Carte Interactive (Folium) :** Visualisation dynamique des Wilayas et Communes. La coloration respecte le zonage sismique officiel (Zone 1 à 3).
* **Analyse de Portefeuille (KPIs) :** Calcul en temps réel du Capital Total Exposé, du cumul des Primes Nettes et du Ratio de Risque moyen.
* **Zonage RPA & Nature du Risque :** Graphiques d'analyse de la répartition des capitaux par zone sismique et par type de bâtiment (Industriel, Commercial, Habitation).
* **Détection des Points Chauds :** Identification automatique du Top 5 des zones (Wilayas/Communes) présentant les plus fortes concentrations de risques.
* **Interactivité Totale :** Cliquez sur une wilaya pour filtrer instantanément l'ensemble du dashboard.

---

### 🛠️ Technologies Utilisées
* **Langage :** Python 3.12+
* **Framework Web :** [Streamlit](https://streamlit.io/)
* **Cartographie :** [Folium](https://python-visualization.github.io/folium/)
* **Analyse de données :** Pandas
* **Données Géo :** GeoJSON (Découpage administratif algérien)

---

### 💻 Installation et Utilisation Locale

1. **Cloner le projet**
   ```bash
   git clone [https://github.com/TON_NOM_UTILISATEUR/TON_NOM_DE_REPO.git](https://github.com/TON_NOM_UTILISATEUR/TON_NOM_DE_REPO.git)
   cd TON_NOM_DE_REPO
