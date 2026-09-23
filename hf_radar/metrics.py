"""
hf_radar.metrics
================
Mathematical and statistical scoring functions for model engagement analysis.
Computes 2D log-space popularity vectors, linear magnitudes, and hidden gem indicators.
"""

import math
from typing import Dict, Any


def calculate_dl_mag(downloads: float, likes: float) -> float:
    """
    Linear Euclidean Magnitude: SQRT(downloads^2 + likes^2).
    Represents raw aggregate volume in linear engagement space.
    """
    return math.sqrt(max(0.0, downloads) ** 2 + max(0.0, likes) ** 2)


def calculate_log10(val: float) -> float:
    """Safely calculates log10, returning 0.0 for values <= 0."""
    return round(math.log10(val), 2) if val > 0 else 0.0


def calculate_magnitude(log10_likes: float, log10_downloads: float) -> float:
    """
    Log-Space Euclidean Magnitude: SQRT(log10_likes^2 + log10_downloads^2).
    Normalized 2D popularity vector length in log-log space.
    Matches Excel formula `=SQRT(G2^2 + I2^2)`.
    """
    return round(math.sqrt(max(0.0, log10_likes) ** 2 + max(0.0, log10_downloads) ** 2), 2)


def calculate_appreciation_rate(likes: float, downloads: float) -> float:
    """
    Appreciation / Conversion Rate (%): (likes / downloads) * 100.
    Measures community satisfaction density.
    """
    if downloads <= 0:
        return 0.0
    return round((likes / downloads) * 100.0, 3)


def calculate_quality_angle(log10_likes: float, log10_downloads: float) -> float:
    """
    Quality Angle theta in degrees: arctan2(log10_likes, log10_downloads).
    Higher angles (approaching 45° or beyond) indicate models with disproportionately
    high community acclaim relative to download footprint.
    """
    if log10_likes <= 0 and log10_downloads <= 0:
        return 0.0
    rad = math.atan2(max(0.0, log10_likes), max(0.0, log10_downloads))
    return round(math.degrees(rad), 2)


def calculate_gem_residual(log10_likes: float, log10_downloads: float, alpha: float = 0.75) -> float:
    """
    Gem Residual: log10_likes - alpha * log10_downloads.
    Quantifies how far above the baseline fame curve a model sits.
    Positive values represent standout gems with excessive like-density.
    """
    if log10_downloads <= 0 and log10_likes <= 0:
        return 0.0
    return round(log10_likes - (alpha * log10_downloads), 3)


def compute_all_metrics(downloads: float, likes: float) -> Dict[str, float]:
    """Computes the complete suite of popularity and gem metrics for a model."""
    d = max(0.0, float(downloads or 0))
    l = max(0.0, float(likes or 0))
    
    dl_mag = calculate_dl_mag(d, l)
    dl_mag_log = calculate_log10(dl_mag)
    
    l_log = calculate_log10(l)
    d_log = calculate_log10(d)
    mag = calculate_magnitude(l_log, d_log)
    
    apprec = calculate_appreciation_rate(l, d)
    angle = calculate_quality_angle(l_log, d_log)
    residual = calculate_gem_residual(l_log, d_log)
    
    return {
        "downloads": int(d),
        "likes": int(l),
        "DL_Mag": round(dl_mag, 3),
        "DL_Mag_log": dl_mag_log,
        "log10_likes": l_log,
        "log10_downloads": d_log,
        "magnitude": mag,
        "appreciation_rate": apprec,
        "quality_angle": angle,
        "gem_residual": residual
    }
