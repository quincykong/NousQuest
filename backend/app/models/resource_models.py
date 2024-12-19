from app import db
from sqlalchemy import func, UniqueConstraint
import uuid

class Resource(db.Model):
    __tablename__ = 'resource'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    name = db.Column(db.String(30), unique=True, nullable=False)  # e.g., 'quiz', 'usergroup', 'class'
    description = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    created_by = db.Column(db.String(36), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by = db.Column(db.String(36), nullable=False)