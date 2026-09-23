#!/usr/bin/env python3
"""
radar.py
========
Main entry point for HF Model Radar & Hidden Gem Scrubber.
Surfaces standout local LLMs and MMLLMs within your hardware's operational range.

Usage:
    # 1-Click Run (Defaults: 3B-12B range, LLMs & MMLLMs, leaderboards + CSV export):
    python radar.py

    # Focus on GGUF models only:
    python radar.py --gguf-only

    # Custom parameter envelope (e.g. up to 14B or 32B):
    python radar.py --params "min:0,max:14B"

    # Multi-angle niche keyword scout (uncensored, abliterated, RP):
    python radar.py --mode keywords

    # Filter for models created after Jan 1, 2024:
    python radar.py --after 2024-01-01
"""

import sys
import argparse
from hf_radar import (
    GemRadarScout,
    display_full_radar_summary,
    export_to_csv,
    DEFAULT_PIPELINE_TAGS,
    DEFAULT_NUM_PARAMS
)

# Ensure clean UTF-8 console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def parse_args():
    parser = argparse.ArgumentParser(
        description="HF Gem Radar: Scout and surface standout LLMs and MMLLMs within your operational range."
    )
    parser.add_argument(
        "--params", "-p",
        default=DEFAULT_NUM_PARAMS,
        help=f"Parameter filter range (default: '{DEFAULT_NUM_PARAMS}'). Examples: 'min:0,max:14B', 'min:6B,max:32B'"
    )
    parser.add_argument(
        "--tags", "-t",
        nargs="+",
        default=DEFAULT_PIPELINE_TAGS,
        help="Pipeline tags to scout (default: text-generation image-text-to-text video-text-to-text)"
    )
    parser.add_argument(
        "--gguf-only", "-g",
        action="store_true",
        help="Filter exclusively for GGUF quantized models"
    )
    parser.add_argument(
        "--mode", "-m",
        choices=["snapshot", "keywords"],
        default="snapshot",
        help="Scouting mode: 'snapshot' (deep pipeline sweep) or 'keywords' (multi-angle niche keyword search)"
    )
    parser.add_argument(
        "--after",
        default="2024-01-01",
        help="Recency cutoff date YYYY-MM-DD (default: '2024-01-01', set to '' to disable)"
    )
    parser.add_argument(
        "--min-downloads",
        type=int,
        default=1,
        help="Minimum downloads required to include a model (default: 1, filters ghost models)"
    )
    parser.add_argument(
        "--min-likes",
        type=int,
        default=1,
        help="Minimum likes required to include a model (default: 1)"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Optional cap on pages fetched per tag/query (useful for fast scans)"
    )
    parser.add_argument(
        "--output", "-o",
        default="huggingface_snapshot.csv",
        help="Path to export the full analyzed dataset CSV (default: 'huggingface_snapshot.csv')"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("=" * 75)
    print("  HF GEM RADAR - LOCAL LLM & MMLLM SCOUT")
    print("=" * 75)
    print(f"  Operational Range : {args.params}")
    print(f"  Target Modalities : {', '.join(args.tags)}")
    print(f"  Format Filter     : {'GGUF Only' if args.gguf_only else 'All Formats (GGUF, Safetensors, etc.)'}")
    print(f"  Scouting Mode     : {args.mode.upper()}")
    print(f"  Recency Cutoff    : {args.after if args.after else 'None (All time)'}")
    print(f"  Output CSV Target : {args.output}")
    print("=" * 75 + "\n")

    scout = GemRadarScout(
        num_parameters=args.params,
        pipeline_tags=args.tags,
        gguf_only=args.gguf_only,
        min_downloads=args.min_downloads,
        min_likes=args.min_likes,
        created_after=args.after if args.after else None
    )

    if args.mode == "keywords":
        models = scout.scout_keywords(max_pages_per_query=args.max_pages or 5)
    else:
        models = scout.scout_snapshot(max_pages_per_tag=args.max_pages)

    if not models:
        print("\n[!] No models met the specified criteria.")
        return

    # Render Leaderboards to Console
    display_full_radar_summary(models)

    # Export full dataset with all calculated metrics
    export_to_csv(models, args.output)


if __name__ == "__main__":
    main()
