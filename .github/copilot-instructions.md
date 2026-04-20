# Copilot instructions for projet-stat-learning

## Objectif principal
Ce repo est un projet académique de régression supervisée pour la prédiction de la courbe des taux US Treasury. L'AI doit privilégier la simplicité, la reproductibilité et les règles de validation temporelle décrites dans `CLAUDE.md`.

## Architecture minimale
- `src/data.py` est la seule implémentation Python existante. Il télécharge et consolide les séries FRED dans `data/raw/fred_data.csv`.
- Le module est conçu pour être lancé depuis n'importe quel dossier grâce à `PROJECT_ROOT = Path(__file__).parent.parent`.
- Le code de chargement est brut : aucune transformation, différenciation ou normalisation n'est faite dans `src/data.py`.

## Flux de données clé
1. `src/data.py` lit `FRED_API_KEY` depuis `.env` à la racine.
2. Il télécharge les séries listées dans `YIELD_SERIES` et `MACRO_SERIES` via `fredapi`.
3. Il réindexe les données sur un calendrier de jours ouvrés avec `pd.bdate_range`.
4. Il applique un `ffill()` uniquement aux variables macro mensuelles.
5. Il sauvegarde le résultat dans `data/raw/fred_data.csv`.

## Commandes et workflow de développement
- Initialisation : `python -m venv .venv` puis `.venv\Scripts\activate`
- Installation : `pip install -r requirements.txt`
- Créer/donner des données brutes : `python src/data.py`
- Ouvrir un environnement interactif : `jupyter lab`

## Conventions spécifiques au projet
- Le projet est construit autour d'une pipeline série temporelle. Ne pas utiliser de validation croisée classique `KFold` pour les modèles temporels.
- La règle métier impose `random_state=42` partout : split, CV, modèle stochastique.
- Toujours préférer `sklearn.pipeline.Pipeline` pour le preprocessing + modèle.
- Ne pas standardiser les données avant le split train/test.
- Le jeu de test doit rester figé et ne doit servir qu'à l'évaluation finale.
- Ne pas inclure de notebook exécuté dans le contrôle de version ; le `.gitignore` ignore les résultats Jupyter.

## Points d'attention et hypotheses
- `CLAUDE.md` contient les règles méthodologiques du cours et les contraintes du projet (OLS baseline, Ridge, PCR/PLS, métriques RMSE/MAE/R², pas de XGBoost/NN).
- Il n'y a pas de notebooks présents pour l'instant, donc l'AI doit éviter de supposer qu'une structure `notebooks/` existe.
- La présence de `.env` et `FRED_API_KEY` est nécessaire pour l'extraction des données.

## Ce qu'il faut éviter
- Ne pas écrire de code de preprocessing dans `src/data.py` si l'on ajoute des transformations : ce module doit rester dédié à la collecte et à la consolidation brute.
- Ne pas modifier les noms de colonnes `YIELD_SERIES / MACRO_SERIES` sans raison, car ils servent de contrat pour le chargement des données.
- Ne pas ignorer les règles de non-leakage temporel décrites dans `CLAUDE.md`.

## Fichiers à consulter en priorité
- `CLAUDE.md` pour les règles méthodologiques et les attentes de l'enseignant.
- `README.md` pour les étapes de reproduction et le contexte général.
- `src/data.py` pour le flux d'ingestion de données FRED.
- `requirements.txt` pour les dépendances autorisées.

> Si tu as besoin d'une section plus précise sur le pipeline d'entraînement ou la validation temporelle, demande-moi avant de générer du code.