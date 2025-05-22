from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.db.database import SessionLocal
from app.db.models import Template
from app.core.pdf_engine import compile_template, render_pdf_bytes
from pydantic import BaseModel
from typing import List
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
import os, uuid, logging

logging.getLogger("fontTools").setLevel(logging.ERROR)
router = APIRouter(prefix="/bulk", tags=["Bulk PDF Generator"])

class PersonData(BaseModel):
    name: str
    address: str
    loan_number: str
    loan_date: str = None
    due_amount: str = None
    sender_name: str = None
    sender_designation: str = None
    sender_company: str = None
    sender_contact: str = None

class BulkNoticeRequest(BaseModel):
    template_id: int
    persons: List[PersonData]

def generate_single_pdf(person_data: dict, template_str: str):
    try:
        filename = f"{person_data.get('name', 'Unknown').replace(' ', '_')}_{uuid.uuid4().hex}.pdf"
        template = compile_template(template_str)
        html = template.render(**person_data)
        if not html.strip() or "<html" not in html:
            return {"status": "error", "filename": filename, "content": None}
        pdf_bytes = render_pdf_bytes(html)
        return {"status": "success", "filename": filename, "content": pdf_bytes}
    except Exception as e:
        return {"status": "error", "filename": "", "content": None}

@router.post("")  # DO NOT CHANGE ROUTE
async def generate_bulk_pdfs(request: BulkNoticeRequest):
    db = SessionLocal()
    template = db.query(Template).filter(Template.id == request.template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    template_str = template.html_content
    persons_dict = [person.dict(exclude_none=True) for person in request.persons]
    total = len(persons_dict)

    print("[Start] PDF generation...")
    start = datetime.now()

    success_files = []
    with ProcessPoolExecutor(max_workers=min(os.cpu_count(), 8)) as executor:
        futures = [executor.submit(generate_single_pdf, person, template_str) for person in persons_dict]
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            if result["status"] == "success":
                success_files.append(result)
            if i % 100 == 0 or i == total:
                print(f"[PDF] {i}/{total} done")

    print(f"[PDF Generation] Completed: {len(success_files)}/{total}")
    print(f"[Time Taken] {(datetime.now() - start).total_seconds():.2f} sec")

    # Stream ZIP creation in memory
    zip_stream = BytesIO()
    with ZipFile(zip_stream, "w", ZIP_DEFLATED) as zipf:
        for file in success_files:
            zipf.writestr(file["filename"], file["content"])
    zip_stream.seek(0)

    return StreamingResponse(
        zip_stream,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=notices.zip"}
    )