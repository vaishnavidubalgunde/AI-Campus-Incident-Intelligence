# Testing & Quality Assurance Documentation
## AI-Based Campus Incident Intelligence & Response System

This document provides testing methodologies, executed test suites, automated test results, and demonstration scenarios for evaluating system correctness.

---

## 1. Test Strategy Overview

Quality assurance was performed across three tiers:
1. **Core Algorithm Unit Testing**: Validating TF-IDF vectorization, Multinomial Naive Bayes classifier, compound severity scoring, cosine similarity duplicate thresholding, and DBSCAN clustering.
2. **API & Workflow Integration Testing**: Verifying JWT authentication, role guards (`student` vs `admin`), incident submission, status lifecycle transitions, department dispatch, and audit logging.
3. **Frontend Production Build Verification**: Validating TypeScript types, JSX compilation, CSS bundling, and production asset optimization.

---

## 2. Automated Test Suite Execution

The backend test suite (`backend/tests/test_api.py`) was executed via `pytest`:

```bash
.\venv\Scripts\pytest backend/tests/test_api.py -v
```

### Execution Log & Test Results:
```text
============================= test session starts =============================
platform win32 -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\vaish\OneDrive\Desktop\ILPPROJECT
collected 18 items

backend/tests/test_api.py::test_ai_classifier_water_plumbing PASSED      [  5%]
backend/tests/test_api.py::test_ai_classifier_electrical_hazard PASSED   [ 11%]
backend/tests/test_api.py::test_ai_classifier_wifi_networking PASSED     [ 16%]
backend/tests/test_api.py::test_severity_engine_critical_compound_risk PASSED [ 22%]
backend/tests/test_api.py::test_severity_engine_low_minor_issue PASSED   [ 27%]
backend/tests/test_api.py::test_duplicate_detector_flags_matching_reports PASSED [ 33%]
backend/tests/test_api.py::test_duplicate_detector_does_not_merge_different_incidents PASSED [ 38%]
backend/tests/test_api.py::test_pattern_discovery_groups_concentrated_hotspot PASSED [ 44%]
backend/tests/test_api.py::test_login_demo_admin PASSED                  [ 50%]
backend/tests/test_api.py::test_login_demo_student PASSED                [ 55%]
backend/tests/test_api.py::test_invalid_login PASSED                     [ 61%]
backend/tests/test_api.py::test_register_new_student PASSED              [ 66%]
backend/tests/test_api.py::test_get_departments_and_categories PASSED    [ 72%]
backend/tests/test_api.py::test_create_incident_with_ai_analysis PASSED  [ 77%]
backend/tests/test_api.py::test_admin_update_status_and_assignment PASSED [ 83%]
backend/tests/test_api.py::test_analytics_overview PASSED                [ 88%]
backend/tests/test_api.py::test_hotspot_analytics PASSED                 [ 94%]
backend/tests/test_api.py::test_natural_language_assistant_admin_only PASSED [100%]

====================== 18 passed in 10.11s =======================
```

**Result: 18 / 18 tests passed (100% pass rate).**

---

## 3. Key Demonstration Scenarios Tested

### Scenario A: Co-Occurring Compound Hazard (Water Near Electrics)
- **Input Text**: *"Water leaking continuously onto the main electrical panel in Computer Lab 3 causing sparks"*
- **Expected Outcome**: Compound hazard escalator triggers ($+35$ pts), elevating priority score $\ge 80$, assigning **Critical** severity tier.
- **Verification**: Verified via `test_severity_engine_critical_compound_risk`. Factor audit logged *"CRITICAL COMPOUND RISK"*.

### Scenario B: Duplicate Incident Identification
- **Existing Report**: *"Wi-Fi connection down in Central Library 2nd floor"*
- **New Report**: *"Central library wifi is not working on 2nd floor"*
- **Expected Outcome**: Semantic cosine similarity exceeds threshold ($\ge 0.50$ with location bonus), linking matching incident ID without duplicate data corruption.
- **Verification**: Verified via `test_duplicate_detector_flags_matching_reports`.

### Scenario C: Unrelated Incident Distinction
- **Existing Report**: *"Broken window in hostel 1 room 12"*
- **New Report**: *"Water leak in cafeteria kitchen tap"*
- **Expected Outcome**: Semantic similarity $< 0.15$, 0 duplicate candidates returned.
- **Verification**: Verified via `test_duplicate_detector_does_not_merge_different_incidents`.

### Scenario D: High Density Hotspot Pattern Discovery
- **Condition**: 4 distinct water leak complaints filed across Block C.
- **Expected Outcome**: Pattern discovery identifies *"Concentrated Water & Plumbing Hotspot in Block C"* with $> 85\%$ confidence and actionable inspection advisory.
- **Verification**: Verified via `test_pattern_discovery_groups_concentrated_hotspot`.

---

## 4. Frontend Production Build Verification

Executed production build:
```bash
npm run build
```

### Result:
```text
vite v8.3.4 building client environment for production...
✓ 2567 modules transformed.
dist/index.html                   0.45 kB
dist/assets/index-qfDchDcU.css   60.66 kB
dist/assets/index-DpvTTghV.js   855.49 kB
✓ built in 1.55s
```
**Result: 0 TypeScript errors, production assets bundled cleanly.**
