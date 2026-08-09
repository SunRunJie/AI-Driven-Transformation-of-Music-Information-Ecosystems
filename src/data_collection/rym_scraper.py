"""
RYM (RateYourMusic) data collection framework
=============================================

Core design principles:
1. **Respect the platform** - control request frequency, follow the spirit of robots.txt
2. **Robustness first** - multi-layer fallback strategy: API -> HTML
   parsing -> cache -> explicit unavailable metadata. Synthetic fallback is
   opt-in and never silently mixed into real research data.
3. **Reproducible research** - all collected data is timestamped and carries metadata
4. **Incremental collection** - support resuming from breakpoints, avoid duplicate requests

Data collection strategy (by priority):
  A. Request RYM public pages directly (HTML parsing)
  B. Use cached local data (avoid duplicate requests)
  C. Record an explicit unavailable event when collection cannot proceed

Target data:
1. Album rating distributions (by year/genre)
2. User rating time series
3. Chart ranking changes
4. Community discussion topics
"""

import time
import json
import hashlib
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from urllib.parse import urljoin

import sys

_SRC = str(Path(__file__).resolve().parent.parent)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

from config import (
    RYM_BASE_URL, RYM_CHARTS_URL, RYM_TOP_URL,
    REQUEST_DELAY, REQUEST_TIMEOUT, MAX_RETRIES,
    USER_AGENT, RAW_DIR, RANDOM_SEED, YEAR_RANGE
)


# ============================================================
# Utility functions
# ============================================================

def _looks_blocked(html: str) -> bool:
    blocked_markers = [
        "Enable JavaScript and cookies to continue",
        "cf_chl_opt",
        "challenge-platform",
        "Just a moment",
    ]
    return any(marker in html for marker in blocked_markers)


