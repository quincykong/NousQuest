from app.extensions import db
from sqlalchemy import UniqueConstraint, func, Index
import uuid
from app.models.shared_tables import usergroup_tag

class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    org_id = db.Column(db.String(36), db.ForeignKey('organization.id', ondelete="SET NULL"), primary_key=True)
    resource_id = db.Column(db.String(36), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    created_by = db.Column(db.String(36), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by = db.Column(db.String(36), nullable=False)
    __table_args__ = (
        UniqueConstraint('org_id', 'name', name='uq_org_tag_name'),
    )