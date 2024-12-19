from app import db
from sqlalchemy import UniqueConstraint, func, Index
import uuid
from app.models.shared_tables import usergroup_user, usergroup_tag

# Table: UserGroup
class UserGroup(db.Model):
    __tablename__ = 'usergroup'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    org_id = db.Column(db.String(36), db.ForeignKey('organization.id', ondelete="SET NULL"), primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(150), nullable=True)
    status = db.Column(db.String(1), nullable=False, default='1')  # 1=open (default); 0=closed
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    created_by = db.Column(db.String(36), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by = db.Column(db.String(36), nullable=False)

    # Relationship to Users (many-to-many)
    users = db.relationship('User', secondary=usergroup_user, backref=db.backref('usergroup'))
    tags = db.relationship('Tag', secondary=usergroup_tag, backref=db.backref('usergroups', lazy='dynamic'))
