from app import db
from sqlalchemy import func, UniqueConstraint, Index

# M:M - SecurityRole to Authorization
securityrole_authorizations = db.Table('securityrole_authorizations',
    db.Column('org_id', db.String(36), db.ForeignKey('organization.id', ondelete="SET NULL"), primary_key=True),
    db.Column('securityrole_id', db.String(36), db.ForeignKey('securityrole.id', ondelete="SET NULL"), primary_key=True),
    db.Column('authorization_id', db.String(36), db.ForeignKey('authorization.id', ondelete="SET NULL"), primary_key=True),
    db.Column('created_at', db.DateTime(timezone=True), default=func.now()),
    db.Column('created_by', db.String(36), nullable=False)
)

# M:M - User to Role
user_securityroles = db.Table('user_securityroles',
    db.Column('org_id', db.String(36), db.ForeignKey('organization.id'), primary_key=True),
    db.Column('user_id', db.String(36), db.ForeignKey('user.id'), primary_key=True),
    db.Column('securityrole_id', db.String(36), db.ForeignKey('securityrole.id'), primary_key=True),
    db.Column('created_at', db.DateTime(timezone=True), default=func.now()),
    db.Column('created_by', db.String(36), nullable=False)
)

# M:M - class to user (enrollment)
class_enrollment = db.Table(
    'class_enrollment',
    db.Column('org_id', db.String(36), db.ForeignKey('organization.id', ondelete="SET NULL"), nullable=False),
    db.Column('class_id', db.String(36), db.ForeignKey('class.id', ondelete="SET NULL"), nullable=False),
    db.Column('user_id', db.String(36), db.ForeignKey('user.id', ondelete="SET NULL"), nullable=False),
    db.Column('created_at', db.DateTime(timezone=True), default=func.now(), nullable=False),
    db.Column('created_by', db.String(36), nullable=False),
    UniqueConstraint('org_id', 'class_id', 'user_id', name='uq_class_enrollment')
)

# M:M - User to Organization
user_organization = db.Table('user_organizations',
    db.Column('user_id', db.String(36), db.ForeignKey('user.id', ondelete="SET NULL"), primary_key=True),
    db.Column('organization_id', db.String(36), db.ForeignKey('organization.id', ondelete="SET NULL"), primary_key=True),
    db.Column('created_at', db.DateTime(timezone=True), default=func.now()),
    db.Column('created_by', db.String(36), nullable=False)
)


# M:M - User Grooup to Tag
usergroup_tag = db.Table('usergroup_tag',
    db.Column('org_id', db.String(36), db.ForeignKey('organization.id', ondelete="SET NULL"), primary_key=True),
    db.Column('usergroup_id', db.String(36), db.ForeignKey('usergroup.id', ondelete="SET NULL"), primary_key=True),
    db.Column('tag_id', db.String(36), db.ForeignKey('tag.id', ondelete="SET NULL"), primary_key=True),
    db.Column('created_at', db.DateTime(timezone=True), default=func.now()),
    db.Column('created_by', db.String(36), nullable=False)
)


# M:M - User Group
usergroup_user = db.Table(
    'usergroup_user',
    db.Column('org_id', db.String(36), db.ForeignKey('organization.id', ondelete="SET NULL"), nullable=False),
    db.Column('group_id', db.String(36), db.ForeignKey('usergroup.id', ondelete="SET NULL"), nullable=False),
    db.Column('user_id', db.String(36), db.ForeignKey('user.id', ondelete="SET NULL"), nullable=False),
    db.Column('created_at', db.DateTime(timezone=True), default=func.now(), nullable=False),
    db.Column('created_by', db.String(36), nullable=False),
    Index('idx_usergroup_user', 'org_id', 'group_id', 'user_id')
)
