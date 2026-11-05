import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings
from backend.app.database.session import Base, engine, SessionLocal
from backend.app.models.entities import Incident
from backend.scripts.seed_data import seed_database

# Endpoint routers
from backend.app.api.v1.endpoints import (
    auth, departments, incidents, analytics,
    intelligence, notifications, system
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and seed demo database if empty
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        count = db.query(Incident).count()
        if count == 0:
            print("Database empty on startup. Running initial seed...")
            seed_database(force=False)
    except Exception as e:
        print(f"Startup check notice: {e}")
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Automated incident classification, severity prioritization, duplicate detection, and campus intelligence platform.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits local dev frontends
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for safe image uploads
upload_dir = os.path.abspath(settings.UPLOAD_DIR)
os.makedirs(upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

# Include API Routers
api_v1 = settings.API_V1_STR
app.include_router(auth.router, prefix=f"{api_v1}/auth", tags=["Authentication"])
app.include_router(departments.router, prefix=f"{api_v1}", tags=["Departments & Categories"])
app.include_router(incidents.router, prefix=f"{api_v1}/incidents", tags=["Incidents"])
app.include_router(analytics.router, prefix=f"{api_v1}/analytics", tags=["Analytics & Hotspots"])
app.include_router(intelligence.router, prefix=f"{api_v1}/intelligence", tags=["Intelligence & Patterns"])
app.include_router(notifications.router, prefix=f"{api_v1}/notifications", tags=["Notifications"])
app.include_router(system.router, prefix=f"{api_v1}/system", tags=["System & Audit"])

@app.get("/", tags=["Health"])
def root():
    return {
        "system": settings.PROJECT_NAME,
        "status": "online",
        "api_documentation": "/docs",
        "version": "1.0.0"
    }
