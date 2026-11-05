# REST API Reference Documentation
## AI-Based Campus Incident Intelligence & Response System

Interactive Swagger UI is accessible at: `http://127.0.0.1:8000/docs`
Redoc Documentation is accessible at: `http://127.0.0.1:8000/redoc`

Base URL: `/api/v1`

---

## 1. Authentication Endpoints

### `POST /api/v1/auth/register`
Register a new student account.

**Request Body (`application/json`):**
```json
{
  "email": "student.name@campus.edu",
  "password": "Password123!",
  "full_name": "Student Name",
  "department": "Computer Science & Engineering",
  "role": "student"
}
```

**Response (`200 OK`):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "role": "student",
  "user_id": 4,
  "full_name": "Student Name",
  "email": "student.name@campus.edu"
}
```

---

### `POST /api/v1/auth/login`
Authenticate existing student or administrator.

**Request Body (`application/json`):**
```json
{
  "email": "admin@campus.edu",
  "password": "Admin@123"
}
```

**Response (`200 OK`):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "role": "admin",
  "user_id": 1,
  "full_name": "Dr. Administrator",
  "email": "admin@campus.edu"
}
```

---

### `GET /api/v1/auth/me`
Retrieve currently authenticated user profile.
*Headers*: `Authorization: Bearer <token>`

---

## 2. Incident Endpoints

### `POST /api/v1/incidents/ai-preview`
Real-time AI pre-flight triage preview evaluated as the student types.

**Request Body:**
```json
{
  "title": "Water leaking continuously from ceiling",
  "description": "Large amount of water leaking near electrical switchboard on 2nd floor",
  "building": "Block C",
  "location": "2nd Floor Corridor"
}
```

**Response:**
```json
{
  "predicted_category": "Water & Plumbing",
  "confidence_score": 0.92,
  "suggested_department": "Maintenance & Plumbing",
  "severity_level": "critical",
  "priority_score": 90.0,
  "score_factors": [
    "Base category score for 'Water & Plumbing': 55 pts",
    "CRITICAL COMPOUND RISK: Water leakage near electrical/computer equipment (+35 pts)"
  ],
  "recommended_actions": [
    "Dispatch rapid-response unit immediately to isolate the area.",
    "Shut off the primary water isolation valve for this riser."
  ],
  "duplicates_found": [],
  "recurrence_warning": false
}
```

---

### `POST /api/v1/incidents`
Submit a validated incident report.

**Request Body:**
```json
{
  "title": "Water pipe burst in washroom",
  "description": "Continuous water leakage onto the hallway floor creating a hazard.",
  "location": "Block C 2nd Floor",
  "building": "Block C",
  "floor_room": "Room 204",
  "category_id": 1,
  "is_anonymous": false,
  "photo_url": null
}
```

---

### `GET /api/v1/incidents`
Retrieve filterable, paginated incident reports.

**Query Parameters:**
- `status` (`string`): e.g. `submitted`, `assigned`, `in_progress`, `resolved`
- `severity` (`string`): e.g. `critical`, `high`, `medium`, `low`
- `building` (`string`): Filter by campus building
- `search` (`string`): Substring query on title, location, or incident number
- `mine_only` (`boolean`): Filter reports submitted by current student
- `page` (`integer`, default `1`)
- `page_size` (`integer`, default `20`)

---

### `POST /api/v1/incidents/{id}/status`
Update incident lifecycle state (Admin only).

**Request Body:**
```json
{
  "status": "in_progress",
  "notes": "Emergency plumbing contractor dispatched to shut off riser valve."
}
```

---

### `POST /api/v1/incidents/{id}/assign`
Assign incident to a response team (Admin only).

**Request Body:**
```json
{
  "department_id": 1,
  "notes": "Assigned to Maintenance & Plumbing unit."
}
```

---

### `POST /api/v1/incidents/{id}/link-duplicate`
Merge incident as a confirmed duplicate of another primary incident (Admin only).

---

## 3. Analytics & Hotspot Endpoints

### `GET /api/v1/analytics/overview`
Retrieves institutional KPIs:
- `total_incidents`, `new_incidents`, `critical_high_count`, `unassigned_count`
- `in_progress_count`, `resolved_count`, `overdue_count`
- `recurring_patterns_count`, `avg_resolution_hours`

### `GET /api/v1/analytics/hotspots`
Retrieves aggregated spatial data for the campus schematic grid:
- Location list with critical counts and primary categories
- Category distribution counts
- Severity distribution counts
- 14-day daily volume vs. resolution trends
- Response team workload distributions

---

## 4. Intelligence & Assistant Endpoints

### `GET /api/v1/intelligence/patterns`
Retrieves AI-discovered patterns (DBSCAN clusters, location hotspots, category spikes, SLA backlogs).

### `POST /api/v1/intelligence/patterns/refresh`
Triggers real-time re-analysis across the entire database.

### `GET /api/v1/intelligence/recommendations`
Retrieves active smart administrative recommendations.

### `POST /api/v1/intelligence/assistant`
Query the Natural-Language Analytics Assistant.

**Request Body:**
```json
{
  "query": "Which block has the highest number of incidents?"
}
```

**Response:**
```json
{
  "query": "Which block has the highest number of incidents?",
  "intent_detected": "top_incident_building",
  "answer": "**Block C** has recorded the highest incident volume on campus, accounting for **38 reports**...",
  "data_summary": { "top_building": "Block C", "count": 38 },
  "relevant_incident_ids": [1, 2, 5, 8],
  "suggested_followups": [
    "What categories of incidents occur in Block C?",
    "Show critical incidents in all buildings"
  ]
}
```
