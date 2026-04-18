# Generated from: code_final_iguess.ipynb
# Converted at: 2026-04-17T21:21:14.659Z
# Next step (optional): refactor into modules & generate tests with RunCell
# Quick start: pip install runcell

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, StratifiedKFold, RandomizedSearchCV
from sklearn.metrics import classification_report, confusion_matrix
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv("cleaned_ds_final_forver.csv", low_memory=False)

# Nettoyage des virgules françaises → décimales
for col in ['CAPITAL_ASSURE', 'PRIME_NETTE']:
    if df[col].dtype == 'object':
        df[col] = df[col].str.replace(',', '.').astype(float)

print(f"✅ Dataset chargé : {df.shape[0]:,} lignes × {df.shape[1]} colonnes")
print(f"   Wilayas uniques : {df['WILAYA'].nunique()}")
print(f"   Communes uniques : {df['COMMUNE'].nunique()}")

# =============================================================================
# 1. ENCODAGE (inclut COMMUNE)
# =============================================================================
le_wilaya  = LabelEncoder()
le_commune = LabelEncoder()
le_type    = LabelEncoder()
le_zone    = LabelEncoder()

df['WILAYA_ENC']  = le_wilaya.fit_transform(df['WILAYA'])
df['COMMUNE_ENC'] = le_commune.fit_transform(df['COMMUNE'])
df['TYPE_ENC']    = le_type.fit_transform(df['TYPE'].fillna('INCONNU'))
df['ZONE_ENC']    = le_zone.fit_transform(df['ZONE_RPA'].fillna('INCONNU'))

print("✅ Encodage terminé (COMMUNE_ENC ajouté)")

# =============================================================================
# 2. CRÉATION DU LABEL "RISQUE ÉLEVÉ"
# =============================================================================
zone_medians = df.groupby('ZONE_RPA')['PRIME_NETTE'].transform('median')
df['LABEL'] = (
    (df['COEFF_A'] >= 0.15) & 
    (df['PRIME_NETTE'] < zone_medians)
).astype(int)

print(f"   Risques détectés (LABEL=1) : {df['LABEL'].sum():,} ({df['LABEL'].mean():.1%})")

# =============================================================================
# 3. MODÈLE XGBoost (avec Commune)
# =============================================================================
features = ['WILAYA_ENC', 'COMMUNE_ENC', 'TYPE_ENC', 'CAPITAL_ASSURE']
X = df[features]
y = df['LABEL']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Gestion du déséquilibre
neg, pos = (y_train == 0).sum(), (y_train == 1).sum()
scale_pos = neg / max(pos, 1)

model = xgb.XGBClassifier(
    n_estimators=400,
    max_depth=6,
    learning_rate=0.05,
    scale_pos_weight=scale_pos,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric='logloss',
    early_stopping_rounds=30,
    random_state=42,
    tree_method='hist'
)

model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

# Prédictions sur tout le dataset
df['PREDICTED_LABEL'] = model.predict(X)
df['RISK_SCORE']      = model.predict_proba(X)[:, 1]

print("\n📊 Classification Report (Test set) :")
print(classification_report(y_test, model.predict(X_test), zero_division=0))



from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder

# 1. Préparation des "Paniers de Risque"
# On transforme chaque ligne en une liste de caractéristiques textuelles
def build_risk_basket(row):
    return [
        f"WILAYA={row['WILAYA']}",
        f"ZONE={row['ZONE_RPA']}",
        f"TYPE={row['TYPE']}",
        f"COEFF={row['COEFF_A']}",
        f"RISQUE={'ELEVE' if row['PREDICTED_LABEL'] == 1 else 'NORMAL'}",
        f"CONCENTRATION={'HAUTE' if row['CAPITAL_ASSURE'] > df['CAPITAL_ASSURE'].median() else 'BASSE'}"
    ]

transactions = df.apply(build_risk_basket, axis=1).tolist()

# 2. Encodage Transactionnel
te = TransactionEncoder()
te_array = te.fit(transactions).transform(transactions)
df_trans = pd.DataFrame(te_array, columns=te.columns_)

