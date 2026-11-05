import re
from typing import Dict, Any, List
import pandas as pd

class AnalyticsAssistant:
    def answer_query(self, query: str, incidents: List[Dict[str, Any]]) -> Dict[str, Any]:
        q = query.lower().strip()
        df = pd.DataFrame(incidents) if incidents else pd.DataFrame()

        if df.empty:
            return {
                "query": query,
                "intent_detected": "empty_database",
                "answer": "No incident records are currently present in the database to analyze.",
                "data_summary": {},
                "relevant_incident_ids": [],
                "suggested_followups": ["Load synthetic demonstration data", "Submit a test incident report"]
            }

        # Intent 1: Highest incidents by block/building
        if any(term in q for term in ["highest number", "most incidents", "which block", "which building", "top location", "most problems"]):
            bldg_counts = df["building"].value_counts()
            top_bldg = bldg_counts.index[0]
            top_count = int(bldg_counts.iloc[0])
            total = len(df)
            pct = round((top_count / total) * 100, 1)

            answer = (
                f"**{top_bldg}** has recorded the highest incident volume on campus, "
                f"accounting for **{top_count} reports** ({pct}% of all campus incidents). "
                f"The runner-up is **{bldg_counts.index[1]}** with {int(bldg_counts.iloc[1])} reports."
            )
            top_ids = df[df["building"] == top_bldg]["id"].tolist()[:10]
            return {
                "query": query,
                "intent_detected": "top_incident_building",
                "answer": answer,
                "data_summary": {
                    "top_building": top_bldg,
                    "count": top_count,
                    "total_incidents": total,
                    "breakdown": {b: int(c) for b, c in bldg_counts.head(5).items()}
                },
                "relevant_incident_ids": top_ids,
                "suggested_followups": [
                    f"What categories of incidents occur in {top_bldg}?",
                    "Show critical incidents in all buildings",
                    "Which department is handling these?"
                ]
            }

        # Intent 2: Critical / Electrical hazards
        if ("electrical" in q and ("critical" in q or "urgent" in q or "hazard" in q or "high" in q)) or ("critical electrical" in q):
            elec_crit = df[(df["category_name"] == "Electrical Hazards") & (df["severity"].isin(["critical", "high"]))]
            count = len(elec_crit)
            ids = elec_crit["id"].tolist()
            bldgs = elec_crit["building"].unique().tolist()

            answer = (
                f"Found **{count} critical or high-priority electrical incident(s)** across campus. "
                f"Affected areas include **{', '.join(bldgs[:4])}**. "
                f"Immediate safety inspections are strongly recommended for open items."
            )
            return {
                "query": query,
                "intent_detected": "critical_electrical_incidents",
                "answer": answer,
                "data_summary": {
                    "count": count,
                    "locations": bldgs,
                    "unresolved_count": len(elec_crit[elec_crit["status"].isin(["submitted", "assigned", "in_progress"])])
                },
                "relevant_incident_ids": ids[:10],
                "suggested_followups": [
                    "What should the electrical team prioritize?",
                    "Which laboratories have electrical issues?"
                ]
            }

        # Intent 3: Water leakage / plumbing unresolved
        if "water" in q or "leak" in q or "plumbing" in q:
            water_df = df[df["category_name"] == "Water & Plumbing"]
            unresolved = water_df[water_df["status"].isin(["submitted", "under_review", "assigned", "in_progress"])]
            unresolved_count = len(unresolved)
            total_water = len(water_df)
            top_bldg = water_df["building"].value_counts().index[0] if not water_df.empty else "N/A"

            answer = (
                f"There are currently **{unresolved_count} unresolved water leakage & plumbing incidents** "
                f"out of {total_water} total plumbing complaints campus-wide. "
                f"The highest concentration of water leaks is in **{top_bldg}**."
            )
            return {
                "query": query,
                "intent_detected": "unresolved_water_leaks",
                "answer": answer,
                "data_summary": {
                    "unresolved_count": unresolved_count,
                    "total_water_incidents": total_water,
                    "top_building": top_bldg
                },
                "relevant_incident_ids": unresolved["id"].tolist()[:10],
                "suggested_followups": [
                    f"Show all water incidents in {top_bldg}",
                    "What should the maintenance team prioritize?"
                ]
            }

        # Intent 4: Pending workload / highest team workload
        if any(term in q for term in ["workload", "pending", "department", "team workload", "highest pending"]):
            active = df[df["status"].isin(["assigned", "in_progress"])]
            workload = active["assigned_department_name"].value_counts()
            if not workload.empty:
                top_dept = workload.index[0]
                top_count = int(workload.iloc[0])
                answer = (
                    f"**{top_dept}** carries the highest active pending workload with "
                    f"**{top_count} unresolved assigned incidents**, followed by "
                    f"**{workload.index[1] if len(workload) > 1 else 'None'}** "
                    f"({int(workload.iloc[1]) if len(workload) > 1 else 0} active)."
                )
                dept_ids = active[active["assigned_department_name"] == top_dept]["id"].tolist()[:10]
                return {
                    "query": query,
                    "intent_detected": "department_workload",
                    "answer": answer,
                    "data_summary": {
                        "top_department": top_dept,
                        "active_count": top_count,
                        "team_breakdown": {d: int(c) for d, c in workload.items()}
                    },
                    "relevant_incident_ids": dept_ids,
                    "suggested_followups": [
                        f"Show open incidents assigned to {top_dept}",
                        "Which incidents are overdue?"
                    ]
                }

        # Intent 5: Priorities for maintenance or general team
        if "prioritize" in q or "priority" in q:
            crit_high = df[
                (df["status"].isin(["submitted", "assigned", "in_progress"])) &
                (df["severity"].isin(["critical", "high"]))
            ].sort_values(by="priority_score", ascending=False)
            
            count = len(crit_high)
            top_3 = crit_high.head(3)
            titles = [f"'{r['title']}' ({r['building']})" for _, r in top_3.iterrows()]
            
            answer = (
                f"Administrators and maintenance should prioritize **{count} critical & high-urgency open tickets**. "
                f"The top urgent tickets right now are: {', '.join(titles)}."
            )
            return {
                "query": query,
                "intent_detected": "action_prioritization",
                "answer": answer,
                "data_summary": {
                    "total_urgent_open": count,
                    "top_priorities": titles
                },
                "relevant_incident_ids": crit_high["id"].tolist()[:8],
                "suggested_followups": [
                    "Which incidents are overdue?",
                    "Show recurring problem patterns"
                ]
            }

        # Intent 6: Recurring problems / patterns summary
        if "recurring" in q or "pattern" in q or "repeated" in q or "summarize" in q:
            grouped = df.groupby(["building", "category_name"]).size()
            recurring = grouped[grouped >= 3].reset_index(name="count")
            
            rec_summaries = [
                f"{row['count']}x {row['category_name']} in {row['building']}"
                for _, row in recurring.head(4).iterrows()
            ]
            answer = (
                f"Identified **{len(recurring)} distinct recurring incident patterns** across the campus database. "
                f"Major highlights include: {'; '.join(rec_summaries)}."
            )
            return {
                "query": query,
                "intent_detected": "recurring_problems_summary",
                "answer": answer,
                "data_summary": {
                    "pattern_count": len(recurring),
                    "recurring_groups": rec_summaries
                },
                "relevant_incident_ids": df[df["building"] == (recurring.iloc[0]["building"] if not recurring.empty else "")]["id"].tolist()[:10],
                "suggested_followups": [
                    "What actions are recommended for recurring Wi-Fi issues?",
                    "Which block has the highest number of incidents?"
                ]
            }

        # Intent 7: General / Fallback with intelligent data overview
        total = len(df)
        open_count = len(df[df["status"].isin(["submitted", "assigned", "in_progress"])])
        crit_count = len(df[df["severity"] == "critical"])
        answer = (
            f"Database analysis indicates **{total} total incidents** registered on campus. "
            f"Currently, **{open_count} are active** and **{crit_count} are marked critical severity**. "
            f"You can ask about specific buildings (e.g. 'Which block has the most incidents?'), "
            f"categories ('How many water leaks?'), team workloads, or recurring patterns."
        )
        return {
            "query": query,
            "intent_detected": "general_campus_overview",
            "answer": answer,
            "data_summary": {
                "total": total,
                "active": open_count,
                "critical": crit_count
            },
            "relevant_incident_ids": df[df["severity"] == "critical"]["id"].tolist()[:5],
            "suggested_followups": [
                "Which block has the highest number of incidents?",
                "Show all critical electrical incidents",
                "Which department has the highest pending workload?",
                "What should the maintenance team prioritize?"
            ]
        }

analytics_assistant = AnalyticsAssistant()
