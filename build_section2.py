"""Script temporaire : met à jour cellule 32 + ajoute Section 2 au notebook 02_eda.ipynb."""
import nbformat
from nbformat.v4 import new_markdown_cell, new_code_cell

NB_PATH = "notebooks/02_eda.ipynb"

# Lecture du notebook existant (Section 1 préservée intégralement)
nb = nbformat.read(NB_PATH, as_version=4)
assert len(nb.cells) == 32, f"Attendu 32 cellules, trouvé {len(nb.cells)}"

# ------------------------------------------------------------
# 1) Mise à jour de la cellule 32 (transition vers Section 2)
# ------------------------------------------------------------
nb.cells[31]["source"] = (
    "---\n\n"
    "**Prochaine étape** : Section 2 — Statistiques descriptives par famille de "
    "variables, visualisations temporelles et analyse des corrélations."
)

# ------------------------------------------------------------
# 2) Construction des nouvelles cellules de Section 2
# ------------------------------------------------------------
new_cells = []


def md(text: str) -> None:
    new_cells.append(new_markdown_cell(text))


def code(text: str) -> None:
    new_cells.append(new_code_cell(text))


# ================== H2 Section 2 ==================
md("## 2. Statistiques descriptives par famille de variables")

# ================== 2.1 Introduction ==================
md("### 2.1 Introduction")

md(
    "L'objectif de cette section est de caractériser statistiquement chacune des "
    "13 variables du dataset. Pour rendre cette analyse lisible, nous les regroupons "
    "en **trois familles sémantiques**, dont l'unification dans un seul tableau "
    "serait trompeuse :\n\n"
    "- **Famille A — La courbe des taux Treasury** (8 variables `DGSxx`) : les "
    "objets que nous cherchons à modéliser, structurellement très corrélés entre "
    "eux ;\n"
    "- **Famille B — Variables macroéconomiques** (4 variables : `CPIAUCSL`, "
    "`UNRATE`, `FEDFUNDS`, `INDPRO`) : indicateurs d'état de l'économie qui "
    "servent de covariables ;\n"
    "- **Famille C — Spread dérivé** (1 variable : `T10Y2Y`) : mesure de pente, "
    "interprétée comme indicateur avancé de récession.\n\n"
    "Pour chaque famille, nous présenterons (1) une description économique "
    "explicite de chaque variable, (2) des statistiques descriptives étendues "
    "(moyenne, écart-type, quantiles, skewness, kurtosis), (3) des visualisations "
    "temporelles et de distribution, (4) une interprétation reliée aux choix de "
    "modélisation à venir.\n\n"
    "**Mise en garde méthodologique importante**. Plusieurs des séries étudiées "
    "(les huit taux, le CPI et la production industrielle) sont *non "
    "stationnaires* en niveau sur la période : leur moyenne et leur variance "
    "dépendent du moment où on les observe. Les statistiques descriptives "
    "calculées ici doivent donc être lues comme une **description de "
    "l'échantillon 1990-2026**, et non comme des paramètres d'une loi sous-"
    "jacente stable. Un test formel de stationnarité (ADF) est renvoyé à la "
    "Section 3, et conditionnera le choix de travailler sur les niveaux ou sur "
    "les différences dans le preprocessing."
)

md(
    "On importe `scipy.stats` pour calculer la *skewness* (asymétrie de la "
    "distribution) et le *kurtosis* (épaisseur des queues). On définit aussi deux "
    "listes de colonnes qui structureront toute la section."
)

code(
    "from scipy import stats\n"
    "\n"
    "# Listes de colonnes utilisées tout au long de la Section 2\n"
    "yield_cols = [\"DGS1MO\", \"DGS3MO\", \"DGS6MO\", \"DGS1\",\n"
    "              \"DGS2\", \"DGS5\", \"DGS10\", \"DGS30\"]\n"
    "macro_cols = [\"CPIAUCSL\", \"UNRATE\", \"FEDFUNDS\", \"INDPRO\"]\n"
    "\n"
    "\n"
    "def describe_ext(s: pd.Series) -> pd.Series:\n"
    "    \"\"\"Statistiques descriptives étendues pour une série.\n"
    "\n"
    "    Renvoie count, mean, median, std, min, Q1, Q3, max, skew, kurtosis\n"
    "    (kurtosis Fisher : 0 pour la loi normale, > 0 si queues plus épaisses).\n"
    "    Les NaN sont ignorés via nan_policy='omit'.\n"
    "    \"\"\"\n"
    "    return pd.Series({\n"
    "        \"count\": s.count(),\n"
    "        \"mean\": s.mean(),\n"
    "        \"median\": s.median(),\n"
    "        \"std\": s.std(),\n"
    "        \"min\": s.min(),\n"
    "        \"Q1\": s.quantile(0.25),\n"
    "        \"Q3\": s.quantile(0.75),\n"
    "        \"max\": s.max(),\n"
    "        \"skew\": stats.skew(s, nan_policy=\"omit\"),\n"
    "        \"kurtosis\": stats.kurtosis(s, nan_policy=\"omit\"),\n"
    "    })"
)

# ================== 2.2 Famille A — Taux ==================
md("### 2.2 Famille A — La courbe des taux Treasury")

