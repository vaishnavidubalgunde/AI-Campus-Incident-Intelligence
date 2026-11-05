import os
import sys
import random
from datetime import datetime, timedelta, timezone

# Ensure project root is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlalchemy.orm import Session
from backend.app.database.session import SessionLocal, Base, engine
from backend.app.core.security import get_password_hash
from backend.app.models.entities import (
    User, Department, IncidentCategory, Incident,
    IncidentStatusHistory, IncidentAssignment, AIAnalysisResult,
    DiscoveredPattern, Recommendation, Notification, AuditLog
)
from backend.app.ai.classifier import classifier
from backend.app.ai.severity_engine import severity_engine
from backend.app.analytics.pattern_discovery import pattern_discovery_engine
from backend.app.analytics.recommendations import recommendation_engine

DEPARTMENTS_DATA = [
    {"name": "Maintenance & Plumbing", "code": "MP", "contact_email": "plumbing@campus.edu", "head_person": "Robert Vance"},
    {"name": "Electrical Services", "code": "ES", "contact_email": "electrical@campus.edu", "head_person": "Elena Rostova"},
    {"name": "IT & Campus Networking", "code": "IT", "contact_email": "network@campus.edu", "head_person": "Alan Turing Jr."},
    {"name": "Estate & Civil Infrastructure", "code": "EC", "contact_email": "infrastructure@campus.edu", "head_person": "David Miller"},
    {"name": "Housekeeping & Sanitation", "code": "HS", "contact_email": "housekeeping@campus.edu", "head_person": "Maria Santos"},
    {"name": "Campus Security & Safety", "code": "SS", "contact_email": "security@campus.edu", "head_person": "Captain James Keller"},
    {"name": "Laboratory & Audio-Visual", "code": "LAV", "contact_email": "labsupport@campus.edu", "head_person": "Dr. Sarah Chen"},
    {"name": "Campus Transport & Logistics", "code": "TL", "contact_email": "transport@campus.edu", "head_person": "Gopal Sharma"},
    {"name": "General Administration", "code": "GA", "contact_email": "admin@campus.edu", "head_person": "Dean Office"},
]

CATEGORIES_DATA = [
    {"name": "Water & Plumbing", "code": "WATER", "description": "Pipe leaks, drainage overflows, taps, washrooms", "dept_code": "MP"},
    {"name": "Electrical Hazards", "code": "ELEC", "description": "Sparking, open wires, panels, short circuits, outages", "dept_code": "ES"},
    {"name": "Internet & Networking", "code": "NET", "description": "Wi-Fi dropouts, LAN issues, portal connection errors", "dept_code": "IT"},
    {"name": "Infrastructure & Building Damage", "code": "INFRA", "description": "Wall cracks, broken glass, doors, staircases, roof", "dept_code": "EC"},
    {"name": "Cleanliness & Sanitation", "code": "CLEAN", "description": "Trash, foul odors, uncleaned washrooms, waste disposal", "dept_code": "HS"},
    {"name": "Security & Safety", "code": "SEC", "description": "Thefts, broken locks, dark areas, fire equipment, trespass", "dept_code": "SS"},
    {"name": "Classroom & Lab Equipment", "code": "EQUIP", "description": "Projectors, computers, AC units, smartboards, instruments", "dept_code": "LAV"},
    {"name": "Transportation & Parking", "code": "TRANS", "description": "Shuttle delays, blocked ramps, parking violations, bike stands", "dept_code": "TL"},
    {"name": "Other / Needs Review", "code": "OTHER", "description": "Unclassified campus operations feedback", "dept_code": "GA"},
]

