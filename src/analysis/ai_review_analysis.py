"""
Feature analysis and classification of AI-generated vs human-written reviews
=============================================================================

Research questions:
  1. What quantifiable differences exist in the linguistic features of AI-generated and human-written music reviews?
  2. Do these differences shrink as AI models improve?
  3. Can a classifier be trained to effectively detect AI-written reviews?
  4. Which linguistic features are the strongest predictors for distinguishing AI and human reviews?

Methodology:
  - TF-IDF + Random Forest as the baseline classifier
  - Extract 9 categories of linguistic features (lexical, syntactic, sentiment, structural, etc.)
  - Feature importance analysis to reveal the "machine-like" quality of AI reviews
  - Temporal analysis: does detector accuracy decline over time?

Evidence boundary:
  The human side uses a deterministic sample of published critic excerpts
  from the documented AOTY/Metacritic archive when it is available. The AI
  side remains a small set of manually authored assistant-style controls.
  This supports a controlled feature comparison, not a prevalence estimate
  or a production detector claim.
"""

import re
import warnings
from typing import Dict, List, Optional, Tuple
from pathlib import Path

import sys
from pathlib import Path

_SRC = str(Path(__file__).resolve().parent.parent)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import (
    cross_val_predict, cross_val_score, StratifiedKFold
)
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, roc_curve, accuracy_score
)

from config import (
    PROCESSED_DIR, FIGURES_DIR, EXTERNAL_DIR, RANDOM_SEED,
    TFIDF_MAX_FEATURES, NGRAM_RANGE, RF_N_ESTIMATORS,
    FILES
)

warnings.filterwarnings("ignore", category=FutureWarning)


# ============================================================
# High-quality English and Chinese music reviews
# ============================================================

# Fallback examples used only when the external review archive is unavailable.
FALLBACK_HUMAN_REVIEWS = [
    # English reviews (in RYM/AOTY style)
    "This album completely changed my perspective on what indie rock can be. "
    "The way the guitar riff builds in track 3 at exactly 2:15 is pure magic. "
    "I've been listening to this band since their debut in 2018, and this is "
    "by far their most cohesive work. The production by Nigel really shines "
    "through on vinyl — you can hear the breath between notes.",

    "Honestly a bit disappointed. The first two tracks are strong but after "
    "that the album loses its way around track 4. The lyrics feel forced "
    "compared to their earlier work, like they're trying too hard to be profound. "
    "I wanted to love this but it just doesn't click for me. Maybe I need more listens.",

    "A masterpiece of modern composition. The orchestration is breathtaking, "
    "particularly the string section in the second movement. This will be "
    "remembered as one of the defining albums of the decade. The way the "
    "cello and violin interweave at 3:45 gives me chills every time.",

    "mid. just mid. nothing special honestly. idk why everyone is hyping "
    "this up, sounds like every other bedroom pop project from 2023. "
    "the lyrics are trying way too hard to be deep lol. 2/10",

    "I've been a fan since 2015 and this album feels like a natural evolution "
    "of their sound. The incorporation of jazz harmonies with their signature "
    "lo-fi aesthetic creates something truly unique. Favorite tracks: 2, 5, 8. "
    "The bassline on track 7 is absolutely filthy, reminds me of Thundercat.",

    "Been spinning this all week and it just keeps getting better. The first "
    "time I heard the drop on track 3 I literally had to stop what I was doing. "
    "This band has come so far since their early EPs, you can hear the growth "
    "in every aspect of the songwriting. AOTY contender for sure.",

    "Not sure how to feel about this one. There are moments of brilliance "
    "('Neon Lights' is gorgeous) but also stretches that feel like filler. "
    "The middle section from tracks 5-8 really drags. Might be a grower though, "
    "their last album took me 6 months to fully appreciate.",

    "this is what happens when you let tiktok produce an album. every song "
    "sounds like it was designed for a 15 second clip. where's the depth? "
    "where's the progression? bring back real songwriting please.",

    "Incredible sound design. The way they use field recordings and found "
    "sounds to build these atmospheric soundscapes is unlike anything I've "
    "heard since Boards of Canada. Headphones recommended for full effect. "
    "The hidden track at 12:34 is pure genius.",

    "Saw them live last week and it completely changed my view of this album. "
    "The energy they bring to these songs in a live setting is unmatched. "
    "The extended jam version of the title track went for 15 minutes and "
    "every second was captivating. Buy tickets if you can.",

    # Chinese reviews (mimicking Douban Music style)
    "I've been waiting for this album since last year and finally got to hear "
    "it. Honestly, the first listen felt average, but after a few more loops "
    "the details gradually emerged. The producer really understands spatiality; "
    "every instrument is placed just right. Recommended with good headphones, "
    "it opens up a new world.",

    "Not great. The lyrics are too deliberate and the melodies aren't catchy "
    "enough. Compared to the previous album it's a clear step back; it feels "
    "like they've hit a creative block. Hopefully the next one finds its "
    "footing again.",

    "A lock for album of the year. I was hooked from the first note; the whole "
    "album flows in one breath with no filler tracks. I especially like tracks "
    "3 and 8; the arrangements are so intricate that every listen reveals "
    "something new.",

    "It's okay, not unpleasant to listen to but nothing memorable. Independent "
    "music is getting more and more homogenized these days; everything sounds "
    "the same after a while. Still a bit better than mainstream pop.",

    "You can tell from one listen that the drum kit was recorded analog; you "
    "rarely hear that these days, it's spot on! The bassline groove brings to "
    "mind 1970s funk, but with modern electronic elements mixed in. The "
    "guitarist finally cuts loose on this one; that solo gave me goosebumps.",
]


