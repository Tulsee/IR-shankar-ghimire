#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import nltk
from typing import Dict, List
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


# Ensure NLTK resources are available
def _ensure_nltk():
    try:
        _ = stopwords.words("english")
        nltk.word_tokenize("test")
    except LookupError:
        nltk.download("stopwords")
        nltk.download("punkt")
        try:
            nltk.download("punkt_tab")
        except Exception:
            pass


_ensure_nltk()


class TextClassifier:
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words("english"))

        # Define category keywords and patterns
        self.categories = {
            "business": [
                "business",
                "management",
                "finance",
                "economics",
                "marketing",
                "strategy",
                "entrepreneur",
                "corporate",
                "commercial",
                "revenue",
                "profit",
                "investment",
                "market",
                "company",
                "organization",
                "enterprise",
                "startup",
                "venture",
                "accounting",
                "financial",
                "budget",
                "cost",
                "sales",
                "customer",
                "client",
                "supply chain",
                "operations",
                "logistics",
                "trade",
                "commerce",
                "industry",
                "competitive",
                "stakeholder",
                "shareholder",
                "executive",
                "leadership",
                "merger",
                "acquisition",
                "partnership",
                "contract",
                "negotiation",
                "innovation",
                "productivity",
                "efficiency",
                "performance",
                "growth",
                "capitalism",
                "economy",
                "economic",
                "fiscal",
                "monetary",
                "banking",
            ],
            "health": [
                "health",
                "medical",
                "medicine",
                "healthcare",
                "hospital",
                "patient",
                "doctor",
                "physician",
                "nurse",
                "therapy",
                "treatment",
                "diagnosis",
                "disease",
                "illness",
                "symptom",
                "clinical",
                "pharmaceutical",
                "drug",
                "surgery",
                "surgical",
                "mental health",
                "psychology",
                "psychiatry",
                "nutrition",
                "diet",
                "fitness",
                "wellness",
                "prevention",
                "epidemic",
                "pandemic",
                "vaccine",
                "immunization",
                "research",
                "biomedical",
                "anatomy",
                "physiology",
                "pathology",
                "oncology",
                "cardiology",
                "neurology",
                "dermatology",
                "pediatric",
                "geriatric",
                "rehabilitation",
                "public health",
                "epidemiology",
                "biotechnology",
                "genetics",
                "genomics",
                "telemedicine",
                "digital health",
                "healthcare technology",
                "medical device",
            ],
            "politics": [
                "politics",
                "political",
                "government",
                "policy",
                "democracy",
                "election",
                "vote",
                "voting",
                "parliament",
                "congress",
                "senate",
                "minister",
                "president",
                "prime minister",
                "legislation",
                "law",
                "legal",
                "regulation",
                "governance",
                "public policy",
                "administration",
                "bureaucracy",
                "citizen",
                "citizenship",
                "rights",
                "civil rights",
                "human rights",
                "constitution",
                "federal",
                "state",
                "local government",
                "municipal",
                "diplomatic",
                "international relations",
                "foreign policy",
                "national security",
                "defense",
                "military",
                "war",
                "peace",
                "conflict",
                "negotiation",
                "treaty",
                "alliance",
                "sovereignty",
                "nationalism",
                "globalization",
                "ideology",
                "conservative",
                "liberal",
                "progressive",
                "populism",
                "socialism",
                "capitalism",
                "authoritarianism",
                "totalitarianism",
            ],
        }

        # Prepare vectorizers for each category
        self.vectorizers = {}
        self.category_vectors = {}
        self._initialize_category_models()

    def _initialize_category_models(self):
        """Initialize TF-IDF vectorizers for each category"""
        for category, keywords in self.categories.items():
            # Create a corpus from keywords
            corpus = [" ".join(keywords)]
            vectorizer = TfidfVectorizer(
                max_features=1000, stop_words="english", ngram_range=(1, 2)
            )
            # Fit the vectorizer on the category keywords
            self.vectorizers[category] = vectorizer
            self.category_vectors[category] = vectorizer.fit_transform(corpus)

    def preprocess_text(self, text: str) -> str:
        """Preprocess text for classification"""
        if not text:
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove special characters and numbers
        text = re.sub(r"[^a-zA-Z\s]", " ", text)

        # Tokenize
        tokens = nltk.word_tokenize(text)

        # Remove stopwords and stem
        processed_tokens = [
            self.stemmer.stem(token)
            for token in tokens
            if token not in self.stop_words and len(token) > 2
        ]

        return " ".join(processed_tokens)

    def classify_text(self, text: str) -> Dict:
        """
        Classify text into business, health, or politics categories
        Returns scores for each category and the predicted category
        """
        if not text.strip():
            return {
                "predicted_category": "unknown",
                "scores": {"business": 0.0, "health": 0.0, "politics": 0.0},
                "confidence": 0.0,
                "explanation": "No text provided for classification",
            }

        # Preprocess the input text
        processed_text = self.preprocess_text(text)

        if not processed_text.strip():
            return {
                "predicted_category": "unknown",
                "scores": {"business": 0.0, "health": 0.0, "politics": 0.0},
                "confidence": 0.0,
                "explanation": "Text contains no meaningful content after preprocessing",
            }

        scores = {}
        keyword_matches = {}

        # Calculate scores for each category
        for category in self.categories.keys():
            # Method 1: Keyword matching
            category_keywords = self.categories[category]
            keyword_count = sum(
                1 for keyword in category_keywords if keyword in text.lower()
            )
            keyword_score = keyword_count / len(category_keywords)

            # Method 2: TF-IDF similarity (simplified approach)
            # Create a simple TF-IDF based on keyword frequency
            text_words = processed_text.split()
            category_word_matches = sum(
                1 for word in text_words if any(kw in word for kw in category_keywords)
            )
            tfidf_score = category_word_matches / max(len(text_words), 1)

            # Combine both methods
            combined_score = (keyword_score * 0.6) + (tfidf_score * 0.4)
            scores[category] = round(combined_score, 4)
            keyword_matches[category] = keyword_count

        # Determine predicted category
        if max(scores.values()) == 0:
            predicted_category = "unknown"
            confidence = 0.0
        else:
            predicted_category = max(scores, key=scores.get)
            max_score = scores[predicted_category]
            # Calculate confidence as the difference between top two scores
            sorted_scores = sorted(scores.values(), reverse=True)
            if len(sorted_scores) > 1:
                confidence = round(
                    (sorted_scores[0] - sorted_scores[1]) + sorted_scores[0], 4
                )
            else:
                confidence = round(max_score, 4)

        # Generate explanation
        explanation = self._generate_explanation(
            text, predicted_category, keyword_matches, scores
        )

        return {
            "predicted_category": predicted_category,
            "scores": scores,
            "confidence": min(confidence, 1.0),  # Cap at 1.0
            "explanation": explanation,
            "keyword_matches": keyword_matches,
        }

    def _generate_explanation(
        self, text: str, predicted_category: str, keyword_matches: Dict, scores: Dict
    ) -> str:
        """Generate human-readable explanation for the classification"""
        if predicted_category == "unknown":
            return "The text doesn't contain enough keywords to confidently classify it into any specific category."

        explanations = []

        # Add information about the predicted category
        match_count = keyword_matches[predicted_category]
        score = scores[predicted_category]

        explanations.append(
            f"This text is classified as '{predicted_category}' with a score of {score:.4f}."
        )

        if match_count > 0:
            explanations.append(
                f"Found {match_count} keyword matches related to {predicted_category}."
            )

        # Add comparison with other categories
        other_categories = [cat for cat in scores.keys() if cat != predicted_category]
        other_scores = [f"{cat}: {scores[cat]:.4f}" for cat in other_categories]

        if other_scores:
            explanations.append(f"Other category scores: {', '.join(other_scores)}")

        return " ".join(explanations)


# Global classifier instance
text_classifier = TextClassifier()


def classify_document(text: str) -> Dict:
    """
    Public function to classify a document
    """
    return text_classifier.classify_text(text)
