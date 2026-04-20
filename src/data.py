"""
Module de chargement des données FRED pour le projet de Statistical Learning.

Ce module télécharge les séries de la courbe des taux US Treasury ainsi que
les principales variables macroéconomiques depuis FRED, puis les consolide
dans un unique DataFrame quotidien sauvegardé en CSV.

Aucun preprocessing (différenciation, standardisation, features dérivées)
n'est effectué ici : ce module ne produit que des données brutes.
"""

from __future__ import annotations

import os
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from urllib.error import HTTPError, URLError

import pandas as pd
from dotenv import load_dotenv
from fredapi import Fred


# Racine du projet : resolved à partir de l'emplacement de ce fichier
# (src/data.py -> parent = src/, parent.parent = racine du projet).
# Permet de lancer le script depuis n'importe quel cwd.
PROJECT_ROOT = Path(__file__).parent.parent

# Séries de la courbe des taux US Treasury (quotidiennes, jours ouvrés).
YIELD_SERIES: List[str] = [
    "DGS1MO",
    "DGS3MO",
    "DGS6MO",
    "DGS1",
    "DGS2",
    "DGS5",
    "DGS10",
    "DGS30",
]

# Variables macroéconomiques. Mix de fréquences :
# - CPIAUCSL, UNRATE, INDPRO : mensuelles
# - FEDFUNDS : mensuelle (moyenne du taux effectif)
# - T10Y2Y : quotidienne
MACRO_SERIES: List[str] = [
    "CPIAUCSL",
    "UNRATE",
    "FEDFUNDS",
    "INDPRO",
    "T10Y2Y",
]


def _get_api_key() -> str:
    """
    Charge la clé API FRED depuis le fichier .env à la racine du projet.

    Returns
    -------
    str
        La clé API FRED.

    Raises
    ------
    ValueError
        Si la variable d'environnement FRED_API_KEY est absente ou vide.
        Le message indique comment la configurer.
    """
    load_dotenv(PROJECT_ROOT / ".env")
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise ValueError(
            "Clé API FRED introuvable. Créez un fichier .env à la racine "
            "du projet contenant :\n"
            "    FRED_API_KEY=votre_cle_ici\n"
            "Obtenez une clé gratuite sur https://fred.stlouisfed.org/docs/api/api_key.html"
        )
    return api_key


# Messages caractéristiques des erreurs HTTP transitoires (5xx) que FRED
# renvoie occasionnellement. On retente uniquement sur celles-ci, pas sur
# les erreurs client (400, 401, 403, 404) qui ne se résoudront pas toutes seules.
_TRANSIENT_MSGS = (
    "Internal Server Error",
    "Bad Gateway",
    "Service Unavailable",
    "Gateway Timeout",
)


def _is_transient(exc: Exception) -> bool:
    """Retourne True si l'exception ressemble à une erreur réseau/serveur transitoire."""
    if isinstance(exc, HTTPError):
        return exc.code in (500, 502, 503, 504)
    if isinstance(exc, URLError):
        return True
    if isinstance(exc, ValueError):
        return any(m in str(exc) for m in _TRANSIENT_MSGS)
    return False