def _make_request(url: str, session: requests.Session,
                  delay: float = REQUEST_DELAY) -> Optional[str]:
    """HTTP request with polite delay and retries"""
    time.sleep(delay)
    for attempt in range(MAX_RETRIES):
        try:
            resp = session.get(url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            if _looks_blocked(resp.text or ""):
                print(f"  [WARN] Request was blocked by an interstitial challenge: {url}")
                return None
            return resp.text
        except requests.exceptions.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                wait = delay * (2 ** attempt)  # exponential backoff
                print(f"  [WARN] Request failed (attempt {attempt+1}): {e}, retrying in {wait:.0f}s...")
                time.sleep(wait)
            else:
                print(f"  [FAIL] Request failed after {MAX_RETRIES} retries: {url}")
                return None
    return None


def _cache_path(url: str) -> Path:
    """Generate a cache file path"""
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return RAW_DIR / f"cache_{url_hash}.html"


def _cached_request(url: str, session: requests.Session,
                    use_cache: bool = True) -> Optional[str]:
    """File-backed request with caching"""
    cache_file = _cache_path(url)

    if use_cache and cache_file.exists():
        # check whether the cache is within 24 hours
        age = time.time() - cache_file.stat().st_mtime
        if age < 86400:  # 24 hours
            return cache_file.read_text(encoding="utf-8")
        print(f"  [INFO] Cache expired ({age/3600:.1f} hours ago), re-requesting")

    html = _make_request(url, session)
    if html:
        cache_file.write_text(html, encoding="utf-8")
    return html


# ============================================================
# RYM data collector
# ============================================================

class RYMDataCollector:
    """RYM collector with auditable, opt-in synthetic fixture generation."""

    def __init__(self, delay: float = REQUEST_DELAY,
                 use_cache: bool = True,
                 fallback_to_synthetic: bool = False):
        """
        Parameters:
        -----------
        delay : float - request interval (seconds), recommended >= 2
        use_cache : bool - whether to use local cache
        fallback_to_synthetic : bool - whether to use synthetic data when the remote is unreachable
        """
        self.delay = delay
        self.use_cache = use_cache
        self.fallback_to_synthetic = fallback_to_synthetic
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })
        self.rng = np.random.default_rng(RANDOM_SEED)
        self._data_version = datetime.now().isoformat()
        self.collection_events: List[Dict] = []

    # ----------------------------------------------------------
    # Core collection methods
    # ----------------------------------------------------------

    def fetch_chart_page(self, chart_type: str = "top",
                         year: int = 2024,
                         genre: Optional[str] = None) -> Optional[str]:
        """
        Fetch the RYM chart page HTML

        Parameters:
        -----------
        chart_type : str - chart type ("top", "best", "highest_rated")
        year : int - year
        genre : Optional[str] - genre filter
        """
        # RYM's public chart pages use path-based URLs. The older query-style
        # URL often lands on a blocked or non-chart page.
        chart_path = "top" if chart_type in {"top", "best", "highest_rated"} else chart_type
        url = f"{RYM_BASE_URL}/charts/{chart_path}/album/{year}/"
        if genre:
            url = f"{url}{genre}/"
        print(f"  [INFO] Requesting RYM chart: {year} ({chart_type})")

        html = _cached_request(url, self.session, self.use_cache)
        self.collection_events.append({
            "url": url,
            "year": year,
            "status": "ok" if html else "unavailable_or_blocked",
            "collection_date": self._data_version,
        })
        return html

    def parse_chart_page(self, html: str, year: int) -> List[Dict]:
        """
        Parse a RYM chart page and extract album information

        Returns a list of album dictionaries
        """
        albums = []
        try:
            soup = BeautifulSoup(html, "lxml")

            # Current RYM chart markup plus conservative legacy fallbacks.
            entries = (
                soup.select(".page_charts_section_charts_item")
                or soup.select(".page_section_charts_item")
                or soup.select("tr.chart_row")
                or soup.select("div.chart_item")
            )

            for position, entry in enumerate(entries, start=1):
                try:
                    title_elem = entry.select_one(
                        ".page_charts_section_charts_item_title a, "
                        "a.album_title, a.chart_item_link, a[href*='/release/album/']"
                    )
                    artist_elem = entry.select_one(
                        ".page_charts_section_charts_item_credited_links_primary a, "
                        "a.artist, span.artist, a[href*='/artist/']"
                    )
                    rating_elem = entry.select_one(
                        ".page_charts_section_charts_item_details_average_num, "
                        "span.avg_rating, span.rating, .score"
                    )

                    title = title_elem.get_text(" ", strip=True) if title_elem else None
                    artist = artist_elem.get_text(" ", strip=True) if artist_elem else None
                    avg_rating = self._first_number(
                        rating_elem.get_text(" ", strip=True) if rating_elem else ""
                    )

                    # Reject partial DOM matches instead of manufacturing plausible rows.
                    if not title or not artist or avg_rating is None or not 0 <= avg_rating <= 5:
                        continue

                    count_elem = entry.select_one(
                        ".page_charts_section_charts_item_details_ratings, "
                        "span.ratings_count, span.count"
                    )
                    count_text = count_elem.get_text(" ", strip=True) if count_elem else ""
                    count_match = re.search(r"([0-9][0-9,]*)", count_text)
                    ratings_count = int(count_match.group(1).replace(",", "")) if count_match else None

                    rank_elem = entry.select_one(
                        ".page_charts_section_charts_item_rank, .chart_rank, [class*=rank]"
                    )
                    rank = int(self._first_number(
                        rank_elem.get_text(" ", strip=True) if rank_elem else ""
                    ) or position)

                    genre_labels = []
                    for genre_link in entry.select("a[href*='/genre/']"):
                        label = genre_link.get_text(" ", strip=True)
                        if label and label not in genre_labels:
                            genre_labels.append(label)

                    release_url = urljoin(RYM_BASE_URL, title_elem.get("href") or "")

                    albums.append({
                        "title": title,
                        "artist": artist,
                        "year": year,
                        "rank": rank,
                        "avg_rating": avg_rating,
                        "ratings_count": ratings_count,
                        "genres": ", ".join(genre_labels) if genre_labels else None,
                        "source": "rym_web",
                        "source_url": release_url,
                        "collection_date": self._data_version,
                        "fetch_status": "ok",
                    })
                except (AttributeError, TypeError, ValueError):
                    continue

        except Exception as e:
            print(f"  [WARN] Failed to parse page: {e}")

        return albums

    @staticmethod
    def _first_number(value: str) -> Optional[float]:
        match = re.search(r"\d+(?:\.\d+)?", value.replace(",", ""))
        return float(match.group(0)) if match else None

    def get_top_albums_by_year(self, year: int, top_n: int = 100) -> pd.DataFrame:
        """
        Get the top N highest-rated albums of a given year

        Strategy:
        1. Try to collect the public RYM chart page.
        2. Return an empty, auditable result if collection is unavailable.
        3. Generate fixtures only when fallback_to_synthetic is explicitly enabled.

        Parameters:
        -----------
        year : int - year
        top_n : int - number of albums to return
        """
        print(f"\n[INFO] Fetching RYM {year} Top {top_n} album data...")

        # try scraping first
        html = self.fetch_chart_page("top", year)
        albums = []

        if html:
            albums = self.parse_chart_page(html, year)

        # if scraping returned too few albums, optionally fall back to synthetic data
        if len(albums) < top_n and self.fallback_to_synthetic:
            if albums:
                print(f"  [INFO] Only got {len(albums)} entries, supplementing with synthetic data up to {top_n}")
            else:
                print(f"  [INFO] Using synthetic data (simulated from RYM historical statistics)")

            synthetic = self._generate_synthetic_albums(year, top_n - len(albums))
            albums.extend(synthetic)

        df = pd.DataFrame(albums[:top_n])
        if not df.empty:
            if "rank" not in df.columns:
                df["rank"] = range(1, len(df) + 1)
            df["is_synthetic"] = df.get("source", "").astype(str).eq("synthetic")

        return df

    def _generate_synthetic_albums(self, year: int, n: int) -> List[Dict]:
        """
        Generate high-quality synthetic album data

        Based on known RYM statistical properties:
        - Rating distribution: mean around 3.3/5.0, std around 0.4, left-skewed
        - Rating counts: power-law distributed, top albums have thousands of ratings
        - Album counts vary by year (more recent years have more)
        """
        albums = []
        for i in range(n):
            # ratings follow a left-skewed distribution (high-quality albums cluster at the top)
            rating = min(5.0, max(1.0,
                self.rng.normal(3.3 + 0.2 * np.sin(year * 0.1), 0.4)
            ))

            # rating counts follow a power law
            ratings_count = int(max(50,
                self.rng.pareto(1.5) * 200 * (1 + (year - 2000) * 0.02)
            ))

            # genre distribution
            genres_pool = [
                "Indie Rock", "Electronic", "Hip-Hop", "Jazz", "Pop", "Metal",
                "Rock", "Folk", "R&B", "Classical", "Experimental", "Punk",
                "Alt. Rock", "Ambient", "Blues", "Reggae", "Country"
            ]
            n_genres = self.rng.integers(1, 4)
            genres = self.rng.choice(genres_pool, size=n_genres, replace=False).tolist()

            albums.append({
                "title": f"Album_{year}_{i+1:04d}",
                "artist": f"Artist_{year}_{i+1:04d}",
                "year": year,
                "avg_rating": round(rating, 2),
                "ratings_count": ratings_count,
                "genres": ", ".join(genres),
                "source": "synthetic",
                "collection_date": self._data_version,
            })

        return albums

    # ----------------------------------------------------------
    # Rating time series collection
    # ----------------------------------------------------------

    def get_album_ratings_timeline(self, album_id: int,
                                   start_date: str = "2020-01-01",
                                   end_date: str = "2026-07-01") -> pd.DataFrame:
        """
        Get an album's rating time series

        Key analytical value:
        - Observe statistical changes in rating patterns around the AI breakthrough
        - Detect changes in the shape of the rating distribution (variance, skewness, kurtosis)
        - Analyze temporal patterns in rating behavior (do AI ratings come more at night?)

        Returns a time series of daily rating aggregates
        """
        print(f"\n[INFO] Fetching rating timeline for album #{album_id}...")

        # generate the date range
        dates = pd.date_range(start=start_date, end=end_date, freq="D")

        # simulate daily rating data - based on patterns observed in real data
        n_days = len(dates)

        # baseline rating pattern
        base_mean = 3.3
        base_std = 0.5

        # AI shock effect: after ChatGPT, the mean rating drops slightly and the variance grows
        chatgpt_idx = dates.searchsorted(pd.Timestamp("2022-11-01"))

        daily_ratings = np.zeros(n_days)
        daily_counts = np.zeros(n_days, dtype=int)
        daily_review_ratio = np.zeros(n_days)

        for i in range(n_days):
            # daily rating count (weekday effect: more on weekends)
            weekday_factor = 1.5 if dates[i].weekday() >= 5 else 1.0
            base_count = self.rng.poisson(8 * weekday_factor)

            # after the AI shock, rating volume increases (AI batch generation)
            if i >= chatgpt_idx:
                ai_multiplier = 1.0 + 0.3 * (1 - np.exp(-(i - chatgpt_idx) / 180))
                base_count = int(base_count * ai_multiplier)

            daily_counts[i] = base_count

            # rating mean (AI reviews tend toward the middle, pulling down extremes)
            if i < chatgpt_idx:
                mean = base_mean + self.rng.normal(0, 0.05)
            else:
                # later period: mean drops slightly, variance grows
                mean = base_mean - 0.1 + self.rng.normal(0, 0.08)

            daily_ratings[i] = mean

            # review ratio (does the share of ratings with written reviews drop after the AI shock?)
            if i < chatgpt_idx:
                daily_review_ratio[i] = max(0.1, min(0.4,
                    self.rng.beta(6, 14)))
            else:
                # AI reviews less often come with detailed text
                daily_review_ratio[i] = max(0.05, min(0.3,
                    self.rng.beta(4, 16)))

        df = pd.DataFrame({
            "date": dates,
            "avg_daily_rating": daily_ratings,
            "rating_count": daily_counts,
            "review_ratio": daily_review_ratio,
            "estimated_ai_ratio": self._estimate_ai_ratio(dates, chatgpt_idx),
            "album_id": album_id,
            "source": "synthetic",
            "is_synthetic": True,
            "collection_date": self._data_version,
        })

        return df

    def _estimate_ai_ratio(self, dates: pd.DatetimeIndex,
                           chatgpt_idx: int) -> np.ndarray:
        """
        Estimate the daily share of AI-generated ratings

        Based on the following assumptions:
        - Before the ChatGPT release: close to 0%
        - 6 months after release: slowly rising to 5-10%
        - 1 year after release: illustrative generator assumption of 15-25%
        - After 2025: possibly reaching 30-40%
        """
        n = len(dates)
        ratios = np.zeros(n)

        if chatgpt_idx >= n:
            return ratios

        for i in range(chatgpt_idx, n):
            days_since = i - chatgpt_idx

            if days_since < 30:  # first month
                ratio = self.rng.uniform(0.001, 0.01)
            elif days_since < 180:  # months 1-6
                ratio = self.rng.uniform(0.01, 0.08)
            elif days_since < 365:  # months 6-12
                ratio = self.rng.uniform(0.05, 0.15)
            elif days_since < 730:  # years 1-2
                ratio = self.rng.uniform(0.12, 0.25)
            else:  # 2+ years
                ratio = self.rng.uniform(0.20, 0.40)

            ratios[i] = ratio

        # apply smoothing
        from scipy.ndimage import gaussian_filter1d
        ratios = gaussian_filter1d(ratios, sigma=3)

        return ratios

    # ----------------------------------------------------------
    # Forum discussion collection
    # ----------------------------------------------------------

    def get_forum_discussions(self, topic: str, pages: int = 5) -> pd.DataFrame:
        """
        Fetch RYM forum discussion data

        Analytical value: track how the community's perception of the AI shock evolves
        - How discussion activity changes over time
        - The shift in sentiment (from curiosity to concern)
        - The coping strategies proposed by the community
        """
        print(f"\n[INFO] Fetching RYM forum discussions: topic='{topic}'...")

        posts = []
        for page in range(pages):
            # simulate forum data
            base_date = pd.Timestamp("2023-01-01") + pd.Timedelta(days=page * 90)
            posts.append({
                "date": base_date,
                "title": f"[RYM Forum] About {topic} - page {page+1}",
                "replies": int(self.rng.poisson(30 - page * 3)),
                "views": int(self.rng.poisson(1500 - page * 100)),
                "sentiment": self.rng.choice(
                    ["Curious", "Concerned", "Opposed", "Accepting", "Discussing"],
                    p=[0.2, 0.3, 0.2, 0.1, 0.2]
                ),
                "topic": topic,
                "page": page + 1,
                "source": "synthetic",
                "is_synthetic": True,
                "collection_date": self._data_version,
            })

        return pd.DataFrame(posts)

    # ----------------------------------------------------------
    # Batch collection and saving
    # ----------------------------------------------------------

    def collect_yearly_charts(self, years: range = YEAR_RANGE,
                              top_n: int = 100) -> pd.DataFrame:
        """
        Collect chart data for multiple years

        This is the main data collection entry point
        """
        all_dfs = []
        for year in years:
            df = self.get_top_albums_by_year(year, top_n=top_n)
            if not df.empty:
                all_dfs.append(df)
            print(f"  [OK] {year}: got {len(df)} records")

        if not all_dfs:
            return pd.DataFrame(columns=[
                "title", "artist", "year", "avg_rating", "ratings_count",
                "genres", "source", "collection_date", "rank", "is_synthetic",
            ])
        combined = pd.concat(all_dfs, ignore_index=True)
        return combined

    def collect_ratings_timeline(self, album_ids: List[int]) -> pd.DataFrame:
        """Collect rating time series for multiple albums"""
        all_dfs = []
        for aid in album_ids:
            df = self.get_album_ratings_timeline(aid)
            if not df.empty:
                all_dfs.append(df)
        return pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()

    def save_data(self, df: pd.DataFrame, filename: str):
        """Save data to CSV"""
        path = RAW_DIR / filename
        df.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"  [OK] Data saved: {path} ({len(df)} rows)")
        return path

    def generate_full_dataset(self) -> Dict[str, pd.DataFrame]:
        """
        Generate the complete dataset

        Returns a dictionary containing all collected data
        """
        print("\n" + "=" * 60)
        print("[INFO] RYM data collection - start")
        print("=" * 60)

        datasets = {}

        # 1. yearly chart data (2000-2026)
        print("\n[1/3] Collecting yearly chart data...")
        yearly = self.collect_yearly_charts(
            years=range(2000, 2027), top_n=100
        )
        datasets["yearly_charts"] = yearly
        self.save_data(yearly, "rym_yearly_charts_2000_2026.csv")

        # 2. rating time series (multiple representative albums)
        print("\n[2/3] Collecting rating time series...")
        if self.fallback_to_synthetic:
            sample_album_ids = [1001, 1002, 1003, 1004, 1005]
            timeline = self.collect_ratings_timeline(sample_album_ids)
        else:
            print("  [INFO] Skipping synthetic RYM timeline; no public timeline endpoint is available")
            timeline = pd.DataFrame()
        datasets["ratings_timeline"] = timeline
        if not timeline.empty:
            self.save_data(timeline, "rym_ratings_timeline.csv")

        # 3. forum discussions
        print("\n[3/3] Collecting forum discussion data...")
        if self.fallback_to_synthetic:
            topics = ["AI review", "chatbot", "fake rating", "AI music", "GPT"]
            forum_dfs = []
            for topic in topics:
                df = self.get_forum_discussions(topic, pages=3)
                forum_dfs.append(df)
            forum_data = pd.concat(forum_dfs, ignore_index=True)
        else:
            print("  [INFO] Skipping synthetic RYM forum discussions")
            forum_data = pd.DataFrame()
        datasets["forum_discussions"] = forum_data
        self.save_data(forum_data, "rym_forum_ai_discussions.csv")

        if self.collection_events:
            events = pd.DataFrame(self.collection_events)
            self.save_data(events, "rym_collection_events.csv")

        print("\n" + "=" * 60)
        print("[OK] RYM data collection complete")
        print(f"   Yearly charts: {len(yearly)} records")
        print(f"   Rating timeline: {len(timeline) if not timeline.empty else 0} records")
        print(f"   Forum discussions: {len(forum_data)} records")
        print("=" * 60)

        return datasets


# ============================================================
# Standalone run
# ============================================================

if __name__ == "__main__":
    collector = RYMDataCollector(delay=2.0, use_cache=True)
    datasets = collector.generate_full_dataset()

    # show a data preview
    for name, df in datasets.items():
        print(f"\n[INFO] {name} preview:")
        print(df.head(3).to_string())
