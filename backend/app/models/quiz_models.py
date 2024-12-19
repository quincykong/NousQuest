from app import db
from sqlalchemy import func, UniqueConstraint
import uuid

class Quiz(db.Model):
    __tablename__ = 'quiz'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    org_id = db.Column(db.String(36), db.ForeignKey('organization.id', ondelete="SET NULL"), primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(1), nullable=False, default='1')  # 1=open; 0=closed
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # Relationships
    questions = db.relationship('QuizQuestion', backref='quiz', cascade='all, delete-orphan', lazy=True)

class QuizQuestion(db.Model):
    __tablename__ = 'quizquestion'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    quiz_id = db.Column(db.String(36), db.ForeignKey('quiz.id', ondelete="SET NULL"), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())

class QuizOption(db.Model):
    __tablename__ = 'quizoption'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    question_id = db.Column(db.String(36), db.ForeignKey('quizquestion.id', ondelete="SET NULL"), nullable=False)  # Corrected foreign key
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
    org_id = db.Column(db.String(36), db.ForeignKey('organization.id', ondelete="SET NULL"), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id', ondelete="SET NULL"), nullable=False)  # References the student who took the quiz
    quiz_id = db.Column(db.String(36), db.ForeignKey('quiz.id', ondelete="SET NULL"), nullable=False)  # References the quiz taken
    question_id = db.Column(db.String(36), db.ForeignKey('quizquestion.id', ondelete="SET NULL"), nullable=False)  # Corrected foreign key
    option_id = db.Column(db.String(36), db.ForeignKey('quizoption.id', ondelete="SET NULL"))  # References the selected option for MC questions
    answer_text = db.Column(db.Text)  # Stores the answer for open-ended questions
    is_correct = db.Column(db.Boolean, default=False)  # Stores whether the answer was correct (for MC questions)
    attempt_number = db.Column(db.Integer, nullable=False, default=1)  # Tracks which attempt this submission belongs to
    submitted_at = db.Column(db.DateTime(timezone=True), default=func.now())
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    created_by = db.Column(db.String(36), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by = db.Column(db.String(36), nullable=False)