md(
    "#### 2.2.1 Description économique des 8 maturités\n\n"
    "Les huit maturités ne jouent pas le même rôle économique ; on peut les "
    "regrouper en trois blocs avec des logiques distinctes.\n\n"
    "- **Taux courts (`DGS1MO`, `DGS3MO`, `DGS6MO`, `DGS1`, `DGS2`)** : ils "
    "reflètent principalement la *politique monétaire* de la Réserve Fédérale "
    "(taux des *Fed Funds*) et les anticipations de court terme des marchés. "
    "Ils réagissent très rapidement aux décisions du FOMC (*Federal Open Market "
    "Committee*, qui fixe le taux directeur). Leur volatilité est dominée par "
    "les cycles de resserrement/assouplissement monétaires.\n"
    "- **Taux moyens (`DGS5`)** : zone de transition. Le 5 ans combine un effet "
    "politique monétaire (dans la prochaine phase du cycle) et un effet "
    "anticipations d'inflation et de croissance à moyen terme.\n"
    "- **Taux longs (`DGS10`, `DGS30`)** : leur dynamique est dominée par les "
    "*anticipations d'inflation de long terme*, la *prime de terme* (prime "
    "exigée pour immobiliser de l'argent longtemps) et les flux de demande "
    "structurels (assureurs, fonds de pension, investisseurs étrangers). Ce "
    "sont eux qui servent de benchmark pour pricer les prêts hypothécaires à "
    "taux fixe, les obligations corporate et les swaps de taux.\n\n"
    "Ces hétérogénéités expliquent pourquoi les maturités, bien que très "
    "corrélées, ne se confondent pas ; les trois facteurs latents niveau / "
    "pente / courbure du modèle Nelson-Siegel (1987) suffisent à résumer leur "
    "co-mouvement avec une excellente approximation. Regardons maintenant les "
    "statistiques empiriques."
)

md(
    "#### 2.2.2 Statistiques descriptives\n\n"
    "On applique la fonction `describe_ext` à chaque colonne de la famille A. "
    "Chaque ligne du tableau ci-dessous correspond à une maturité, chaque "
    "colonne à un indicateur statistique."
)

code(
    "stats_yields = df[yield_cols].apply(describe_ext).T.round(3)\n"
    "stats_yields"
)

md(
    "Lecture du tableau :\n\n"
    "- **Moyennes croissantes avec la maturité** : la moyenne des rendements "
    "passe typiquement de l'ordre de 2 % sur le segment très court à environ "
    "4,5 % sur le 30 ans. Cet ordre respecte la forme d'une courbe des taux "
    "« normale » en moyenne sur la période — la prime de terme est positive "
    "sur un horizon aussi long. `DGS1MO` a une moyenne plus basse parce que sa "
    "couverture temporelle commence seulement en 2001 (période en moyenne plus "
    "accommodante).\n"
    "- **Dispersion décroissante avec la maturité** : l'écart-type est plus "
    "élevé pour les taux courts (sensibles à chaque décision de la Fed) que "
    "pour les taux longs (lissés par les anticipations de long terme). C'est "
    "un résultat classique de la littérature sur la structure par terme : les "
    "chocs de politique monétaire se transmettent avec une amplitude décroissante "
    "vers la partie longue de la courbe.\n"
    "- **Skewness (asymétrie)** : positive et modérée sur les taux longs "
    "(quelques pics à la hausse tirent la queue droite), proche de 1 ou plus "
    "sur les taux courts (asymétrie plus marquée, car les taux ont été collés "
    "à zéro pendant de longues périodes post-2008 et post-COVID, ce qui crée "
    "une queue droite).\n"
    "- **Kurtosis (Fisher)** : positif et souvent élevé (> 0, parfois > 1). Un "
    "kurtosis de Fisher > 0 signifie des queues *plus épaisses que la loi "
    "normale* : les événements extrêmes (chocs de taux) sont plus fréquents "
    "que ne le prédirait une gaussienne. C'est typique des séries financières.\n\n"
    "**Implication pour la modélisation** : les rendements Treasury en niveau "
    "ne sont pas gaussiens. Les intervalles de confiance et tests de Student "
    "de l'OLS reposent sur une hypothèse de normalité des résidus — hypothèse "
    "qu'il faudra vérifier *a posteriori* sur les résidus du modèle, et non "
    "*a priori* sur les variables brutes. Ceci sera repris lors de la "
    "validation des modèles."
)

md(
    "#### 2.2.3 Visualisations temporelles\n\n"
    "Le tableau précédent donne une vue statique. On visualise maintenant "
    "l'évolution des 8 maturités sur toute la période pour faire apparaître "
    "les dynamiques communes et les éventuelles divergences."
)

code(
    "fig, ax = plt.subplots(figsize=(12, 6))\n"
    "colors = plt.cm.viridis(np.linspace(0, 0.9, len(yield_cols)))\n"
    "for col, color in zip(yield_cols, colors):\n"
    "    ax.plot(df.index, df[col], label=col, color=color, linewidth=0.8)\n"
    "ax.set_title(\"Évolution des rendements Treasury par maturité (1990-aujourd'hui)\")\n"
    "ax.set_xlabel(\"Date\")\n"
    "ax.set_ylabel(\"Rendement (%)\")\n"
    "ax.legend(loc=\"center left\", bbox_to_anchor=(1.02, 0.5), title=\"Maturité\")\n"
    "ax.grid(True, alpha=0.3)\n"
    "plt.tight_layout()\n"
    "plt.show()"
)