def load_human_review_excerpts(max_examples: int = 15) -> Tuple[List[str], str]:
    """Return a reproducible, publication-diverse human-review sample."""
    path = (
        EXTERNAL_DIR
        / "aoty_metacritic_30000"
        / "Review excerpts for NLP"
        / "train.csv"
    )
    if not path.exists():
        return FALLBACK_HUMAN_REVIEWS[:max_examples], "manual fallback examples"

    try:
        reviews = pd.read_csv(path, usecols=["Source", "Review"])
        reviews = reviews.dropna(subset=["Source", "Review"]).drop_duplicates("Review")
        lengths = reviews["Review"].astype(str).str.len()
        reviews = reviews.loc[lengths.between(120, 600)].copy()
        one_per_source = (
            reviews.sort_values(["Source", "Review"])
            .groupby("Source", group_keys=False)
            .sample(n=1, random_state=RANDOM_SEED)
        )
        if len(one_per_source) < max_examples:
            return FALLBACK_HUMAN_REVIEWS[:max_examples], "manual fallback examples"
        sample = one_per_source.sample(
            n=max_examples, random_state=RANDOM_SEED
        )["Review"].astype(str).tolist()
        return sample, "15 published critic excerpts from the AOTY/Metacritic archive"
    except (OSError, ValueError, KeyError, pd.errors.ParserError):
        return FALLBACK_HUMAN_REVIEWS[:max_examples], "manual fallback examples"


HUMAN_REVIEWS, HUMAN_CORPUS_LABEL = load_human_review_excerpts()

