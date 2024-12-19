from app import db
from sqlalchemy import func, UniqueConstraint
import uuid
from app.models.shared_tables import user_organization

class Organization(db.Model):
    __tablename__ = 'organization'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False, unique=True)
    timezone = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(100), nullable=True)
    # mail server config
    smtp_server = db.Column(db.String(255), nullable=False)
    smtp_port = db.Column(db.Integer, nullable=False)
    smtp_use_tls = db.Column(db.Boolean, nullable=False, default=True)
    smtp_use_ssl = db.Column(db.Boolean, nullable=False, default=False)
    smtp_username = db.Column(db.String(255), nullable=False)
    smtp_password = db.Column(db.String(255), nullable=False)  # Consider encrypting or securing the password
    smtp_sender = db.Column(db.String(255), nullable=False)  # Email address used as the sender
    #
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    created_by = db.Column(db.String(36), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by = db.Column(db.String(36), nullable=False)