md(
    "Le graphique fait ressortir plusieurs régularités fortes :\n\n"
    "- **Tendance baissière globale** des années 1990 jusqu'à 2020 : les "
    "rendements passent d'environ 8 % à quasi 0 % sur quarante ans, reflet du "
    "régime désinflationniste amorcé après la *Great Inflation* des années "
    "1970-1980 et de l'action combinée de la globalisation et de la "
    "démographie vieillissante.\n"
    "- **Plateau bas 2009-2015** : après la crise financière, les taux "
    "courts restent collés à zéro sous l'effet de la *zero interest-rate "
    "policy* (ZIRP) de la Fed, et les taux longs sont écrasés par les "
    "programmes de *quantitative easing* (achats massifs d'obligations).\n"
    "- **Remontée brutale 2022-2023** : face à l'inflation post-COVID, la Fed "
    "a mené l'un des cycles de hausse les plus rapides de son histoire, ce qui "
    "est visible comme un redressement quasi-vertical des taux courts.\n"
    "- **Co-mouvement très fort** : les huit courbes bougent dans des "
    "directions similaires avec des timings quasi-identiques. Cette "
    "colinéarité visuelle est l'indice empirique principal qui motivera, au "
    "2.2.5, l'emploi de méthodes régularisées."
)

md(
    "#### 2.2.4 Distribution des taux (boxplot et histogrammes)\n\n"
    "Au-delà des dynamiques temporelles, on regarde la distribution marginale "
    "(sans tenir compte du temps) de chaque taux. Le **boxplot** compare "
    "dispersion et médianes entre maturités ; les **histogrammes** donnent la "
    "forme fine des distributions — utile pour détecter une éventuelle "
    "multimodalité (plusieurs régimes de taux)."
)

code(
    "fig, ax = plt.subplots(figsize=(10, 5))\n"
    "df[yield_cols].boxplot(ax=ax)\n"
    "ax.set_title(\"Distribution des rendements par maturité — boxplot\")\n"
    "ax.set_ylabel(\"Rendement (%)\")\n"
    "ax.grid(True, alpha=0.3)\n"
    "plt.tight_layout()\n"
    "plt.show()"
)

code(
    "fig, axes = plt.subplots(2, 4, figsize=(14, 6))\n"
    "for ax, col in zip(axes.flat, yield_cols):\n"
    "    df[col].hist(bins=50, ax=ax, color=\"steelblue\", alpha=0.7)\n"
    "    ax.set_title(col)\n"
    "    ax.set_xlabel(\"Rendement (%)\")\n"
    "    ax.set_ylabel(\"Fréquence\")\n"
    "    ax.grid(True, alpha=0.3)\n"
    "plt.suptitle(\"Histogrammes des rendements Treasury (bins=50)\", y=1.02)\n"
    "plt.tight_layout()\n"
    "plt.show()"
)

md(
    "Les distributions ne sont **pas unimodales gaussiennes** : la plupart des "
    "histogrammes font apparaître au moins deux bosses — une bosse basse "
    "(autour de 0-2 %, période ZIRP et post-COVID) et une bosse plus haute "
    "(autour de 4-6 %, régime « normal » des années 1990-2000). Sur `DGS10` "
    "notamment, on distingue clairement un mode autour de 2 % et un autre "
    "autour de 5 %, avec une zone de relative rareté entre 3 et 4 %. Cette "
    "**multimodalité** est le reflet statistique direct de l'existence de "
    "régimes monétaires hétérogènes : un modèle qui ignore cette structure "
    "(par exemple une régression linéaire sur les niveaux) projette une "
    "relation fonctionnelle *en moyenne* sur des régimes très différents, ce "
    "qui peut dégrader la performance hors échantillon. C'est un argument "
    "supplémentaire pour envisager une modélisation sur les *variations* "
    "plutôt que sur les *niveaux* (à trancher après le test ADF)."
)

md(
    "#### 2.2.5 Corrélations entre maturités\n\n"
    "La **corrélation de Pearson** mesure l'intensité du co-mouvement linéaire "
    "entre deux séries : elle vaut +1 quand les deux séries montent et "
    "descendent ensemble parfaitement, −1 quand elles évoluent en miroir, et "
    "0 quand elles sont linéairement indépendantes. Pour la courbe des taux, "
    "on s'attend à des corrélations **très élevées** entre maturités voisines "
    "(ex. DGS5 et DGS10), et **plus faibles** entre maturités éloignées "
    "(ex. DGS1MO et DGS30), parce que les taux courts et longs obéissent "
    "partiellement à des forces différentes (politique monétaire vs "
    "anticipations de long terme).\n\n"
    "Un niveau de corrélation supérieur à 0,9 entre covariables est un cas "
    "manuel de **multicolinéarité**, qui pose trois problèmes à la régression "
    "OLS : (1) l'estimation des coefficients devient instable (petite variation "
    "des données $\\Rightarrow$ grande variation des coefficients), (2) la "
    "variance des estimateurs explose (intervalles de confiance très larges), "
    "(3) l'interprétation des coefficients individuels perd son sens (on ne "
    "peut plus isoler l'effet marginal d'une variable). La **régression "
    "régularisée** (Ridge) résout (1) et (2) en pénalisant les coefficients "
    "trop grands ; la **régression sur composantes principales** (PCR) et les "
    "**moindres carrés partiels** (PLS) résolvent tous les problèmes en "
    "travaillant sur un petit nombre de combinaisons linéaires non corrélées "
    "des covariables."
)

