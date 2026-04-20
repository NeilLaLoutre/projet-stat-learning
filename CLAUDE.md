# Projet Statistical Learning — Prédiction de la courbe des taux US

## Contexte académique

- **Cours** : Statistical Learning, M1 Mathématiques et Applications (Statistiques)
- **Institution** : Université Paris Dauphine
- **Type de problème** : régression supervisée sur données réelles (séries temporelles)
- **Deadline** : vendredi 15 mai 2026, 23h59 (envoi à comminges@ceremade.dauphine.fr)
- **Groupe** : 4 étudiants
- **Livrables** : 1 rapport PDF + 1 notebook Jupyter
- **Nommage imposé** : `Subject1_Nom1_Nom2_Nom3_Nom4.pdf` et `.ipynb`

## Sujet

Prédiction de la courbe des taux US Treasury. Comparaison d'au moins deux méthodes de régression sur données FRED, avec justification statistique des choix.

### Variable cible (à finaliser au démarrage)
Deux candidats, à trancher en phase 1 :
- rendement du 10 ans à horizon 1 mois (`DGS10_{t+21}`)
- variation du spread 10Y–2Y à horizon 1 mois

### Covariables
- Reste de la courbe : DGS1MO, DGS3MO, DGS6MO, DGS1, DGS2, DGS5, DGS30
- Macro : CPI, chômage, Fed Funds, production industrielle, spread T10Y2Y
- Features dérivées : momentum 10Y, pente, courbure
- Cible : 10 à 15 variables au total

## Source de données

FRED (Federal Reserve Bank of St. Louis), via `pandas-datareader` ou l'API FRED.
Données quotidiennes depuis 1976 pour la majorité des maturités.

## Méthodes à comparer

1. **OLS** — baseline obligatoire
2. **Ridge** — justifiée par la multicolinéarité forte entre maturités
3. **PCR ou PLS** — exploite la structure factorielle (Nelson–Siegel : 3 facteurs ≈ 99% de variance)
4. *Optionnel* : Lasso, ou régression Nelson–Siegel explicite (niveau/pente/courbure)

## Règles méthodologiques NON-NÉGOCIABLES

1. **Split train/test figé AVANT toute décision basée sur les données.** Tout preprocessing dérivé des données se fait sur le train uniquement.
2. **Toujours utiliser `sklearn.pipeline.Pipeline`** pour preprocessing + modèle. Jamais de fit manuel hors pipeline.
3. **Validation croisée temporelle** : `TimeSeriesSplit`, jamais de k-fold naïf.
4. **Le test set ne sert qu'UNE fois**, pour l'évaluation finale. Jamais pour la sélection de modèle ou le tuning.
5. **Toujours une baseline OLS avant tout modèle complexe.** Si un modèle ne bat pas la baseline, il n'a pas sa place dans le rapport.
6. **Stationnarité** : travailler sur les variations (`.diff()`) des taux, pas les niveaux bruts. À justifier par un test ADF.
7. **Random seed fixé** (`random_state=42`) partout (split, CV, modèles stochastiques).
8. **Pas de data leakage temporel** : toute feature à la date `t` doit n'utiliser que des informations strictement antérieures ou contemporaines à `t`.

## Métriques

- **RMSE** (primaire)
- **MAE** (secondaire, plus robuste aux outliers)
- **R² out-of-sample** (à commenter, mais pas décisif)

Définir mathématiquement chaque métrique dans le rapport final (exigence explicite du PDF d'instructions du cours).

## Conventions de code

- **Langage** : Python 3.11+
- **Librairies autorisées** : pandas, numpy, matplotlib, scikit-learn, seaborn (si nécessaire), pandas-datareader, scipy, statsmodels (pour les tests de stationnarité)
- **Style** : fonctions modulaires et courtes, docstrings sur les fonctions publiques, notebooks découpés par phase
- **Reproductibilité** : tout notebook doit tourner top-to-bottom sans intervention manuelle (`Kernel → Restart & Run All`)
- **Outputs des notebooks** : ne pas commiter les cellules exécutées (utiliser nbstripout en hook Git)

## Structure du repo

```
.
├── CLAUDE.md
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/          # données brutes FRED (gitignored si lourdes)
│   └── processed/    # données après preprocessing
├── notebooks/
│   ├── 01_data_loading.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_preprocessing.ipynb
│   ├── 04_baseline_ols.ipynb
│   ├── 05_ridge_pcr.ipynb
│   ├── 06_evaluation.ipynb
│   └── final_submission.ipynb   # notebook fusionné pour rendu
├── src/
│   ├── __init__.py
│   ├── data.py             # chargement FRED
│   ├── preprocessing.py    # pipelines sklearn
│   ├── models.py           # définitions modèles
│   └── evaluation.py       # métriques et CV temporelle
├── figures/
└── report/
```

## Répartition des rôles (groupe de 4)

- **A — Data Lead** : chargement FRED, nettoyage, pipeline preprocessing, split train/test figé
- **B — EDA & Visualization** : stats descriptives, ACF/PACF, corrélations, stationnarité, toutes les figures
- **C — Modeling & Validation** : baseline OLS, Ridge, PCR/PLS, tuning par `TimeSeriesSplit`, comparaison finale
- **D — Integration & Report** : assemblage du notebook final, rédaction du rapport PDF, garant de la reproductibilité

## Préférences de réponse de Claude Code

- **Répondre en français** par défaut
- Distinguer explicitement : (1) faits certains, (2) hypothèses, (3) recommandations
- Ne pas inventer d'information sur le dataset ; dire si non vérifié
- Privilégier les solutions simples et explicables aux solutions "flashy"
- **Justifier statistiquement chaque choix** de méthode, preprocessing ou hyperparamètre
- Ne pas produire de gros blocs de code sans demande explicite ; procéder étape par étape
- Avant d'écrire du code substantiel, proposer un plan et attendre validation

## Ce qu'il ne faut PAS faire

- Ne pas utiliser XGBoost, LightGBM ni réseaux de neurones : non justifiés pour ce sujet et hors du programme M1 core
- Ne pas sur-ingénier : le jury évalue la rigueur méthodologique, pas la complexité technique
- Ne pas faire de k-fold CV naïf sur des séries temporelles
- Ne pas standardiser avant le split train/test (leakage)
- Ne pas utiliser le test set pour sélectionner ou tuner un modèle
- Ne pas inclure de variable connue ex-post ou qui encode le futur
