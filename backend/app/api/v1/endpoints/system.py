import os
import uuid
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.api.deps import get_db, get_current_user, get_current_admin
from backend.app.models.entities import AuditLog, User
from backend.app.schemas.schemas import AuditLogResponse
from backend.app.core.config import settings
from backend.scripts.seed_data import seed_database

router = APIRouter()

ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/webp"]
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    logs = db.query(AuditLog).order_by(desc(AuditLog.created_at)).limit(100).all()
    results = []
    for l in logs:
        results.append(AuditLogResponse(
            id=l.id,
            user_name=l.user.full_name if l.user else "System",
            action=l.action,
            entity_type=l.entity_type,
            entity_id=l.entity_id,
            details=l.details,
            created_at=l.created_at
        ))
    return results

@router.post("/seed-demo")
def trigger_seed_demo(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    try:
        seed_database(force=True)
        return {"message": "Synthetic demonstration dataset re-seeded successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
def upload_incident_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image format. Allowed: JPEG, PNG, WEBP."
        )

    # Secure unique filename
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else "jpg"
    safe_name = f"inc_{uuid.uuid4().hex[:16]}.{ext}"
    
    upload_dir = os.path.abspath(settings.UPLOAD_DIR)
    os.makedirs(upload_dir, exist_ok=True)
    destination = os.path.join(upload_dir, safe_name)

    # Validate file size
    try:
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(destination)
        if file_size > MAX_FILE_SIZE:
            os.remove(destination)
            raise HTTPException(status_code=400, detail="Image file exceeds maximum 5MB size limit.")
    except Exception as e:
        if os.path.exists(destination):
            os.remove(destination)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    return {"photo_url": f"/uploads/{safe_name}", "filename": safe_name}
