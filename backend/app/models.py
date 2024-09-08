from app import db
from datetime import datetime
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from sqlalchemy import UniqueConstraint, func
import uuid

bcrypt = Bcrypt()

# M:M - Class enrollment
class_enrollment = db.Table('class_enrollment',
    db.Column('class_id', db.String(36), db.ForeignKey('class.id'), primary_key=True),
    db.Column('user_id', db.String(36), db.ForeignKey('user.id'), primary_key=True),
    db.Column('created_at', db.DateTime(timezone=True), default=func.now()),
    db.Column('created_by', db.String(36), nullable=False)
)

# M:M - User Group
usergroup_membership = db.Table('usergroup_membership',
    db.Column('group_id', db.String(36), db.ForeignKey('usergroup.id'), primary_key=True),
    db.Column('user_id', db.String(36), db.ForeignKey('user.id'), primary_key=True),
    db.Column('created_at', db.DateTime(timezone=True), default=func.now()),
    db.Column('created_by', db.String(36), nullable=False)
)

# M:M - SecurityRole to Authorization
securityrole_authorizations = db.Table('securityrole_authorizations',
    db.Column('securityrole_id', db.String(36), db.ForeignKey('securityrole.id'), primary_key=True),
    db.Column('authorization_id', db.String(36), db.ForeignKey('authorization.id'), primary_key=True),
    db.Column('created_at', db.DateTime(timezone=True), default=func.now()),
    db.Column('created_by', db.String(36), nullable=False)
)

# M:M - User to Role
user_securityroles = db.Table('user_securityroles',
    db.Column('user_id', db.String(36), db.ForeignKey('user.id'), primary_key=True),
    db.Column('securityrole_id', db.String(36), db.ForeignKey('securityrole.id'), primary_key=True),
    db.Column('created_at', db.DateTime(timezone=True), default=func.now()),
    db.Column('created_by', db.String(36), nullable=False)
)

# M:M - User to Organization
user_oganization = db.table('user_organizations',
    db.Column('user_id', db.String(36), db.ForeignKey('user.id'), primary_key=True),
    db.Column('organization_id', db.String(36), db.ForeignKey('organization.id'), primary_key=True),
    db.Column('created_at', db.DateTime(timezone=True), default=func.now()),
    db.Column('created_by', db.String(36), nullable=False)
)