CAMPUS_LOCATIONS = [
    ("Block C", "Block C", "2nd Floor, Room 204"),
    ("Block C", "Block C", "3rd Floor Washroom"),
    ("Block C", "Block C", "Ground Floor Corridor"),
    ("Central Library", "Central Library", "2nd Floor Digital Section"),
    ("Central Library", "Central Library", "1st Floor Reading Room"),
    ("Central Library", "Central Library", "Basement Stacks"),
    ("Block B (Science Wing)", "Block B", "Chemistry Lab 101"),
    ("Block B (Science Wing)", "Block B", "Physics Lab 202"),
    ("Computer Science Block", "Block A", "Lab 3 High Performance Lab"),
    ("Computer Science Block", "Block A", "Network Server Room"),
    ("Mechanical Engineering Block", "Block E", "Workshop 1"),
    ("Mechanical Engineering Block", "Block E", "Foundry Section"),
    ("Student Cafeteria & Food Court", "Cafeteria", "Main Dining Hall"),
    ("Student Cafeteria & Food Court", "Cafeteria", "Service Counter West"),
    ("Boys Hostel 1", "Hostel 1", "Wing B 2nd Floor"),
    ("Boys Hostel 1", "Hostel 1", "Mess Dining Hall"),
    ("Girls Hostel 2", "Hostel 2", "Ground Floor Lobby"),
    ("Girls Hostel 2", "Hostel 2", "1st Floor Wing A"),
    ("Main Auditorium", "Auditorium", "Balcony Level"),
    ("Sports Complex & Gymnasium", "Sports Complex", "Indoor Badminton Court"),
    ("Admin Building", "Admin Block", "Registrar Office Corridor"),
]

