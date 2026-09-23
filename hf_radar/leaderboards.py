"""
hf_radar.leaderboards
=====================
Leaderboard generators and export utilities.
Filters out mainstream noise to surface hidden gems, standout MMLLMs,
GGUF quantized crafts, and top uncensored/abliterated models.
"""

import csv
from typing import List, Dict, Any, Optional

CSV_COLUMNS = [
    "modelId", "author", "createdAt", "lastModified", "Date_Created",
    "pipeline_tag", "likes", "log10_likes", "downloads", "log10_downloads",
    "magnitude", "DL_Mag", "DL_Mag_log", "trendingScore", 
    "appreciation_rate", "quality_angle", "gem_residual",
    "Is_GGUF", "Is_Safetensors", "Is_Uncensored", "Is_Abliterated", 
    "Is_Roleplay", "Is_MMLLM", "tags", "url"
]


def filter_hidden_gems(
    models: List[Dict[str, Any]],
    min_downloads: int = 50,
    max_downloads: int = 250000,
    min_likes: int = 10,
    min_angle: float = 25.0
) -> List[Dict[str, Any]]:
    """
    Surfaces models that punch disproportionately above their weight class.
    Excludes hyper-famous mainstream models (> max_downloads) and noisy low-count models (< min_downloads).
    """
    gems = [
        m for m in models
        if min_downloads <= m["downloads"] <= max_downloads
        and m["likes"] >= min_likes
        and m["quality_angle"] >= min_angle
    ]
    # Primary sort by gem residual, secondary by quality angle
    return sorted(gems, key=lambda x: (x["gem_residual"], x["quality_angle"]), reverse=True)


def filter_rising_stars(
    models: List[Dict[str, Any]],
    min_trending: float = 5.0,
    max_downloads: int = 500000
) -> List[Dict[str, Any]]:
    """Identifies breakout models with high current momentum relative to download scale."""
    stars = [
        m for m in models
        if m["trendingScore"] >= min_trending and m["downloads"] <= max_downloads
    ]
    return sorted(stars, key=lambda x: x["trendingScore"], reverse=True)


def filter_mmllm_standouts(models: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filters for multimodal vision/video models and ranks by 2D magnitude."""
    mm_models = [m for m in models if m.get("Is_MMLLM") == 1]
    return sorted(mm_models, key=lambda x: (x["magnitude"], x["likes"]), reverse=True)


def filter_uncensored_gems(models: List[Dict[str, Any]], min_likes: int = 5) -> List[Dict[str, Any]]:
    """Filters for abliterated, uncensored, and dealigned fine-tunes ranked by quality angle."""
    unc = [m for m in models if (m.get("Is_Uncensored") == 1 or m.get("Is_Abliterated") == 1) and m["likes"] >= min_likes]
    return sorted(unc, key=lambda x: (x["quality_angle"], x["gem_residual"]), reverse=True)


def filter_gguf_top(models: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filters for GGUF quantized models ranked by 2D log-space magnitude."""
    ggufs = [m for m in models if m.get("Is_GGUF") == 1]
    return sorted(ggufs, key=lambda x: x["magnitude"], reverse=True)


def export_to_csv(models: List[Dict[str, Any]], filepath: str):
    """Exports all model records and calculated metrics to a clean CSV."""
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for m in models:
            writer.writerow(m)
    print(f"\n[✓] Exported {len(models)} models to: {filepath}")


def print_table(title: str, models: List[Dict[str, Any]], limit: int = 12):
    """Prints a formatted console table of top standout models."""
    print("\n" + "=" * 95)
    print(f"  {title}")
    print("=" * 95)
    header = f"{'#':<3} | {'Model ID':<48} | {'DLs':<8} | {'Likes':<6} | {'Mag':<5} | {'Angle':<6} | {'Resid':<6}"
    print(header)
    print("-" * 95)
    
    subset = models[:limit]
    if not subset:
        print("  (No models matched this specific criteria)")
        print("=" * 95)
        return

    for idx, m in enumerate(subset, 1):
        mid = m["modelId"]
        if len(mid) > 48:
            mid = mid[:45] + "..."
        dls = f"{m['downloads']:,}"
        lks = f"{m['likes']:,}"
        mag = f"{m['magnitude']:.2f}"
        ang = f"{m['quality_angle']:.1f}°"
        res = f"{m['gem_residual']:+.2f}"
        print(f"{idx:<3} | {mid:<48} | {dls:<8} | {lks:<6} | {mag:<5} | {ang:<6} | {res:<6}")
    print("=" * 95)


def display_full_radar_summary(models: List[Dict[str, Any]]):
    """Renders comprehensive terminal leaderboards across all key discovery dimensions."""
    total = len(models)
    gguf_cnt = sum(1 for m in models if m.get("Is_GGUF") == 1)
    unc_cnt = sum(1 for m in models if m.get("Is_Uncensored") == 1)
    ablit_cnt = sum(1 for m in models if m.get("Is_Abliterated") == 1)
    mm_cnt = sum(1 for m in models if m.get("Is_MMLLM") == 1)

    print("\n" + "#" * 95)
    print("  HF GEM RADAR - SUMMARY OVERVIEW")
    print("#" * 95)
    print(f"  Total Scouted Models  : {total:,}")
    print(f"  GGUF Quantized        : {gguf_cnt:,} ({(gguf_cnt/total*100):.1f}%)" if total else "")
    print(f"  Uncensored / Dealigned: {unc_cnt:,}")
    print(f"  Abliterated Models    : {ablit_cnt:,}")
    print(f"  Multimodal (MMLLM)    : {mm_cnt:,}")

    # 1. Hidden Gems Leaderboard
    gems = filter_hidden_gems(models)
    print_table("💎 TOP HIDDEN GEMS (High Acclaim & Outlier Residual, Fame-Capped)", gems)

    # 2. Top MMLLM Standouts
    mmllms = filter_mmllm_standouts(models)
    if mmllms:
        print_table("👁️ STANDOUT LOCAL MMLLMs (Vision & Multimodal in Operational Range)", mmllms)

    # 3. Top Abliterated & Uncensored Crafts
    unc_gems = filter_uncensored_gems(models)
    if unc_gems:
        print_table("🔓 TOP UNCENSORED & ABLITERATED CRAFTS (Ranked by Quality Angle)", unc_gems)

    # 4. Top GGUF Quantized Overall
    ggufs = filter_gguf_top(models)
    print_table("⚡ TOP GGUF IN-RANGE MODELS (Ranked by 2D Popularity Magnitude)", ggufs)
