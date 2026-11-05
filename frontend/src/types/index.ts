export type UserRole = 'student' | 'admin';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  department?: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  role: UserRole;
  user_id: number;
  full_name: string;
  email: string;
}

export interface Department {
  id: number;
  name: string;
  code: string;
  contact_email?: string;
  head_person?: string;
  is_active: boolean;
}

export interface IncidentCategory {
  id: number;
  name: string;
  code: string;
  description?: string;
  default_department_id?: number;
}

export interface DuplicateMatch {
  incident_id: number;
  incident_number: string;
  title: string;
  description: string;
  location: string;
  similarity_score: number;
  status: string;
  created_at: string;
}

export interface AIAnalysisSummary {
  predicted_category: string;
  confidence_score: number;
  severity_level: 'critical' | 'high' | 'medium' | 'low';
  priority_score: number;
  score_factors: string[];
  suggested_department?: string;
  summary: string;
  recurrence_warning: boolean;
  similar_incident_ids: number[];
  recommended_actions: string[];
  similar_incidents?: DuplicateMatch[];
}

export interface StatusHistoryItem {
  id: number;
  previous_status?: string;
  new_status: string;
  notes?: string;
  changed_by_name?: string;
  created_at: string;
}

export interface AssignmentItem {
  id: number;
  department_id: number;
  department_name?: string;
  assigned_by_name?: string;
  notes?: string;
  status: string;
  created_at: string;
}

export interface Incident {
  id: number;
  incident_number: string;
  title: string;
  description: string;
  location: string;
  building: string;
  floor_room?: string;
  category_id?: number;
  category_name?: string;
  reporter_id?: number;
  reporter_name?: string;
  is_anonymous: boolean;
  photo_url?: string;
  status: 'submitted' | 'under_review' | 'verified' | 'assigned' | 'in_progress' | 'resolved' | 'closed' | 'rejected' | 'duplicate';
  severity: 'critical' | 'high' | 'medium' | 'low';
  priority_score: number;
  assigned_department_id?: number;
  assigned_department_name?: string;
  is_duplicate: boolean;
  duplicate_of_id?: number;
  resolution_notes?: string;
  created_at: string;
  updated_at: string;
  resolved_at?: string;
  ai_analysis?: AIAnalysisSummary;
  status_history: StatusHistoryItem[];
  assignments: AssignmentItem[];
}

export interface StatsOverview {
  total_incidents: number;
  new_incidents: number;
  critical_high_count: number;
  unassigned_count: number;
  in_progress_count: number;
  resolved_count: number;
  overdue_count: number;
  recurring_patterns_count: number;
  avg_resolution_hours: number;
}

export interface LocationHotspot {
  location: string;
  building: string;
  count: number;
  critical_count: number;
  high_count: number;
  unresolved_count: number;
  primary_category: string;
}

export interface CategoryCount {
  category: string;
  count: number;
}

export interface SeverityCount {
  severity: string;
  count: number;
}

export interface TrendPoint {
  date: string;
  count: number;
  resolved: number;
}

export interface TeamWorkload {
  department: string;
  pending_count: number;
  in_progress_count: number;
  resolved_count: number;
}

export interface HotspotDashboardData {
  locations: LocationHotspot[];
  categories: CategoryCount[];
  severities: SeverityCount[];
  trends: TrendPoint[];
  team_workloads: TeamWorkload[];
}

export interface DiscoveredPattern {
  id: number;
  pattern_title: string;
  pattern_type: 'recurring_issue' | 'location_hotspot' | 'category_spike' | 'unresolved_cluster';
  incident_count: number;
  affected_locations: string[];
  categories: string[];
  time_period: string;
  supporting_incident_ids: number[];
  explanation: string;
  suggested_action: string;
  confidence_score: number;
  status: string;
  created_at: string;
}

export interface Recommendation {
  id: number;
  title: string;
  reason: string;
  supporting_incident_count: number;
  supporting_incident_ids: number[];
  suggested_department: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  confidence: number;
  status: string;
  created_at: string;
}

export interface AssistantResponse {
  query: string;
  intent_detected: string;
  answer: string;
  data_summary: Record<string, any>;
  relevant_incident_ids: number[];
  suggested_followups: string[];
}

export interface NotificationItem {
  id: number;
  title: string;
  message: string;
  incident_id?: number;
  is_read: boolean;
  notification_type: string;
  created_at: string;
}

export interface AuditLogItem {
  id: number;
  user_name?: string;
  action: string;
  entity_type: string;
  entity_id?: number;
  details?: string;
  created_at: string;
}
