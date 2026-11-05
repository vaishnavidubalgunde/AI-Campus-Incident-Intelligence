from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import json
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from backend.app.api.deps import get_db, get_current_user, get_current_admin
from backend.app.models.entities import (
    Incident, IncidentCategory, Department, User,
    AIAnalysisResult, IncidentStatusHistory, IncidentAssignment,
    DuplicateLink, Notification, AuditLog
)
from backend.app.schemas.schemas import (
    IncidentCreate, IncidentUpdate, IncidentStatusUpdate,
    IncidentAssignRequest, IncidentResponse, IncidentListResponse,
    AIAnalysisSummary, DuplicateMatch
)
from backend.app.ai.classifier import classifier
from backend.app.ai.severity_engine import severity_engine
from backend.app.ai.duplicate_detector import duplicate_detector

router = APIRouter()

def serialize_incident(inc: Incident, db: Session) -> Dict[str, Any]:
    reporter_name = "Anonymous Student" if inc.is_anonymous else (inc.reporter.full_name if inc.reporter else "Unknown")
    cat_name = inc.category.name if inc.category else "Uncategorized"
    dept_name = inc.assigned_department.name if inc.assigned_department else None

    ai_data = None
    if inc.ai_analysis:
        # Load similar incidents
        sim_matches = []
        similar_ids = inc.ai_analysis.get_similar_ids()
        if similar_ids:
            sim_records = db.query(Incident).filter(Incident.id.in_(similar_ids)).all()
            for s in sim_records:
                sim_matches.append(DuplicateMatch(
                    incident_id=s.id,
                    incident_number=s.incident_number,
                    title=s.title,
                    description=s.description[:100] + "...",
                    location=s.location,
                    similarity_score=0.75,
                    status=s.status,
                    created_at=s.created_at
                ))

        ai_data = AIAnalysisSummary(
            predicted_category=inc.ai_analysis.predicted_category,
            confidence_score=inc.ai_analysis.confidence_score,
            severity_level=inc.ai_analysis.severity_level,
            priority_score=inc.ai_analysis.priority_score,
            score_factors=inc.ai_analysis.get_score_factors(),
            suggested_department=inc.ai_analysis.suggested_department,
            summary=inc.ai_analysis.summary,
            recurrence_warning=inc.ai_analysis.recurrence_warning,
            similar_incident_ids=similar_ids,
            recommended_actions=inc.ai_analysis.get_recommended_actions(),
            similar_incidents=sim_matches
        )

    history_list = []
    for h in inc.status_history:
        history_list.append({
            "id": h.id,
            "previous_status": h.previous_status,
            "new_status": h.new_status,
            "notes": h.notes,
            "changed_by_name": h.changed_by.full_name if h.changed_by else "System",
            "created_at": h.created_at
        })

    assignments_list = []
    for a in inc.assignments:
        assignments_list.append({
            "id": a.id,
            "department_id": a.department_id,
            "department_name": a.department.name if a.department else None,
            "assigned_by_name": a.assigned_by.full_name if a.assigned_by else "System",
            "notes": a.notes,
            "status": a.status,
            "created_at": a.created_at
        })

    return {
        "id": inc.id,
        "incident_number": inc.incident_number,
        "title": inc.title,
        "description": inc.description,
        "location": inc.location,
        "building": inc.building,
        "floor_room": inc.floor_room,
        "category_id": inc.category_id,
        "category_name": cat_name,
        "reporter_id": inc.reporter_id if not inc.is_anonymous else None,
        "reporter_name": reporter_name,
        "is_anonymous": inc.is_anonymous,
        "photo_url": inc.photo_url,
        "status": inc.status,
        "severity": inc.severity,
        "priority_score": inc.priority_score,
        "assigned_department_id": inc.assigned_department_id,
        "assigned_department_name": dept_name,
        "is_duplicate": inc.is_duplicate,
        "duplicate_of_id": inc.duplicate_of_id,
        "resolution_notes": inc.resolution_notes,
        "created_at": inc.created_at,
        "updated_at": inc.updated_at,
        "resolved_at": inc.resolved_at,
        "ai_analysis": ai_data,
        "status_history": history_list,
        "assignments": assignments_list,
    }

