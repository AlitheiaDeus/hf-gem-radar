"""
hf_radar
========
Hugging Face Model Radar & Hidden Gem Scrubber.
Scout, filter, and score local LLMs and MMLLMs within hardware constraints.
"""

from .client import HFClient
from .metrics import (
    calculate_dl_mag,
    calculate_log10,
    calculate_magnitude,
    calculate_appreciation_rate,
    calculate_quality_angle,
    calculate_gem_residual,
    compute_all_metrics
)
from .normalizer import normalize_model, parse_date_to_excel_serial
from .scout import GemRadarScout, DEFAULT_PIPELINE_TAGS, DEFAULT_NUM_PARAMS, CURATED_KEYWORDS
from .leaderboards import (
    filter_hidden_gems,
    filter_rising_stars,
    filter_mmllm_standouts,
    filter_uncensored_gems,
    filter_gguf_top,
    export_to_csv,
    display_full_radar_summary
)

__version__ = "2.0.0"
__all__ = [
    "HFClient",
    "GemRadarScout",
    "calculate_dl_mag",
    "calculate_log10",
    "calculate_magnitude",
    "calculate_appreciation_rate",
    "calculate_quality_angle",
    "calculate_gem_residual",
    "compute_all_metrics",
    "normalize_model",
    "parse_date_to_excel_serial",
    "filter_hidden_gems",
    "filter_rising_stars",
    "filter_mmllm_standouts",
    "filter_uncensored_gems",
    "filter_gguf_top",
    "export_to_csv",
    "display_full_radar_summary",
    "DEFAULT_PIPELINE_TAGS",
    "DEFAULT_NUM_PARAMS",
    "CURATED_KEYWORDS"
]
