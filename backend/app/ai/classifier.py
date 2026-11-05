import re
from typing import Tuple, Dict, Any, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import numpy as np

# Training dataset with representative campus problem descriptions
TRAINING_DATA = [
    # Water & Plumbing
    ("There is a large amount of water leaking near Block C", "Water & Plumbing"),
    ("Water leaking continuously from ceiling on second floor", "Water & Plumbing"),
    ("The washroom tap is broken and water is overflowing everywhere", "Water & Plumbing"),
    ("Water is accumulating near the main entrance after rainfall", "Water & Plumbing"),
    ("Burst pipe in girls hostel ground floor flooding the corridor", "Water & Plumbing"),
    ("Restroom flush is not working and pipe leaking", "Water & Plumbing"),
    ("Severe sewage blockage and water backflow in cafeteria", "Water & Plumbing"),
    ("Drinking water cooler pipe leaking dirty water", "Water & Plumbing"),
    ("Ceiling dampness and dripping water onto desks", "Water & Plumbing"),
    ("Basement drainage clogged and water stagnation", "Water & Plumbing"),

    # Electrical Hazards
    ("Someone has damaged the electrical panel in the laboratory", "Electrical Hazards"),
    ("The lights are flickering in the computer laboratory", "Electrical Hazards"),
    ("Exposed electrical wires hanging from hallway ceiling", "Electrical Hazards"),
    ("Electric spark and burning smell from switchboard in Room 301", "Electrical Hazards"),
    ("Power outage in Block B and smoke coming from circuit breaker", "Electrical Hazards"),
    ("High voltage transformer buzzing loudly with visible sparks", "Electrical Hazards"),
    ("Exposed wire touching metal door frame in engineering workshop", "Electrical Hazards"),
    ("Broken wall socket with loose live wires in student lounge", "Electrical Hazards"),
    ("Short circuit caused spark near computer workstations", "Electrical Hazards"),
    ("Frequent voltage fluctuation blowing tube lights", "Electrical Hazards"),

    # Internet & Networking
    ("The Wi-Fi connection has stopped working in the library", "Internet & Networking"),
    ("Several students are facing the same internet connectivity issue", "Internet & Networking"),
    ("Wi-Fi network signal is extremely weak in Block D classrooms", "Internet & Networking"),
    ("LAN port in computer science lab 3 has no internet access", "Internet & Networking"),
    ("DNS error and unable to connect to campus Wi-Fi portal", "Internet & Networking"),
    ("Campus wireless router keeps disconnecting every 5 minutes", "Internet & Networking"),
    ("High latency and packet loss affecting online exam portal", "Internet & Networking"),
    ("Library 2nd floor access point appears offline", "Internet & Networking"),
    ("Ethernet cable snapped in multimedia seminar hall", "Internet & Networking"),
    ("Entire hostel block disconnected from university intranet", "Internet & Networking"),

    # Infrastructure & Building Damage
    ("Large crack visible on the exterior wall of mechanical block", "Infrastructure & Building Damage"),
    ("Ceiling plaster fell down in classroom 102", "Infrastructure & Building Damage"),
    ("Broken window glass in chemistry corridor posing hazard", "Infrastructure & Building Damage"),
    ("Staircase handrail is loose and shaking when held", "Infrastructure & Building Damage"),
    ("Floor tiles are cracked and broken in main auditorium foyer", "Infrastructure & Building Damage"),
    ("Door lock broken and door hinges detached in lecture hall", "Infrastructure & Building Damage"),
    ("Roof sheet damaged and flapping loudly during wind", "Infrastructure & Building Damage"),
    ("Concrete chunks chipping off the pedestrian walkway bridge", "Infrastructure & Building Damage"),
    ("Pothole and uneven surface at the campus entrance road", "Infrastructure & Building Damage"),
    ("Classroom door handle completely broken cannot close", "Infrastructure & Building Damage"),

    # Cleanliness & Sanitation
    ("Garbage bin overflowing with food waste near food court", "Cleanliness & Sanitation"),
    ("Foul smell and unsanitary conditions in 3rd floor washroom", "Cleanliness & Sanitation"),
    ("Trash discarded on open grounds behind sports complex", "Cleanliness & Sanitation"),
    ("Dust and debris accumulated in seminar hall after renovation", "Cleanliness & Sanitation"),
    ("No soap and uncleaned washroom basins in science block", "Cleanliness & Sanitation"),
    ("Pest infestation and insects found in hostel mess dining area", "Cleanliness & Sanitation"),
    ("Discarded plastic cups and papers littering the amphitheater", "Cleanliness & Sanitation"),
    ("Dirty stagnant puddles attracting mosquitoes near hostel garden", "Cleanliness & Sanitation"),
    ("Corridor floor has not been mopped for several days", "Cleanliness & Sanitation"),
    ("Washroom clogged with paper towels causing unhygienic conditions", "Cleanliness & Sanitation"),

    # Security & Safety
    ("Unauthorized individuals wandering near girls hostel at night", "Security & Safety"),
    ("Emergency exit door is locked from outside in main auditorium", "Security & Safety"),
    ("Fire extinguisher is past expiration date and pressure gauge empty", "Security & Safety"),
    ("Bicycle stolen from cycle stand outside library", "Security & Safety"),
    ("CCTV camera in parking lot appears physically tilted or broken", "Security & Safety"),
    ("Streetlights not working on pathway behind sports ground completely dark", "Security & Safety"),
    ("Suspicious package left unattended near campus admin office", "Security & Safety"),
    ("Trespasser jumped perimeter fence near north gate", "Security & Safety"),
    ("Fire alarm sensor flashing error code and beeping continuously", "Security & Safety"),
    ("Campus security guard booth unattended during late evening", "Security & Safety"),

    # Classroom & Lab Equipment
    ("Projector in lecture hall 3 is displaying distorted green colors", "Classroom & Lab Equipment"),
    ("Air conditioning unit in computer center not cooling making grinding noise", "Classroom & Lab Equipment"),
    ("Microscope focus knob broken in biology lab station 4", "Classroom & Lab Equipment"),
    ("Public address sound system and microphone screeching in hall", "Classroom & Lab Equipment"),
    ("Interactive smart board touch screen unresponsive", "Classroom & Lab Equipment"),
    ("Oscilloscope in electronics lab fails to power on", "Classroom & Lab Equipment"),
    ("Lab fume hood exhaust fan stopped working in chemistry lab", "Classroom & Lab Equipment"),
    ("Broken desk and wobbly chairs in Room 204", "Classroom & Lab Equipment"),
    ("Computer workstation 12 blue screen and keyboard damaged", "Classroom & Lab Equipment"),
    ("Podium speaker amplifier not producing audio", "Classroom & Lab Equipment"),

    # Transportation & Parking
    ("Campus shuttle bus broke down near South Gate blocking traffic", "Transportation & Parking"),
    ("Illegal car parking blocking handicap ramp and emergency vehicle lane", "Transportation & Parking"),
    ("Bicycle rack fully collapsed under weight of bikes", "Transportation & Parking"),
    ("Speed breaker paint faded causing accidents on ring road", "Transportation & Parking"),
    ("Visitor cars parked in designated faculty parking bays", "Transportation & Parking"),
    ("Campus electric shuttle charger station displaying malfunction", "Transportation & Parking"),
    ("Fallen tree branch blocking two-wheeler parking lot", "Transportation & Parking"),
    ("Electric barrier gate at main entrance stuck in upright position", "Transportation & Parking"),
]

