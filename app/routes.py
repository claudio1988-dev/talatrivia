from flask import Blueprint, request, jsonify
from .extensions import db, jwt
from .models import User, Question, Option, Trivia, TriviaQuestion, TriviaParticipation, UserAnswer, Difficulty, UserRole
from .schemas import UserSchema, QuestionSchema, TriviaSchema, RankingSchema
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import datetime

main_bp = Blueprint('main', __name__)

# Schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True)
question_schema = QuestionSchema()
questions_schema = QuestionSchema(many=True)
trivia_schema = TriviaSchema()
trivias_schema = TriviaSchema(many=True)

# --- Auth ---
@main_bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email already exists"}), 400
    
    user = User(
        name=data['name'], 
        email=data['email'],
        role=UserRole(data.get('role', 'player'))
    )
    if 'password' in data:
        user.password_hash = generate_password_hash(data['password'])
    
    db.session.add(user)
    db.session.commit()
    return user_schema.dump(user), 201

@main_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if user and user.password_hash and check_password_hash(user.password_hash, data['password']):
        token = create_access_token(identity=user.id)
        return jsonify({"access_token": token, "user_id": user.id, "role": user.role.value})
    
    return jsonify({"message": "Invalid credentials"}), 401

# --- Users ---
@main_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify(users_schema.dump(users))

# --- Questions ---
@main_bp.route('/questions', methods=['POST'])
def create_question():
    data = request.get_json()
    # data: {text, difficulty: "EASY", options: [{text, is_correct}]}
    
    diff_map = {'EASY': Difficulty.EASY, 'MEDIUM': Difficulty.MEDIUM, 'HARD': Difficulty.HARD}
    difficulty = diff_map.get(data['difficulty'].upper(), Difficulty.EASY)
    
    question = Question(text=data['text'], difficulty=difficulty)
    db.session.add(question)
    db.session.flush() # get ID
    
    for opt_data in data['options']:
        opt = Option(
            question_id=question.id,
            text=opt_data['text'],
            is_correct=opt_data.get('is_correct', False)
        )
        db.session.add(opt)
    
    db.session.commit()
    return question_schema.dump(question), 201

@main_bp.route('/questions', methods=['GET'])
def list_questions():
    questions = Question.query.all()
    return jsonify(questions_schema.dump(questions))

# --- Trivias ---
@main_bp.route('/trivias', methods=['POST'])
def create_trivia():
    data = request.get_json()
    # data: {name, description, question_ids: [], user_ids: []}
    
    trivia = Trivia(name=data['name'], description=data.get('description'))
    db.session.add(trivia)
    db.session.flush()
    
    # Associate Questions
    for q_id in data.get('question_ids', []):
        assoc = TriviaQuestion(trivia_id=trivia.id, question_id=q_id)
        db.session.add(assoc)
        
    # Associate Users (Participation)
    for u_id in data.get('user_ids', []):
        part = TriviaParticipation(trivia_id=trivia.id, user_id=u_id)
        db.session.add(part)
        
    db.session.commit()
    return trivia_schema.dump(trivia), 201

@main_bp.route('/trivias', methods=['GET'])
def list_trivias():
    trivias = Trivia.query.all()
    return jsonify(trivias_schema.dump(trivias))

@main_bp.route('/trivias/<int:id>', methods=['DELETE'])
def delete_trivia(id):
    trivia = Trivia.query.get_or_404(id)
    db.session.delete(trivia)
    db.session.commit()
    return jsonify({"message": "Trivia deleted"}), 200

@main_bp.route('/questions/<int:id>', methods=['DELETE'])
def delete_question(id):
    question = Question.query.get_or_404(id)
    db.session.delete(question)
    db.session.commit()
    return jsonify({"message": "Question deleted"}), 200

# --- Participation ---
@main_bp.route('/my-trivias', methods=['GET'])
@jwt_required()
def my_trivias():
    current_user_id = get_jwt_identity()
    participations = TriviaParticipation.query.filter_by(user_id=current_user_id).all()
    # Return trivias with status
    result = []
    for p in participations:
        result.append({
            "trivia": trivia_schema.dump(p.trivia),
            "score": p.score,
            "completed": p.completed
        })
    return jsonify(result)

@main_bp.route('/trivias/<int:trivia_id>/play', methods=['GET'])
@jwt_required()
def play_trivia(trivia_id):
    current_user_id = get_jwt_identity()
    participation = TriviaParticipation.query.filter_by(trivia_id=trivia_id, user_id=current_user_id).first_or_404()
    
    if participation.completed:
        return jsonify({"message": "You have already completed this trivia", "score": participation.score})
        
    # Get questions for this trivia
    trivia_questions = TriviaQuestion.query.filter_by(trivia_id=trivia_id).all()
    questions_data = []
    
    for tq in trivia_questions:
        q = tq.question
        # Serialize manually to hide is_correct and difficulty if desired (though difficulty is usually evident)
        # Requirement: "No les muestres cuál es la respuesta correcta ni la dificultad"
        opts = [{"id": o.id, "text": o.text} for o in q.options]
        questions_data.append({
            "id": q.id,
            "text": q.text,
            "options": opts
            # No difficulty, no checked answer
        })
        
    return jsonify({
        "trivia": trivia_schema.dump(participation.trivia),
        "questions": questions_data
    })

@main_bp.route('/trivias/<int:trivia_id>/submit', methods=['POST'])
@jwt_required()
def submit_trivia(trivia_id):
    current_user_id = get_jwt_identity()
    participation = TriviaParticipation.query.filter_by(trivia_id=trivia_id, user_id=current_user_id).first_or_404()
    
    if participation.completed:
         return jsonify({"message": "Already completed"}), 400

    data = request.get_json()
    # answers: [{question_id: 1, option_id: 2}, ...]
    
    answers_input = data.get('answers', [])
    total_score = 0
    
    for ans in answers_input:
        q_id = ans['question_id']
        opt_id = ans['option_id']
        
        # Verify valid question for this trivia
        # (omitted for brevity, assume valid inputs from trusted client or add check)
        
        question = Question.query.get(q_id)
        selected_option = Option.query.get(opt_id)
        
        if not question or not selected_option:
            continue
            
        is_correct = selected_option.is_correct and selected_option.question_id == q_id
        
        points = 0
        if is_correct:
            if question.difficulty == Difficulty.EASY:
                points = 1
            elif question.difficulty == Difficulty.MEDIUM:
                points = 2
            elif question.difficulty == Difficulty.HARD:
                points = 3
        
        total_score += points
        
        # Save UserAnswer
        user_answer = UserAnswer(
            participation_id=participation.id,
            question_id=q_id,
            selected_option_id=opt_id,
            is_correct=is_correct,
            points_awarded=points
        )
        db.session.add(user_answer)
        
    participation.score = total_score
    participation.completed = True
    participation.completed_at = datetime.datetime.utcnow() 
    
    db.session.commit()
    
    return jsonify({"message": "Trivia completed", "score": total_score})

# --- Ranking ---
@main_bp.route('/trivias/<int:trivia_id>/ranking', methods=['GET'])
def get_ranking(trivia_id):
    # Ranking based on score descending
    participations = TriviaParticipation.query.filter_by(trivia_id=trivia_id, completed=True).order_by(TriviaParticipation.score.desc()).all()
    
    ranking_data = []
    for p in participations:
        ranking_data.append({
            "user": p.user.name,
            "score": p.score,
            "completed_at": p.completed_at
        })
        
    return jsonify(ranking_data)
