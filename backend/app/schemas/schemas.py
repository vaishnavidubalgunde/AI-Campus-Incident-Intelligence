from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any, Dict
from datetime import datetime

# --- Auth & User ---
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: int
    full_name: str
    email: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    department: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: str = Field(default="student")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- Department & Category ---
class DepartmentResponse(BaseModel):
    id: int
    name: str
    code: str
    contact_email: Optional[str] = None
    head_person: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class CategoryResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    default_department_id: Optional[int] = None

    class Config:
        from_attributes = True


# --- AI Analysis ---
class DuplicateMatch(BaseModel):
    incident_id: int
    incident_number: str
    title: str
    description: str
    location: str
    similarity_score: float
    status: str
    created_at: datetime

class AIAnalysisSummary(BaseModel):
    predicted_category: str
    confidence_score: float
    severity_level: str
    priority_score: float
    score_factors: List[str] = []
    suggested_department: Optional[str] = None
    summary: str
    recurrence_warning: bool = False
    similar_incident_ids: List[int] = []
    recommended_actions: List[str] = []
    similar_incidents: List[DuplicateMatch] = []

    class Config:
        from_attributes = True


# --- Incident ---
class IncidentCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10)
    location: str = Field(..., min_length=2, max_length=255)
    building: str = Field(..., min_length=2, max_length=100)
    floor_room: Optional[str] = None
    category_id: Optional[int] = None
    is_anonymous: bool = False
    photo_url: Optional[str] = None

class IncidentStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

class IncidentAssignRequest(BaseModel):
    department_id: int
    notes: Optional[str] = None

class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    building: Optional[str] = None
    floor_room: Optional[str] = None
    category_id: Optional[int] = None
    severity: Optional[str] = None
    priority_score: Optional[float] = None
    assigned_department_id: Optional[int] = None
    status: Optional[str] = None
    resolution_notes: Optional[str] = None

class IncidentStatusHistoryResponse(BaseModel):
    id: int
    previous_status: Optional[str] = None
    new_status: str
    notes: Optional[str] = None
    changed_by_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class IncidentAssignmentResponse(BaseModel):
    id: int
    department_id: int
    department_name: Optional[str] = None
    assigned_by_name: Optional[str] = None
    notes: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class IncidentResponse(BaseModel):
    id: int
    incident_number: str
    title: str
    description: str
    location: str
    building: str
    floor_room: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    reporter_id: Optional[int] = None
    reporter_name: Optional[str] = None
    is_anonymous: bool
    photo_url: Optional[str] = None
    status: str
    severity: str
    priority_score: float
    assigned_department_id: Optional[int] = None
    assigned_department_name: Optional[str] = None
    is_duplicate: bool
    duplicate_of_id: Optional[int] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    ai_analysis: Optional[AIAnalysisSummary] = None
    status_history: List[IncidentStatusHistoryResponse] = []
    assignments: List[IncidentAssignmentResponse] = []

    class Config:
        from_attributes = True

class IncidentListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    incidents: List[IncidentResponse]


# --- Patterns & Recommendations ---
class DiscoveredPatternResponse(BaseModel):
    id: int
    pattern_title: str
    pattern_type: str
    incident_count: int
    affected_locations: List[str]
    categories: List[str]
    time_period: str
    supporting_incident_ids: List[int]
    explanation: str
    suggested_action: str
    confidence_score: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class RecommendationResponse(BaseModel):
    id: int
    title: str
    reason: str
    supporting_incident_count: int
    supporting_incident_ids: List[int]
    suggested_department: str
    priority: str
    confidence: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Analytics & Hotspots ---
class StatsOverview(BaseModel):
    total_incidents: int
    new_incidents: int
    critical_high_count: int
    unassigned_count: int
    in_progress_count: int
    resolved_count: int
    overdue_count: int
    recurring_patterns_count: int
    avg_resolution_hours: float

class CategoryCount(BaseModel):
    category: str
    count: int

class SeverityCount(BaseModel):
    severity: str
    count: int

class LocationHotspot(BaseModel):
    location: str
    building: str
    count: int
    critical_count: int
    high_count: int
    unresolved_count: int
    primary_category: str

class TrendPoint(BaseModel):
    date: str
    count: int
    resolved: int

class TeamWorkload(BaseModel):
    department: str
    pending_count: int
    in_progress_count: int
    resolved_count: int

class HotspotDashboardResponse(BaseModel):
    locations: List[LocationHotspot]
    categories: List[CategoryCount]
    severities: List[SeverityCount]
    trends: List[TrendPoint]
    team_workloads: List[TeamWorkload]


# --- Natural Language Analytics Assistant ---
class AssistantQueryRequest(BaseModel):
    query: str

class AssistantQueryResponse(BaseModel):
    query: str
    intent_detected: str
    answer: str
    data_summary: Dict[str, Any]
    relevant_incident_ids: List[int] = []
    suggested_followups: List[str] = []


# --- Notification & Audit ---
class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    incident_id: Optional[int] = None
    is_read: bool
    notification_type: str
    created_at: datetime

    class Config:
        from_attributes = True

class AuditLogResponse(BaseModel):
    id: int
    user_name: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    details: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