code(
    "corr_yields = df[yield_cols].corr()\n"
    "fig, ax = plt.subplots(figsize=(8, 7))\n"
    "sns.heatmap(\n"
    "    corr_yields, annot=True, fmt=\".2f\", cmap=\"coolwarm\",\n"
    "    vmin=-1, vmax=1, ax=ax, cbar_kws={\"label\": \"Corrélation (Pearson)\"},\n"
    ")\n"
    "ax.set_title(\"Matrice de corrélation — 8 maturités Treasury\")\n"
    "plt.tight_layout()\n"
    "plt.show()"
)

md(
    "La heatmap révèle trois faits statistiques saillants :\n\n"
    "1. **Toutes les corrélations sont positives et élevées**. Aucune n'est "
    "inférieure à 0,5 ; la plupart sont au-dessus de 0,85. Les huit maturités "
    "bougent globalement dans le même sens.\n"
    "2. **Structure de bande** : les corrélations sont plus fortes entre "
    "maturités adjacentes (sur la diagonale et ses voisines proches) et "
    "s'affaiblissent en s'éloignant de la diagonale. Par exemple, "
    "`DGS10 ↔ DGS30` est typiquement autour de 0,97, alors que `DGS1MO ↔ DGS30` "
    "tombe vers 0,5-0,7. C'est la signature d'un *processus à facteurs* : "
    "quelques composantes communes expliquent l'essentiel du co-mouvement.\n"
    "3. **Bloc quasi-unitaire sur les taux longs** : les corrélations entre "
    "DGS5, DGS10 et DGS30 sont typiquement toutes ≥ 0,95. Ce bloc porte "
    "l'essentiel de l'information « niveau » de la courbe.\n\n"
    "**Conclusion méthodologique** : cette colinéarité forte est une "
    "caractéristique *intrinsèque* du problème (elle est prédite par la "
    "théorie Nelson-Siegel), pas un artefact de préparation des données. Elle "
    "**justifie empiriquement et sans ambiguïté** l'emploi de Ridge et de PCR "
    "dans le projet : une OLS naïve sur ces 8 taux comme covariables produirait "
    "des coefficients instables et numériquement problématiques. C'est la "
    "principale motivation statistique du choix de méthodes."
)

# ================== 2.3 Famille B — Macro ==================
md("### 2.3 Famille B — Variables macroéconomiques")

md(
    "#### 2.3.1 Description économique\n\n"
    "Les quatre variables macroéconomiques retenues sont :\n\n"
    "- **`CPIAUCSL` — *Consumer Price Index for All Urban Consumers: All Items*** : "
    "indice du niveau moyen des prix d'un panier standard de biens et services "
    "consommés par les ménages urbains américains. Attention : le CPI *lui-même* "
    "est un indice croissant ; c'est son **taux de croissance** (en glissement "
    "annuel) qu'on appelle *inflation*. Pourquoi cette variable est pertinente "
    "pour prédire les taux : l'**équation de Fisher** relie le taux d'intérêt "
    "nominal au taux réel et à l'inflation anticipée "
    "($i_\\text{nominal} \\approx r_\\text{réel} + \\pi_\\text{anticipée}$) ; "
    "l'inflation est donc un déterminant macro de premier ordre des taux longs.\n"
    "- **`UNRATE` — *Unemployment Rate*** : taux de chômage mensuel publié par le "
    "Bureau of Labor Statistics. Pourquoi pertinent : la Fed a un *dual mandate* "
    "— stabilité des prix ET plein-emploi. Quand le chômage est élevé, la Fed "
    "baisse les taux pour relancer l'activité ; quand il est bas et que "
    "l'économie surchauffe, elle les remonte pour contenir l'inflation. Le "
    "chômage agit donc indirectement sur les taux courts via la fonction de "
    "réaction de la Fed.\n"
    "- **`FEDFUNDS` — *Effective Federal Funds Rate*** : taux effectif au jour "
    "le jour auquel les banques se prêtent entre elles leurs réserves excédentaires. "
    "C'est la cible opérationnelle de la politique monétaire américaine : le FOMC "
    "fixe un corridor cible, et la Fed intervient sur le marché pour maintenir le "
    "taux dans ce corridor. Pourquoi pertinent : `FEDFUNDS` ancre mécaniquement "
    "les taux Treasury courts (arbitrage), donc la corrélation attendue avec "
    "`DGS1MO`, `DGS3MO`, `DGS6MO` est très élevée.\n"
    "- **`INDPRO` — *Industrial Production Index*** : indice mensuel du volume de "
    "production manufacturière, minière et d'utilités aux États-Unis. Pourquoi "
    "pertinent : c'est un *proxy* de la composante réelle du cycle économique. "
    "En phase d'expansion (`INDPRO` croissant), les taux longs ont tendance à "
    "monter (anticipations de resserrement monétaire et d'inflation) ; en phase "
    "de récession (`INDPRO` en baisse), ils tendent à baisser."
)