# Keyword dictionary for rule-assisted high confidence matching
KEYWORD_RULES = {
    "Water & Plumbing": [
        "water", "leak", "leaking", "pipe", "drain", "drainage", "tap", "sink", "flush",
        "sewage", "overflow", "flooding", "restroom tap", "toilet leak", "dampness", "puddle"
    ],
    "Electrical Hazards": [
        "electric", "electrical", "spark", "wire", "wires", "shock", "panel", "switchboard",
        "short circuit", "voltage", "power outage", "flickering light", "circuit breaker", "transformer"
    ],
    "Internet & Networking": [
        "wifi", "wi-fi", "internet", "network", "lan", "ethernet", "router", "signal",
        "connectivity", "dns", "latency", "offline", "portal", "bandwidth"
    ],
    "Infrastructure & Building Damage": [
        "crack", "wall", "plaster", "window", "glass", "staircase", "handrail", "tile",
        "tiles", "ceiling fall", "door", "hinge", "roof", "pothole", "concrete", "structural"
    ],
    "Cleanliness & Sanitation": [
        "garbage", "trash", "waste", "dust", "foul smell", "odor", "dirty", "unhygienic",
        "litter", "pest", "insects", "soap", "mopping", "sanitation", "toilet smell"
    ],
    "Security & Safety": [
        "security", "stolen", "theft", "unauthorized", "trespasser", "cctv", "fire extinguisher",
        "fire alarm", "emergency exit", "dark", "streetlight", "guard", "fence", "safe"
    ],
    "Classroom & Lab Equipment": [
        "projector", "screen", "smartboard", "microscope", "ac", "air condition", "speaker",
        "microphone", "oscilloscope", "fume hood", "bench", "desk", "computer lab", "audio"
    ],
    "Transportation & Parking": [
        "bus", "shuttle", "parking", "parked", "traffic", "bicycle rack", "speed breaker",
        "barrier gate", "vehicle", "ramp blocked"
    ],
}

