from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime
from sqlalchemy.sql import func

Base = declarative_base()

class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    html_content = Column(Text, nullable=False)

    notices = relationship("Notice", back_populates="template")


class Notice(Base):
    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, index=True)
    recipient_name = Column(String(100), nullable=False)
    data_json = Column(Text, nullable=False)  # will hold dict as string
    template_id = Column(Integer, ForeignKey("templates.id"))

    template = relationship("Template", back_populates="notices")

class BatchJob(Base):
    __tablename__ = "batch_jobs"

    id = Column(Integer, primary_key=True, index=True)
    notice_ids = Column(Text, nullable=False)  # store as JSON string
    zip_path = Column(String(255), nullable=True)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