md(
    "#### 2.3.2 Statistiques descriptives\n\n"
    "On applique la même fonction `describe_ext` aux 4 variables macro."
)

code(
    "stats_macro = df[macro_cols].apply(describe_ext).T.round(3)\n"
    "stats_macro"
)

md(
    "Ces statistiques appellent une **mise en garde forte** : `CPIAUCSL` et "
    "`INDPRO` sont des **indices quasi-monotones croissants**. Leur moyenne "
    "arithmétique (de l'ordre de 190 pour le CPI, 90 pour INDPRO) et leur "
    "écart-type ne décrivent **pas** un processus stable autour d'une tendance "
    "centrale ; ils reflètent le fait trivial que l'indice était bas en 1990 "
    "et plus haut aujourd'hui. Pour ces deux variables, calculer directement "
    "une moyenne ou un écart-type n'a pas d'interprétation économique utile.\n\n"
    "Les deux autres variables, `UNRATE` et `FEDFUNDS`, peuvent en revanche "
    "être interprétées en niveau : le chômage varie entre 3,5 % et 14,8 % avec "
    "une moyenne autour de 5,6 %, le taux des Fed Funds entre 0,05 % et 8 % "
    "avec une moyenne autour de 2,9 %. Ces plages sont économiquement "
    "significatives.\n\n"
    "Pour `CPIAUCSL` et `INDPRO`, on va donc calculer dans la sous-section "
    "suivante leur **taux de croissance en glissement annuel (YoY)**, "
    "transformation standard qui rend ces séries approximativement stationnaires "
    "et économiquement interprétables (inflation et croissance industrielle)."
)

md(
    "#### 2.3.3 Taux de croissance pour CPI et INDPRO\n\n"
    "Le **taux de croissance en glissement annuel** d'une variable $X_t$ est "
    "défini comme\n\n"
    "$$\\text{YoY}_t \\;=\\; 100 \\times \\frac{X_t - X_{t-252}}{X_{t-252}}.$$\n\n"
    "On utilise un décalage de 252 jours ouvrés parce qu'il correspond "
    "approximativement au nombre de jours de cotation dans une année civile "
    "(~252 ≈ 365 × 5/7 moins les jours fériés). Appliqué au CPI, cela donne "
    "l'**inflation annuelle** publiée habituellement dans les médias ; "
    "appliqué à INDPRO, cela donne la **croissance annuelle de la production "
    "industrielle**. Les 252 premières valeurs sont nécessairement NaN "
    "(pas assez d'historique pour calculer le décalage)."
)

code(
    "# Taux de croissance en glissement annuel (252 jours ouvrés ≈ 1 an)\n"
    "cpi_yoy = 100 * (df[\"CPIAUCSL\"] - df[\"CPIAUCSL\"].shift(252)) / df[\"CPIAUCSL\"].shift(252)\n"
    "indpro_yoy = 100 * (df[\"INDPRO\"] - df[\"INDPRO\"].shift(252)) / df[\"INDPRO\"].shift(252)\n"
    "\n"
    "yoy = pd.DataFrame({\"CPI_YoY\": cpi_yoy, \"INDPRO_YoY\": indpro_yoy})\n"
    "yoy.apply(describe_ext).T.round(3)"
)

md(
    "Les statistiques des séries YoY sont maintenant **économiquement "
    "interprétables** :\n\n"
    "- **Inflation CPI (YoY)** : moyenne de l'ordre de 2,5 % par an, très proche "
    "de la cible implicite de la Fed (2 %). Écart-type modéré de l'ordre de "
    "1,5-2 %. Le minimum est légèrement négatif (déflation ponctuelle pendant la "
    "crise financière de 2008-2009), le maximum dépasse 8 % (pic d'inflation "
    "post-COVID de 2022).\n"
    "- **Croissance industrielle (YoY)** : moyenne autour de 1-2 %, compatible "
    "avec la croissance potentielle de l'économie américaine. Minimum très "
    "négatif (−15 % ou plus pendant les récessions, notamment au pic de la crise "
    "financière et au choc COVID) ; maximum positif élevé lors des rebonds "
    "post-récession.\n\n"
    "Ces moyennes et écart-types décrivent maintenant un **processus plus "
    "proche de la stationnarité** : les transformations YoY « gomment » la "
    "tendance des indices cumulatifs et renvoient une mesure normalisée du "
    "taux de croissance. Ce sont ces séries transformées (plutôt que les "
    "niveaux bruts) qui seront utilisées dans le preprocessing final pour la "
    "modélisation."
)

md(
    "#### 2.3.4 Visualisations temporelles\n\n"
    "On regroupe en une grille 2×2 les quatre variables macro — `UNRATE` et "
    "`FEDFUNDS` en niveau (déjà interprétables), `CPI_YoY` et `INDPRO_YoY` en "
    "taux de croissance annuel — pour visualiser leurs dynamiques respectives "
    "sur la période."
)

