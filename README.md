# AI-Based Campus Incident Intelligence & Response System

An intelligent campus incident management platform that transforms student natural-language problem reports into actionable operations intelligence. The system automatically classifies issues, estimates hazard severity, flags duplicate submissions, discovers recurring campus patterns using unsupervised DBSCAN clustering, maps location hotspots, and assists administrators via a natural-language analytics assistant.

Operates **100% locally and offline** without requiring external paid AI APIs.

---

## 🌟 Key Features

1. **Natural-Language Incident Submission**:
   - Students describe issues naturally (e.g., *"Water leaking continuously from ceiling on second floor of Block C"*).
   - Real-time **AI Pre-Flight Triage Preview** predicting category, priority, and duplicate alerts as the student types.
   - Optional photo attachment and anonymous reporting mode.

2. **Core AI Classification Engine**:
   - Hybrid NLP pipeline using Scikit-learn TF-IDF n-grams + Multinomial Naive Bayes paired with domain keyword verification.
   - 8 campus facility categories with confidence scores and responsible department routing.

3. **Multi-Factor Transparent Severity Scoring**:
   - Transparent, auditable priority score ($10 - 100$) factoring category base points, immediate hazard signals, location sensitivity, and co-occurring risks (e.g. *water near electrical equipment escalator*).

4. **Semantic Duplicate Incident Detection**:
   - Cosine similarity vector matching with contextual bonuses for same-building and same-category reports.
   - Distinguishes identical duplicates ($\ge 72\%$) from recurring related issues.

5. **AI Incident Pattern Discovery (Most Important Feature)**:
   - Unsupervised **DBSCAN Density Clustering** grouping semantically correlated reports.
   - Discovers recurring complaints by location, category spikes across multiple buildings, and overdue SLA backlogs.

6. **Interactive Campus Hotspot Schematic**:
   - Grid visualization showing live report density, critical hazard badges, and one-click building filtering.

7. **Smart Administrative Recommendations**:
   - Algorithmic recommendations for proactive facilities management (e.g. plumbing audits, switch overhauls, lab inspections).

8. **Natural-Language Analytics Assistant**:
   - Safe intent-based conversational console answering operational questions directly against live SQLite database records.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- Node.js v18+ (Tested on Node v22.19)

---

### Step 1: Set Up Backend

1. Open a terminal in the project root:
   ```bash
   cd c:\Users\vaish\OneDrive\Desktop\ILPPROJECT
   ```

2. Activate the virtual environment (or create one):
   ```powershell
   # Activate existing virtual environment
   .\venv\Scripts\Activate.ps1
   ```

3. Install backend dependencies (already installed):
   ```bash
   pip install -r backend/requirements.txt
   ```

4. Initialize and seed the demonstration database with 220+ synthetic reports:
   ```bash
   python backend/scripts/seed_data.py --force
   ```

5. Start the backend server:
   ```bash
   python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

- **Backend API**: `http://127.0.0.1:8000`
- **Interactive OpenAPI Documentation**: `http://127.0.0.1:8000/docs`

---

### Step 2: Set Up Frontend

1. Open a second terminal and navigate to `frontend`:
   ```bash
   cd frontend
   ```

2. Start the Vite development server:
   ```bash
   npm run dev
   ```

- **Frontend Application URL**: `http://localhost:5173`

---

## 🔑 Demonstration Accounts

The login page includes convenient **One-Click Quick Login** buttons:

| Role | Email | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@campus.edu` | `Admin@123` | Full access: Triage, Hotspots, DBSCAN Patterns, Recommendations, Assistant, Team Dispatch, Audit Trail |
| **Student** | `student@campus.edu` | `Student@123` | Report incidents, live AI preview, view personal report history, notifications |

---

## 🧪 Running Automated Tests

Run the complete Pytest backend test suite:
```bash
.\venv\Scripts\pytest backend/tests/test_api.py -v
```
*(All 18 tests covering AI classifiers, severity engine, duplicate detection, pattern discovery, auth, and analytics pass 100%)*

Validate the production frontend build:
```bash
cd frontend
npm run build
```

---

## 📂 Project Structure

```
campus-incident-intelligence/
├── backend/
│   ├── app/
│   │   ├── ai/                # Hybrid NLP classifier, severity engine, duplicate detector
│   │   ├── analytics/         # DBSCAN pattern discovery, recommendation engine, NL assistant
│   │   ├── api/v1/endpoints/  # Auth, incidents, analytics, intelligence, notifications, system
│   │   ├── core/              # Config, security (bcrypt & JWT), dependencies
│   │   ├── database/          # SQLAlchemy session and Base
│   │   ├── models/            # Normalized database entities
│   │   ├── schemas/           # Pydantic request and response models
│   │   └── main.py            # FastAPI entrypoint with CORS & upload mounts
│   ├── scripts/
│   │   └── seed_data.py       # Seeds 220+ realistic synthetic campus incidents
│   ├── tests/
│   │   └── test_api.py        # Automated Pytest suite (18 tests)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/        # Navbar, Sidebar, StatCard, CampusMapSchematic, Timeline, Badges
│   │   ├── context/           # AuthContext (JWT state management)
│   │   ├── pages/             # 14 distinct functional pages
│   │   ├── services/          # Typed Axios API client
│   │   ├── types/             # TypeScript interfaces
│   │   └── App.tsx            # React Router role-guarded routes
│   └── package.json
├── docs/
│   ├── PROJECT_REPORT.md      # Comprehensive 20-section academic CSE project report
│   ├── SYSTEM_ARCHITECTURE.md # Architecture topology and Mermaid diagrams
│   ├── API_DOCUMENTATION.md   # Complete REST API reference
│   ├── ALGORITHMS.md          # Student-friendly algorithm formulations
│   └── TESTING.md             # Quality assurance and test case verification
├── .env.example
├── .gitignore
└── README.md
```

---

## 🎓 Academic Presentation Highlights

For your project presentation, demonstrate:
1. **Student Submission**: Type *"There is water leaking near the electrical switchboard in Block C"* to show real-time compound hazard escalation to **Critical** and duplicate warning.
2. **AI Pattern Discovery**: Navigate to `/intelligence` to showcase how DBSCAN clustered disparate complaints into recurring Wi-Fi and plumbing issues.
3. **Campus Hotspot Grid**: Filter by *"Block C"* or *"Central Library"* to see live facility density.
4. **Natural-Language Assistant**: Ask *"Which block has the highest number of incidents?"* or *"What should the maintenance team prioritize?"*.
5. **Audit Log & Re-seeding**: Demonstrate the immutable event trail and one-click database re-seeding at `/settings`.
