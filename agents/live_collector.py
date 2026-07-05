
"""Free live-data collection for ExamDigest.

The collector prefers configured RSS/Atom feeds and falls back to GDELT's free
DOC API. It normalizes every item into the article shape expected by the rest of
the pipeline: title, content, url, and tags.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any, Dict, List


class LiveNewsCollector:
    """Collect articles from free public sources with a small local cache."""

    GDELT_DOC_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

    def __init__(
        self,
        source_config_path: str,
        cache_dir: str,
        cache_ttl_seconds: int = 21600,
        timeout_seconds: int = 10,
    ):
        self.source_config_path = source_config_path
        self.cache_dir = cache_dir
        self.cache_ttl_seconds = cache_ttl_seconds
        self.timeout_seconds = timeout_seconds
        self.warnings: List[str] = []

    def collect(self, exam_type: str) -> List[Dict[str, Any]]:
        """Fetch and normalize live articles for an exam type."""
        self.warnings = []
        config = self._load_exam_config(exam_type)
        articles: List[Dict[str, Any]] = []
        default_tags = config.get("default_tags", [])

        for feed_url in config.get("rss_feeds", []):
            articles.extend(self._collect_rss_feed(feed_url, default_tags))

        gdelt_queries = config.get("gdelt_queries", [])
        if gdelt_queries:
            query_articles = self._collect_gdelt(gdelt_queries[0], default_tags)
            if query_articles:
                articles.extend(query_articles)

        return self._dedupe_articles(articles)

    def _load_exam_config(self, exam_type: str) -> Dict[str, Any]:
        with open(self.source_config_path, "r", encoding="utf-8") as config_file:
            source_config = json.load(config_file)
        return source_config.get(exam_type.lower(), {})

    def _collect_rss_feed(
        self, feed_url: str, default_tags: List[str]
    ) -> List[Dict[str, Any]]:
        try:
            payload = self._fetch_text(feed_url)
            root = ET.fromstring(payload)
        except Exception as exc:
            self.warnings.append(f"RSS source failed: {feed_url} ({exc})")
            return []

        articles = []
        items = root.findall(".//item") or root.findall(
            ".//{http://www.w3.org/2005/Atom}entry"
        )
        for item in items:
            title = self._xml_text(item, "title")
            link = self._xml_text(item, "link")
            summary = (
                self._xml_text(item, "description")
                or self._xml_text(item, "summary")
                or title
            )
            article = self._normalize_article(title, summary, link, default_tags)
            if article:
                articles.append(article)
        return articles

    def _collect_gdelt(
        self, query: str, default_tags: List[str]
    ) -> List[Dict[str, Any]]:
        params = {
            "query": query,
            "mode": "ArtList",
            "format": "json",
            "maxrecords": "20",
            "sort": "DateDesc",
        }
        url = f"{self.GDELT_DOC_URL}?{urllib.parse.urlencode(params)}"
        try:
            payload = self._fetch_text(url)
            body = json.loads(payload)
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                return []
            self.warnings.append(f"GDELT query failed: {query} ({exc})")
            return []
        except Exception as exc:
            self.warnings.append(f"GDELT query failed: {query} ({exc})")
            return []

        articles = []
        for item in body.get("articles", []):
            title = item.get("title", "")
            link = item.get("url", "")
            domain = item.get("domain") or item.get("sourceCollectionIdentifier", "")
            content = title
            if domain:
                content = f"{title}. Source: {domain}."
            article = self._normalize_article(title, content, link, default_tags)
            if article:
                articles.append(article)
        return articles

    def _fetch_text(self, url: str) -> str:
        os.makedirs(self.cache_dir, exist_ok=True)
        cache_path = os.path.join(self.cache_dir, self._cache_key(url) + ".txt")
        if self._is_cache_fresh(cache_path):
            with open(cache_path, "r", encoding="utf-8") as cache_file:
                return cache_file.read()

        request = urllib.request.Request(
            url,
            headers={"User-Agent": "ExamDigest/1.0 (+https://github.com/Akhil-R/ExamDigest)"},
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            payload = response.read().decode("utf-8", errors="replace")

        with open(cache_path, "w", encoding="utf-8") as cache_file:
            cache_file.write(payload)
        return payload

    def _normalize_article(
        self, title: str, content: str, url: str, tags: List[str]
    ) -> Dict[str, Any] | None:
        clean_title = " ".join((title or "").split())
        clean_content = " ".join((content or "").split())
        clean_url = (url or "").strip()

        if not clean_title or not clean_content:
            return None
        if not clean_url.startswith(("http://", "https://")):
            return None

        return {
            "title": clean_title,
            "content": clean_content,
            "url": clean_url,
            "tags": tags,
        }

    def _dedupe_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen_urls = set()
        unique_articles = []
        for article in articles:
            url = article["url"]
            if url in seen_urls:
                continue
            seen_urls.add(url)
            unique_articles.append(article)
        return unique_articles

    def _is_cache_fresh(self, cache_path: str) -> bool:
        return (
            os.path.exists(cache_path)
            and time.time() - os.path.getmtime(cache_path) < self.cache_ttl_seconds
        )

    def _cache_key(self, value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def _xml_text(self, item: ET.Element, name: str) -> str:
        element = item.find(name)
        if element is None:
            element = item.find(f"{{http://www.w3.org/2005/Atom}}{name}")
        if element is None:
            return ""
        if name == "link" and "href" in element.attrib:
            return element.attrib["href"]
        return element.text or ""
