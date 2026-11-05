from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
import re

def clean_text(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", str(text).lower())
    return " ".join(cleaned.split())

class PatternDiscoveryEngine:
    def analyze_patterns(self, incidents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not incidents or len(incidents) < 3:
            return []

        df = pd.DataFrame(incidents)
        patterns: List[Dict[str, Any]] = []

        # Convert created_at to datetime
        if "created_at" in df.columns:
            df["created_at_dt"] = pd.to_datetime(df["created_at"])
        else:
            df["created_at_dt"] = datetime.now(timezone.utc)

        # -----------------------------------------------------------------
        # Pattern Type 1: Location & Building Hotspots (High frequency in one location)
        # -----------------------------------------------------------------
        loc_groups = df.groupby(["building", "category_name"])
        for (building, category), group in loc_groups:
            count = len(group)
            if count >= 3:
                unresolved = group[group["status"].isin(["submitted", "under_review", "assigned", "in_progress"])]
                unresolved_count = len(unresolved)
                inc_ids = group["id"].tolist()
                locations = group["location"].unique().tolist()
                
                # Check for critical/high severity count
                high_crit_count = len(group[group["severity"].isin(["critical", "high"])])
                
                confidence = min(0.96, 0.75 + (count * 0.03))
                explanation = (
                    f"Identified {count} incidents of type '{category}' concentrated in {building} "
                    f"({unresolved_count} currently active/unresolved). "
                    f"Concentration exceeds normal single-incident variance."
                )
                
                action = f"Initiate comprehensive inspection for {category} infrastructure across {building}."
                if high_crit_count >= 2:
                    action = f"URGENT: Dispatch senior engineering specialist to {building} due to multiple severe {category} reports."

                patterns.append({
                    "pattern_title": f"Concentrated {category} Hotspot in {building}",
                    "pattern_type": "location_hotspot",
                    "incident_count": count,
                    "affected_locations": locations,
                    "categories": [category],
                    "time_period": "Past 30 Days",
                    "supporting_incident_ids": inc_ids[:15],
                    "explanation": explanation,
                    "suggested_action": action,
                    "confidence_score": round(confidence, 2),
                    "status": "active"
                })

        # -----------------------------------------------------------------
        # Pattern Type 2: Semantic Text Clustering via TF-IDF + DBSCAN
        # Group reports that describe essentially the exact same campus problem
        # -----------------------------------------------------------------
        text_corpus = (df["title"].fillna("") + " " + df["description"].fillna("")).apply(clean_text).tolist()
        if len(text_corpus) >= 5:
            try:
                vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", max_features=1000)
                tfidf_mat = vectorizer.fit_transform(text_corpus)
                
                # Compute distance matrix for DBSCAN: distance = 1 - cosine_similarity
                sim_matrix = cosine_similarity(tfidf_mat)
                dist_matrix = np.clip(1.0 - sim_matrix, 0.0, 1.0)
                
                # DBSCAN clustering with eps=0.45 (similarity >= 0.55) and min_samples=3
                dbscan = DBSCAN(eps=0.45, min_samples=3, metric="precomputed")
                labels = dbscan.fit_predict(dist_matrix)
                
                unique_clusters = set(labels) - {-1}
                for cluster_id in unique_clusters:
                    cluster_indices = np.where(labels == cluster_id)[0]
                    cluster_df = df.iloc[cluster_indices]
                    count = len(cluster_df)
                    
                    cats = cluster_df["category_name"].unique().tolist()
                    bldgs = cluster_df["building"].unique().tolist()
                    inc_ids = cluster_df["id"].tolist()
                    sample_title = cluster_df["title"].iloc[0]
                    
                    patterns.append({
                        "pattern_title": f"Recurring Problem Cluster: {sample_title[:45]}...",
                        "pattern_type": "recurring_issue",
                        "incident_count": count,
                        "affected_locations": bldgs,
                        "categories": cats,
                        "time_period": "Recent Window",
                        "supporting_incident_ids": inc_ids[:12],
                        "explanation": (
                            f"Semantic vector clustering (DBSCAN) discovered {count} distinct reports "
                            f"sharing strong linguistic and situational overlap across {', '.join(bldgs[:3])}."
                        ),
                        "suggested_action": "Merge duplicate reports and assign single high-level remediation ticket.",
                        "confidence_score": 0.88,
                        "status": "active"
                    })
            except Exception:
                pass

        # -----------------------------------------------------------------
        # Pattern Type 3: Unresolved Incident Backlog Accumulation
        # Incidents open longer than standard SLA threshold (e.g. > 5 days)
        # -----------------------------------------------------------------
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=5)
        # Handle timezone-naive vs timezone-aware comparisons cleanly
        try:
            old_unresolved = df[
                (df["status"].isin(["submitted", "under_review", "assigned", "in_progress"])) &
                (pd.to_datetime(df["created_at"], utc=True) < cutoff_date)
            ]
        except Exception:
            old_unresolved = pd.DataFrame()

        if len(old_unresolved) >= 4:
            dept_groups = old_unresolved.groupby("assigned_department_name")
            for dept, g in dept_groups:
                if len(g) >= 3 and dept != "Unassigned":
                    patterns.append({
                        "pattern_title": f"Delayed Incident Resolution Backlog - {dept}",
                        "pattern_type": "unresolved_cluster",
                        "incident_count": len(g),
                        "affected_locations": g["building"].unique().tolist(),
                        "categories": g["category_name"].unique().tolist(),
                        "time_period": "Overdue (> 5 Days)",
                        "supporting_incident_ids": g["id"].tolist()[:10],
                        "explanation": (
                            f"{len(g)} active incidents assigned to {dept} remain unresolved beyond 5 days. "
                            f"Represents a potential resource bottleneck."
                        ),
                        "suggested_action": f"Review team workload allocation and prioritize aging tickets for {dept}.",
                        "confidence_score": 0.91,
                        "status": "investigating"
                    })

        # -----------------------------------------------------------------
        # Pattern Type 4: Cross-Campus Multi-Building Infrastructure Failure
        # Same category appearing simultaneously across >= 3 separate buildings
        # -----------------------------------------------------------------
        cat_groups = df.groupby("category_name")
        for cat, group in cat_groups:
            unique_buildings = group["building"].unique().tolist()
            if len(unique_buildings) >= 3 and len(group) >= 6:
                if cat in ["Internet & Networking", "Water & Plumbing", "Electrical Hazards"]:
                    patterns.append({
                        "pattern_title": f"Campus-Wide Infrastructure Anomaly: {cat}",
                        "pattern_type": "category_spike",
                        "incident_count": len(group),
                        "affected_locations": unique_buildings[:5],
                        "categories": [cat],
                        "time_period": "Current Term",
                        "supporting_incident_ids": group["id"].tolist()[:15],
                        "explanation": (
                            f"Multiple buildings ({', '.join(unique_buildings[:4])}) simultaneously reported "
                            f"{cat} faults. Indicates probable central distribution or trunk-line failure."
                        ),
                        "suggested_action": f"Inspect campus central trunk distribution and server/switch core for {cat}.",
                        "confidence_score": 0.94,
                        "status": "active"
                    })

        # Sort patterns by incident count descending, deduplicate pattern titles
        seen_titles = set()
        deduped_patterns = []
        for p in patterns:
            if p["pattern_title"] not in seen_titles:
                seen_titles.add(p["pattern_title"])
                deduped_patterns.append(p)

        deduped_patterns.sort(key=lambda x: x["incident_count"], reverse=True)
        return deduped_patterns

pattern_discovery_engine = PatternDiscoveryEngine()