# 3. Extraction des Itemsets Fréquents (Support min 5%)
frequent_itemsets = apriori(df_trans, min_support=0.05, use_colnames=True)

# 4. Génération des Implications (Focus sur le Risque Elevé)
rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.2)

# On filtre pour voir ce qui "mène" au Risque Élevé
risk_implications = rules[rules['consequents'].apply(lambda x: 'RISQUE=ELEVE' in x)]
risk_implications = risk_implications.sort_values(by='lift', ascending=False)

print("🔍 Implications stratégiques extraites :")
print(risk_implications[['antecedents', 'confidence', 'lift']].head(10))


from sklearn.metrics import classification_report
from catboost import CatBoostClassifier

# 1. Préparation et Nettoyage des données
# On remplit les valeurs manquantes pour les catégories
df['TYPE'] = df['TYPE'].fillna('INCONNU')
df['COMMUNE'] = df['COMMUNE'].fillna('INCONNU')

# On s'assure que toutes les colonnes catégorielles sont bien des chaînes de caractères (string)
cat_features = ['WILAYA', 'COMMUNE', 'TYPE', 'ZONE_RPA']
for col in cat_features:
    df[col] = df[col].astype(str)

# 2. Définition des variables
features = ['WILAYA', 'COMMUNE', 'TYPE', 'ZONE_RPA', 'COEFF_A']
X = df[features]
y = df['LABEL']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 3. Configuration et Entraînement de CatBoost
# auto_class_weights='Balanced' va aider pour le déséquilibre (0.74/0.26)
model_cat = CatBoostClassifier(
    iterations=500,
    learning_rate=0.05,
    depth=6,
    cat_features=cat_features,
    auto_class_weights='Balanced',
    verbose=100,
    eval_metric='F1'
)

model_cat.fit(X_train, y_train, eval_set=(X_test, y_test))

# 4. Évaluation
y_pred = model_cat.predict(X_test)
print("\nClassification Report (CatBoost - Corrigé):")
print(classification_report(y_test, y_pred))

# Ajout du score au dataframe
df['RISK_SCORE_CAT'] = model_cat.predict_proba(X)[:, 1]

from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt

# 1. Définition des colonnes que le modèle a appris à utiliser (les versions ENCODÉES)
features_model = ['WILAYA_ENC', 'COMMUNE_ENC', 'TYPE_ENC', 'CAPITAL_ASSURE']

# 2. On prépare le X_test en allant chercher ces colonnes dans le DataFrame d'origine 'df'
# On utilise l'index de X_test pour garder les mêmes lignes que votre découpage actuel
X_test_numeric = df.loc[X_test.index, features_model]

# 3. Calcul des probabilités de risque (Classe 1)
y_probs = model.predict_proba(X_test_numeric)[:, 1]

# 4. Calcul et affichage ROC/AUC
fpr, tpr, thresholds = roc_curve(y_test, y_probs)
roc_auc = auc(fpr, tpr)

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.4f})')
plt.plot([0, 1], color='navy', linestyle='--')
plt.xlabel('Taux de Faux Positifs')
plt.ylabel('Taux de Vrais Positifs (Recall)')
plt.title('Courbe ROC - Détection de Sous-Tarification')
plt.legend(loc="lower right")
plt.grid(alpha=0.2)
plt.show()

print(f"✅ Analyse terminée. AUC : {roc_auc:.4f}")

import pandas as pd
import numpy as np

# 1. Sélection aléatoire de 20 indices dans le set de test
random_indices = np.random.choice(X_test.index, size=20, replace=False)

# 2. Préparation des données pour la prédiction (uniquement les colonnes encodées)
features_model = ['WILAYA_ENC', 'COMMUNE_ENC', 'TYPE_ENC', 'CAPITAL_ASSURE']
X_test_samples = df.loc[random_indices, features_model]

# 3. Prédiction
probs = model.predict_proba(X_test_samples)[:, 1]
preds = model.predict(X_test_samples)

