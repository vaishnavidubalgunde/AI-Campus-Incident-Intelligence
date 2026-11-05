from typing import List, Dict, Any
import pandas as pd

class RecommendationEngine:
    def generate_recommendations(self, incidents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not incidents or len(incidents) < 2:
            return []

        df = pd.DataFrame(incidents)
        recs: List[Dict[str, Any]] = []

        # 1. Plumbing inspection rule
        plumbing = df[df["category_name"] == "Water & Plumbing"]
        if len(plumbing) >= 3:
            bldg_plumbing = plumbing.groupby("building")
            for bldg, grp in bldg_plumbing:
                if len(grp) >= 2:
                    recs.append({
                        "title": f"Mandatory Plumbing Pipeline Audit at {bldg}",
                        "reason": f"{len(grp)} water and drainage leaks recorded at {bldg}. Risk of structural dampness and ceiling damage.",
                        "supporting_incident_count": len(grp),
                        "supporting_incident_ids": grp["id"].tolist()[:10],
                        "suggested_department": "Maintenance & Plumbing",
                        "priority": "high",
                        "confidence": 0.92,
                        "status": "active"
                    })

        # 2. Campus Wi-Fi & Network Infrastructure Rule
        network = df[df["category_name"] == "Internet & Networking"]
        if len(network) >= 3:
            unique_bldgs = network["building"].unique().tolist()
            if len(unique_bldgs) >= 2:
                recs.append({
                    "title": f"Core Switch & Access Point Overhaul ({', '.join(unique_bldgs[:3])})",
                    "reason": f"{len(network)} internet connectivity failures reported across multiple zones. Central RADIUS/VLAN or uplink saturation suspected.",
                    "supporting_incident_count": len(network),
                    "supporting_incident_ids": network["id"].tolist()[:12],
                    "suggested_department": "IT & Campus Networking",
                    "priority": "high",
                    "confidence": 0.89,
                    "status": "active"
                })

        # 3. Laboratory Electrical Safety Audit Rule
        elec_labs = df[
            (df["category_name"] == "Electrical Hazards") &
            (df["location"].str.lower().str.contains("lab", na=False))
        ]
        if len(elec_labs) >= 2:
            recs.append({
                "title": "Immediate Electrical Hazard Inspection for Academic Labs",
                "reason": f"{len(elec_labs)} electrical faults detected in student laboratory environments. Immediate fire and shock risk mitigation required.",
                "supporting_incident_count": len(elec_labs),
                "supporting_incident_ids": elec_labs["id"].tolist()[:8],
                "suggested_department": "Electrical Services",
                "priority": "critical",
                "confidence": 0.95,
                "status": "active"
            })

        # 4. Sanitation Roster Review Rule
        sanitation = df[df["category_name"] == "Cleanliness & Sanitation"]
        if len(sanitation) >= 4:
            active_san = sanitation[sanitation["status"].isin(["submitted", "under_review", "assigned"])]
            if len(active_san) >= 3:
                top_bldg = sanitation["building"].value_counts().index[0]
                recs.append({
                    "title": f"Revise Sanitation & Waste Disposal Roster at {top_bldg}",
                    "reason": f"High accumulation of unaddressed sanitation and waste reports ({len(active_san)} open) in high-footfall areas.",
                    "supporting_incident_count": len(active_san),
                    "supporting_incident_ids": active_san["id"].tolist()[:10],
                    "suggested_department": "Housekeeping & Sanitation",
                    "priority": "medium",
                    "confidence": 0.86,
                    "status": "active"
                })

        # 5. Department Workload Imbalance Rule
        active_tickets = df[df["status"].isin(["assigned", "in_progress"])]
        if len(active_tickets) >= 5:
            dept_counts = active_tickets["assigned_department_name"].value_counts()
            for dept, count in dept_counts.items():
                if count >= 6 and dept != "Unassigned":
                    recs.append({
                        "title": f"Resource Augmentation for {dept}",
                        "reason": f"{dept} currently manages {count} concurrent in-progress incidents, exceeding recommended threshold. Potential bottleneck.",
                        "supporting_incident_count": count,
                        "supporting_incident_ids": active_tickets[active_tickets["assigned_department_name"] == dept]["id"].tolist()[:10],
                        "suggested_department": dept,
                        "priority": "high",
                        "confidence": 0.88,
                        "status": "active"
                    })

        # Deduplicate recommendations by title
        seen = set()
        deduped = []
        for r in recs:
            if r["title"] not in seen:
                seen.add(r["title"])
                deduped.append(r)

        return deduped

recommendation_engine = RecommendationEngine()
