from datetime import datetime, timezone
import json
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

def utcnow():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="student", nullable=False)  # 'student' or 'admin'
    department = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relationships
    incidents = relationship("Incident", back_populates="reporter", foreign_keys="Incident.reporter_id")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    contact_email = Column(String(255), nullable=True)
    head_person = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)

    categories = relationship("IncidentCategory", back_populates="default_department")
    assigned_incidents = relationship("Incident", back_populates="assigned_department")


class IncidentCategory(Base):
    __tablename__ = "incident_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    default_department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    created_at = Column(DateTime, default=utcnow)

    default_department = relationship("Department", back_populates="categories")
    incidents = relationship("Incident", back_populates="category")


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_number = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(255), nullable=False, index=True)  # e.g., "Block C", "Central Library"
    building = Column(String(100), nullable=False, index=True)  # e.g., "Block C"
    floor_room = Column(String(100), nullable=True)              # e.g., "2nd Floor, Lab 204"
    category_id = Column(Integer, ForeignKey("incident_categories.id"), nullable=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_anonymous = Column(Boolean, default=False)
    photo_url = Column(String(500), nullable=True)

    status = Column(String(50), default="submitted", index=True, nullable=False)
    # Statuses: submitted, under_review, verified, assigned, in_progress, resolved, closed, rejected, duplicate
    severity = Column(String(50), default="medium", index=True, nullable=False)
    # Severity: low, medium, high, critical
    priority_score = Column(Float, default=50.0)  # 0 to 100

    assigned_department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    is_duplicate = Column(Boolean, default=False)
    duplicate_of_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=utcnow, index=True)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    reporter = relationship("User", back_populates="incidents", foreign_keys=[reporter_id])
    category = relationship("IncidentCategory", back_populates="incidents")
    assigned_department = relationship("Department", back_populates="assigned_incidents")
    duplicate_of = relationship("Incident", remote_side=[id])

    status_history = relationship("IncidentStatusHistory", back_populates="incident", cascade="all, delete-orphan", order_by="IncidentStatusHistory.created_at")
    assignments = relationship("IncidentAssignment", back_populates="incident", cascade="all, delete-orphan", order_by="IncidentAssignment.created_at")
    ai_analysis = relationship("AIAnalysisResult", back_populates="incident", uselist=False, cascade="all, delete-orphan")
    duplicate_links_source = relationship("DuplicateLink", foreign_keys="DuplicateLink.source_incident_id", cascade="all, delete-orphan")
    duplicate_links_target = relationship("DuplicateLink", foreign_keys="DuplicateLink.target_incident_id", cascade="all, delete-orphan")


class IncidentStatusHistory(Base):
    __tablename__ = "incident_status_history"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    previous_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False)
    changed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    incident = relationship("Incident", back_populates="status_history")
    changed_by = relationship("User")


class IncidentAssignment(Base):
    __tablename__ = "incident_assignments"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    assigned_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=utcnow)

    incident = relationship("Incident", back_populates="assignments")
    department = relationship("Department")
    assigned_by = relationship("User")


class DuplicateLink(Base):
    __tablename__ = "duplicate_links"

    id = Column(Integer, primary_key=True, index=True)
    source_incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    target_incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    similarity_score = Column(Float, nullable=False)
    linked_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    is_confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)

    source_incident = relationship("Incident", foreign_keys=[source_incident_id], overlaps="duplicate_links_source")
    target_incident = relationship("Incident", foreign_keys=[target_incident_id], overlaps="duplicate_links_target")
    linked_by = relationship("User")


class AIAnalysisResult(Base):
    __tablename__ = "ai_analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False, unique=True)
    predicted_category = Column(String(100), nullable=False)
    confidence_score = Column(Float, nullable=False)  # 0.0 to 1.0
    severity_level = Column(String(50), nullable=False)  # low, medium, high, critical
    priority_score = Column(Float, nullable=False)  # 0 to 100
    score_factors = Column(Text, nullable=True)  # JSON string
    suggested_department = Column(String(100), nullable=True)
    summary = Column(Text, nullable=False)
    recurrence_warning = Column(Boolean, default=False)
    similar_incident_ids = Column(Text, nullable=True)  # JSON array string [1, 2, 5]
    recommended_actions = Column(Text, nullable=True)  # JSON array string
    raw_analysis_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    incident = relationship("Incident", back_populates="ai_analysis")

    def get_score_factors(self):
        try:
            return json.loads(self.score_factors) if self.score_factors else []
        except Exception:
            return []

    def get_similar_ids(self):
        try:
            return json.loads(self.similar_incident_ids) if self.similar_incident_ids else []
        except Exception:
            return []

    def get_recommended_actions(self):
        try:
            return json.loads(self.recommended_actions) if self.recommended_actions else []
        except Exception:
            return []


class DiscoveredPattern(Base):
    __tablename__ = "discovered_patterns"

    id = Column(Integer, primary_key=True, index=True)
    pattern_title = Column(String(255), nullable=False)
    pattern_type = Column(String(100), nullable=False)  # recurring_issue, location_hotspot, category_spike, unresolved_cluster
    incident_count = Column(Integer, default=0)
    affected_locations = Column(Text, nullable=False)  # JSON array string
    categories = Column(Text, nullable=False)          # JSON array string
    time_period = Column(String(100), nullable=False)
    supporting_incident_ids = Column(Text, nullable=False)  # JSON array string
    explanation = Column(Text, nullable=False)
    suggested_action = Column(Text, nullable=False)
    confidence_score = Column(Float, default=0.85)
    status = Column(String(50), default="active")  # active, investigating, resolved
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    reason = Column(Text, nullable=False)
    supporting_incident_count = Column(Integer, default=0)
    supporting_incident_ids = Column(Text, nullable=False)  # JSON array string
    suggested_department = Column(String(100), nullable=False)
    priority = Column(String(50), default="medium")  # critical, high, medium, low
    confidence = Column(Float, default=0.85)
    status = Column(String(50), default="active")  # active, actioned, dismissed
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    is_read = Column(Boolean, default=False)
    notification_type = Column(String(50), default="status_update")
    created_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="notifications")
    incident = relationship("Incident")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="audit_logs")
