"""Web scraping and search API utilities for Codex AI."""

import os
from pathlib import Path
from typing import List

import requests
from bs4 import BeautifulSoup


class DataScraper:
    """Simple scraper and search API wrapper."""

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        if not self.data_dir.exists():
            self.data_dir.mkdir(parents=True)

    def scrape_url(self, url: str) -> str:
        """Download the contents of a URL and return text."""
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(separator="\n")
        file_path = self.data_dir / f"{Path(url).stem}.txt"
        file_path.write_text(text)
        return text

    def search(self, query: str, api_key: str = None, engine_id: str = None) -> List[str]:
        """Perform a web search using Google Custom Search API (if keys provided)."""
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        engine_id = engine_id or os.getenv("GOOGLE_ENGINE_ID")
        if not api_key or not engine_id:
            raise RuntimeError("Google API key and engine ID must be provided")
        params = {
            "key": api_key,
            "cx": engine_id,
            "q": query,
        }
        resp = requests.get("https://www.googleapis.com/customsearch/v1", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = [item["link"] for item in data.get("items", [])]
        return results
