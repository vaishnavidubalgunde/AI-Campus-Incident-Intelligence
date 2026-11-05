import re
from typing import Dict, Any, List, Optional

HIGH_RISK_KEYWORDS = {
    "critical": [
        "exposed wire", "electric spark", "short circuit", "fire", "smoke", "burning smell",
        "gas leak", "structural collapse", "ceiling fell", "transformer buzzing", "live wire",
        "emergency exit locked", "unconscious", "explosion", "severe flooding"
    ],
    "high": [
        "spark", "water leak near computer", "water near electric", "shaking handrail",
        "broken window glass", "trespasser", "theft", "unauthorized individual",
        "fume hood stopped", "deep puddle", "sewage overflow", "continuous leak",
        "outage affecting", "medical", "hazard"
    ],
    "medium": [
        "slow wifi", "leaking tap", "flickering light", "dust", "broken chair", "ac not cooling",
        "projector distorted", "door lock broken", "handicap ramp blocked", "uneven road"
    ]
}

CATEGORY_BASE_SCORES = {
    "Electrical Hazards": 75.0,
    "Security & Safety": 70.0,
    "Water & Plumbing": 55.0,
    "Infrastructure & Building Damage": 50.0,
    "Classroom & Lab Equipment": 40.0,
    "Internet & Networking": 35.0,
    "Cleanliness & Sanitation": 30.0,
    "Transportation & Parking": 25.0,
    "Other / Needs Review": 35.0,
}

CRITICAL_LOCATIONS = ["laboratory", "lab", "hostel", "auditorium", "library", "exam hall", "server room"]

class SeverityEngine:
    def calculate(
        self,
        title: str,
        description: str,
        category: str,
        location: str,
        building: str,
        similar_count: int = 0
    ) -> Dict[str, Any]:
        text = f"{title} {description} {location}".lower()
        base_score = CATEGORY_BASE_SCORES.get(category, 40.0)
        factors: List[str] = [f"Base category score for '{category}': {base_score:.0f} pts"]
        current_score = base_score

        # Check for water near electrical equipment compound risk
        has_water = any(w in text for w in ["water", "leak", "leaking", "flood", "damp"])
        has_electric = any(e in text for e in ["wire", "electric", "socket", "computer", "panel", "switchboard", "server"])
        if has_water and has_electric:
            compound_boost = 35.0
            current_score += compound_boost
            factors.append("CRITICAL COMPOUND RISK: Water leakage near electrical/computer equipment (+35 pts)")

        # Critical keywords
        matched_crit = [k for k in HIGH_RISK_KEYWORDS["critical"] if k in text]
        if matched_crit:
            boost = min(30.0, len(matched_crit) * 18.0)
            current_score += boost
            factors.append(f"Immediate hazard signals: {', '.join(matched_crit)} (+{boost:.0f} pts)")

        # High risk keywords
        matched_high = [k for k in HIGH_RISK_KEYWORDS["high"] if k in text and k not in matched_crit]
        if matched_high:
            boost = min(20.0, len(matched_high) * 10.0)
            current_score += boost
            factors.append(f"Elevated risk signals: {', '.join(matched_high)} (+{boost:.0f} pts)")

        # High-traffic / sensitive location multiplier
        loc_lower = f"{location} {building}".lower()
        if any(cl in loc_lower for cl in CRITICAL_LOCATIONS):
            current_score += 10.0
            factors.append(f"High-traffic or academic facility ({building} / {location}) (+10 pts)")

        # Repetition / recurrence escalation
        if similar_count >= 3:
            current_score += 15.0
            factors.append(f"Persistent issue: {similar_count} similar incidents detected (+15 pts)")
        elif similar_count >= 1:
            current_score += 8.0
            factors.append(f"Recurring pattern: {similar_count} related report(s) noted (+8 pts)")

        # Clamp priority score between 10 and 100
        priority_score = min(100.0, max(10.0, current_score))

        # Determine severity level
        if priority_score >= 80.0:
            severity = "critical"
        elif priority_score >= 60.0:
            severity = "high"
        elif priority_score >= 40.0:
            severity = "medium"
        else:
            severity = "low"

        # Actionable recommendations based on score and category
        recommended_actions = self._generate_recommendations(severity, category, text)
        summary = self._generate_summary(title, category, severity, building)

        return {
            "severity_level": severity,
            "priority_score": round(priority_score, 1),
            "score_factors": factors,
            "recommended_actions": recommended_actions,
            "summary": summary
        }

    def _generate_recommendations(self, severity: str, category: str, text: str) -> List[str]:
        actions = []
        if severity == "critical":
            actions.append("Dispatch rapid-response unit immediately to isolate the area.")
            actions.append("Notify building superintendent and facility safety supervisor.")
            if "electric" in text or category == "Electrical Hazards":
                actions.append("Cut power to the affected section if safe to do so.")
            if "water" in text or category == "Water & Plumbing":
                actions.append("Shut off the primary water isolation valve for this riser.")
        elif severity == "high":
            actions.append("Assign priority work order to maintenance team within 2 hours.")
            actions.append("Display warning signage or cordon off hazardous vicinity.")
        elif severity == "medium":
            actions.append("Schedule inspection during the standard maintenance shift.")
            actions.append("Log item in preventive maintenance tracking ledger.")
        else:
            actions.append("Queue for routine facilities upkeep and monitor for recurring reports.")

        return actions

    def _generate_summary(self, title: str, category: str, severity: str, building: str) -> str:
        return f"{severity.upper()} severity {category.lower()} issue detected at {building}: '{title}'."

severity_engine = SeverityEngine()
