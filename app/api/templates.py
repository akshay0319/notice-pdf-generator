from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import SessionLocal
from app.db.models import Template

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Pydantic model for JSON-based POST request
class TemplateCreateRequest(BaseModel):
    name: str
    html_content: str

# ✅ Create a new template (expects JSON)
@router.post("/")
def create_template(payload: TemplateCreateRequest, db: Session = Depends(get_db)):
    template = Template(name=payload.name, html_content=payload.html_content)
    db.add(template)
    db.commit()
    db.refresh(template)
    return {"id": template.id, "message": "Template created"}

# ✅ Get list of all templates
@router.get("/list")
def list_templates(db: Session = Depends(get_db)):
    templates = db.query(Template).all()
    return [{"id": t.id, "name": t.name} for t in templates]

# ✅ Delete a template by ID
@router.delete("/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    db.delete(template)
    db.commit()
    return {"message": "Template deleted successfully"}
