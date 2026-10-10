"""
hf_radar.client
===============
HTTP client for Hugging Face Models API with session persistence,
polite rate-limiting, retry with exponential backoff, and RFC-5988 link pagination.
"""

import time
import requests
from typing import Dict, Any, List, Optional, Generator, Callable


class HFClient:
    """Client for querying the Hugging Face Hub Models API."""
    
    BASE_URL = "https://huggingface.co/api/models"
    
    def __init__(self, delay_seconds: float = 0.2, timeout: float = 20.0, max_retries: int = 3):
        self.delay_seconds = delay_seconds
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "HF-Gem-Radar/1.0",
            "Accept": "application/json"
        })

    def fetch_paginated_models(
        self,
        pipeline_tag: Optional[str] = "text-generation",
        num_parameters: Optional[str] = "min:3B,max:6B",
        filter_format: Optional[str] = None,
        search_term: Optional[str] = None,
        sort: str = "downloads",
        direction: int = -1,
        full: bool = True,
        max_pages: Optional[int] = None,
        page_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetches all matching models across paginated responses.
        
        Args:
            pipeline_tag: e.g. 'text-generation', 'image-text-to-text'
            num_parameters: e.g. 'min:3B,max:12B'
            filter_format: e.g. 'gguf'
            search_term: optional keyword search
            sort: 'downloads', 'likes', 'trendingScore', 'lastModified'
            direction: -1 for descending, 1 for ascending
            full: whether to request full metadata (author, tags, dates)
            max_pages: optional cap on number of pages fetched
            page_callback: callback(page_num, total_models_so_far)
        """
        params: Dict[str, Any] = {
            "sort": sort,
            "direction": direction,
        }
        if pipeline_tag:
            params["pipeline_tag"] = pipeline_tag
        if num_parameters:
            params["num_parameters"] = num_parameters
        if filter_format:
            params["filter"] = filter_format
        if search_term:
            params["search"] = search_term
        if full:
            params["full"] = "true"

        url: Optional[str] = self.BASE_URL
        collected_models: List[Dict[str, Any]] = []
        page_count = 0

        # Treat 0 or negative values as unlimited (None)
        effective_max_pages = None if (max_pages is not None and max_pages <= 0) else max_pages

        while url:
            time.sleep(self.delay_seconds)
            page_count += 1
            
            response = None
            for attempt in range(1, self.max_retries + 1):
                try:
                    response = self.session.get(url, params=params, timeout=self.timeout)
                    if response.status_code == 429:
                        wait = attempt * 2.0
                        time.sleep(wait)
                        continue
                    response.raise_for_status()
                    break
                except requests.RequestException as e:
                    if attempt == self.max_retries:
                        print(f"  [!] Request error on page {page_count}: {e}")
                        return collected_models
                    time.sleep(attempt * 1.5)

            if not response or response.status_code != 200:
                break

            page_data = response.json()
            if not isinstance(page_data, list) or len(page_data) == 0:
                break

            collected_models.extend(page_data)
            if page_callback:
                page_callback(page_count, len(collected_models))

            if effective_max_pages and page_count >= effective_max_pages:
                break

            # Hugging Face pagination uses Link: <url>; rel="next"
            params = None  # query params are embedded in the next link
            next_url = None
            
            link_header = response.links.get("next")
            if link_header and "url" in link_header:
                next_url = link_header["url"]
            elif "Link" in response.headers:
                for link in response.headers["Link"].split(","):
                    if 'rel="next"' in link and "<" in link and ">" in link:
                        next_url = link[link.find("<") + 1:link.find(">")]
                        break
            
            url = next_url

        return collected_models

    def close(self):
        """Closes the underlying HTTP session."""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
