from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import Notice, BatchJob
from app.core.pdf_engine import render_pdf_bytes, compile_template

from pydantic import BaseModel
from multiprocessing import Process, Manager
from datetime import datetime
import os, uuid, json, asyncio, shutil

router = APIRouter()

class NoticeBatchRequest(BaseModel):
    notice_ids: list[int]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def pdf_worker(notice_id, output_dir, result_list):
    db = SessionLocal()
    notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if not notice:
        result_list.append({"notice_id": notice_id, "status": "not_found"})
        return

    try:
        data = json.loads(notice.data_json)
        rendered_html = generate_html(notice.template.html_content, data)
        filename = f"{notice_id}_{uuid.uuid4().hex}.pdf"
        output_path = os.path.join(output_dir, filename)

        pdf_bytes = render_pdf_bytes(html)

        result_list.append({
            "notice_id": notice_id,
            "status": "success",
            "file": filename
        })
    except Exception as e:
        result_list.append({"notice_id": notice_id, "status": f"error: {str(e)}"})

@router.post("/batch")
async def generate_pdfs_in_batch(request: NoticeBatchRequest):
    try:
        db = SessionLocal()

        # Create batch job and flush to get ID
        job = BatchJob(
            notice_ids=json.dumps(request.notice_ids),
            status="pending"
        )
        db.add(job)
        db.flush()  # Get job.id before commit
        job_id = job.id  # ✅ Store safely now

        # Prepare output directory
        batch_id = f"batch_{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        output_dir = f"generated_pdfs/{batch_id}"
        os.makedirs(output_dir, exist_ok=True)

        # Generate PDFs in parallel
        manager = Manager()
        result_list = manager.list()
        processes = []

        for nid in request.notice_ids:
            p = Process(target=pdf_worker, args=(nid, output_dir, result_list))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        # Zip generated PDFs
        zip_name = f"{batch_id}.zip"
        zip_path = os.path.join("downloads", zip_name)
        os.makedirs("downloads", exist_ok=True)
        shutil.make_archive(zip_path.replace(".zip", ""), 'zip', output_dir)

        # Finalize batch job
        job.status = "completed"
        job.zip_path = f"/downloads/{zip_name}"
        db.commit()
        db.close()

        return {
            "batch_id": job_id,  # ✅ Use stored value, not job.id
            "zip_file": f"/downloads/{zip_name}",
            "results": list(result_list)
        }

    except Exception as e:
        print("🔥 ERROR:", e)
        return {"error": str(e)}

@router.get("/downloads/{zip_filename}")
def download_zip(zip_filename: str):
    zip_path = os.path.join("downloads", zip_filename)
    if not os.path.exists(zip_path):
        return {"error": "ZIP file not found"}
    return FileResponse(zip_path, filename=zip_filename, media_type="application/zip")

@router.get("/batches")
def list_batches(db: Session = Depends(get_db)):
    batches = db.query(BatchJob).order_by(BatchJob.created_at.desc()).all()
    return [
        {
            "id": batch.id,
            "notice_ids": json.loads(batch.notice_ids),
            "status": batch.status,
            "zip_path": batch.zip_path,
            "created_at": str(batch.created_at)
        } for batch in batches
    ]

@router.get("/batches/{job_id}")
def get_batch(job_id: int, db: Session = Depends(get_db)):
    batch = db.query(BatchJob).filter(BatchJob.id == job_id).first()
    if not batch:
        return {"error": "Batch not found"}
    return {
        "id": batch.id,
        "notice_ids": json.loads(batch.notice_ids),
        "status": batch.status,
        "zip_path": batch.zip_path,
        "created_at": str(batch.created_at)
    }