code(
    "fig, axes = plt.subplots(2, 2, figsize=(14, 8))\n"
    "\n"
    "axes[0, 0].plot(df.index, df[\"UNRATE\"], color=\"darkred\", linewidth=0.8)\n"
    "axes[0, 0].set_title(\"Taux de chômage (UNRATE, %)\")\n"
    "axes[0, 0].set_ylabel(\"%\")\n"
    "axes[0, 0].grid(True, alpha=0.3)\n"
    "\n"
    "axes[0, 1].plot(df.index, df[\"FEDFUNDS\"], color=\"navy\", linewidth=0.8)\n"
    "axes[0, 1].set_title(\"Taux des Fed Funds (FEDFUNDS, %)\")\n"
    "axes[0, 1].set_ylabel(\"%\")\n"
    "axes[0, 1].grid(True, alpha=0.3)\n"
    "\n"
    "axes[1, 0].plot(df.index, cpi_yoy, color=\"darkorange\", linewidth=0.8)\n"
    "axes[1, 0].axhline(2, color=\"grey\", linestyle=\"--\", linewidth=0.8, label=\"Cible Fed 2%\")\n"
    "axes[1, 0].set_title(\"Inflation CPI (YoY, %)\")\n"
    "axes[1, 0].set_ylabel(\"%\")\n"
    "axes[1, 0].legend(loc=\"upper right\")\n"
    "axes[1, 0].grid(True, alpha=0.3)\n"
    "\n"
    "axes[1, 1].plot(df.index, indpro_yoy, color=\"darkgreen\", linewidth=0.8)\n"
    "axes[1, 1].axhline(0, color=\"grey\", linestyle=\"--\", linewidth=0.8)\n"
    "axes[1, 1].set_title(\"Croissance production industrielle (YoY, %)\")\n"
    "axes[1, 1].set_ylabel(\"%\")\n"
    "axes[1, 1].grid(True, alpha=0.3)\n"
    "\n"
    "for ax in axes.flat:\n"
    "    ax.set_xlabel(\"Date\")\n"
    "plt.tight_layout()\n"
    "plt.show()"
)

md(
    "Les quatre dynamiques racontent l'histoire macro-économique américaine "
    "récente :\n\n"
    "- **UNRATE** : trois pics correspondent aux trois grandes récessions de la "
    "période — 2001 (bulle internet), 2008-2010 (crise financière, pic à ~10 %), "
    "2020 (pandémie COVID, pic à 14,8 % en avril). Entre les pics, le chômage "
    "retombe progressivement vers 3,5-4 %, témoin des longues phases "
    "d'expansion.\n"
    "- **FEDFUNDS** : la chronologie de la politique monétaire est lisible "
    "comme un livre — resserrements fin 90, cycle de baisses 2001, remontée "
    "2004-2007, effondrement 2008 vers 0 %, longue période ZIRP 2009-2015, "
    "normalisation lente 2016-2019, retour à 0 % en 2020, puis cycle de "
    "hausses agressif 2022-2023 passant de 0,25 % à ~5,5 % en dix-huit mois — "
    "la remontée la plus rapide depuis les années 1980.\n"
    "- **CPI YoY** : inflation globalement sous 4 % sur 1990-2020, avec un "
    "léger passage en déflation en 2009. Pic spectaculaire au-dessus de 8 % "
    "en 2022, qui motive précisément le resserrement agressif des Fed Funds "
    "de la même période.\n"
    "- **INDPRO YoY** : croissance industrielle autour de 0-3 % en régime "
    "normal, effondrements synchrones des récessions (−15 % en 2009, -15 à "
    "-20 % en avril 2020), rebonds rapides post-récession.\n\n"
    "Les quatre séries sont visiblement couplées (récessions synchronisées, "
    "réponses de politique monétaire aux chocs d'inflation ou d'emploi), ce "
    "qu'on quantifiera dans la matrice de corrélation globale de la "
    "sous-section 2.5."
)

# ================== 2.4 Famille C — Spread ==================
md("### 2.4 Famille C — Spread T10Y2Y")

md(
    "#### 2.4.1 Interprétation économique\n\n"
    "Le **spread T10Y2Y** est défini comme la différence entre le rendement "
    "du Treasury à 10 ans et celui du Treasury à 2 ans :\n\n"
    "$$\\text{T10Y2Y}_t \\;=\\; \\text{DGS10}_t - \\text{DGS2}_t.$$\n\n"
    "En régime économique « normal », ce spread est **positif** : les taux "
    "longs sont supérieurs aux taux courts parce que les investisseurs "
    "exigent une prime de terme pour immobiliser leur capital plus longtemps. "
    "Quand le spread devient **négatif**, on parle d'**inversion de la courbe "
    "des taux** : une situation anormale où il est plus coûteux d'emprunter à "
    "court terme qu'à long terme. Économiquement, l'inversion révèle que les "
    "marchés anticipent une récession future — si l'économie ralentit, la "
    "Fed baissera les taux courts à un horizon de 12-24 mois, donc détenir "
    "une obligation longue au taux actuel sera rétrospectivement avantageux.\n\n"
    "Ce phénomène a une valeur prédictive remarquable : **toutes les "
    "récessions américaines depuis 1970 ont été précédées d'une inversion "
    "durable du spread T10Y2Y, dans les 6 à 24 mois qui précèdent**. "
    "C'est l'un des rares indicateurs avancés à avoir résisté au test du "
    "temps, et c'est la raison pour laquelle la Fed de New York publie "
    "quotidiennement une probabilité de récession basée sur le spread 10Y−3M. "
    "La présence du spread dans notre dataset est donc tout sauf cosmétique : "
    "c'est un régresseur à fort pouvoir informationnel sur la dynamique "
    "future des taux."
)