# 4. Création du tableau de synthèse lisible
test_reels = df.loc[random_indices, ['WILAYA', 'COMMUNE', 'ZONE_RPA', 'PRIME_NETTE', 'COEFF_A']].copy()
test_reels['RISQUE_REEL'] = y_test.loc[random_indices].values
test_reels['PRED_MODELE'] = preds
test_reels['SCORE_RISQUE'] = (probs * 100).round(2)

# 5. Ajout d'un indicateur de succès
test_reels['RESULTAT'] = test_reels.apply(
    lambda x: "✅" if x['RISQUE_REEL'] == x['PRED_MODELE'] else "❌", axis=1
)

print("🧪 TEST ALÉATOIRE SUR 20 DOSSIERS D'ASSURANCE")
print("=" * 110)
print(test_reels.to_string(index=False))
print("=" * 110)

# Calcul du taux de réussite sur cet échantillon
succes = (test_reels['RESULTAT'] == "✅").sum()
print(f"🎯 Précision sur cet échantillon : {succes}/20 ({(succes/20)*100}%)")

# # CDC


# **1-Concentration**


import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# --- 1. SÉCURISATION ET CALCUL ---
# On définit les colonnes vraiment nécessaires
cols_disponibles = df.columns.tolist()

# Nettoyage sécurisé des colonnes numériques existantes
for col in ['CAPITAL_ASSURE', 'PRIME_NETTE', 'COEFF_A']:
    if col in df.columns:
        if df[col].dtype == 'object':
            df[col] = pd.to_numeric(df[col].str.replace(',', '.'), errors='coerce')

# Gestion de la Sévérité (Valeur par défaut 0.4 si absente)
if 'SEVERITE' not in df.columns:
    print("ℹ️ Colonne 'SEVERITE' absente, utilisation de la valeur standard 0.4")
    df['SEVERITE'] = 0.4

# Recalcul du PML si nécessaire
if 'PML' not in df.columns or df['PML'].isnull().all():
    df['PML'] = df['CAPITAL_ASSURE'] * df['COEFF_A'] * df['SEVERITE']

# --- 2. ANALYSE D'EXPOSITION (Finalité : Mesurer l'adéquation) ---
exposure_summary = df.groupby('ZONE_RPA').agg(
    Nombre_Contrats=('PRIME_NETTE', 'count'),
    Capital_Expose=('CAPITAL_ASSURE', 'sum'),
    PML_Total=('PML', 'sum'),
    Primes_Totatles=('PRIME_NETTE', 'sum')
).reset_index()

# Ratio de couverture : Prime collectée par rapport au risque pris (PML)
exposure_summary['Ratio_Securite'] = (exposure_summary['Primes_Totatles'] / exposure_summary['PML_Total']) * 100
# Poids du risque dans le portefeuille total
total_pml = exposure_summary['PML_Total'].sum()
exposure_summary['Part_Risque_%'] = (exposure_summary['PML_Total'] / total_pml) * 100

# --- 3. IDENTIFICATION CONCENTRATION (Finalité : Zones d'assainissement) ---
def identifier_zone(row):
    if row['Part_Risque_%'] > 35:
        return "🔥 SURCONCENTRATION (Action : Réduire l'exposition)"
    elif row['Part_Risque_%'] < 10:
        return "❄️ SOUS-CONCENTRATION (Action : Développement commercial)"
    else:
        return "⚖️ ÉQUILIBRÉ"

exposure_summary['Strategie'] = exposure_summary.apply(identifier_zone, axis=1)

print("📋 SYNTHÈSE STRATÉGIQUE DU PORTEFEUILLE")
print("=" * 100)
print(exposure_summary.to_string(index=False))
print("=" * 100)

# --- 4. TOP 10 COMMUNES À ASSAINIR ---
# (Où la perte maximale possible est la plus élevée)
top_risques = df.groupby(['WILAYA', 'COMMUNE'])['PML'].sum().reset_index()
top_risques = top_risques.sort_values('PML', ascending=False).head(10)

print("\n📍 TOP 10 DES POINTS DE CONCENTRATION (COMMUNES) :")
print(top_risques.to_string(index=False))