# Manually authored examples intended to resemble generic assistant prose.
AI_REVIEWS = [
    # English AI reviews
    "This album presents a compelling fusion of genres that demonstrates the "
    "artist's versatility and technical proficiency. The production quality is "
    "consistently high throughout, with each track contributing to a cohesive "
    "thematic narrative. Recommended for fans of alternative and experimental music.",

    "The album offers a well-crafted listening experience with balanced "
    "instrumentation and thoughtful composition. While it may not revolutionize "
    "the genre, it stands as a solid addition to the artist's discography and "
    "showcases their continued artistic development.",

    "An interesting collection of songs that blend various musical influences "
    "into a coherent whole. The artist demonstrates strong technical skills and "
    "creative ambition. The album's production values are professional and the "
    "overall sound is polished and accessible to a wide audience.",

    "This work represents a significant artistic statement that explores themes "
    "of identity and belonging through a sophisticated musical lens. The "
    "arrangements are intricate and reward repeated listening. A noteworthy "
    "contribution to contemporary music that showcases the artist's growth.",

    "The album successfully achieves its artistic goals through a combination "
    "of strong songwriting and polished production. The artist's vision is "
    "clearly realized across all tracks, creating a unified listening "
    "experience that will appeal to both longtime fans and new listeners.",

    "Overall, this is a well-structured album with good production values "
    "and consistent quality throughout. The artist shows promise and "
    "delivers a solid body of work that deserves recognition in the "
    "contemporary music landscape. Rating: 7.5/10",

    "This album effectively combines elements of various genres to create "
    "a unique sound that sets it apart from contemporaries. The lyrical "
    "content is thoughtful and addresses relevant themes. The production "
    "is polished and professional, making for an enjoyable listening "
    "experience from start to finish.",

    "An impressive display of musical talent and creative vision. The album "
    "flows well from track to track, maintaining listener engagement "
    "throughout its runtime. The artist's attention to detail is evident "
    "in every aspect of the production. Highly recommended.",

    "This release demonstrates significant artistic growth and maturation. "
    "The songwriting is confident and the execution is polished. "
    "Each track contributes meaningfully to the album's overall narrative "
    "arc, creating a cohesive and satisfying listening journey.",

    "A solid and well-executed album that showcases the artist's strengths "
    "while pushing their sound in new directions. The production is crisp, "
    "the performances are tight, and the songwriting is consistently strong. "
    "A worthy addition to any music lover's collection.",

    # Chinese AI reviews
    "This album demonstrates the artist's maturity and technical ability in "
    "music creation. The overall structure of the work is complete, and each "
    "song reflects careful arrangement and production. Recommended for "
    "listeners who enjoy independent and experimental music.",

    "While maintaining the artist's consistent style, the album also "
    "experiments with new musical elements. The production is refined and "
    "the transitions between songs are natural and smooth. Overall, this is "
    "a work worth listening to.",

    "From a music production perspective, this album demonstrates a high "
    "level of professionalism. The melodies are elegant, the harmonies are "
    "rich, and the rhythm is well controlled. Through this work, the artist "
    "establishes a distinctive musical identity.",

    "This album successfully balances artistry and commercial appeal; it has "
    "both depth and accessibility. Every song is carefully polished, and the "
    "whole presents a consistently high quality. Recommended for the collection.",

    "The work shows the artist's deep understanding of music and a unique "
    "creative perspective. The arrangements are richly layered and the "
    "production details are meticulous, reflecting a high level of "
    "professionalism. Worth savoring for music lovers.",
]


# ============================================================
# AI review detection and analysis
# ============================================================

