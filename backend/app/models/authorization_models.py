from app import db
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from sqlalchemy import func, UniqueConstraint, Index
from app.models.shared_tables import securityrole_authorizations, user_securityroles

import uuid

bcrypt = Bcrypt()

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    org_id = db.Column(db.String(36), db.ForeignKey('organization.id', ondelete="SET NULL"), primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
    locked = db.Column(db.Boolean, default=False)
    last_logon = db.Column(db.DateTime)
    logon_attempt = db.Column(db.Integer, nullable=False, default=0)
    created_by = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_by = db.Column(db.String(36), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())

    __table_args__ = (
        db.Index('idx_user_email', 'email'),
        db.Index('idx_user_username', 'username'),
    )

    # Relationships
    roles = db.relationship('SecurityRole', secondary='user_securityroles', backref='users')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Authorization(db.Model):
    __tablename__ = 'authorization'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    resource_id = db.Column(db.String(36), db.ForeignKey('resource.id', ondelete="SET NULL"), nullable=False)
    action_id = db.Column(db.String(36), db.ForeignKey('action.id', ondelete="SET NULL"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    created_by = db.Column(db.String(36), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by = db.Column(db.String(36), nullable=False)

    # Unique constraint to ensure no duplicate permissions for a role-resource-action combination
    __table_args__ = (
        UniqueConstraint('resource_id', 'action_id', name='uix_securityrole_resource_action'),
    )

# Table: SecurityRole
class SecurityRole(db.Model):
    __tablename__ = 'securityrole'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    org_id = db.Column(db.String(36), db.ForeignKey('organization.id', ondelete="SET NULL"), primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    created_by = db.Column(db.String(36), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by = db.Column(db.String(36), nullable=False)

    authorizations = db.relationship('Authorization', secondary=securityrole_authorizations, backref=db.backref('securityrole'))