# Curated synthetic scenarios containing deliberate patterns
PATTERN_TEMPLATES = [
    # Pattern 1: Water leakage in Block C (Plumbing hotspot)
    {"cat": "Water & Plumbing", "bldg": "Block C", "loc": "Block C", "flr": "2nd Floor, Corridor",
     "title": "Continuous water leaking from ceiling near Room 204",
     "desc": "There is a large amount of water leaking continuously from the ceiling on the second floor of Block C. Water is dripping onto the floor creating a slippery hazard.",
     "sev": "high", "weight": 8},
    {"cat": "Water & Plumbing", "bldg": "Block C", "loc": "Block C", "flr": "3rd Floor Washroom",
     "title": "Severe washroom tap leak and water overflowing in Block C",
     "desc": "The main washroom tap on the 3rd floor of Block C is broken and water is overflowing onto the hallway. Urgently needs maintenance shutoff valve closure.",
     "sev": "high", "weight": 6},
    {"cat": "Water & Plumbing", "bldg": "Block C", "loc": "Block C", "flr": "Ground Floor Entrance",
     "title": "Water accumulation and dampness near Block C entrance",
     "desc": "Water is accumulating near the main entrance after rainfall and seeping under the floor tiles. The drainage pipe seems completely clogged.",
     "sev": "medium", "weight": 5},

    # Pattern 2: Wi-Fi failures in Library and adjoining Academic Blocks (Networking hotspot)
    {"cat": "Internet & Networking", "bldg": "Central Library", "loc": "Central Library", "flr": "2nd Floor Digital Lab",
     "title": "Wi-Fi connection completely down in Central Library",
     "desc": "The Wi-Fi connection has stopped working in the library digital study zone. Multiple students are unable to submit digital assignments.",
     "sev": "medium", "weight": 10},
    {"cat": "Internet & Networking", "bldg": "Central Library", "loc": "Central Library", "flr": "1st Floor Reading Room",
     "title": "Campus Wi-Fi authentication portal loop and frequent drops",
     "desc": "Students on the 1st floor of the Central Library keep getting disconnected from the captive portal every 2 minutes with high packet loss.",
     "sev": "medium", "weight": 8},
    {"cat": "Internet & Networking", "bldg": "Block A", "loc": "Computer Science Block", "flr": "1st Floor Classrooms",
     "title": "Poor Wi-Fi signal coverage in Block A lecture halls",
     "desc": "Several students are facing the same internet connectivity issue in Block A classrooms. The signal is under -85dBm.",
     "sev": "medium", "weight": 6},
    {"cat": "Internet & Networking", "bldg": "Block B", "loc": "Block B (Science Wing)", "flr": "Ground Floor",
     "title": "Intermittent network outage in Block B faculty and student rooms",
     "desc": "No internet access through Wi-Fi or ethernet ports in Block B science wing since morning.",
     "sev": "high", "weight": 5},

    # Pattern 3: Electrical hazards in laboratories (High urgency)
    {"cat": "Electrical Hazards", "bldg": "Block A", "loc": "Computer Science Block", "flr": "Lab 3 High Performance Lab",
     "title": "Sparking switchboard and burning smell in Computer Lab 3",
     "desc": "Someone noticed sparking and a sharp burning smell from the main electrical distribution panel in Computer Lab 3. Lights flickering dangerously.",
     "sev": "critical", "weight": 7},
    {"cat": "Electrical Hazards", "bldg": "Block B", "loc": "Block B (Science Wing)", "flr": "Physics Lab 202",
     "title": "Exposed high voltage wiring near experimental bench",
     "desc": "Exposed electrical wires hanging near the student experiment workbench in Physics Lab 202. Direct electric shock risk for students.",
     "sev": "critical", "weight": 6},
    {"cat": "Electrical Hazards", "bldg": "Block E", "loc": "Mechanical Engineering Block", "flr": "Workshop 1",
     "title": "Circuit breaker tripping repeatedly and buzzing sound",
     "desc": "The 3-phase power breaker in mechanical workshop 1 keeps tripping with a loud buzzing sound and visible electric arc.",
     "sev": "critical", "weight": 5},

    # Pattern 4: Cleanliness & Sanitation in Cafeteria & Hostels
    {"cat": "Cleanliness & Sanitation", "bldg": "Cafeteria", "loc": "Student Cafeteria & Food Court", "flr": "Main Dining Area",
     "title": "Overflowing waste bins and uncleaned food waste tables",
     "desc": "Garbage bins near the food court are overflowing with food waste and foul smell is spreading across the dining area. Housekeeping required.",
     "sev": "medium", "weight": 7},
    {"cat": "Cleanliness & Sanitation", "bldg": "Cafeteria", "loc": "Student Cafeteria & Food Court", "flr": "Rear Handwash Area",
     "title": "Stagnant wastewater and clogged sink in cafeteria",
     "desc": "Wastewater is not draining from the handwashing stations and backing up onto the floor creating an unsanitary environment.",
     "sev": "high", "weight": 5},
    {"cat": "Cleanliness & Sanitation", "bldg": "Hostel 1", "loc": "Boys Hostel 1", "flr": "Common Washroom Wing B",
     "title": "Foul odor and unhygienic conditions in hostel washroom",
     "desc": "Hostel washroom on 2nd floor has not been sanitized and has a persistent foul smell. Soap dispensers are empty.",
     "sev": "medium", "weight": 6},

    # General Campus Issues
    {"cat": "Infrastructure & Building Damage", "bldg": "Block E", "loc": "Mechanical Engineering Block", "flr": "Exterior Staircase",
     "title": "Loose and shaking staircase railing on 2nd floor",
     "desc": "The steel staircase handrail is physically loose and wobbles when students lean on it. High fall risk.",
     "sev": "high", "weight": 6},
    {"cat": "Infrastructure & Building Damage", "bldg": "Auditorium", "loc": "Main Auditorium", "flr": "Balcony Entrance",
     "title": "Broken glass pane on fire exit door",
     "desc": "Glass pane on the secondary emergency fire exit door has cracked with sharp shards threatening to drop.",
     "sev": "high", "weight": 5},
    {"cat": "Infrastructure & Building Damage", "bldg": "Block C", "loc": "Block C", "flr": "Room 105",
     "title": "Ceiling plaster chipped off and fell near lecture podium",
     "desc": "A piece of concrete plaster fell from the ceiling onto an empty student desk. Needs structural civil inspection.",
     "sev": "high", "weight": 5},
    {"cat": "Security & Safety", "bldg": "Central Library", "loc": "Central Library", "flr": "Cycle Parking Stand",
     "title": "Bicycle lock broken and student cycle reported missing",
     "desc": "A student bicycle was stolen from the cycle rack outside the library. Security camera angle does not cover the far corner.",
     "sev": "medium", "weight": 5},
    {"cat": "Security & Safety", "bldg": "Hostel 2", "loc": "Girls Hostel 2", "flr": "Perimeter Pathway",
     "title": "Streetlights not functioning on hostel back pathway",
     "desc": "Three streetlights on the pedestrian walkway behind Girls Hostel 2 have been dead for three nights, leaving the road pitch dark.",
     "sev": "high", "weight": 7},
    {"cat": "Classroom & Lab Equipment", "bldg": "Block A", "loc": "Computer Science Block", "flr": "Seminar Hall 2",
     "title": "Projector color distorted and sound system humming loudly",
     "desc": "The HDMI projector is displaying washed-out yellow tones and the audio amplifier produces a loud 60Hz buzzing feedback.",
     "sev": "low", "weight": 6},
    {"cat": "Classroom & Lab Equipment", "bldg": "Block B", "loc": "Block B (Science Wing)", "flr": "Chemistry Lab 101",
     "title": "Chemical fume hood exhaust fan stopped spinning",
     "desc": "Fume hood unit in chemistry lab is not extracting fumes. Students cannot perform synthesis experiments safely.",
     "sev": "high", "weight": 5},
    {"cat": "Transportation & Parking", "bldg": "Admin Block", "loc": "Admin Building", "flr": "Main Porch Ramp",
     "title": "Unauthorized vehicle parked blocking wheelchair ramp",
     "desc": "A visitor SUV has parked directly across the disabled ramp entrance preventing wheelchair access to the admin building.",
     "sev": "medium", "weight": 5},
]

