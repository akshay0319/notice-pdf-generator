from fastapi import FastAPI
from app.db.database import init_db
from app.api import templates, notices
from app.api import generate
from app.api import bulk

import logging
import warnings

# === Suppress noisy logs ===
modules_to_silence = [
    "fontTools",
    "fontTools.ttLib.ttFont",
    "fontTools.subset",
    "fontTools.subset.timer",
    "weasyprint",
]

for module in modules_to_silence:
    logging.getLogger(module).setLevel(logging.CRITICAL)
    logging.getLogger(module).propagate = False

warnings.filterwarnings("ignore")

# === App Setup ===
app = FastAPI()

# Initialize the DB on startup
init_db()

# Include routers
app.include_router(templates.router, prefix="/templates", tags=["Templates"])
app.include_router(notices.router, prefix="/notices", tags=["Notices"])
app.include_router(generate.router, prefix="/generate", tags=["Generate PDF"])
app.include_router(bulk.router, prefix="/generate", tags=["Bulk PDF Generation"])

@app.get("/")
def read_root():
    return {"message": "Notice PDF Generator API running"}