@router.post("/ai-preview")
def preview_incident_ai(
    payload: Dict[str, Any],
    db: Session = Depends(get_db)
):
    title = payload.get("title", "")
    description = payload.get("description", "")
    building = payload.get("building", "")
    location = payload.get("location", "")

    if not title and not description:
        return {"error": "Title or description required"}

    # 1. Run classifier
    ai_cls = classifier.predict(f"{title} {description}")
    
    # 2. Check duplicates against active incidents
    recent_incidents = db.query(Incident).order_by(desc(Incident.created_at)).limit(100).all()
    inc_dicts = [
        {
            "id": i.id,
            "incident_number": i.incident_number,
            "title": i.title,
            "description": i.description,
            "location": i.location,
            "building": i.building,
            "category_name": i.category.name if i.category else "",
            "status": i.status,
            "created_at": i.created_at
        }
        for i in recent_incidents
    ]
    duplicates = duplicate_detector.find_duplicates(
        target_title=title,
        target_description=description,
        target_building=building,
        target_category=ai_cls["predicted_category"],
        existing_incidents=inc_dicts,
        limit=4
    )

    # 3. Severity calculation
    ai_sev = severity_engine.calculate(
        title=title,
        description=description,
        category=ai_cls["predicted_category"],
        location=location,
        building=building,
        similar_count=len(duplicates)
    )

    return {
        "predicted_category": ai_cls["predicted_category"],
        "confidence_score": ai_cls["confidence_score"],
        "suggested_department": ai_cls["suggested_department"],
        "severity_level": ai_sev["severity_level"],
        "priority_score": ai_sev["priority_score"],
        "score_factors": ai_sev["score_factors"],
        "recommended_actions": ai_sev["recommended_actions"],
        "summary": ai_sev["summary"],
        "duplicates_found": duplicates,
        "recurrence_warning": len(duplicates) > 0
    }