class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    resource = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)  # e.g., 'loop', 'variables'
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    created_by = db.Column(db.String(36), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by = db.Column(db.String(36), nullable=False)

# Association table for the many-to-many relationship between Question and Tag
question_tags = db.Table('question_tags',
    db.Column('question_id', db.String(36), db.ForeignKey('quizquestion.id'), primary_key=True),  # Corrected reference
    db.Column('tag_id', db.String(36), db.ForeignKey('tag.id'), primary_key=True),
    db.Column('created_at', db.DateTime(timezone=True), default=func.now()),
    db.Column('created_by', db.String(36), nullable=False)
)

class Quiz(db.Model):
    __tablename__ = 'quiz'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    # Quiz properties
    status = db.Column(db.String(1), nullable=False, default='1')  # 1=open (default); 0=closed
    display_sequence = db.Column(db.String(1), nullable=False, default='C') # C=creation; #S=shuffle
    quiz_duration = db.Column(db.Integer, nullable=False, default=0)
    total_score = db.Column(db.Integer, nullable=False, default=100)
    students_assigned = db.Column(db.Integer, nullable=False, default=0)
    attempt_limit = db.Column(db.Integer, nullable=False, default=1)
    attempt_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    created_by = db.Column(db.String(36), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by = db.Column(db.String(36), nullable=False)

    questions = db.relationship('QuizQuestion', backref='quiz', cascade='all, delete-orphan', lazy=True)

class QuizQuestion(db.Model):
    __tablename__ = 'quizquestion'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    quiz_id = db.Column(db.String(36), db.ForeignKey('quiz.id'), nullable=False)
    question_sequence = db.Column(db.Integer, nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(1), nullable=False) # M=Multiple Choice; O=Open-ended
    image_url = db.Column(db.String(256))
    score_weight = db.Column(db.Integer) # Question individual score
    question_duration = db.Column(db.Integer, nullable=False, default=0)    # in minutes
    shuffle_option = db.Column(db.String(1), nullable=False, default="N") # Y=Shuffle options for MC question; N=In creation sequence
    tags = db.relationship('Tag', secondary=question_tags, backref='question')
    reviewer_id = db.Column(db.String(36), db.ForeignKey('user.id'))
    review_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    created_by = db.Column(db.String(36), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by = db.Column(db.String(36), nullable=False)

    options = db.relationship('QuizOption', backref='question', cascade='all, delete-orphan', lazy=True)

# Table: UserGroup
class UserGroup(db.Model):
    __tablename__ = 'usergroup'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    org_id = db.Column(db.String(36), db.ForeignKey('organization.id'), nullable=False)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(150), nullable=True)
    studentcount = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(1), nullable=False, default='1')  # 1=open (default); 0=closed
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    created_by = db.Column(db.String(36), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by = db.Column(db.String(36), nullable=False)

    # Relationship to Users (many-to-many)
    members = db.relationship('User', secondary=usergroup_membership, backref=db.backref('usergroup'))

# Table: User
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    userclass = db.Column(db.String(10), unique=True, nullable=False)   # system, org, student
    locked = db.Column(db.Boolean, default=False)
    last_logon = db.Column(db.DateTime)
    logon_attempt = db.Column(db.Integer, nullable=False, default=0)
    created_by = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_by = db.Column(db.String(36), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    org_id = db.Column(db.String(36), db.ForeignKey('organization.id'))

    # Relationships
    enrolled_students = db.relationship(
        'Class', 
        secondary=class_enrollment, 
        back_populates='enrolled_students',  # Explicitly link this to Class.enrolled_students
        overlaps="enrolled_courses"
    )

    def set_password(self, password):
        """Hashes the password and stores it."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Checks the hashed password against the user-provided password."""
        return bcrypt.check_password_hash(self.password_hash, password)

class Class(db.Model):
    __tablename__ = 'class'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    class_url = db.Column(db.String(256))  # for course materials or video link
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    venue = db.Column(db.String(256))
    owner = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    invitation_key = db.Column(db.String(12), nullable=False)
    status = db.Column(db.String(1), nullable=False, default='1')  # 1=open; 0=closed
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    created_by = db.Column(db.String(36), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by = db.Column(db.String(36), nullable=False)
    
    org_id = db.Column(db.String(36), db.ForeignKey('organization.id'))

    # Correctly link the relationship
    enrolled_students = db.relationship(
        'User', 
        secondary=class_enrollment, 
        back_populates='enrolled_students',  # Explicitly link this to User.enrolled_students
        overlaps="enrolled_courses"
    )

class QuizOption(db.Model):
    __tablename__ = 'quizoption'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    question_id = db.Column(db.String(36), db.ForeignKey('quizquestion.id'), nullable=False)  # Corrected foreign key
    option_sequence = db.Column(db.Integer, nullable=False)
    option_text = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    created_by = db.Column(db.String(36), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by = db.Column(db.String(36), nullable=False)

class QuizSubmission(db.Model):
    __tablename__ = 'quizsubmission'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)  # References the student who took the quiz
    quiz_id = db.Column(db.String(36), db.ForeignKey('quiz.id'), nullable=False)  # References the quiz taken
    question_id = db.Column(db.String(36), db.ForeignKey('quizquestion.id'), nullable=False)  # Corrected foreign key
    option_id = db.Column(db.String(36), db.ForeignKey('quizoption.id'))  # References the selected option for MC questions
    answer_text = db.Column(db.Text)  # Stores the answer for open-ended questions
    is_correct = db.Column(db.Boolean, default=False)  # Stores whether the answer was correct (for MC questions)
    attempt_number = db.Column(db.Integer, nullable=False, default=1)  # Tracks which attempt this submission belongs to
    submitted_at = db.Column(db.DateTime(timezone=True), default=func.now())
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    created_by = db.Column(db.String(36), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by = db.Column(db.String(36), nullable=False)

# Table: SecurityRole
class SecurityRole(db.Model):
    __tablename__ = 'securityrole'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    created_by = db.Column(db.String(36), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by = db.Column(db.String(36), nullable=False)

    authorizations = db.relationship('Authorization', secondary=securityrole_authorizations, backref=db.backref('securityrole'))

# Table: Security - Resource
class Resource(db.Model):
    __tablename__ = 'resource'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    name = db.Column(db.String(30), unique=True, nullable=False)  # e.g., 'quiz', 'usergroup', 'class'
    description = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    created_by = db.Column(db.String(36), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by = db.Column(db.String(36), nullable=False)

# Table: Security - Action
class Action(db.Model):
    __tablename__ = 'action'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    name = db.Column(db.String(30), unique=True, nullable=False)  # e.g., 'create', 'read', 'update', 'delete', 'export'
    description = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    created_by = db.Column(db.String(36), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by = db.Column(db.String(36), nullable=False)

# Table: Authorization
class Authorization(db.Model):
    __tablename__ = 'authorization'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    role_id = db.Column(db.String(36), db.ForeignKey('securityrole.id'), nullable=False)
    resource_id = db.Column(db.String(36), db.ForeignKey('resource.id'), nullable=False)
    action_id = db.Column(db.String(36), db.ForeignKey('action.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    created_by = db.Column(db.String(36), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by = db.Column(db.String(36), nullable=False)

    # Unique constraint to ensure no duplicate permissions for a role-resource-action combination
    __table_args__ = (
        UniqueConstraint('role_id', 'resource_id', 'action_id', name='uix_securityrole_resource_action'),
    )

# Table: Organization
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

    users = db.relationship('User', backref='organization', lazy=True)
    usergroups = db.relationship('UserGroup', backref='organization', lazy=True)
    classes = db.relationship('Class', backref='organization', lazy=True)
