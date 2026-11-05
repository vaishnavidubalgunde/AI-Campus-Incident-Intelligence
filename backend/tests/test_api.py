import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.main import app
from backend.app.ai.classifier import classifier
from backend.app.ai.severity_engine import severity_engine
from backend.app.ai.duplicate_detector import duplicate_detector
from backend.app.analytics.pattern_discovery import pattern_discovery_engine
from backend.app.analytics.recommendations import recommendation_engine

client = TestClient(app)

# =====================================================================
# 1. AI Core Algorithm Unit Tests
# =====================================================================
def test_ai_classifier_water_plumbing():
    result = classifier.predict("There is water leaking continuously from ceiling on second floor of Block C")
    assert result["predicted_category"] == "Water & Plumbing"
    assert result["confidence_score"] >= 0.70
    assert "Plumbing" in result["suggested_department"]

def test_ai_classifier_electrical_hazard():
    result = classifier.predict("Someone noticed sparking and burning smell from electrical panel in lab")
    assert result["predicted_category"] == "Electrical Hazards"
    assert result["confidence_score"] >= 0.70
    assert "Electrical" in result["suggested_department"]

def test_ai_classifier_wifi_networking():
    result = classifier.predict("The Wi-Fi connection has stopped working in the central library")
    assert result["predicted_category"] == "Internet & Networking"
    assert result["confidence_score"] >= 0.70
    assert "Networking" in result["suggested_department"]

def test_severity_engine_critical_compound_risk():
    # Water leaking near electrical switchboard
    res = severity_engine.calculate(
        title="Water leaking on electrical switchboard",
        description="Water dripping onto the main electrical panel causing sparks and shock risk in lab",
        category="Electrical Hazards",
        location="Computer Lab 3",
        building="Block A",
        similar_count=1
    )
    assert res["severity_level"] in ["critical", "high"]
    assert res["priority_score"] >= 75.0
    assert any("COMPOUND" in factor or "hazard" in factor.lower() or "spark" in factor.lower() for factor in res["score_factors"])

def test_severity_engine_low_minor_issue():
    res = severity_engine.calculate(
        title="Faded room sign board",
        description="The room number acrylic plate is slightly faded on the door",
        category="Infrastructure & Building Damage",
        location="Storage Room",
        building="Block C",
        similar_count=0
    )
    assert res["severity_level"] in ["low", "medium"]
    assert res["priority_score"] < 65.0

def test_duplicate_detector_flags_matching_reports():
    existing = [
        {
            "id": 101,
            "incident_number": "INC-2026-0101",
            "title": "Wi-Fi connection down in Central Library",
            "description": "Students cannot connect to campus wifi in library 2nd floor",
            "location": "Central Library",
            "building": "Central Library",
            "category_name": "Internet & Networking",
            "status": "submitted"
        }
    ]
    # New report describing the same incident
    matches = duplicate_detector.find_duplicates(
        target_title="Central library wifi is not working",
        target_description="Internet connection has stopped working on 2nd floor of library",
        target_building="Central Library",
        target_category="Internet & Networking",
        existing_incidents=existing
    )
    assert len(matches) > 0
    assert matches[0]["incident_id"] == 101
    assert matches[0]["similarity_score"] >= 0.50

def test_duplicate_detector_does_not_merge_different_incidents():
    existing = [
        {
            "id": 102,
            "incident_number": "INC-2026-0102",
            "title": "Broken window in hostel",
            "description": "Window glass shattered in room 12",
            "location": "Hostel 1",
            "building": "Hostel 1",
            "category_name": "Infrastructure & Building Damage",
            "status": "submitted"
        }
    ]
    # Completely different incident
    matches = duplicate_detector.find_duplicates(
        target_title="Water leak in cafeteria kitchen",
        target_description="Plumbing tap leaking water in food court",
        target_building="Cafeteria",
        target_category="Water & Plumbing",
        existing_incidents=existing
    )
    assert len(matches) == 0

