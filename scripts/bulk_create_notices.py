from app.db.database import SessionLocal
from app.db.models import Notice
import json
import random

db = SessionLocal()

TEMPLATE_ID = 1  # Make sure this exists first
COUNT = 1000     # Number of notices to create

for i in range(COUNT):
    data = {
        "name": f"User {i}",
        "address": f"Test Address {i}",
        "loan_number": f"LN{i:05}"
    }
    notice = Notice(
        recipient_name=data["name"],
        data_json=json.dumps(data),
        template_id=TEMPLATE_ID
    )
    db.add(notice)

db.commit()
db.close()
print(f"✅ Created {COUNT} notices.")