class AIReviewAnalyzer:
    """AI review detection and analysis."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=TFIDF_MAX_FEATURES,
            ngram_range=NGRAM_RANGE,
            analyzer="char_wb",
            sublinear_tf=True,
        )
        self.classifier = RandomForestClassifier(
            n_estimators=RF_N_ESTIMATORS,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=RANDOM_SEED,
            n_jobs=-1,
        )
        self.rng = np.random.default_rng(RANDOM_SEED)
        self.is_trained = False
        self.feature_importance_ = None

    # ----------------------------------------------------------
    # Linguistic feature extraction
    # ----------------------------------------------------------

    @staticmethod
    def extract_linguistic_features(text: str) -> Dict[str, float]:
        """
        Extract linguistic features used to distinguish AI from human reviews.

        9 categories of features:
        1. Basic statistics: length, word count, sentence count
        2. Lexical diversity: type-token ratio
        3. Syntactic complexity: average sentence length, subordinate clauses
        4. Sentiment expression: exclamation marks, sentiment words
        5. Specificity: concrete references (tracks, timestamps)
        6. Expertise: musical technical terms
        7. Subjectivity: first person, personal opinions
        8. Hesitation/vagueness: colloquial filler words
        9. Structural uniformity: sentence length consistency
        """
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not words:
            return {f"feat_{i}": 0.0 for i in range(18)}

        text_lower = text.lower()

        features = {
            # 1. Basic statistics
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_word_length": float(np.mean([len(w) for w in words])),

            # 2. Lexical diversity
            "vocabulary_diversity": len(set(w.lower() for w in words)) / max(len(words), 1),

            # 3. Syntax
            "avg_sentence_length": float(np.mean(
                [len(s.split()) for s in sentences]
            )) if sentences else 0,

            # 4. Sentiment expression
            "exclamation_count": text.count("!"),
            "emotional_words": AIReviewAnalyzer._count_emotional_words(text),

            # 5. Specificity
            "specific_references": AIReviewAnalyzer._count_specific_references(text),

            # 6. Expertise
            "technical_terms": AIReviewAnalyzer._count_technical_terms(text),

            # 7. Subjectivity
            "first_person_count": sum(
                1 for w in words
                if w.lower() in ["i", "me", "my", "we", "our", "us"]
            ),

            # 8. Filler words/hesitation
            "filler_words": sum(
                1 for w in words
                if w.lower() in ["honestly", "literally", "basically",
                                 "actually", "pretty", "quite", "rather"]
            ),

            # 9. Structural features
            "sentence_length_std": float(np.std(
                [len(s.split()) for s in sentences]
            )) if len(sentences) > 1 else 0,

            # Extra: proportion of all-caps words (humans like emphasis)
            "allcaps_ratio": sum(1 for w in words if w.isupper() and len(w) > 1) / max(len(words), 1),

            # Extra: punctuation density
            "punctuation_density": sum(
                1 for c in text if c in ",.!?;:"
            ) / max(len(text), 1),

            # Extra: number references (tracks, years, etc.)
            "number_references": len(re.findall(r'\d+', text)),

            # Extra: contrastive language (humans use more contrast)
            "contrastive_words": sum(
                1 for w in words
                if w.lower() in ["but", "however", "although", "though",
                                 "yet", "while", "despite"]
            ),
        }

        return features

    @staticmethod
    def _count_emotional_words(text: str) -> int:
        """Count sentiment words."""
        emotional = [
            "beautiful", "amazing", "terrible", "boring", "exciting",
            "emotional", "powerful", "weak", "brilliant", "disappointing",
            "magic", "chills", "breathtaking", "gorgeous", "awful",
            "mediocre", "fantastic", "incredible", "love", "hate",
        ]
        text_lower = text.lower()
        return sum(1 for word in emotional if word in text_lower)

    @staticmethod
    def _count_specific_references(text: str) -> int:
        """Count references to specific details; humans tend to cite specific details."""
        patterns = [
            r'track \d+', r'song \d+', r'\d+:\d+',  # specific track/timing
            r'verse \d+', r'chorus', r'bridge',      # song structure
            r'at \d+:\d+', r'in the \w+ (track|song|part|movement)',
            r'the [Bb]-side', r'hidden track',
        ]
        return sum(
            len(re.findall(p, text, re.IGNORECASE))
            for p in patterns
        )

    @staticmethod
    def _count_technical_terms(text: str) -> int:
        """Count musical technical terms; humans tend to use professional terminology."""
        terms = [
            'timbre', 'texture', 'harmony', 'melody', 'rhythm', 'dynamics',
            'reverb', 'compression', 'mastering', 'mixing', 'arrangement',
            'crescendo', 'diminuendo', 'staccato', 'legato', 'arpeggio',
            'polyrhythm', 'syncopation', 'modulation', 'cadence',
            'overdub', 'multitrack', 'analog', 'vinyl', 'mastering',
            'soundscape', 'atmospheric', 'lo-fi', 'sound design',
            'field recording', 'sampling', 'synthesis',
        ]
        text_lower = text.lower()
        return sum(1 for term in terms if term in text_lower)

    # ----------------------------------------------------------
    # Feature comparison visualization
    # ----------------------------------------------------------

    def get_feature_comparison_df(self,
                                   human_reviews: List[str],
                                   ai_reviews: List[str]) -> pd.DataFrame:
        """Generate a feature comparison DataFrame of AI vs human reviews."""
        human_features = [self.extract_linguistic_features(r)
                         for r in human_reviews]
        ai_features = [self.extract_linguistic_features(r)
                      for r in ai_reviews]

        df_human = pd.DataFrame(human_features)
        df_human["source"] = "Human review"
        df_ai = pd.DataFrame(ai_features)
        df_ai["source"] = "AI review"

        return pd.concat([df_human, df_ai], ignore_index=True)

    # ----------------------------------------------------------
    # Classifier training and evaluation
    # ----------------------------------------------------------

    def prepare_data(self,
                     human_reviews: Optional[List[str]] = None,
                     ai_reviews: Optional[List[str]] = None,
                     expand_factor: int = 1) -> Tuple:
        """
        Prepare training data, expanding the sample with slight perturbations.

        Parameters:
        -----------
        human_reviews : list - list of human reviews
        ai_reviews : list - list of AI reviews
        expand_factor : int - expansion factor (number of variants per sample)
        """
        if human_reviews is None:
            human_reviews = HUMAN_REVIEWS
        if ai_reviews is None:
            ai_reviews = AI_REVIEWS

        texts = []
        labels = []

        # Optional augmentation is for demonstrations only. Evaluation calls
        # this with expand_factor=1 so every source example appears once.
        for review in human_reviews:
            for variant_idx in range(expand_factor):
                variant = review if variant_idx == 0 else self._create_variant(review, noise_level=0.05)
                texts.append(variant)
                labels.append(0)

        for review in ai_reviews:
            for variant_idx in range(expand_factor):
                variant = review if variant_idx == 0 else self._create_variant(review, noise_level=0.03)
                texts.append(variant)
                labels.append(1)

        return texts, labels

    def _create_variant(self, text: str, noise_level: float = 0.05) -> str:
        """Create a text variant through slight perturbation (simulating real-world variation)."""
        if self.rng.random() > noise_level:
            return text

        words = text.split()
        if len(words) < 5:
            return text

        op = self.rng.integers(0, 3)
        if op == 0 and len(words) > 10:
            # Delete one word
            idx = self.rng.integers(1, len(words) - 1)
            words.pop(idx)
        elif op == 1:
            # Swap two adjacent words
            idx = self.rng.integers(0, len(words) - 2)
            words[idx], words[idx + 1] = words[idx + 1], words[idx]
        # op == 2: unchanged

        return " ".join(words)

    def train(self, human_reviews: Optional[List[str]] = None,
              ai_reviews: Optional[List[str]] = None):
        """
        Train the AI review detection classifier.

        Uses TF-IDF vectorization + Random Forest.
        """
        print("\n" + "=" * 50)
        print("[INFO] Training AI review detection classifier")
        print("=" * 50)

        texts, labels = self.prepare_data(human_reviews, ai_reviews, expand_factor=1)
        y = np.array(labels)

        print("\n[1/3] Leakage-safe cross-validation on original examples...")
        cv = StratifiedKFold(5, shuffle=True, random_state=RANDOM_SEED)
        evaluation_model = Pipeline([
            ("tfidf", TfidfVectorizer(
                max_features=TFIDF_MAX_FEATURES,
                ngram_range=NGRAM_RANGE,
                analyzer="char_wb",
                sublinear_tf=True,
            )),
            ("classifier", RandomForestClassifier(
                n_estimators=RF_N_ESTIMATORS,
                max_depth=20,
                min_samples_split=5,
                min_samples_leaf=2,
                class_weight="balanced",
                random_state=RANDOM_SEED,
                n_jobs=-1,
            )),
        ])
        y_pred = cross_val_predict(evaluation_model, texts, y, cv=cv, method="predict")
        y_prob = cross_val_predict(
            evaluation_model, texts, y, cv=cv, method="predict_proba"
        )[:, 1]

        accuracy = accuracy_score(y, y_pred)
        auc = roc_auc_score(y, y_prob)

        print(f"\n[INFO] Controlled-corpus cross-validated performance:")
        print(f"  Accuracy: {accuracy:.4f}")
        print(f"  AUC:      {auc:.4f}")
        print(f"\nClassification report:")
        print(classification_report(y, y_pred,
              target_names=["Human review", "AI review"]))

        cv_scores = cross_val_score(
            evaluation_model, texts, y, cv=cv,
            scoring="accuracy"
        )
        print(f"\n5-fold accuracy: {cv_scores.mean():.4f} (+/-{cv_scores.std():.4f})")

        print("[2/3] Fitting the demonstrator on all original examples...")
        X = self.vectorizer.fit_transform(texts)
        self.classifier.fit(X, y)
        self.is_trained = True

        # Feature importance
        self.feature_importance_ = pd.DataFrame({
            "feature": self.vectorizer.get_feature_names_out(),
            "importance": self.classifier.feature_importances_
        }).sort_values("importance", ascending=False)

        print("\nKey distinguishing features (Top 15):")
        for _, row in self.feature_importance_.head(15).iterrows():
            direction = "-> AI" if self._feature_direction(row["feature"]) > 0 else "Human ->"
            print(f"  {row['feature']:20s} importance={row['importance']:.4f}  {direction}")

        return {
            "accuracy": float(accuracy),
            "auc": float(auc),
            "cv_mean": float(cv_scores.mean()),
            "cv_std": float(cv_scores.std()),
            "n_original_examples": int(len(texts)),
            "evaluation_design": (
                "5-fold out-of-fold evaluation on 15 archived critic excerpts "
                "and 15 manually authored AI-style controls"
            ),
            "external_validation": False,
            "feature_importance": self.feature_importance_,
        }

    def _feature_direction(self, feature: str) -> float:
        """Determine feature direction (positive = appears more in AI reviews)."""
        # Simplified version: judged based on keywords
        ai_indicators = ["overall", "recommended", "successful", "effectively",
                        "showcases", "demonstrates", "well-crafted",
                        "noteworthy", "polished", "cohesive", "solid"]
        human_indicators = ["honestly", "literally", "but", "just",
                           "feels", "sounds", "reminds", "favorite"]

        for w in ai_indicators:
            if w in feature:
                return 1
        for w in human_indicators:
            if w in feature:
                return -1
        return 0

    # ----------------------------------------------------------
    # Batch detection
    # ----------------------------------------------------------

    def predict(self, texts: List[str]) -> pd.DataFrame:
        """
        Run AI detection on a batch of reviews.

        Returns:
        --------
        DataFrame with columns: text, ai_probability, prediction, features
        """
        if not self.is_trained:
            raise RuntimeError("Classifier has not been trained yet; call train() first")

        X = self.vectorizer.transform(texts)
        probas = self.classifier.predict_proba(X)[:, 1]
        preds = self.classifier.predict(X)

        results = []
        for i, text in enumerate(texts):
            features = self.extract_linguistic_features(text)
            results.append({
                "text": text[:100] + "..." if len(text) > 100 else text,
                "ai_probability": probas[i],
                "prediction": "AI review" if preds[i] == 1 else "Human review",
                **features,
            })

        return pd.DataFrame(results)

    # ----------------------------------------------------------
    # Complete analysis pipeline
    # ----------------------------------------------------------

    def run_full_analysis(self) -> Dict:
        """Run the complete AI review detection analysis."""
        print("\n" + "=" * 60)
        print("[INFO] AI review detection and feature analysis - start")
        print("=" * 60)

        results = {}

        # 1. Feature comparison
        print("\n[Stage 1] AI vs human review feature comparison...")
        feature_df = self.get_feature_comparison_df(HUMAN_REVIEWS, AI_REVIEWS)
        results["feature_comparison"] = self._summarize_features(feature_df)

        # 2. Train detector
        print("\n[Stage 2] Training and evaluating detector...")
        model_results = self.train()
        results["model"] = model_results

        # 3. Sample prediction
        print("\n[Stage 3] Sample prediction demo...")
        test_samples = [
            "This is the most incredible album I've heard this year. "
            "The way the drums kick in at track 2 just blows my mind.",
            "The album presents a cohesive artistic vision with polished "
            "production values and strong songwriting throughout.",
        ]
        predictions = self.predict(test_samples)
        results["sample_predictions"] = predictions
        print(predictions[["text", "ai_probability", "prediction"]].to_string())

        print("\n" + "=" * 60)
        print("[OK] AI review analysis complete")
        print("=" * 60)

        return results

    def _summarize_features(self, df: pd.DataFrame) -> Dict:
        """Summarize feature comparison results."""
        compare_cols = [
            "vocabulary_diversity", "avg_sentence_length",
            "emotional_words", "specific_references",
            "technical_terms", "first_person_count",
            "filler_words", "sentence_length_std",
            "allcaps_ratio", "number_references", "contrastive_words",
        ]

        summary = {}
        for col in compare_cols:
            if col in df.columns:
                human_values = df[df["source"] == "Human review"][col]
                ai_values = df[df["source"] == "AI review"][col]
                human_mean = human_values.mean()
                ai_mean = ai_values.mean()
                pooled_std = np.sqrt(
                    (human_values.std(ddof=1) ** 2 + ai_values.std(ddof=1) ** 2) / 2
                )
                standardized_difference = (
                    (ai_mean - human_mean) / pooled_std if pooled_std > 1e-9 else 0.0
                )
                if standardized_difference > 0:
                    direction = "higher in AI-style controls"
                elif standardized_difference < 0:
                    direction = "higher in critic excerpts"
                else:
                    direction = "no difference in sample"
                summary[col] = {
                    "human_mean": round(float(human_mean), 3),
                    "ai_mean": round(float(ai_mean), 3),
                    "standardized_difference": round(
                        float(standardized_difference), 3
                    ),
                    "direction": direction,
                }

        print("\n[INFO] AI vs human review feature differences:")
        for feat, vals in summary.items():
            print(f"  {feat:25s}: human={vals['human_mean']:.3f}  "
                  f"AI={vals['ai_mean']:.3f}  "
                  f"(SMD={vals['standardized_difference']:+.3f}; "
                  f"{vals['direction']})")

        return summary


# ============================================================
# Convenience functions
# ============================================================

def generate_synthetic_review_dataset(
    n_human: int = 500,
    n_ai: int = 500
) -> Tuple[List[str], List[str], List[str]]:
    """
    Generate a large-scale synthetic review dataset for analysis.

    Generate more diverse reviews by combining templates and rules.
    """
    rng = np.random.default_rng(RANDOM_SEED)

    # Templates for human reviews
    human_templates = [
        "The {adj} {noun} on track {n} is absolutely {emotion}. "
        "I've been listening to this {timeframe} and it {verb} me every time.",

        "Honestly, {opinion}. The {aspect} reminds me of {reference}. "
        "Not their best work but still {quality}.",

        "This album is a {adj} journey from start to finish. "
        "Favorite moment: when the {instrument} comes in at {time}. "
        "{rating}/10",
    ]

    ai_templates = [
        "This album presents a {adj} fusion of {genre1} and {genre2} "
        "that demonstrates the artist's {quality}. The production is {adj2} "
        "throughout, creating a cohesive listening experience.",

        "An {adj} collection of songs that showcases the artist's "
        "technical {quality} and creative vision. The album maintains "
        "consistent {aspect} across all tracks.",

        "This work represents a significant contribution to contemporary "
        "music, blending {genre1} influences with {quality} songwriting. "
        "Recommended for fans of {genre2} and {genre3}.",
    ]

    # Word banks
    adjectives = ["amazing", "incredible", "beautiful", "stunning",
                  "breathtaking", "powerful", "haunting", "sublime"]
    nouns = ["guitar riff", "vocal performance", "bassline", "drum fill",
             "melody", "harmony", "production", "arrangement"]
    emotions = ["gives me chills", "makes me cry", "blows my mind",
                "takes my breath away", "hits me right in the feels"]
    opinions = ["it's overrated", "it's underrated", "it's a grower",
                "I don't get the hype", "it's exactly what I needed"]

    # Generation logic is similar, but this is only a skeleton
    human_reviews = list(HUMAN_REVIEWS)
    ai_reviews = list(AI_REVIEWS)

    # Expand
    for _ in range(n_human - len(human_reviews)):
        human_reviews.append(
            f"The {rng.choice(adjectives)} {rng.choice(nouns)} on track "
            f"{rng.integers(1,12)} is absolutely {rng.choice(emotions)}. "
            f"{rng.choice(opinions)}."
        )

    for _ in range(n_ai - len(ai_reviews)):
        ai_reviews.append(
            f"This album presents a {rng.choice(adjectives)} fusion of "
            f"musical styles that demonstrates the artist's technical "
            f"proficiency and creative ambition. Recommended."
        )

    return human_reviews, ai_reviews, human_reviews + ai_reviews


# ============================================================
# Standalone run
# ============================================================

if __name__ == "__main__":
    analyzer = AIReviewAnalyzer()
    results = analyzer.run_full_analysis()

    print("\n[INFO] Feature importance Top 10:")
    top_features = results["model"]["feature_importance"].head(10)
    print(top_features.to_string())
