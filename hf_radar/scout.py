"""
hf_radar.scout
==============
Core radar scout orchestrator. Coordinates deep sweeps across pipeline tags
(LLMs & MMLLMs), handles parameter range enforcement, keyword discovery,
deduplication, and date threshold filtering.
"""

from typing import List, Dict, Any, Optional, Set
from .client import HFClient
from .normalizer import normalize_model, parse_date_to_excel_serial

DEFAULT_PIPELINE_TAGS = ["text-generation", "image-text-to-text", "video-text-to-text"]
DEFAULT_NUM_PARAMS = "min:3B,max:6B"

CURATED_KEYWORDS = [
    "nsfw", "uncensored", "rp", "roleplay", "abliterated", "obliterated",
    "lewd", "sex", "erotic", "spice", "spicy", "sexy", "erp", "waifu",
    "sillytavern", "unslop", "dealigned", "unaligned", "decensored",
    "unfiltered", "no-refusal", "heretic", "dolphin", "dark"
]


class GemRadarScout:
    """Orchestrates model gathering across Hugging Face within hardware constraints."""

    def __init__(
        self,
        num_parameters: str = DEFAULT_NUM_PARAMS,
        pipeline_tags: Optional[List[str]] = None,
        gguf_only: bool = False,
        min_downloads: int = 1,
        min_likes: int = 1,
        created_after: Optional[str] = None,  # e.g. "2024-01-01"
        client: Optional[HFClient] = None
    ):
        self.num_parameters = num_parameters
        self.pipeline_tags = pipeline_tags or DEFAULT_PIPELINE_TAGS
        self.gguf_only = gguf_only
        self.min_downloads = min_downloads
        self.min_likes = min_likes
        self.created_after = created_after
        self.client = client or HFClient()
        self._excel_cutoff = parse_date_to_excel_serial(f"{created_after}T00:00:00Z") if created_after else 0.0

    def scout_snapshot(
        self,
        max_pages_per_tag: Optional[int] = 1,
        verbose: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Runs a structured snapshot sweep across all target pipeline tags within the parameter range.
        Normalizes and enriches each record with 2D magnitude, quality angle, and gem residual.
        """
        seen_ids: Set[str] = set()
        scouted_models: List[Dict[str, Any]] = []

        filter_fmt = "gguf" if self.gguf_only else None

        for tag in self.pipeline_tags:
            if verbose:
                fmt_str = " (GGUF Only)" if self.gguf_only else ""
                print(f"[*] Scouting pipeline: '{tag}' [{self.num_parameters}]{fmt_str}...")

            def progress_cb(page, total):
                if verbose and page % 5 == 0:
                    print(f"    Fetched page {page} ({total} models from '{tag}')...")

            raw_records = self.client.fetch_paginated_models(
                pipeline_tag=tag,
                num_parameters=self.num_parameters,
                filter_format=filter_fmt,
                full=True,
                max_pages=max_pages_per_tag,
                page_callback=progress_cb
            )

            tag_accepted = 0
            for raw in raw_records:
                mid = raw.get("id") or raw.get("modelId")
                if not mid or mid in seen_ids:
                    continue
                
                norm = normalize_model(raw)
                
                # Minimum activity filtering (filter out ghost models)
                if norm["downloads"] < self.min_downloads or norm["likes"] < self.min_likes:
                    continue

                # Recency cutoff (e.g. 2024-01-01)
                if self._excel_cutoff > 0 and norm["Date_Created"] < self._excel_cutoff:
                    continue

                seen_ids.add(mid)
                scouted_models.append(norm)
                tag_accepted += 1

            if verbose:
                print(f"  -> Accepted {tag_accepted} active models for tag '{tag}'. (Total unique: {len(scouted_models)})")

        return scouted_models

    def scout_keywords(
        self,
        keywords: Optional[List[str]] = None,
        sort_strategies: Optional[List[str]] = None,
        max_pages_per_query: Optional[int] = 5,
        verbose: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Runs a multi-angle keyword search across sorting dimensions (trendingScore, likes, downloads).
        Surfaces niche community models that don't appear in default broad searches.
        """
        kw_list = keywords or CURATED_KEYWORDS
        sorts = sort_strategies or ["trendingScore", "likes", "downloads"]
        seen_ids: Set[str] = set()
        models: List[Dict[str, Any]] = []

        filter_fmt = "gguf" if self.gguf_only else None

        for sort_type in sorts:
            if verbose:
                print(f"\n[*] Scanning keyword angle sorted by '{sort_type}'...")
            for kw in kw_list:
                raw_records = self.client.fetch_paginated_models(
                    pipeline_tag="text-generation",
                    num_parameters=self.num_parameters,
                    filter_format=filter_fmt,
                    search_term=kw,
                    sort=sort_type,
                    full=True,
                    max_pages=max_pages_per_query
                )
                added = 0
                for raw in raw_records:
                    mid = raw.get("id") or raw.get("modelId")
                    if not mid or mid in seen_ids:
                        continue
                    norm = normalize_model(raw)
                    if norm["downloads"] < self.min_downloads or norm["likes"] < self.min_likes:
                        continue
                    seen_ids.add(mid)
                    models.append(norm)
                    added += 1
                if verbose and added > 0:
                    print(f"    Keyword '{kw}': +{added} new models")

        return models
