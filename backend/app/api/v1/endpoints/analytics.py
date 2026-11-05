from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.api.deps import get_db, get_current_user
from backend.app.models.entities import Incident, DiscoveredPattern, Department
from backend.app.schemas.schemas import (
    StatsOverview, HotspotDashboardResponse, LocationHotspot,
    CategoryCount, SeverityCount, TrendPoint, TeamWorkload
)

router = APIRouter()

@router.get("/overview", response_model=StatsOverview)
def get_stats_overview(db: Session = Depends(get_db)):
    incidents = db.query(Incident).all()
    total = len(incidents)
    new_incidents = len([i for i in incidents if i.status == "submitted"])
    crit_high = len([i for i in incidents if i.severity in ["critical", "high"]])
    unassigned = len([i for i in incidents if i.assigned_department_id is None and i.status not in ["resolved", "closed", "duplicate", "rejected"]])
    in_prog = len([i for i in incidents if i.status in ["in_progress", "assigned", "under_review"]])
    resolved = len([i for i in incidents if i.status in ["resolved", "closed"]])

    # Overdue incidents: active tickets created > 4 days ago
    cutoff_overdue = datetime.now(timezone.utc) - timedelta(days=4)
    overdue = 0
    res_hours = []

    for i in incidents:
        # Check overdue
        c_at = i.created_at
        if c_at.tzinfo is None:
            c_at = c_at.replace(tzinfo=timezone.utc)
        if i.status in ["submitted", "under_review", "assigned", "in_progress"] and c_at < cutoff_overdue:
            overdue += 1

        # Calculate resolution time
        if i.resolved_at and i.created_at:
            r_at = i.resolved_at
            if r_at.tzinfo is None:
                r_at = r_at.replace(tzinfo=timezone.utc)
            duration_hrs = (r_at - c_at).total_seconds() / 3600.0
            if duration_hrs > 0:
                res_hours.append(duration_hrs)

    avg_res = round(sum(res_hours) / len(res_hours), 1) if res_hours else 24.5
    pattern_count = db.query(DiscoveredPattern).count()

    return StatsOverview(
        total_incidents=total,
        new_incidents=new_incidents,
        critical_high_count=crit_high,
        unassigned_count=unassigned,
        in_progress_count=in_prog,
        resolved_count=resolved,
        overdue_count=overdue,
        recurring_patterns_count=pattern_count,
        avg_resolution_hours=avg_res
    )

@router.get("/hotspots", response_model=HotspotDashboardResponse)
def get_hotspot_analytics(db: Session = Depends(get_db)):
    incidents = db.query(Incident).all()
    departments = db.query(Department).all()

    # 1. Location Aggregation
    loc_stats: Dict[str, Dict[str, Any]] = {}
    for i in incidents:
        key = i.building or i.location
        if key not in loc_stats:
            loc_stats[key] = {
                "location": i.location,
                "building": i.building,
                "count": 0,
                "critical_count": 0,
                "high_count": 0,
                "unresolved_count": 0,
                "categories": {}
            }
        loc_stats[key]["count"] += 1
        if i.severity == "critical":
            loc_stats[key]["critical_count"] += 1
        elif i.severity == "high":
            loc_stats[key]["high_count"] += 1

        if i.status in ["submitted", "under_review", "assigned", "in_progress"]:
            loc_stats[key]["unresolved_count"] += 1

        cat_name = i.category.name if i.category else "Other"
        loc_stats[key]["categories"][cat_name] = loc_stats[key]["categories"].get(cat_name, 0) + 1

    location_list: List[LocationHotspot] = []
    for k, v in loc_stats.items():
        primary_cat = max(v["categories"].items(), key=lambda x: x[1])[0] if v["categories"] else "General"
        location_list.append(LocationHotspot(
            location=v["location"],
            building=v["building"],
            count=v["count"],
            critical_count=v["critical_count"],
            high_count=v["high_count"],
            unresolved_count=v["unresolved_count"],
            primary_category=primary_cat
        ))

    location_list.sort(key=lambda x: x.count, reverse=True)

    # 2. Category Distribution
    cat_counts: Dict[str, int] = {}
    for i in incidents:
        c = i.category.name if i.category else "Other / Needs Review"
        cat_counts[c] = cat_counts.get(c, 0) + 1
    categories = [CategoryCount(category=k, count=v) for k, v in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)]

    # 3. Severity Distribution
    sev_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for i in incidents:
        s = i.severity.lower() if i.severity else "medium"
        if s in sev_counts:
            sev_counts[s] += 1
        else:
            sev_counts["medium"] += 1
    severities = [SeverityCount(severity=k.title(), count=v) for k, v in sev_counts.items()]

    # 4. 14-day Trend Analysis
    today = datetime.now(timezone.utc).date()
    trend_dict = {}
    for d in range(13, -1, -1):
        dt = today - timedelta(days=d)
        date_str = dt.strftime("%b %d")
        trend_dict[date_str] = {"count": 0, "resolved": 0}

    for i in incidents:
        if i.created_at:
            c_date = i.created_at.date()
            d_str = c_date.strftime("%b %d")
            if d_str in trend_dict:
                trend_dict[d_str]["count"] += 1

        if i.resolved_at:
            r_date = i.resolved_at.date()
            rd_str = r_date.strftime("%b %d")
            if rd_str in trend_dict:
                trend_dict[rd_str]["resolved"] += 1

    trends = [TrendPoint(date=k, count=v["count"], resolved=v["resolved"]) for k, v in trend_dict.items()]

    # 5. Team Workloads
    workloads: List[TeamWorkload] = []
    dept_map = {d.id: d.name for d in departments}
    dept_counts: Dict[str, Dict[str, int]] = {
        name: {"pending": 0, "in_progress": 0, "resolved": 0}
        for name in dept_map.values()
    }

    for i in incidents:
        if i.assigned_department_id and i.assigned_department_id in dept_map:
            d_name = dept_map[i.assigned_department_id]
            if i.status in ["assigned", "under_review", "submitted"]:
                dept_counts[d_name]["pending"] += 1
            elif i.status == "in_progress":
                dept_counts[d_name]["in_progress"] += 1
            elif i.status in ["resolved", "closed"]:
                dept_counts[d_name]["resolved"] += 1

    for d_name, counts in dept_counts.items():
        workloads.append(TeamWorkload(
            department=d_name,
            pending_count=counts["pending"],
            in_progress_count=counts["in_progress"],
            resolved_count=counts["resolved"]
        ))
    workloads.sort(key=lambda x: (x.pending_count + x.in_progress_count), reverse=True)

    return HotspotDashboardResponse(
        locations=location_list,
        categories=categories,
        severities=severities,
        trends=trends,
        team_workloads=workloads
    )
