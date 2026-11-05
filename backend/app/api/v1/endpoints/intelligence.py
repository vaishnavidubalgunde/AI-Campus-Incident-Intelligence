import json
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.api.deps import get_db, get_current_user, get_current_admin
from backend.app.models.entities import Incident, DiscoveredPattern, Recommendation, User
from backend.app.schemas.schemas import (
    DiscoveredPatternResponse, RecommendationResponse,
    AssistantQueryRequest, AssistantQueryResponse
)
from backend.app.analytics.pattern_discovery import pattern_discovery_engine
from backend.app.analytics.recommendations import recommendation_engine
from backend.app.analytics.assistant import analytics_assistant

router = APIRouter()

def get_all_incidents_dict(db: Session) -> List[Dict[str, Any]]:
    incidents = db.query(Incident).all()
    results = []
    for i in incidents:
        results.append({
            "id": i.id,
            "incident_number": i.incident_number,
            "title": i.title,
            "description": i.description,
            "location": i.location,
            "building": i.building,
            "category_name": i.category.name if i.category else "Other",
            "severity": i.severity,
            "priority_score": i.priority_score,
            "status": i.status,
            "assigned_department_name": i.assigned_department.name if i.assigned_department else "Unassigned",
            "created_at": i.created_at.isoformat() if i.created_at else None
        })
    return results

@router.get("/patterns", response_model=List[DiscoveredPatternResponse])
def get_patterns(db: Session = Depends(get_db)):
    patterns = db.query(DiscoveredPattern).order_by(desc(DiscoveredPattern.incident_count)).all()
    
    # If no patterns exist, automatically generate and persist
    if not patterns:
        inc_data = get_all_incidents_dict(db)
        if len(inc_data) >= 3:
            discovered = pattern_discovery_engine.analyze_patterns(inc_data)
            for pat in discovered:
                p_obj = DiscoveredPattern(
                    pattern_title=pat["pattern_title"],
                    pattern_type=pat["pattern_type"],
                    incident_count=pat["incident_count"],
                    affected_locations=json.dumps(pat["affected_locations"]),
                    categories=json.dumps(pat["categories"]),
                    time_period=pat["time_period"],
                    supporting_incident_ids=json.dumps(pat["supporting_incident_ids"]),
                    explanation=pat["explanation"],
                    suggested_action=pat["suggested_action"],
                    confidence_score=pat["confidence_score"],
                    status=pat["status"]
                )
                db.add(p_obj)
            db.commit()
            patterns = db.query(DiscoveredPattern).order_by(desc(DiscoveredPattern.incident_count)).all()

    response = []
    for p in patterns:
        try:
            locs = json.loads(p.affected_locations) if p.affected_locations else []
        except Exception:
            locs = []
        try:
            cats = json.loads(p.categories) if p.categories else []
        except Exception:
            cats = []
        try:
            ids = json.loads(p.supporting_incident_ids) if p.supporting_incident_ids else []
        except Exception:
            ids = []

        response.append(DiscoveredPatternResponse(
            id=p.id,
            pattern_title=p.pattern_title,
            pattern_type=p.pattern_type,
            incident_count=p.incident_count,
            affected_locations=locs,
            categories=cats,
            time_period=p.time_period,
            supporting_incident_ids=ids,
            explanation=p.explanation,
            suggested_action=p.suggested_action,
            confidence_score=p.confidence_score,
            status=p.status,
            created_at=p.created_at
        ))
    return response

@router.post("/patterns/refresh")
def refresh_patterns(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    inc_data = get_all_incidents_dict(db)
    discovered = pattern_discovery_engine.analyze_patterns(inc_data)
    
    db.query(DiscoveredPattern).delete()
    for pat in discovered:
        p_obj = DiscoveredPattern(
            pattern_title=pat["pattern_title"],
            pattern_type=pat["pattern_type"],
            incident_count=pat["incident_count"],
            affected_locations=json.dumps(pat["affected_locations"]),
            categories=json.dumps(pat["categories"]),
            time_period=pat["time_period"],
            supporting_incident_ids=json.dumps(pat["supporting_incident_ids"]),
            explanation=pat["explanation"],
            suggested_action=pat["suggested_action"],
            confidence_score=pat["confidence_score"],
            status=pat["status"]
        )
        db.add(p_obj)
    db.commit()

    return {"message": f"Refreshed pattern analysis. Discovered {len(discovered)} active patterns."}

@router.get("/recommendations", response_model=List[RecommendationResponse])
def get_recommendations(db: Session = Depends(get_db)):
    recs = db.query(Recommendation).filter(Recommendation.status == "active").all()
    if not recs:
        inc_data = get_all_incidents_dict(db)
        if len(inc_data) >= 2:
            new_recs = recommendation_engine.generate_recommendations(inc_data)
            for r in new_recs:
                r_obj = Recommendation(
                    title=r["title"],
                    reason=r["reason"],
                    supporting_incident_count=r["supporting_incident_count"],
                    supporting_incident_ids=json.dumps(r["supporting_incident_ids"]),
                    suggested_department=r["suggested_department"],
                    priority=r["priority"],
                    confidence=r["confidence"],
                    status=r["status"]
                )
                db.add(r_obj)
            db.commit()
            recs = db.query(Recommendation).filter(Recommendation.status == "active").all()

    response = []
    for r in recs:
        try:
            ids = json.loads(r.supporting_incident_ids) if r.supporting_incident_ids else []
        except Exception:
            ids = []
        response.append(RecommendationResponse(
            id=r.id,
            title=r.title,
            reason=r.reason,
            supporting_incident_count=r.supporting_incident_count,
            supporting_incident_ids=ids,
            suggested_department=r.suggested_department,
            priority=r.priority,
            confidence=r.confidence,
            status=r.status,
            created_at=r.created_at
        ))
    return response

@router.post("/recommendations/{rec_id}/action")
def action_recommendation(
    rec_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    rec = db.query(Recommendation).filter(Recommendation.id == rec_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    status_val = payload.get("status", "actioned")
    rec.status = status_val
    db.commit()
    return {"message": f"Recommendation '{rec.title}' updated to {status_val}"}

@router.post("/assistant", response_model=AssistantQueryResponse)
def query_assistant(
    request: AssistantQueryRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    inc_data = get_all_incidents_dict(db)
    result = analytics_assistant.answer_query(request.query, inc_data)
    return AssistantQueryResponse(**result)
