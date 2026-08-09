"""
AOTY (Album of The Year) data collection framework
==================================================

Core design principles:
1. Real scraper first - prefer collecting real data from AOTY public pages
2. Auditable degradation - when real scraping is restricted, record the
   failure explicitly instead of silently mixing synthetic rows into the
   research dataset
3. Multi-dimensional collection - full coverage of ratings, reviews, genre trends, and user behavior

Key differences from the RYM collector:
- AOTY ratings use a 10-point scale (vs RYM's 5-point scale)
- AOTY places more emphasis on social media integration
- AOTY has a well-defined "album of the year" chart structure
"""

import hashlib
import re
import time
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

import sys
from pathlib import Path

_SRC = str(Path(__file__).resolve().parent.parent)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

from config import (
    AOTY_BASE_URL, REQUEST_DELAY, REQUEST_TIMEOUT,
    MAX_RETRIES, USER_AGENT, RAW_DIR, RANDOM_SEED,
    TARGET_GENRES, PRE_AI_YEARS, POST_AI_YEARS
)


# ============================================================
# AOTY data collector
# ============================================================

class AOTYDataCollector:
    """AOTY data collector"""

    def __init__(self, delay: float = REQUEST_DELAY,
                 use_cache: bool = True,
                 fallback_to_synthetic: bool = False):
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
    # Page requests
    # ----------------------------------------------------------

    def _cache_path(self, url: str) -> Path:
        url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()
        return RAW_DIR / f"cache_aoty_{url_hash}.html"

    @staticmethod
    def _looks_blocked(html: str) -> bool:
        blocked_markers = [
            "Enable JavaScript and cookies to continue",
            "cf_chl_opt",
            "challenge-platform",
            "Just a moment",
        ]
        return any(marker in html for marker in blocked_markers)

    def _request(self, url: str) -> Optional[str]:
        """HTTP request with delay, cache, and explicit challenge detection."""
        cache_file = self._cache_path(url)
        if self.use_cache and cache_file.exists():
            html = cache_file.read_text(encoding="utf-8", errors="ignore")
            if html and not self._looks_blocked(html):
                self.collection_events.append({
                    "url": url,
                    "status": "cache_hit",
                    "collection_date": self._data_version,
                })
                return html

        time.sleep(self.delay)
        for attempt in range(MAX_RETRIES):
            try:
                resp = self.session.get(url, timeout=REQUEST_TIMEOUT)
                status = resp.status_code
                html = resp.text or ""
                if status == 200 and html and not self._looks_blocked(html):
                    cache_file.write_text(html, encoding="utf-8")
                    self.collection_events.append({
                        "url": url,
                        "status": "ok",
                        "http_status": status,
                        "collection_date": self._data_version,
                    })
                    return html

                self.collection_events.append({
                    "url": url,
                    "status": "blocked_or_empty",
                    "http_status": status,
                    "collection_date": self._data_version,
                })
                print(f"  [WARN] AOTY returned blocked/empty content: {url} (HTTP {status})")
                return None
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    print(f"  [WARN] Request failed (attempt {attempt+1}): {e}")
                    time.sleep(self.delay * (2 ** attempt))
                else:
                    print(f"  [FAIL] Request failed: {url}")
                    self.collection_events.append({
                        "url": url,
                        "status": "request_failed",
                        "error": str(e),
                        "collection_date": self._data_version,
                    })
                    return None
        return None

    @staticmethod
    def _parse_number(text: str) -> Optional[float]:
        if text is None:
            return None
        cleaned = re.sub(r"[^0-9.]", "", str(text))
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None

    @staticmethod
    def _absolute_url(href: Optional[str]) -> Optional[str]:
        if not href:
            return None
        if href.startswith("http"):
            return href
        return f"{AOTY_BASE_URL}{href}"

    # ----------------------------------------------------------
    # Real album chart data
    # ----------------------------------------------------------

    def get_user_highest_rated_albums(self, year: int,
                                      page: int = 1) -> pd.DataFrame:
        """
        Fetch AOTY's public user-highest-rated album chart.

        The result is album-level public chart data: title, artist, year,
        user score, rating count, genres, rank, and source URL. It is not a
        dump of individual user ratings.
        """
        page_part = "" if page == 1 else f"{page}/"
        url = f"{AOTY_BASE_URL}/ratings/user-highest-rated/{year}/{page_part}"
        print(f"  [INFO] Fetching AOTY user chart: {year} page {page}")

        html = self._request(url)
        if not html:
            return pd.DataFrame()

        rows = self._parse_user_chart_page(html, year=year, page=page, url=url)
        return pd.DataFrame(rows)

    def _parse_user_chart_page(self, html: str, year: int,
                               page: int, url: str) -> List[Dict]:
        soup = BeautifulSoup(html, "lxml")
        rows: List[Dict] = []

        candidates = (
            soup.select(".albumListRow")
            or soup.select(".albumBlock")
            or soup.select(".albumBlockSmall")
            or soup.select("[class*=album][class*=Row]")
        )

        for idx, item in enumerate(candidates, start=1):
            text = item.get_text(" ", strip=True)
            if not text:
                continue

            links = item.select("a[href]")
            album_link = next(
                (a for a in links if "/album/" in (a.get("href") or "")),
                links[0] if links else None,
            )
            artist_link = next(
                (a for a in links if "/artist/" in (a.get("href") or "")),
                None,
            )

            title = album_link.get_text(" ", strip=True) if album_link else None
            artist = artist_link.get_text(" ", strip=True) if artist_link else None

            rank = self._parse_rank(item, text) or ((page - 1) * 25 + idx)
            user_score = self._parse_user_score(item, text)
            ratings_count = self._parse_rating_count(item, text)
            genres = self._parse_genres(item)
            release_date = self._parse_release_date(text)

            if title and artist:
                rows.append({
                    "album_id": self._absolute_url(album_link.get("href")) if album_link else None,
                    "title": title,
                    "artist": artist,
                    "year": year,
                    "rank": rank,
                    "rating": user_score,
                    "ratings_count": ratings_count,
                    "genres": ", ".join(genres) if genres else None,
                    "release_date": release_date,
                    "source": "aoty_web",
                    "source_url": url,
                    "page": page,
                    "is_synthetic": False,
                    "collection_date": self._data_version,
                    "fetch_status": "ok",
                    "notes": "AOTY public user-highest-rated album chart; album-level public aggregate.",
                })

        if rows:
            return rows

        # Fallback for pages rendered into plain text by another fetcher.
        return self._parse_user_chart_text(soup.get_text("\n", strip=True), year, page, url)

    @staticmethod
    def _parse_rank(item, text: str) -> Optional[int]:
        rank_elem = item.select_one(".rank, .albumListRank, [class*=rank]")
        rank_text = rank_elem.get_text(" ", strip=True) if rank_elem else text[:12]
        match = re.search(r"\b(\d{1,4})\s*[.)]", rank_text)
        return int(match.group(1)) if match else None

    @classmethod
    def _parse_user_score(cls, item, text: str) -> Optional[float]:
        for sel in [".userScore", ".rating", ".score", "[class*=user][class*=Score]"]:
            elem = item.select_one(sel)
            if elem:
                value = cls._parse_number(elem.get_text(" ", strip=True))
                if value is not None and 0 <= value <= 100:
                    return value
        match = re.search(r"USER\s+SCORE\s+([0-9]{1,3})", text, re.I)
        if match:
            return float(match.group(1))
        return None

    @classmethod
    def _parse_rating_count(cls, item, text: str) -> Optional[int]:
        for sel in [".ratingCount", ".userRatingCount", "[class*=rating][class*=Count]"]:
            elem = item.select_one(sel)
            if elem:
                value = cls._parse_number(elem.get_text(" ", strip=True))
                return int(value) if value is not None else None
        match = re.search(r"([0-9,]+)\s+(?:ratings|user ratings|votes)", text, re.I)
        if match:
            return int(match.group(1).replace(",", ""))
        return None

    @staticmethod
    def _parse_genres(item) -> List[str]:
        genres = []
        for link in item.select("a[href*='/genre/'], a[href*='/tag/']"):
            label = link.get_text(" ", strip=True)
            if label and label not in genres:
                genres.append(label)
        return genres

    @staticmethod
    def _parse_release_date(text: str) -> Optional[str]:
        match = re.search(
            r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b",
            text,
        )
        return match.group(0) if match else None

    def _parse_user_chart_text(self, text: str, year: int,
                               page: int, url: str) -> List[Dict]:
        """Best-effort parser for text snapshots. Keeps only high-confidence rows."""
        rows: List[Dict] = []
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for i, line in enumerate(lines):
            rank_match = re.match(r"^(\d{1,4})[.)]\s+(.+?)\s+-\s+(.+)$", line)
            if not rank_match:
                continue
            nearby = " ".join(lines[i:i + 8])
            score_match = re.search(r"USER\s+SCORE\s+([0-9]{1,3})", nearby, re.I)
            if not score_match:
                continue
            rows.append({
                "album_id": None,
                "title": rank_match.group(2).strip(),
                "artist": rank_match.group(3).strip(),
                "year": year,
                "rank": int(rank_match.group(1)),
                "rating": float(score_match.group(1)),
                "ratings_count": None,
                "genres": None,
                "release_date": self._parse_release_date(nearby),
                "source": "aoty_text_snapshot",
                "source_url": url,
                "page": page,
                "is_synthetic": False,
                "collection_date": self._data_version,
                "fetch_status": "ok_text_snapshot",
                "notes": "Parsed from public AOTY chart text snapshot; album-level aggregate.",
            })
        return rows

    def collect_user_highest_rated_charts(self,
                                          years: range = range(2020, 2027),
                                          pages_per_year: int = 2) -> pd.DataFrame:
        all_dfs = []
        for year in years:
            for page in range(1, pages_per_year + 1):
                df = self.get_user_highest_rated_albums(year, page=page)
                if df.empty:
                    print(f"  [WARN] No AOTY rows parsed for {year} page {page}")
                    break
                all_dfs.append(df)
        return pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()

    # ----------------------------------------------------------
    # Album rating data
    # ----------------------------------------------------------

    def get_album_ratings(self, album_id: str = "example") -> pd.DataFrame:
        """
        Fetch rating data for a single album

        Key analysis dimensions:
        - Rating distribution (histogram): AI ratings tend to cluster near the mean
        - Review text features: the linguistic patterns of AI reviews
        - User activity: differences in rating behavior between new and old users

        Parameters:
        -----------
        album_id : str - AOTY album identifier
        """
        print(f"\n[INFO] Fetching AOTY album #{album_id} rating data...")

        # Try to scrape real data
        url = f"{AOTY_BASE_URL}/album/{album_id}/ratings"
        html = self._request(url)

        if html:
            parsed = self._parse_ratings_page(html)
            if parsed:
                df = pd.DataFrame(parsed)
                df["album_id"] = album_id
                df["source"] = "aoty_web"
                df["source_url"] = url
                df["is_synthetic"] = False
                df["collection_date"] = self._data_version
                return df

        if self.fallback_to_synthetic:
            return self._generate_ratings_data(album_id)

        return pd.DataFrame(columns=[
            "album_id", "rating", "has_review", "user_age_days", "timestamp",
            "source", "source_url", "is_synthetic", "collection_date",
        ])

    def _parse_ratings_page(self, html: str) -> Optional[List[Dict]]:
        """Parse an AOTY ratings page"""
        try:
            soup = BeautifulSoup(html, "lxml")
            ratings = []
            # AOTY rating item selectors (may need to be adjusted to the actual page structure)
            items = soup.select("div.ratingItem, tr.rating-row, .review-item")

            for item in items[:500]:  # Cap at 500 items
                try:
                    rating = {
                        "rating": self._extract_rating(item),
                        "has_review": self._has_review(item),
                        "user_age_days": self._extract_user_age(item),
                        "timestamp": self._extract_timestamp(item),
                    }
                    if rating["rating"] is not None:
                        ratings.append(rating)
                except Exception:
                    continue

            return ratings if ratings else None
        except Exception:
            return None

    @staticmethod
    def _extract_rating(item) -> Optional[float]:
        """Extract the rating value"""
        for sel in ["span.rating", ".score", ".userScore"]:
            elem = item.select_one(sel)
            if elem:
                try:
                    return float(elem.get_text(strip=True))
                except ValueError:
                    pass
        return None

    @staticmethod
    def _has_review(item) -> bool:
        """Check whether the item contains a written review"""
        for sel in [".review-text", ".comment", "p.review"]:
            if item.select_one(sel):
                return True
        return False

    @staticmethod
    def _extract_user_age(item) -> Optional[int]:
        """Extract the user's account age in days"""
        for sel in [".userAge", ".memberSince", ".joinDate"]:
            elem = item.select_one(sel)
            if elem:
                text = elem.get_text(strip=True)
                # Try to parse the number of days
                import re
                nums = re.findall(r'\d+', text)
                if nums:
                    return int(nums[0])
        return None

    @staticmethod
    def _extract_timestamp(item) -> Optional[str]:
        """Extract the rating timestamp"""
        for sel in ["time", ".date", ".timestamp", "span.date"]:
            elem = item.select_one(sel)
            if elem:
                ts = elem.get("datetime") or elem.get_text(strip=True)
                if ts:
                    return ts
        return None

    def _generate_ratings_data(self, album_id: str) -> pd.DataFrame:
        """
        Generate high-quality synthetic rating data

        Based on known AOTY statistical characteristics:
        - 10-point scale, mean around 7.2, standard deviation around 1.8
        - The rating distribution is slightly left-skewed
        - About 20-30% of ratings include a written review
        - After ChatGPT's release: rating variance increases and extreme ratings decrease
        """
        n_ratings = self.rng.poisson(800)

        # Timestamp distribution
        timestamps = pd.date_range(
            start="2020-01-01", end="2026-07-01",
            periods=n_ratings
        )

        # Generate ratings (distributional differences before and after the AI shock)
        ratings = np.zeros(n_ratings)
        for i, ts in enumerate(timestamps):
            if ts < pd.Timestamp("2022-11-01"):
                # Pre-AI era: normal distribution
                r = self.rng.normal(7.2, 1.8)
            else:
                # AI era: mean drops slightly, variance increases slightly, extreme values decrease
                r = self.rng.normal(7.0, 2.0)
                # But AI ratings tend to be moderate (6-8 range)
                if self.rng.random() < 0.15:  # 15% chance the rating is AI-generated
                    r = self.rng.normal(7.0, 0.8)  # More concentrated distribution
            ratings[i] = np.clip(r, 1, 10)

        # User account age in days (more new users appear in the later period)
        user_ages = np.zeros(n_ratings)
        for i, ts in enumerate(timestamps):
            if ts < pd.Timestamp("2022-11-01"):
                user_ages[i] = self.rng.exponential(800)
            else:
                # More new users flood in during the later period (including AI accounts)
                user_ages[i] = self.rng.exponential(300)

        df = pd.DataFrame({
            "album_id": album_id,
            "rating": ratings.round(1),
            "has_review": self.rng.choice([True, False], n_ratings, p=[0.25, 0.75]),
            "user_age_days": user_ages.astype(int),
            "timestamp": timestamps,
            "is_verified_user": self.rng.choice([True, False], n_ratings, p=[0.6, 0.4]),
            "is_synthetic": True,
            "collection_date": self._data_version,
        })

        return df

    # ----------------------------------------------------------
    # Genre trends
    # ----------------------------------------------------------

    def get_genre_trends(self, genre: str,
                         years: range) -> pd.DataFrame:
        """
        Fetch the rating trends of a genre over a given set of years

        Used to analyze:
        - Whether the AI shock has differential effects across genres
        - Which genres are more susceptible to AI review penetration
        - Changes in rating consensus within a genre
        """
        print(f"  [INFO] Fetching rating trends for genre '{genre}'...")

        data = []
        for year in years:
            # AI shock effect: some genres are affected more than others
            ai_sensitivity = {
                "Indie Rock": 0.8, "Electronic": 0.7, "Hip-Hop": 0.6,
                "Jazz": 0.3, "Pop": 0.9, "Metal": 0.4,
                "Rock": 0.5, "Folk": 0.3, "R&B": 0.6,
                "Classical": 0.2, "Experimental": 0.5, "Punk": 0.4,
            }
            sensitivity = ai_sensitivity.get(genre, 0.5)

            # Whether the genre has already been affected by AI
            ai_impacted = year >= 2023
            impact_factor = sensitivity * 0.15 if ai_impacted else 0

            data.append({
                "year": year,
                "genre": genre,
                "avg_rating": round(
                    7.0 + self.rng.normal(0, 0.3) - impact_factor, 2
                ),
                "albums_count": int(self.rng.poisson(200 + (year - 2000) * 5)),
                "ratings_count": int(self.rng.poisson(
                    10000 + (year - 2000) * 500
                )),
                "critic_score": round(
                    75 + self.rng.normal(0, 5) - impact_factor * 20, 1
                ),
                "user_score": round(
                    7.0 + self.rng.normal(0, 0.3) - impact_factor, 1
                ),
                "score_gap": round(
                    abs(self.rng.normal(0.5, 0.3) + impact_factor), 2
                ),
                "ai_sensitivity": sensitivity,
                "source": "synthetic",
                "is_synthetic": True,
                "collection_date": self._data_version,
            })

        return pd.DataFrame(data)

    # ----------------------------------------------------------
    # Batch collection
    # ----------------------------------------------------------

    def collect_all_genre_trends(self,
                                  years: range = range(2010, 2027)) -> pd.DataFrame:
        """Collect rating trends for all target genres"""
        print("\n[INFO] Collecting AOTY genre trend data...")

        all_dfs = []
        for genre in TARGET_GENRES:
            df = self.get_genre_trends(genre, years)
            all_dfs.append(df)

        combined = pd.concat(all_dfs, ignore_index=True)
        return combined

    def generate_full_dataset(self) -> Dict[str, pd.DataFrame]:
        """Generate the complete AOTY dataset"""
        print("\n" + "=" * 60)
        print("[INFO] AOTY data collection - start")
        print("=" * 60)

        datasets = {}

        # 1. Genre trends
        print("\n[1/2] Collecting genre rating trends...")
        if self.fallback_to_synthetic:
            genre_trends = self.collect_all_genre_trends()
        else:
            genre_trends = pd.DataFrame()
        datasets["genre_trends"] = genre_trends

        if not genre_trends.empty:
            path = RAW_DIR / "aoty_genre_trends_2010_2026.csv"
            genre_trends.to_csv(path, index=False, encoding="utf-8-sig")
            print(f"  [SAVE] Saved: {path} ({len(genre_trends)} rows)")

        # 2. Real public album aggregate ratings
        print("\n[2/2] Collecting real AOTY public album aggregates...")
        ratings = self.collect_user_highest_rated_charts(
            years=range(2020, 2027),
            pages_per_year=2,
        )
        datasets["album_ratings"] = ratings

        if not ratings.empty:
            path = RAW_DIR / "aoty_album_ratings.csv"
            ratings.to_csv(path, index=False, encoding="utf-8-sig")
            print(f"  [SAVE] Saved: {path} ({len(ratings)} rows)")
        else:
            print("  [WARN] No real AOTY rows collected; leaving existing files untouched")

        metadata_path = RAW_DIR / "aoty_collection_events.csv"
        if self.collection_events:
            pd.DataFrame(self.collection_events).to_csv(
                metadata_path, index=False, encoding="utf-8-sig"
            )
            print(f"  [SAVE] Saved collection events: {metadata_path}")

        print("\n" + "=" * 60)
        print("[OK] AOTY data collection complete")
        print(f"   Genre trends: {len(genre_trends)} rows")
        print(f"   Album ratings: {len(ratings)} rows")
        print("=" * 60)

        return datasets


# ============================================================
# Standalone execution
# ============================================================

if __name__ == "__main__":
    collector = AOTYDataCollector(delay=2.0, use_cache=True)
    datasets = collector.generate_full_dataset()

    for name, df in datasets.items():
        print(f"\n[INFO] {name} preview:")
        print(df.head(3).to_string())
