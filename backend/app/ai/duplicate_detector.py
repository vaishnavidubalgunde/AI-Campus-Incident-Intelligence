import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def normalize_text(text: str) -> str:
    lower = text.lower()
    lower = re.sub(r"\bwi[- ]?fi\b", "wifi", lower)
    lower = re.sub(r"\blab\b", "laboratory", lower)
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", lower)
    return " ".join(cleaned.split())

class DuplicateDetector:
    def __init__(self, similarity_threshold: float = 0.40):
        self.similarity_threshold = similarity_threshold

    def find_duplicates(
        self,
        target_title: str,
        target_description: str,
        target_building: str,
        target_category: str,
        existing_incidents: List[Dict[str, Any]],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Calculates semantic similarity using TF-IDF and Cosine Similarity
        combined with contextual signals (location and category match).
        """
        if not existing_incidents:
            return []

        target_corpus = f"{normalize_text(target_title)} {normalize_text(target_description)}"
        doc_texts = [
            f"{normalize_text(inc.get('title', ''))} {normalize_text(inc.get('description', ''))}"
            for inc in existing_incidents
        ]

        all_texts = [target_corpus] + doc_texts
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", max_features=2000)
        
        try:
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            cosine_sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        except Exception:
            return []

        results = []
        for idx, inc in enumerate(existing_incidents):
            base_sim = float(cosine_sims[idx])
            
            # Contextual bonuses
            sim_boost = 0.0
            same_building = (
                inc.get("building", "").strip().lower() == target_building.strip().lower()
                and target_building.strip() != ""
            )
            if same_building:
                sim_boost += 0.12

            same_cat = (
                inc.get("category_name", "").strip().lower() == target_category.strip().lower()
                and target_category.strip() != ""
            )
            if same_cat:
                sim_boost += 0.08

            final_similarity = min(1.0, base_sim + sim_boost)

            if final_similarity >= self.similarity_threshold:
                match_type = "duplicate" if final_similarity >= 0.72 else "recurring_related"
                results.append({
                    "incident_id": inc["id"],
                    "incident_number": inc["incident_number"],
                    "title": inc["title"],
                    "description": inc["description"],
                    "location": inc["location"],
                    "building": inc.get("building", ""),
                    "similarity_score": round(final_similarity, 3),
                    "status": inc["status"],
                    "match_type": match_type,
                    "created_at": inc.get("created_at")
                })

        # Sort by similarity descending
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:limit]

duplicate_detector = DuplicateDetector()
