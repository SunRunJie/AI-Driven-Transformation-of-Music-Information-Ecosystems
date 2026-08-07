"""
Central configuration and constants
===================================

A single academic-grade configuration module that keeps every tunable
parameter, path, and API setting in one place. Follows a
"configuration as documentation" principle: each parameter carries its
units, range, and a short explanation.
"""

import os
from pathlib import Path
from typing import Dict, List

# ================================================================
# 1. Project paths
# ================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
EXTERNAL_DIR = DATA_DIR / "external"
SRC_DIR = PROJECT_ROOT / "src"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
FIGURES_DIR = PROJECT_ROOT / "figures"
REPORT_DIR = PROJECT_ROOT / "docs"

# Create all directories automatically
for d in [RAW_DIR, PROCESSED_DIR, EXTERNAL_DIR, FIGURES_DIR, REPORT_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ================================================================
# 2. Web scraping configuration
# ================================================================

REQUEST_DELAY = 2.0        # Seconds between requests (polite crawling)
REQUEST_TIMEOUT = 30       # Request timeout (seconds)
MAX_RETRIES = 3            # Maximum retry attempts
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

# -- RYM (RateYourMusic) --
RYM_BASE_URL = "https://rateyourmusic.com"
RYM_CHARTS_URL = f"{RYM_BASE_URL}/charts"
RYM_TOP_URL = f"{RYM_BASE_URL}/customchart"
RYM_SEARCH_PARAMS = {
    "genre_include": 1,
    "include_child_genres": 1,
    "type": "l",
    "year_min": 2000,
    "year_max": 2026,
}

# -- AOTY (Album of The Year) --
AOTY_BASE_URL = "https://www.albumoftheyear.org"

# -- Last.fm (real API data source) --
LASTFM_API_KEY = ""        # Fill in your real API key: https://www.last.fm/api
LASTFM_API_SECRET = ""
LASTFM_BASE_URL = "https://ws.audioscrobbler.com/2.0/"

# -- Discogs API --
DISCOGS_TOKEN = ""
DISCOGS_BASE_URL = "https://api.discogs.com/"

# -- MusicBrainz API --
MUSICBRAINZ_BASE_URL = "https://musicbrainz.org/ws/2/"


# ================================================================
# 3. Core research parameters
# ================================================================

# Study time window
STUDY_START_YEAR = 2002     # Year RYM was founded
STUDY_END_YEAR = 2026       # Current year
YEAR_RANGE = range(STUDY_START_YEAR, STUDY_END_YEAR + 1)

# Key structural break: ChatGPT release date
CHATGPT_RELEASE_DATE = "2022-11-01"

# AI-impact period segments
PRE_AI_YEARS = range(2018, 2023)      # Baseline period
EARLY_AI_YEARS = range(2023, 2025)    # Early impact period
LATE_AI_YEARS = range(2025, 2027)     # Deepening period
POST_AI_YEARS = range(2023, 2027)     # Full post-ChatGPT window

# Analysis window parameters
ROLLING_WINDOW = 30          # Rolling mean window (days)
ROLLING_WINDOW_WEEKLY = 8    # Weekly rolling window (8 weeks)
CUSUM_THRESHOLD = 1.96       # CUSUM threshold (95% confidence level)
BOOTSTRAP_ITERATIONS = 1000  # Bootstrap resamples
MONTE_CARLO_SIMULATIONS = 5000  # Monte Carlo simulations

# -- Trust threshold model parameters --
TRUST_MODEL_PARAMS: Dict = {
    "alpha": 0.7,            # Preference intensity for genuine reviews [0,1]
    "beta": 2.0,             # Signal-to-noise ratio: user discrimination [0.1,10]
    "gamma": 0.3,            # Network effect strength [0,1]
    "trust_threshold": 0.4,  # Trust collapse threshold [0,1]
    "heterogeneity": True,   # Enable user heterogeneity
    "network_effects": True, # Enable network effects
}

# -- AI review detection parameters --
TFIDF_MAX_FEATURES = 2000    # Max TF-IDF features
NGRAM_RANGE = (1, 3)         # n-gram range
RF_N_ESTIMATORS = 500        # Number of random forest trees (for stability)
BERT_MODEL_NAME = "bert-base-uncased"  # Optional BERT model
DETECTION_CONFIDENCE = 0.85  # Detection confidence threshold

# -- Monte Carlo simulation parameters --
MC_PENETRATION_INIT = 0.01   # Initial AI penetration rate
MC_MONTHLY_GROWTH = 0.03     # Monthly growth rate
MC_TIME_HORIZON = 240        # Simulation horizon in months (20 years)
MC_N_SIMULATIONS = 1000      # Number of simulations

# -- Data quality thresholds --
MIN_SAMPLE_SIZE = 30         # Minimum sample size (required for statistical tests)
MIN_ALBUMS_PER_YEAR = 50     # Minimum albums per year
QUALITY_CONFIDENCE = 0.95    # Data quality confidence

# -- Sensitivity analysis parameter ranges --
SENSITIVITY_ALPHA_RANGE = [0.5, 0.6, 0.7, 0.8, 0.9]
SENSITIVITY_BETA_RANGE = [0.5, 1.0, 2.0, 3.0, 5.0]
SENSITIVITY_GAMMA_RANGE = [0.0, 0.15, 0.3, 0.45, 0.6]


# ================================================================
# 4. Classification and label system
# ================================================================

# Target genres (core coverage of the independent-music space)
TARGET_GENRES: List[str] = [
    "Indie Rock", "Electronic", "Hip-Hop", "Jazz", "Pop", "Metal",
    "Rock", "Folk", "R&B", "Classical", "Experimental", "Punk",
    "Ambient", "Blues", "Reggae", "Alt. Rock", "Pop Rock",
]

# Genres considered in sensitivity analyses (English labels only)
GENRE_EN_CN: Dict[str, str] = {
    "Indie Rock": "Indie Rock",
    "Electronic": "Electronic",
    "Hip-Hop": "Hip-Hop",
    "Jazz": "Jazz",
    "Pop": "Pop",
    "Metal": "Metal",
    "Rock": "Rock",
    "Folk": "Folk",
    "R&B": "R&B",
    "Classical": "Classical",
    "Experimental": "Experimental",
    "Punk": "Punk",
    "Ambient": "Ambient",
    "Blues": "Blues",
    "Reggae": "Reggae",
    "Alt. Rock": "Alt. Rock",
    "Pop Rock": "Pop Rock",
}

# Platforms in the competitive landscape analysis
PLATFORMS: List[str] = [
    "RYM", "AOTY", "Pitchfork", "Discogs",
    "Spotify", "Bandcamp", "Douban Music", "Last.fm",
    "SoundCloud",
]

# Full platform names
PLATFORM_CN: Dict[str, str] = {
    "RYM": "RateYourMusic",
    "AOTY": "Album of The Year",
    "Pitchfork": "Pitchfork",
    "Discogs": "Discogs",
    "Spotify": "Spotify",
    "Bandcamp": "Bandcamp",
    "Douban Music": "Douban Music",
    "Last.fm": "Last.fm",
    "SoundCloud": "SoundCloud",
}

# Method labels used in reports
METHOD_EN_CN: Dict[str, str] = {
    "CUSUM": "Cumulative Sum Test",
    "Chow": "Chow Test",
    "Bai-Perron": "Bai-Perron Multiple Breaks",
    "TF-IDF": "Term Frequency-Inverse Document Frequency",
    "Random Forest": "Random Forest",
    "BERT": "BERT Deep Semantic Model",
    "S-curve": "S-shaped Phase Transition Curve",
    "Monte Carlo": "Monte Carlo Simulation",
}


# ================================================================
# 5. File naming conventions
# ================================================================

FILES: Dict[str, str] = {
    # -- Raw data --
    "rym_albums": "rym_top_albums_{year}.csv",
    "rym_ratings": "rym_album_ratings_{album_id}.csv",
    "rym_forum": "rym_forum_{topic}.csv",
    "rym_yearly_charts": "rym_yearly_charts_{year}.csv",
    "aoty_ratings": "aoty_album_ratings.csv",
    "aoty_genre_trends": "aoty_genre_trends_2010_2026.csv",
    "lastfm_album_data": "lastfm_album_data.csv",
    "discogs_releases": "discogs_releases.csv",

    # -- Processed data --
    "merged_ratings": "merged_ratings_timeseries.csv",
    "review_texts": "review_texts_labeled.csv",
    "feature_engineered": "feature_engineered_data.csv",

    # -- External data --
    "reddit_posts": "reddit_ai_discussions.csv",

    # -- Figure outputs --
    "figure_break": "structural_break_analysis.png",
    "figure_ai_features": "ai_vs_human_review_features.png",
    "figure_trust": "trust_threshold_model.png",
    "figure_competitive": "competitive_landscape.png",
    "figure_four_dimensions": "four_dimensions_framework.png",
    "figure_genre_impact": "genre_impact_heatmap.png",
    "figure_rating_dist": "rating_distribution_evolution.png",
    "figure_timeline": "ai_impact_timeline.png",
    "figure_heterogeneous_trust": "heterogeneous_trust.png",
    "figure_policy_intervention": "policy_intervention.png",
    "figure_sensitivity": "sensitivity_analysis.png",
    "figure_correlation": "feature_correlation_heatmap.png",

    # -- Report outputs --
    "report": "analysis_report.md",
    "report_pdf": "analysis_report.pdf",
}

# Figure descriptions (used in the report appendix)
FIGURE_DESCRIPTIONS: Dict[str, str] = {
    "structural_break_analysis.png": "Three-panel structural break analysis - CUSUM test + rolling statistics + ChatGPT break annotation",
    "ai_vs_human_review_features.png": "AI vs human feature comparison - radar plot (polar projection) + diverging difference bar chart",
    "trust_threshold_model.png": "Trust threshold model - S-shaped phase transition curve + multi-scenario Monte Carlo simulation",
    "competitive_landscape.png": "Competitive landscape quadrant bubble chart - data depth x social experience, log-scale bubbles",
    "four_dimensions_framework.png": "AI impact four-dimensional framework - grouped bar impact assessment + strategic priority matrix",
    "genre_impact_heatmap.png": "Genre-differentiated impact heatmap - cool/warm gradient + marginal sensitivity ranking",
    "rating_distribution_evolution.png": "Rating distribution evolution - KDE density comparison before/after ChatGPT + K-S test annotation",
    "ai_impact_timeline.png": "Serpentine timeline - alternating event layout + large text + AI penetration S-curve",
    "heterogeneous_trust.png": "Heterogeneous user trust curves - four user groups + safe/warning/collapse zones",
    "policy_intervention.png": "Policy intervention comparison - no intervention / AI detection / user education / dual intervention",
    "sensitivity_analysis.png": "Parameter sensitivity analysis - alpha (preference) / beta (discrimination) / gamma (network)",
    "feature_correlation_heatmap.png": "Feature correlation matrix - Pearson correlations across 11 linguistic features",
}


# ================================================================
# 6. Randomness and reproducibility
# ================================================================

RANDOM_SEED = 42             # Global random seed (full reproducibility)
NP_RNG = None                # numpy random generator (initialized by programs)


def get_rng():
    """Return a reproducible random number generator."""
    global NP_RNG
    if NP_RNG is None:
        import numpy as np
        NP_RNG = np.random.default_rng(RANDOM_SEED)
    return NP_RNG


# ================================================================
# 7. Visualization style configuration
# ================================================================

# Academic color scheme (Nature/Science style, colorblind friendly)
ACADEMIC_COLORS = {
    # Main palette (from Nature color schemes)
    "blue": "#3B75AF",        # Deep blue
    "red": "#CC3311",         # Vermilion
    "green": "#228833",       # Green
    "orange": "#EE7733",      # Orange
    "purple": "#AA3377",      # Purple
    "cyan": "#33BBEE",        # Cyan
    "gray": "#BBBBBB",        # Gray
    "dark": "#222222",        # Body text black
    "light_blue": "#A0C4E8",
    "light_red": "#F4A8A0",
    "light_green": "#A8D8A8",
    "light_orange": "#FAD6A0",
    "light_purple": "#D4A0C8",
}

# Colorblind-friendly palette (based on Wong, 2011, Nature Methods)
COLORBLIND_PALETTE = [
    "#0077BB",  # Blue
    "#EE7733",  # Orange
    "#228833",  # Green
    "#CC3311",  # Red
    "#33BBEE",  # Cyan
    "#AA3377",  # Purple
    "#BBBBBB",  # Gray
]

# Standard figure sizes (16:9 widescreen, PPT-friendly)
FIGURE_WIDTH = 16
FIGURE_HEIGHT = 9
FIGURE_DPI = 150
SAVE_DPI = 300

# Font names (used by the visualization module)
CHINESE_FONT = "SimSun"
ENGLISH_FONT = "Times New Roman"
MONO_FONT = "Consolas"


# ================================================================
# 8. Report metadata
# ================================================================

REPORT_META = {
    "title_cn": "Generative AI and the Transformation of Music Information Ecosystems",
    "title_en": "Generative AI and the Transformation of Music Information Ecosystems",
    "subtitle": "A Dual-Case Study of AOTY (Album of The Year) and RYM (RateYourMusic)",
    "competition": "Undergraduate Research Project - Management Science / Information Systems",
    "framework": "Signal-Institution Framework",
    "core_theory": "Signaling Theory - Lemons Market - Institutional Change - Second-Order Observation - Trust Paradox",
    "version": "v2.0",
    "generated": "",  # Filled in programmatically
}

# Key references (core literature in BibTeX-style)
REFERENCES = [
    {
        "key": "akerlof1970",
        "text": "Akerlof, G. (1970). The Market for 'Lemons': Quality Uncertainty and the Market Mechanism. Quarterly Journal of Economics.",
    },
    {
        "key": "spence1973",
        "text": "Spence, M. (1973). Job Market Signaling. Quarterly Journal of Economics.",
    },
    {
        "key": "north1990",
        "text": "North, D. (1990). Institutions, Institutional Change and Economic Performance. Cambridge University Press.",
    },
    {
        "key": "luhmann1979",
        "text": "Luhmann, N. (1979). Trust and Power. Wiley.",
    },
    {
        "key": "granovetter1978",
        "text": "Granovetter, M. (1978). Threshold Models of Collective Behavior. American Journal of Sociology.",
    },
    {
        "key": "wong2011",
        "text": "Wong, B. (2011). Points of View: Color Blindness. Nature Methods.",
    },
    {
        "key": "bai1998",
        "text": "Bai, J., & Perron, P. (1998). Estimating and Testing Linear Models with Multiple Structural Changes. Econometrica.",
    },
    {
        "key": "chow1960",
        "text": "Chow, G. (1960). Tests of Equality Between Sets of Coefficients in Two Linear Regressions. Econometrica.",
    },
    {
        "key": "page2022",
        "text": "Page et al. (2022). The AI Generation Gap in User-Generated Content Platforms. arXiv.",
    },
    {
        "key": "epstein2023",
        "text": "Epstein, Z. et al. (2023). Art and the Science of Generative AI. Science.",
    },
    {
        "key": "bommasani2022",
        "text": "Bommasani, R. et al. (2022). On the Opportunities and Risks of Foundation Models. Stanford CRFM.",
    },
    {
        "key": "vaswani2017",
        "text": "Vaswani, A. et al. (2017). Attention Is All You Need. NeurIPS.",
    },
]


def print_banner():
    """Print the research banner (with version information)."""
    banner = f"""
====================================================================
  {REPORT_META['title_cn']}
  {REPORT_META['subtitle']}
  ------------------------------------------------------------------
  {REPORT_META['competition']}
  Version: {REPORT_META['version']} | Framework: {REPORT_META['framework']}
  Cases: AOTY & RYM | Time span: {STUDY_START_YEAR}-{STUDY_END_YEAR}
====================================================================
    """
    print(banner)
