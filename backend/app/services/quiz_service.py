from app.models.quiz_models import Quiz, QuizQuestion, QuizOption
from datetime import datetime

def get_open_quizzes():
    open_quizzes = Quiz.query.filter(Quiz.end_date >= datetime.utcnow()).all()
    quizzes_data = [
        {
            "id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
            "end_date": quiz.end_date
        } for quiz in open_quizzes
    ]
    return quizzes_data

def create_quiz_service(data, current_user):
    # Logic for creating a new quiz
    new_quiz = save_quiz(data, current_user)
    return new_quiz
