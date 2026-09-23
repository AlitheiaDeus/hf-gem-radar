"""
hf_radar.normalizer
===================
Normalizes raw Hugging Face API responses into structured model dictionaries.
Handles date cleaning, Excel serial dates, tag categorization, and metric enrichment.
"""

import re
from datetime import datetime, timezone
from typing import Dict, Any, List
from .metrics import compute_all_metrics

# Base epoch for Excel serial date numbers (Windows 1900 date system)
EXCEL_EPOCH = datetime(1899, 12, 30, tzinfo=timezone.utc)

UNCENSORED_KEYWORDS = {
    "uncensored", "no-refusal", "dealigned", "unaligned", 
    "decensored", "unfiltered", "heretic", "dolphin", "dark"
}

ABLITERATED_KEYWORDS = {
    "abliterated", "abliteration", "obliterated"
}

ROLEPLAY_KEYWORDS = {
    "rp", "roleplay", "sillytavern", "erotic", "lewd", 
    "waifu", "spicy", "unslop", "narrative"
}

MMLLM_TAGS = {"image-text-to-text", "video-text-to-text"}


def parse_date_to_excel_serial(date_str: str) -> float:
    """Converts an ISO date string (e.g. '2026-06-25T04:56:13.000Z') to an Excel serial number."""
    if not date_str:
        return 0.0
    try:
        clean_str = date_str.replace(".000Z", "+00:00").replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        delta = dt - EXCEL_EPOCH
        return round(delta.days + (delta.seconds / 86400.0), 4)
    except Exception:
        return 0.0


def clean_iso_date(date_str: str) -> str:
    """Removes trailing sub-second/Z artifacts for clean display."""
    if not date_str:
        return ""
    return str(date_str).replace(".000Z", "").replace("Z", "").strip()


def normalize_model(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses a raw Hugging Face model API record into a standardized, metric-enriched record.
    """
    model_id = raw.get("id") or raw.get("modelId") or ""
    author = raw.get("author") or (model_id.split("/")[0] if "/" in model_id else "")
    pipeline_tag = raw.get("pipeline_tag") or "text-generation"
    
    downloads = raw.get("downloads", 0) or 0
    likes = raw.get("likes", 0) or 0
    trending_score = raw.get("trendingScore", 0) or 0
    
    raw_created = raw.get("createdAt") or ""
    raw_modified = raw.get("lastModified") or ""
    
    created_at = clean_iso_date(raw_created)
    last_modified = clean_iso_date(raw_modified)
    excel_date = parse_date_to_excel_serial(raw_created)
    
    raw_tags = raw.get("tags") or []
    if isinstance(raw_tags, str):
        raw_tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
    
    tags_lower = [str(t).lower() for t in raw_tags]
    tags_str = ", ".join(raw_tags)
    
    # Archetype detection
    is_gguf = "gguf" in tags_lower or "gguf" in model_id.lower()
    is_safetensors = "safetensors" in tags_lower
    
    is_abliterated = any(k in tags_lower or k in model_id.lower() for k in ABLITERATED_KEYWORDS)
    is_uncensored = is_abliterated or any(k in tags_lower or k in model_id.lower() for k in UNCENSORED_KEYWORDS)
    is_roleplay = any(k in tags_lower or k in model_id.lower() for k in ROLEPLAY_KEYWORDS)
    is_mmllm = pipeline_tag in MMLLM_TAGS or any(k in tags_lower for k in ("vision", "llava", "vl", "multimodal"))

    # Compute mathematical engagement metrics
    metrics = compute_all_metrics(downloads, likes)
    
    return {
        "modelId": model_id,
        "author": author,
        "pipeline_tag": pipeline_tag,
        "createdAt": created_at,
        "lastModified": last_modified,
        "Date_Created": excel_date,
        "downloads": metrics["downloads"],
        "likes": metrics["likes"],
        "DL_Mag": metrics["DL_Mag"],
        "DL_Mag_log": metrics["DL_Mag_log"],
        "log10_likes": metrics["log10_likes"],
        "log10_downloads": metrics["log10_downloads"],
        "magnitude": metrics["magnitude"],
        "trendingScore": trending_score,
        "appreciation_rate": metrics["appreciation_rate"],
        "quality_angle": metrics["quality_angle"],
        "gem_residual": metrics["gem_residual"],
        "Is_GGUF": 1 if is_gguf else 0,
        "Is_Safetensors": 1 if is_safetensors else 0,
        "Is_Uncensored": 1 if is_uncensored else 0,
        "Is_Abliterated": 1 if is_abliterated else 0,
        "Is_Roleplay": 1 if is_roleplay else 0,
        "Is_MMLLM": 1 if is_mmllm else 0,
        "tags": tags_str,
        "url": f"https://huggingface.co/{model_id}" if model_id else ""
    }
