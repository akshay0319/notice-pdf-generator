from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import Template

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def create_template(name: str, html_content: str, db: Session = Depends(get_db)):
    template = Template(name=name, html_content=html_content)
    db.add(template)
    db.commit()
    db.refresh(template)
    return {"id": template.id, "message": "Template created"}
