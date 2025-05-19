from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import Notice

import json

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def create_notice(recipient_name: str, data_json: str, template_id: int, db: Session = Depends(get_db)):
    notice = Notice(recipient_name=recipient_name, data_json=data_json, template_id=template_id)
    db.add(notice)
    db.commit()
    db.refresh(notice)
    return {"id": notice.id, "message": "Notice created"}