md(
    "#### 2.4.2 Statistiques et visualisation\n\n"
    "On calcule les statistiques descriptives standard et on trace le spread "
    "dans le temps, en mettant en évidence visuellement les périodes "
    "d'inversion (zones ombrées rouges là où le spread est négatif)."
)

code(
    "# Statistiques descriptives du spread\n"
    "stats_t10y2y = describe_ext(df[\"T10Y2Y\"]).to_frame(\"T10Y2Y\").T.round(3)\n"
    "\n"
    "# Plot temporel avec ombrage des inversions\n"
    "fig, ax = plt.subplots(figsize=(12, 5))\n"
    "ax.plot(df.index, df[\"T10Y2Y\"], color=\"steelblue\", linewidth=0.8)\n"
    "ax.axhline(0, color=\"red\", linestyle=\"--\", linewidth=1)\n"
    "ax.fill_between(\n"
    "    df.index, df[\"T10Y2Y\"], 0,\n"
    "    where=(df[\"T10Y2Y\"] < 0), color=\"red\", alpha=0.3,\n"
    "    label=\"Inversion (spread < 0)\",\n"
    ")\n"
    "ax.set_title(\"Spread T10Y2Y : différence DGS10 − DGS2 (1990-aujourd'hui)\")\n"
    "ax.set_xlabel(\"Date\")\n"
    "ax.set_ylabel(\"Spread (points de %)\")\n"
    "ax.legend(loc=\"upper right\")\n"
    "ax.grid(True, alpha=0.3)\n"
    "plt.tight_layout()\n"
    "plt.show()\n"
    "\n"
    "stats_t10y2y"
)

md(
    "Le spread oscille entre environ −1,1 et +2,9 points de pourcentage, avec "
    "une moyenne d'environ 1,0 et une médiane proche, ce qui confirme qu'une "
    "courbe ascendante est le régime par défaut sur la période. Les zones "
    "ombrées rouges révèlent **quatre épisodes majeurs d'inversion** :\n\n"
    "- **2000** : inversion précédant la récession de 2001 (éclatement de la "
    "bulle internet).\n"
    "- **2006-2007** : inversion précédant la grande crise financière de "
    "2008-2009, pendant environ 18 mois.\n"
    "- **Été 2019** : brève inversion, suivie (de manière parfois discutée "
    "statistiquement) par la récession COVID de 2020 — même si celle-ci a été "
    "déclenchée par un choc exogène, l'inversion préalable indiquait déjà un "
    "ralentissement cyclique en cours.\n"
    "- **2022-2024** : la plus longue inversion de la série (≈ 2 ans), "
    "conséquence directe du resserrement ultra-rapide des Fed Funds face à "
    "l'inflation post-COVID. Ce signal annonce statistiquement une récession "
    "à un horizon 2024-2025.\n\n"
    "La **corrélation historique entre inversion et récession ultérieure** "
    "est donc visuellement très nette. Pour le projet, cela justifie de "
    "conserver `T10Y2Y` comme covariable : bien qu'elle soit une combinaison "
    "linéaire de `DGS10` et `DGS2`, elle isole précisément la dimension "
    "« pente » qui a une valeur prédictive propre — argument qui sera renforcé "
    "par l'analyse en composantes principales de Nelson-Siegel."
)

# ================== 2.5 Cross-familles ==================
md("### 2.5 Vue d'ensemble cross-familles")

md(
    "#### 2.5.1 Matrice de corrélation globale\n\n"
    "Jusqu'ici, on a regardé les trois familles séparément. Pour identifier "
    "les **ponts informationnels entre macro et courbe des taux** — qui sont "
    "précisément ce que cherche à exploiter le modèle prédictif — on calcule "
    "la matrice de corrélation complète sur les 13 variables. Les blocs de "
    "forte corrélation inter-familles sont les candidats naturels pour être "
    "des régresseurs utiles."
)

code(
    "corr_all = df.corr()\n"
    "fig, ax = plt.subplots(figsize=(10, 8))\n"
    "sns.heatmap(\n"
    "    corr_all, annot=True, fmt=\".2f\", cmap=\"coolwarm\",\n"
    "    vmin=-1, vmax=1, ax=ax,\n"
    "    cbar_kws={\"label\": \"Corrélation (Pearson)\"},\n"
    ")\n"
    "ax.set_title(\"Matrice de corrélation complète — 13 variables\")\n"
    "plt.tight_layout()\n"
    "plt.show()"
)