CATEGORY_TO_DEPARTMENT = {
    "Water & Plumbing": "Maintenance & Plumbing",
    "Electrical Hazards": "Electrical Services",
    "Internet & Networking": "IT & Campus Networking",
    "Infrastructure & Building Damage": "Estate & Civil Infrastructure",
    "Cleanliness & Sanitation": "Housekeeping & Sanitation",
    "Security & Safety": "Campus Security & Safety",
    "Classroom & Lab Equipment": "Laboratory & Audio-Visual",
    "Transportation & Parking": "Campus Transport & Logistics",
    "Other / Needs Review": "General Administration",
}

class IncidentClassifier:
    def __init__(self):
        texts = [item[0] for item in TRAINING_DATA]
        labels = [item[1] for item in TRAINING_DATA]
        
        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), stop_words="english", min_df=1)),
            ("clf", MultinomialNB(alpha=0.1))
        ])
        self.pipeline.fit(texts, labels)
        self.classes_ = self.pipeline.named_steps["clf"].classes_

    def predict(self, text: str) -> Dict[str, Any]:
        cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
        
        # 1. Check keyword frequency score
        kw_scores: Dict[str, int] = {}
        for category, kws in KEYWORD_RULES.items():
            score = 0
            for kw in kws:
                if re.search(r"\b" + re.escape(kw) + r"\b", cleaned):
                    score += 2
                elif kw in cleaned:
                    score += 1
            if score > 0:
                kw_scores[category] = score

        # 2. Scikit-learn model prediction
        probs = self.pipeline.predict_proba([cleaned])[0]
        max_idx = int(np.argmax(probs))
        ml_category = str(self.classes_[max_idx])
        ml_conf = float(probs[max_idx])

        # 3. Hybrid decision logic
        if kw_scores:
            best_kw_cat = max(kw_scores.items(), key=lambda x: x[1])
            if best_kw_cat[0] == ml_category:
                # Strong consensus
                final_category = ml_category
                final_confidence = min(0.98, max(ml_conf, 0.82) + 0.1)
            elif best_kw_cat[1] >= 3:
                # Strong keyword evidence overrides weak ML
                final_category = best_kw_cat[0]
                final_confidence = min(0.92, 0.70 + (best_kw_cat[1] * 0.05))
            else:
                # Marginal case
                final_category = ml_category if ml_conf >= 0.55 else best_kw_cat[0]
                final_confidence = max(ml_conf, 0.65)
        else:
            if ml_conf >= 0.45:
                final_category = ml_category
                final_confidence = float(ml_conf)
            else:
                final_category = "Other / Needs Review"
                final_confidence = 0.40

        suggested_dept = CATEGORY_TO_DEPARTMENT.get(final_category, "General Administration")

        return {
            "predicted_category": final_category,
            "confidence_score": round(final_confidence, 2),
            "suggested_department": suggested_dept,
            "all_probabilities": {str(c): round(float(p), 3) for c, p in zip(self.classes_, probs)}
        }

classifier = IncidentClassifier()