def seed_database(force: bool = False):
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        existing_count = db.query(Incident).count()
        if existing_count >= 150 and not force:
            print(f"Database already contains {existing_count} incidents. Skipping seed to prevent duplicates.")
            return

        if force and existing_count > 0:
            print("Force flag set: clearing existing incident records...")
            db.query(AuditLog).delete()
            db.query(Notification).delete()
            db.query(AIAnalysisResult).delete()
            db.query(IncidentStatusHistory).delete()
            db.query(IncidentAssignment).delete()
            db.query(DiscoveredPattern).delete()
            db.query(Recommendation).delete()
            db.query(Incident).delete()
            db.commit()

        # 1. Seed Departments
        dept_map = {}
        for d_data in DEPARTMENTS_DATA:
            dept = db.query(Department).filter(Department.code == d_data["code"]).first()
            if not dept:
                dept = Department(
                    name=d_data["name"],
                    code=d_data["code"],
                    contact_email=d_data["contact_email"],
                    head_person=d_data["head_person"],
                    is_active=True
                )
                db.add(dept)
                db.flush()
            dept_map[d_data["code"]] = dept
            dept_map[d_data["name"]] = dept
        db.commit()

        # 2. Seed Incident Categories
        cat_map = {}
        for c_data in CATEGORIES_DATA:
            cat = db.query(IncidentCategory).filter(IncidentCategory.code == c_data["code"]).first()
            default_dept = dept_map.get(c_data["dept_code"])
            if not cat:
                cat = IncidentCategory(
                    name=c_data["name"],
                    code=c_data["code"],
                    description=c_data["description"],
                    default_department_id=default_dept.id if default_dept else None
                )
                db.add(cat)
                db.flush()
            cat_map[c_data["name"]] = cat
        db.commit()

        # 3. Seed Users (Admin & Students)
        admin = db.query(User).filter(User.email == "admin@campus.edu").first()
        if not admin:
            admin = User(
                email="admin@campus.edu",
                hashed_password=get_password_hash("Admin@123"),
                full_name="Dr. Administrator",
                role="admin",
                department="Campus Operations",
                is_active=True
            )
            db.add(admin)

        student_demo = db.query(User).filter(User.email == "student@campus.edu").first()
        if not student_demo:
            student_demo = User(
                email="student@campus.edu",
                hashed_password=get_password_hash("Student@123"),
                full_name="Alex Student",
                role="student",
                department="Computer Science & Engineering",
                is_active=True
            )
            db.add(student_demo)

        additional_students = [
            ("rahul.sharma@campus.edu", "Rahul Sharma", "Mechanical Engineering"),
            ("priya.patel@campus.edu", "Priya Patel", "Electronics & Comm"),
            ("ananya.deshmukh@campus.edu", "Ananya Deshmukh", "Civil Engineering"),
            ("vikram.singh@campus.edu", "Vikram Singh", "Information Technology"),
        ]
        student_users = [student_demo]
        for s_email, s_name, s_dept in additional_students:
            s_obj = db.query(User).filter(User.email == s_email).first()
            if not s_obj:
                s_obj = User(
                    email=s_email,
                    hashed_password=get_password_hash("Student@123"),
                    full_name=s_name,
                    role="student",
                    department=s_dept,
                    is_active=True
                )
                db.add(s_obj)
                db.flush()
            student_users.append(s_obj)
        db.commit()

        # 4. Generate >= 210 Realistic Incidents
        statuses = ["submitted", "under_review", "verified", "assigned", "in_progress", "resolved", "closed"]
        status_weights = [0.15, 0.10, 0.10, 0.20, 0.20, 0.20, 0.05]

        now = datetime.now(timezone.utc)
        all_created_incidents = []

        total_target = 220
        inc_counter = 1

        # Expand templates according to weights
        weighted_pool = []
        for tmpl in PATTERN_TEMPLATES:
            w = tmpl.get("weight", 3)
            for _ in range(w):
                weighted_pool.append(tmpl)

        while inc_counter <= total_target:
            tmpl = random.choice(weighted_pool)
            days_ago = random.randint(0, 28)
            hours_ago = random.randint(1, 23)
            minutes_ago = random.randint(0, 59)
            created_timestamp = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)

            status = random.choices(statuses, weights=status_weights)[0]
            reporter = random.choice(student_users)
            is_anon = random.choice([False, False, False, True])

            category_obj = cat_map.get(tmpl["cat"], cat_map["Other / Needs Review"])
            default_dept = category_obj.default_department or dept_map["General Administration"]

            incident_num = f"INC-2026-{inc_counter:04d}"

            # Variations on titles and descriptions
            title_prefix = random.choice(["", "Urgent: ", "Report: ", "Attention: ", "Notice: "])
            title = f"{title_prefix}{tmpl['title']}" if title_prefix else tmpl["title"]
            desc = tmpl["desc"]
            if random.random() < 0.35:
                desc += f" Observed at {tmpl['flr']} by multiple students."

            resolved_time = None
            if status in ["resolved", "closed"]:
                resolve_delay_hours = random.randint(4, 72)
                resolved_time = min(now, created_timestamp + timedelta(hours=resolve_delay_hours))

            # Run AI classifier and severity engine
            ai_cls = classifier.predict(f"{title} {desc}")
            ai_sev = severity_engine.calculate(
                title=title,
                description=desc,
                category=tmpl["cat"],
                location=tmpl["loc"],
                building=tmpl["bldg"],
                similar_count=random.randint(0, 4)
            )

            # Create Incident
            inc = Incident(
                incident_number=incident_num,
                title=title,
                description=desc,
                location=tmpl["loc"],
                building=tmpl["bldg"],
                floor_room=tmpl["flr"],
                category_id=category_obj.id,
                reporter_id=reporter.id if not is_anon else None,
                is_anonymous=is_anon,
                photo_url=None,
                status=status,
                severity=ai_sev["severity_level"],
                priority_score=ai_sev["priority_score"],
                assigned_department_id=default_dept.id if status not in ["submitted", "under_review"] else None,
                is_duplicate=False,
                duplicate_of_id=None,
                resolution_notes="Remediation completed by duty staff. Verified operational." if status in ["resolved", "closed"] else None,
                created_at=created_timestamp,
                updated_at=created_timestamp + timedelta(minutes=random.randint(10, 180)),
                resolved_at=resolved_time
            )
            db.add(inc)
            db.flush()

            # Create AI Analysis Result
            import json
            ai_result = AIAnalysisResult(
                incident_id=inc.id,
                predicted_category=ai_cls["predicted_category"],
                confidence_score=ai_cls["confidence_score"],
                severity_level=ai_sev["severity_level"],
                priority_score=ai_sev["priority_score"],
                score_factors=json.dumps(ai_sev["score_factors"]),
                suggested_department=ai_cls["suggested_department"],
                summary=ai_sev["summary"],
                recurrence_warning=bool(inc_counter % 3 == 0),
                similar_incident_ids=json.dumps([]),
                recommended_actions=json.dumps(ai_sev["recommended_actions"]),
                created_at=created_timestamp
            )
            db.add(ai_result)

            # Create Status History
            hist1 = IncidentStatusHistory(
                incident_id=inc.id,
                previous_status=None,
                new_status="submitted",
                changed_by_id=reporter.id if not is_anon else None,
                notes="Incident reported via web portal.",
                created_at=created_timestamp
            )
            db.add(hist1)

            if status != "submitted":
                hist2 = IncidentStatusHistory(
                    incident_id=inc.id,
                    previous_status="submitted",
                    new_status=status,
                    changed_by_id=admin.id,
                    notes=f"Admin triaged status to {status}.",
                    created_at=created_timestamp + timedelta(minutes=45)
                )
                db.add(hist2)

            if inc.assigned_department_id:
                assignment = IncidentAssignment(
                    incident_id=inc.id,
                    department_id=inc.assigned_department_id,
                    assigned_by_id=admin.id,
                    notes=f"Auto-assigned to {default_dept.name} based on AI category analysis.",
                    status="active" if status in ["assigned", "in_progress"] else "completed",
                    created_at=created_timestamp + timedelta(minutes=30)
                )
                db.add(assignment)

            all_created_incidents.append({
                "id": inc.id,
                "incident_number": inc.incident_number,
                "title": inc.title,
                "description": inc.description,
                "location": inc.location,
                "building": inc.building,
                "category_name": category_obj.name,
                "severity": inc.severity,
                "priority_score": inc.priority_score,
                "status": inc.status,
                "assigned_department_name": default_dept.name if inc.assigned_department_id else "Unassigned",
                "created_at": inc.created_at.isoformat()
            })

            inc_counter += 1

        db.commit()
        print(f"Successfully generated {len(all_created_incidents)} synthetic campus incident records.")

        # 5. Run Pattern Discovery and Recommendation Engines on newly seeded data
        print("Running Pattern Discovery Engine...")
        discovered = pattern_discovery_engine.analyze_patterns(all_created_incidents)
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

        print("Running Smart Recommendation Engine...")
        recs = recommendation_engine.generate_recommendations(all_created_incidents)
        for r in recs:
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

        # 6. Add Audit Log
        audit = AuditLog(
            user_id=admin.id,
            action="SEED_DEMO_DATABASE",
            entity_type="SYSTEM",
            entity_id=None,
            details=f"Seeded {len(all_created_incidents)} realistic synthetic incidents and ran initial AI pattern discovery.",
            ip_address="127.0.0.1"
        )
        db.add(audit)

        db.commit()
        print("Database seed and AI intelligence initialization complete!")

    except Exception as e:
        db.rollback()
        print(f"Error during database seed: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    force_seed = "--force" in sys.argv
    seed_database(force=force_seed)
