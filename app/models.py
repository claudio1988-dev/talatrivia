from .extensions import db
from datetime import datetime
import enum

class Difficulty(enum.Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3

class UserRole(enum.Enum):
    ADMIN = 'admin'
    PLAYER = 'player'

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True) # For auth
    role = db.Column(db.Enum(UserRole), default=UserRole.PLAYER)
    
    # Relationships
    participations = db.relationship('TriviaParticipation', back_populates='user')

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    difficulty = db.Column(db.Enum(Difficulty), nullable=False)
    
    # Relationships
    options = db.relationship('Option', back_populates='question', cascade='all, delete-orphan')
    trivias = db.relationship('TriviaQuestion', back_populates='question')

class Option(db.Model):
    __tablename__ = 'options'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    text = db.Column(db.String(200), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    
    question = db.relationship('Question', back_populates='options')

class Trivia(db.Model):
    __tablename__ = 'trivias'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    questions = db.relationship('TriviaQuestion', back_populates='trivia', cascade='all, delete-orphan')
    participations = db.relationship('TriviaParticipation', back_populates='trivia')

class TriviaQuestion(db.Model):
    __tablename__ = 'trivia_questions'
    trivia_id = db.Column(db.Integer, db.ForeignKey('trivias.id'), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), primary_key=True)
    
    trivia = db.relationship('Trivia', back_populates='questions')
    question = db.relationship('Question', back_populates='trivias')

class TriviaParticipation(db.Model):
    __tablename__ = 'trivia_participations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trivia_id = db.Column(db.Integer, db.ForeignKey('trivias.id'), nullable=False)
    score = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)    
    
    user = db.relationship('User', back_populates='participations')
    trivia = db.relationship('Trivia', back_populates='participations')
    answers = db.relationship('UserAnswer', back_populates='participation')

class UserAnswer(db.Model):
    __tablename__ = 'user_answers'
    id = db.Column(db.Integer, primary_key=True)
    participation_id = db.Column(db.Integer, db.ForeignKey('trivia_participations.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    selected_option_id = db.Column(db.Integer, db.ForeignKey('options.id'), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    points_awarded = db.Column(db.Integer, default=0)
    
    participation = db.relationship('TriviaParticipation', back_populates='answers')
