from app import db
from sqlalchemy import func, UniqueConstraint
import uuid
from app.models.shared_tables import class_enrollment

class Class(db.Model):
    __tablename__ = 'class'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    org_id = db.Column(db.String(36), db.ForeignKey('organization.id', ondelete="SET NULL"), primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    venue = db.Column(db.String(256))
    owner_id = db.Column(db.String(36), db.ForeignKey('user.id', ondelete="SET NULL"), nullable=False)
    status = db.Column(db.String(1), nullable=False, default='1')  # 1=open; 0=closed
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # Relationships
    enrolled_users = db.relationship(
        'User', 
        secondary=class_enrollment, 
        backref='enrolled_classes',
        lazy='dynamic'
    )
