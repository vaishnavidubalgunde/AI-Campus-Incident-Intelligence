import httpx

def check_system():
    client = httpx.Client(base_url="http://127.0.0.1:8000")
    
    # 1. Health
    health = client.get("/").json()
    print("Backend System Status:", health["status"])

    # 2. Login Admin
    login_res = client.post("/api/v1/auth/login", json={
        "email": "admin@campus.edu",
        "password": "Admin@123"
    }).json()
    token = login_res["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Admin Authenticated: {login_res['full_name']} (Role: {login_res['role']})")

    # 3. Overview Stats
    stats = client.get("/api/v1/analytics/overview", headers=headers).json()
    print(f"Total Database Incidents: {stats['total_incidents']}")
    print(f"Critical & High Priority: {stats['critical_high_count']}")
    print(f"Average Resolution Time: {stats['avg_resolution_hours']} hours")

    # 4. Pattern Discovery (DBSCAN / Hotspots)
    patterns = client.get("/api/v1/intelligence/patterns", headers=headers).json()
    print(f"AI Discovered Patterns: {len(patterns)} active patterns")
    for p in patterns[:3]:
        print(f"  • [{p['pattern_type']}] {p['pattern_title']} ({p['incident_count']} incidents)")

    # 5. Recommendations
    recs = client.get("/api/v1/intelligence/recommendations", headers=headers).json()
    print(f"Smart Recommendations: {len(recs)} active recommendations")
    for r in recs[:2]:
        print(f"  • {r['title']} (Target: {r['suggested_department']}, Priority: {r['priority']})")

    # 6. NL Analytics Assistant
    query = client.post("/api/v1/intelligence/assistant", json={
        "query": "Which block has the highest number of incidents?"
    }, headers=headers).json()
    print(f"NL Assistant Query Answer:\n  {query['answer']}")

if __name__ == "__main__":
    check_system()