@router.post("", response_model=IncidentResponse)
def create_incident(
    incident_in: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    # Determine category
    category_id = incident_in.category_id
    if not category_id:
        ai_pred = classifier.predict(f"{incident_in.title} {incident_in.description}")
        matched_cat = db.query(IncidentCategory).filter(
            IncidentCategory.name == ai_pred["predicted_category"]
        ).first()
        if matched_cat:
            category_id = matched_cat.id
        else:
            other_cat = db.query(IncidentCategory).filter(
                IncidentCategory.code == "OTHER"
            ).first()
            category_id = other_cat.id if other_cat else None

    cat_obj = db.query(IncidentCategory).filter(IncidentCategory.id == category_id).first() if category_id else None
    cat_name = cat_obj.name if cat_obj else "Other / Needs Review"

    # Find duplicates
    recent_incidents = db.query(Incident).order_by(desc(Incident.created_at)).limit(100).all()
    inc_dicts = [
        {
            "id": i.id,
            "incident_number": i.incident_number,
            "title": i.title,
            "description": i.description,
            "location": i.location,
            "building": i.building,
            "category_name": i.category.name if i.category else "",
            "status": i.status,
            "created_at": i.created_at
        }
        for i in recent_incidents
    ]
    duplicates = duplicate_detector.find_duplicates(
        target_title=incident_in.title,
        target_description=incident_in.description,
        target_building=incident_in.building,
        target_category=cat_name,
        existing_incidents=inc_dicts,
        limit=5
    )

    # Calculate AI severity
    ai_sev = severity_engine.calculate(
        title=incident_in.title,
        description=incident_in.description,
        category=cat_name,
        location=incident_in.location,
        building=incident_in.building,
        similar_count=len(duplicates)
    )

    # Generate sequential incident number
    count_today = db.query(Incident).count() + 1
    incident_number = f"INC-2026-{count_today:04d}"

    # Default department assignment based on category
    assigned_dept_id = cat_obj.default_department_id if cat_obj else None

    new_incident = Incident(
        incident_number=incident_number,
        title=incident_in.title,
        description=incident_in.description,
        location=incident_in.location,
        building=incident_in.building,
        floor_room=incident_in.floor_room,
        category_id=category_id,
        reporter_id=current_user.id if current_user and not incident_in.is_anonymous else None,
        is_anonymous=incident_in.is_anonymous,
        photo_url=incident_in.photo_url,
        status="submitted",
        severity=ai_sev["severity_level"],
        priority_score=ai_sev["priority_score"],
        assigned_department_id=assigned_dept_id,
        is_duplicate=bool(len(duplicates) > 0 and duplicates[0]["similarity_score"] >= 0.85),
        duplicate_of_id=duplicates[0]["incident_id"] if (len(duplicates) > 0 and duplicates[0]["similarity_score"] >= 0.85) else None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(new_incident)
    db.flush()

    # Save AI Analysis Record
    ai_cls = classifier.predict(f"{incident_in.title} {incident_in.description}")
    ai_record = AIAnalysisResult(
        incident_id=new_incident.id,
        predicted_category=ai_cls["predicted_category"],
        confidence_score=ai_cls["confidence_score"],
        severity_level=ai_sev["severity_level"],
        priority_score=ai_sev["priority_score"],
        score_factors=json.dumps(ai_sev["score_factors"]),
        suggested_department=ai_cls["suggested_department"],
        summary=ai_sev["summary"],
        recurrence_warning=len(duplicates) > 0,
        similar_incident_ids=json.dumps([d["incident_id"] for d in duplicates]),
        recommended_actions=json.dumps(ai_sev["recommended_actions"]),
        created_at=datetime.now(timezone.utc)
    )
    db.add(ai_record)

    # Initial status history
    status_entry = IncidentStatusHistory(
        incident_id=new_incident.id,
        previous_status=None,
        new_status="submitted",
        changed_by_id=current_user.id if current_user else None,
        notes="Incident reported and registered in the system.",
        created_at=datetime.now(timezone.utc)
    )
    db.add(status_entry)

    # Audit log
    audit = AuditLog(
        user_id=current_user.id if current_user else None,
        action="CREATE_INCIDENT",
        entity_type="INCIDENT",
        entity_id=new_incident.id,
        details=f"Created {incident_number} - Severity: {ai_sev['severity_level'].upper()}",
        ip_address="127.0.0.1"
    )
    db.add(audit)

    # User notification
    if current_user and not incident_in.is_anonymous:
        notif = Notification(
            user_id=current_user.id,
            title="Incident Report Received",
            message=f"Your incident report '{incident_in.title}' ({incident_number}) was successfully submitted.",
            incident_id=new_incident.id,
            notification_type="submission_confirmation"
        )
        db.add(notif)

    db.commit()
    db.refresh(new_incident)

    return serialize_incident(new_incident, db)

@router.get("", response_model=IncidentListResponse)
def list_incidents(
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    severity: Optional[str] = None,
    category_id: Optional[int] = None,
    building: Optional[str] = None,
    department_id: Optional[int] = None,
    search: Optional[str] = None,
    mine_only: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_current_user)
):
    query = db.query(Incident)

    if mine_only and current_user:
        query = query.filter(Incident.reporter_id == current_user.id)

    if status:
        query = query.filter(Incident.status == status)
    if severity:
        query = query.filter(Incident.severity == severity)
    if category_id:
        query = query.filter(Incident.category_id == category_id)
    if building:
        query = query.filter(Incident.building == building)
    if department_id:
        query = query.filter(Incident.assigned_department_id == department_id)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Incident.title.ilike(search_pattern),
                Incident.description.ilike(search_pattern),
                Incident.location.ilike(search_pattern),
                Incident.incident_number.ilike(search_pattern)
            )
        )

    total = query.count()
    incidents = query.order_by(desc(Incident.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    return IncidentListResponse(
        total=total,
        page=page,
        page_size=page_size,
        incidents=[serialize_incident(i, db) for i in incidents]
    )

@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return serialize_incident(inc, db)

@router.patch("/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: int,
    update_in: IncidentUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    if update_in.severity is not None:
        inc.severity = update_in.severity
    if update_in.priority_score is not None:
        inc.priority_score = update_in.priority_score
    if update_in.category_id is not None:
        inc.category_id = update_in.category_id
    if update_in.assigned_department_id is not None:
        inc.assigned_department_id = update_in.assigned_department_id
    if update_in.resolution_notes is not None:
        inc.resolution_notes = update_in.resolution_notes
    if update_in.status is not None and update_in.status != inc.status:
        old_status = inc.status
        inc.status = update_in.status
        if update_in.status in ["resolved", "closed"]:
            inc.resolved_at = datetime.now(timezone.utc)
        hist = IncidentStatusHistory(
            incident_id=inc.id,
            previous_status=old_status,
            new_status=update_in.status,
            changed_by_id=admin.id,
            notes=f"Status modified via admin edit: {update_in.resolution_notes or ''}"
        )
        db.add(hist)

    inc.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(inc)
    return serialize_incident(inc, db)

@router.post("/{incident_id}/status", response_model=IncidentResponse)
def update_incident_status(
    incident_id: int,
    status_in: IncidentStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    previous_status = inc.status
    inc.status = status_in.status
    inc.updated_at = datetime.now(timezone.utc)

    if status_in.status in ["resolved", "closed"]:
        inc.resolved_at = datetime.now(timezone.utc)
        if status_in.notes:
            inc.resolution_notes = status_in.notes

    # Create status history
    history = IncidentStatusHistory(
        incident_id=inc.id,
        previous_status=previous_status,
        new_status=status_in.status,
        changed_by_id=admin.id,
        notes=status_in.notes
    )
    db.add(history)

    # Notify student reporter
    if inc.reporter_id:
        notif = Notification(
            user_id=inc.reporter_id,
            title=f"Incident Status: {status_in.status.replace('_', ' ').title()}",
            message=f"Your incident report '{inc.title}' status was updated from {previous_status} to {status_in.status}. {status_in.notes or ''}",
            incident_id=inc.id,
            notification_type="status_change"
        )
        db.add(notif)

    # Audit log
    audit = AuditLog(
        user_id=admin.id,
        action="UPDATE_STATUS",
        entity_type="INCIDENT",
        entity_id=inc.id,
        details=f"Status changed from {previous_status} to {status_in.status}. Notes: {status_in.notes or ''}",
        ip_address="127.0.0.1"
    )
    db.add(audit)

    db.commit()
    db.refresh(inc)
    return serialize_incident(inc, db)

@router.post("/{incident_id}/assign", response_model=IncidentResponse)
def assign_incident(
    incident_id: int,
    assign_in: IncidentAssignRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    dept = db.query(Department).filter(Department.id == assign_in.department_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")

    inc.assigned_department_id = dept.id
    if inc.status in ["submitted", "under_review", "verified"]:
        inc.status = "assigned"

    inc.updated_at = datetime.now(timezone.utc)

    assignment = IncidentAssignment(
        incident_id=inc.id,
        department_id=dept.id,
        assigned_by_id=admin.id,
        notes=assign_in.notes,
        status="active"
    )
    db.add(assignment)

    # Audit log
    audit = AuditLog(
        user_id=admin.id,
        action="ASSIGN_DEPARTMENT",
        entity_type="INCIDENT",
        entity_id=inc.id,
        details=f"Assigned to {dept.name}. Notes: {assign_in.notes or ''}",
        ip_address="127.0.0.1"
    )
    db.add(audit)

    db.commit()
    db.refresh(inc)
    return serialize_incident(inc, db)

@router.post("/{incident_id}/link-duplicate")
def link_duplicate(
    incident_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    target_id = payload.get("target_incident_id")
    notes = payload.get("notes", "Confirmed duplicate by administrator.")
    
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    target_inc = db.query(Incident).filter(Incident.id == target_id).first()
    if not inc or not target_inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    inc.is_duplicate = True
    inc.duplicate_of_id = target_inc.id
    inc.status = "duplicate"
    inc.resolution_notes = f"Merged into {target_inc.incident_number}. {notes}"
    inc.updated_at = datetime.now(timezone.utc)

    link = DuplicateLink(
        source_incident_id=inc.id,
        target_incident_id=target_inc.id,
        similarity_score=payload.get("similarity_score", 0.85),
        linked_by_id=admin.id,
        notes=notes,
        is_confirmed=True
    )
    db.add(link)

    audit = AuditLog(
        user_id=admin.id,
        action="LINK_DUPLICATE",
        entity_type="INCIDENT",
        entity_id=inc.id,
        details=f"Linked as duplicate of {target_inc.incident_number}",
        ip_address="127.0.0.1"
    )
    db.add(audit)

    db.commit()
    return {"message": f"Successfully linked {inc.incident_number} as duplicate of {target_inc.incident_number}"}
