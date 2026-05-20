"""Tools for municipality scoring.

Baseline generico: ScoreIndicator + calculate_municipality_scores (soma ponderada).
Trilha climatica: vulnerabilidade (PCA/IDW/peso per-capita), arquetipos e projecao.
"""

from municipios_score.scoring import ScoreIndicator, calculate_municipality_scores
from municipios_score.vulnerabilidade import alocar, montar_scores, peso_per_capita

__all__ = [
    "ScoreIndicator",
    "calculate_municipality_scores",
    "montar_scores",
    "alocar",
    "peso_per_capita",
]