def _get_series_with_retry(
    fred: Fred,
    ticker: str,
    start_date: str,
    end_date: str,
    max_attempts: int = 4,
) -> pd.Series:
    """
    Télécharge une série FRED avec backoff exponentiel sur erreur transitoire.

    Attente entre tentatives : 2s, 4s, 8s. Les erreurs non-transitoires
    (clé invalide, ticker inconnu, etc.) sont propagées immédiatement.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            return fred.get_series(
                ticker,
                observation_start=start_date,
                observation_end=end_date,
            )
        except Exception as exc:
            if attempt == max_attempts or not _is_transient(exc):
                raise
            delay = 2 ** attempt
            print(f"  [!] {ticker}: {type(exc).__name__} ({exc}). "
                  f"Retry {attempt}/{max_attempts - 1} dans {delay}s...")
            time.sleep(delay)


def load_fred_series(
    series_ids: List[str],
    start_date: str,
    end_date: str,
    api_key: str,
) -> pd.DataFrame:
    """
    Télécharge une liste de séries FRED et les concatène en un DataFrame.

    Chaque série est récupérée à sa fréquence native (quotidienne pour les
    taux, mensuelle pour la plupart des macros). Aucune harmonisation de
    fréquence n'est effectuée à ce stade : la sortie est brute.

    Les appels API passent par un wrapper avec retries (4 tentatives max,
    backoff exponentiel) pour tolérer les erreurs 5xx transitoires de FRED.

    Parameters
    ----------
    series_ids : list of str
        Identifiants FRED des séries à télécharger (ex. "DGS10", "CPIAUCSL").
    start_date : str
        Date de début au format "YYYY-MM-DD".
    end_date : str
        Date de fin au format "YYYY-MM-DD".
    api_key : str
        Clé API FRED.

    Returns
    -------
    pd.DataFrame
        DataFrame indexé par date, une colonne par série (nom = ticker FRED).
        Les NaN sont conservés tels quels.
    """
    fred = Fred(api_key=api_key)
    series_dict: dict[str, pd.Series] = {}

    for ticker in series_ids:
        print(f"Téléchargement de {ticker}...")
        s = _get_series_with_retry(fred, ticker, start_date, end_date)
        s.name = ticker
        series_dict[ticker] = s

    df = pd.concat(series_dict.values(), axis=1, sort=False)
    df.columns = list(series_dict.keys())
    df.index.name = "date"
    return df


def build_dataset(
    start_date: str = "1990-01-01",
    end_date: Optional[str] = None,
    save_path: str = "data/raw/fred_data.csv",
) -> pd.DataFrame:
    """
    Orchestre le téléchargement, la consolidation et la sauvegarde des données FRED.

    Pipeline :
    1. Télécharge les séries définies dans YIELD_SERIES + MACRO_SERIES.
    2. Reindex sur un calendrier de jours ouvrés (pd.bdate_range) : plus
       fidèle aux données de marché que le calendaire et évite les NaN
       systématiques du weekend.
    3. Applique un forward-fill UNIQUEMENT sur les variables macro mensuelles.
       Justification : ces séries (CPI, UNRATE, etc.) ne sont publiées qu'une
       fois par mois, et la valeur la plus récente reste "l'information
       disponible" jusqu'à la publication suivante. Les taux gardent leurs
       NaN natifs (jours fériés, données manquantes) pour rester visibles
       à l'EDA.

    Parameters
    ----------
    start_date : str, default "1990-01-01"
        Date de début au format "YYYY-MM-DD".
    end_date : str or None, default None
        Date de fin. Si None, utilise la date d'aujourd'hui.
    save_path : str, default "data/raw/fred_data.csv"
        Chemin de sauvegarde, relatif à la racine du projet.

    Returns
    -------
    pd.DataFrame
        DataFrame quotidien (jours ouvrés) indexé par date, avec une colonne
        par série FRED.
    """
    if end_date is None:
        end_date = datetime.today().strftime("%Y-%m-%d")

    api_key = _get_api_key()

    all_series = YIELD_SERIES + MACRO_SERIES
    print(f"Téléchargement de {len(all_series)} séries FRED "
          f"de {start_date} à {end_date}.")
    df = load_fred_series(all_series, start_date, end_date, api_key)

    # Reindex sur les jours ouvrés pour uniformiser la fréquence.
    business_days = pd.bdate_range(start=start_date, end=end_date, name="date")
    df = df.reindex(business_days)

    # Forward-fill sélectif sur les macros uniquement.
    df[MACRO_SERIES] = df[MACRO_SERIES].ffill()

    print(f"Consolidation : {df.shape[0]} observations, {df.shape[1]} colonnes.")

    # Résolution du chemin absolu par rapport à la racine du projet.
    output_path = PROJECT_ROOT / save_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path)
    print(f"Sauvegardé dans {save_path}")

    return df


if __name__ == "__main__":
    df = build_dataset()

    print("\n" + "=" * 60)
    print("Résumé du dataset")
    print("=" * 60)
    print(f"Période couverte : {df.index.min().date()} -> {df.index.max().date()}")
    print(f"Shape            : {df.shape[0]} lignes x {df.shape[1]} colonnes")
    print("\nPourcentage de NaN par colonne :")
    nan_pct = (df.isna().mean() * 100).round(2).sort_values(ascending=False)
    for col, pct in nan_pct.items():
        print(f"  {col:10s} : {pct:6.2f} %")