md(
    "Quatre structures ressortent de la matrice complète :\n\n"
    "1. **Bloc intra-taux (8 × 8, coin supérieur gauche)** : déjà analysé en "
    "2.2.5, corrélations très élevées (0,5 à 0,99), structure de bande.\n"
    "2. **FEDFUNDS ↔ taux courts** : corrélation très forte (typiquement "
    "> 0,9 avec `DGS1MO`, `DGS3MO`, `DGS6MO`). C'est la signature directe de "
    "la transmission de la politique monétaire : les taux courts Treasury "
    "sont mécaniquement ancrés au taux des Fed Funds par arbitrage. Cette "
    "redondance signifie que `FEDFUNDS` apporte peu d'information "
    "supplémentaire aux taux courts — à garder en tête pour éviter de "
    "sur-pondérer cette dimension dans la régression.\n"
    "3. **CPI en niveau ↔ taux** : corrélation apparemment faible à modérée, "
    "résultat contre-intuitif mais **artefact de non-stationnarité**. Le "
    "CPI est un indice monotone croissant alors que les taux oscillent ; la "
    "corrélation de Pearson entre une série croissante et une série "
    "oscillante sous-estime systématiquement la relation économique réelle "
    "(qui porte sur la croissance du CPI, pas son niveau). On s'attend à "
    "retrouver une corrélation plus claire avec `CPI_YoY` — confirmation à "
    "vérifier en Section 3.\n"
    "4. **T10Y2Y relativement décorrélé des niveaux de taux** : le spread "
    "est par construction une *différence* ; il capte l'information de "
    "pente, orthogonale à l'information de niveau. C'est précisément ce qui "
    "en fait un régresseur complémentaire utile, et non redondant avec "
    "`DGS2` ou `DGS10` pris séparément.\n\n"
    "Ces observations renforcent trois décisions méthodologiques : (a) "
    "**régulariser** (Ridge ou PCR) vu la redondance intra-taux et FEDFUNDS-"
    "taux courts, (b) **travailler sur les différences ou taux de "
    "croissance** pour CPI et INDPRO afin de révéler leur vraie relation "
    "avec les taux, (c) **standardiser** les covariables avant toute "
    "régularisation (Ridge pénalise les coefficients en norme $\\ell_2$, ce "
    "qui n'a pas de sens si les variables ont des échelles hétérogènes — "
    "pourcentages, indices à niveaux différents, points de base)."
)

# ================== 2.6 Synthèse ==================
md("### 2.6 Synthèse de la Section 2")

md(
    "**Sur les distributions.** Les rendements Treasury en niveau ne sont pas "
    "gaussiens : skewness légèrement positive, kurtosis de Fisher strictement "
    "positif, et surtout multimodalité marquée liée à l'existence de régimes "
    "monétaires hétérogènes (pré/post-2008, pré/post-COVID). Les ordres de "
    "grandeur sont physiquement cohérents (rendements entre 0 % et 8 %, "
    "chômage entre 3,5 % et 14,8 %, inflation typiquement autour de 2-3 % "
    "avec pics à 8 % en 2022). Les variables d'indice (CPI, INDPRO) ne sont "
    "pas analysables en niveau ; leur transformation en taux de croissance "
    "annuel les rend statistiquement exploitables.\n\n"
    "**Sur les relations entre variables.** La matrice de corrélation fait "
    "apparaître trois blocs structurels : (1) une **très forte colinéarité "
    "intra-taux** (souvent > 0,9) résultat direct de la structure factorielle "
    "de la courbe, (2) un **couplage mécanique FEDFUNDS–taux courts** "
    "reflétant la transmission de la politique monétaire, (3) une "
    "**quasi-orthogonalité** du spread T10Y2Y par rapport aux niveaux de "
    "taux, confirmant qu'il apporte une information propre (la pente) "
    "distincte de l'information niveau.\n\n"
    "**Ce qu'il reste à établir.** Les caractères *non stationnaires* des "
    "taux en niveau, du CPI et d'INDPRO sont visibles graphiquement mais "
    "n'ont pas été **testés formellement**. C'est l'objet de la Section 3 "
    "(test de Dickey-Fuller augmenté, ADF), qui tranchera entre modélisation "
    "en niveaux, en différences premières ou en taux de croissance. Les "
    "résidus des modèles de régression devront aussi être analysés "
    "*a posteriori* pour vérifier les hypothèses classiques de l'OLS "
    "(normalité, homoscédasticité, non-autocorrélation), ce qui se fera en "
    "phase de validation.\n\n"
    "**Conséquences pour la modélisation.** Trois choix méthodologiques sont "
    "déjà justifiés par l'analyse descriptive seule, sans attendre les "
    "tests : (1) **régularisation** (Ridge) ou **réduction de dimension** "
    "(PCR, PLS) plutôt qu'OLS naïf sur les 8 taux, en raison de la "
    "multicolinéarité ; (2) **standardisation** systématique des covariables "
    "dans le pipeline, pour que la pénalité Ridge ait du sens sur des "
    "variables à échelles différentes ; (3) probable usage des **différences "
    "premières** ou des **taux de croissance YoY** pour les variables non "
    "stationnaires en niveau, à confirmer par ADF."
)

md(
    "---\n\n"
    "**Prochaine étape** : Section 3 — Test formel de stationnarité (Dickey-"
    "Fuller augmenté, ADF) et décisions finales de preprocessing pour la "
    "modélisation."
)

# ------------------------------------------------------------
# 3) Assemblage final et écriture
# ------------------------------------------------------------
nb.cells.extend(new_cells)
nbformat.validator.normalize(nb)
nbformat.write(nb, NB_PATH)

md_n = sum(1 for c in nb.cells if c.cell_type == "markdown")
code_n = sum(1 for c in nb.cells if c.cell_type == "code")
print(f"[OK] Notebook mis a jour : {len(nb.cells)} cellules au total")
print(f"     ({md_n} markdown + {code_n} code)")
print(f"     Section 2 ajoutee : {len(new_cells)} cellules")