def test_pattern_discovery_groups_concentrated_hotspot():
    incidents = [
        {"id": 1, "building": "Block C", "location": "Block C 2nd Floor", "category_name": "Water & Plumbing", "title": "Water leak 1", "description": "pipe leak", "severity": "high", "status": "submitted"},
        {"id": 2, "building": "Block C", "location": "Block C Washroom", "category_name": "Water & Plumbing", "title": "Water leak 2", "description": "pipe leak", "severity": "high", "status": "submitted"},
        {"id": 3, "building": "Block C", "location": "Block C Entrance", "category_name": "Water & Plumbing", "title": "Water leak 3", "description": "pipe leak", "severity": "medium", "status": "submitted"},
        {"id": 4, "building": "Block C", "location": "Block C 3rd Floor", "category_name": "Water & Plumbing", "title": "Water leak 4", "description": "pipe leak", "severity": "high", "status": "submitted"},
    ]
    patterns = pattern_discovery_engine.analyze_patterns(incidents)
    assert len(patterns) >= 1
    assert "Block C" in patterns[0]["pattern_title"] or "Water & Plumbing" in patterns[0]["pattern_title"]
    assert patterns[0]["incident_count"] >= 3

# =====================================================================
# 2. Authentication & Authorization API Tests
# =====================================================================
def test_login_demo_admin():
    response = client.post("/api/v1/auth/login", json={
        "email": "admin@campus.edu",
        "password": "Admin@123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "admin"
    assert data["email"] == "admin@campus.edu"

def test_login_demo_student():
    response = client.post("/api/v1/auth/login", json={
        "email": "student@campus.edu",
        "password": "Student@123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "student"

def test_invalid_login():
    response = client.post("/api/v1/auth/login", json={
        "email": "admin@campus.edu",
        "password": "WrongPassword999"
    })
    assert response.status_code == 401

def test_register_new_student():
    import uuid
    rand_email = f"test_{uuid.uuid4().hex[:8]}@campus.edu"
    response = client.post("/api/v1/auth/register", json={
        "email": rand_email,
        "password": "Password123!",
        "full_name": "Test Student User",
        "department": "Biotechnology",
        "role": "student"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "student"
    assert "access_token" in data

# =====================================================================
# 3. Incident Endpoints & Workflows
# =====================================================================
def test_get_departments_and_categories():
    r1 = client.get("/api/v1/departments")
    assert r1.status_code == 200
    assert len(r1.json()) >= 5

    r2 = client.get("/api/v1/categories")
    assert r2.status_code == 200
    assert len(r2.json()) >= 7

def test_create_incident_with_ai_analysis():
    # Login as student
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "student@campus.edu",
        "password": "Student@123"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_payload = {
        "title": "Severe water pipe burst in hostel washroom",
        "description": "The main water pipe under the washroom basin burst and water is flooding the hallway floor rapidly.",
        "location": "Hostel 1 Wing B",
        "building": "Hostel 1",
        "floor_room": "2nd Floor Washroom",
        "is_anonymous": False
    }

    resp = client.post("/api/v1/incidents", json=create_payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["incident_number"].startswith("INC-")
    assert data["status"] == "submitted"
    assert data["ai_analysis"] is not None
    assert data["ai_analysis"]["predicted_category"] == "Water & Plumbing"
    assert data["ai_analysis"]["priority_score"] >= 40.0

def test_admin_update_status_and_assignment():
    # Login as admin
    admin_login = client.post("/api/v1/auth/login", json={
        "email": "admin@campus.edu",
        "password": "Admin@123"
    })
    token = admin_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch first incident
    list_resp = client.get("/api/v1/incidents?page_size=1", headers=headers)
    inc_id = list_resp.json()["incidents"][0]["id"]

    # Change status to in_progress
    status_resp = client.post(
        f"/api/v1/incidents/{inc_id}/status",
        json={"status": "in_progress", "notes": "Technician dispatched to inspect"},
        headers=headers
    )
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "in_progress"

# =====================================================================
# 4. Analytics, Hotspots & Assistant Endpoints
# =====================================================================
def test_analytics_overview():
    resp = client.get("/api/v1/analytics/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_incidents"] > 0
    assert "critical_high_count" in data
    assert "avg_resolution_hours" in data

def test_hotspot_analytics():
    resp = client.get("/api/v1/analytics/hotspots")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["locations"]) > 0
    assert len(data["categories"]) > 0
    assert len(data["severities"]) > 0
    assert len(data["trends"]) > 0

def test_natural_language_assistant_admin_only():
    admin_login = client.post("/api/v1/auth/login", json={
        "email": "admin@campus.edu",
        "password": "Admin@123"
    })
    token = admin_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    query_payload = {"query": "Which block has the highest number of incidents?"}
    resp = client.post("/api/v1/intelligence/assistant", json=query_payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent_detected"] == "top_incident_building"
    assert "Block" in data["answer"] or "Library" in data["answer"]
    assert len(data["relevant_incident_ids"]) > 0
