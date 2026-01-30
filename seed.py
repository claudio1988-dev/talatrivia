from app import create_app, db
from app.models import User, Question, Option, Trivia, TriviaQuestion, TriviaParticipation, UserAnswer, Difficulty, UserRole
from werkzeug.security import generate_password_hash
import random
from datetime import datetime, timedelta

def seed_database():
    app = create_app()
    with app.app_context():
        print("Clearing database...")
        db.drop_all()
        db.create_all()

        print("Creating Users...")
        # Admin
        admin = User(name="Admin Talana", email="admin@talana.com", role=UserRole.ADMIN, password_hash=generate_password_hash("admin123"))
        # Players
        players = []
        for i in range(1, 6):
            p = User(name=f"Jugador {i}", email=f"jugador{i}@talana.com", role=UserRole.PLAYER, password_hash=generate_password_hash("123456"))
            players.append(p)
        
        db.session.add(admin)
        db.session.add_all(players)
        db.session.commit()

        print("Creating Questions...")
        questions_data = [
            # Easy (1 point)
            {
                "text": "¿Cuál es el documento principal que regula la relación laboral en Chile?",
                "difficulty": Difficulty.EASY,
                "options": [
                    ("Contrato de Trabajo", True),
                    ("Reglamento Interno", False),
                    ("Liquidación de Sueldo", False),
                    ("Certificado de Antigüedad", False)
                ]
            },
            {
                "text": "¿Qué significa RRHH?",
                "difficulty": Difficulty.EASY,
                "options": [
                    ("Recursos Humanos", True),
                    ("Riesgos Humanos", False),
                    ("Relaciones Humanas", False),
                    ("Reclutamiento Humano", False)
                ]
            },
            # Medium (2 points)
            {
                "text": "¿Cuántas horas máximas ordinarias se pueden trabajar a la semana en Chile (ley 40 horas)?",
                "difficulty": Difficulty.MEDIUM,
                "options": [
                    ("40 horas", True),
                    ("45 horas", False),
                    ("48 horas", False),
                    ("35 horas", False)
                ]
            },
            {
                "text": "¿Qué es el feriado legal?",
                "difficulty": Difficulty.MEDIUM,
                "options": [
                    ("Vacaciones anuales pagadas", True),
                    ("Un día festivo religioso", False),
                    ("Un permiso sin goce de sueldo", False),
                    ("Licencia médica", False)
                ]
            },
            # Hard (3 points)
            {
                "text": "¿En qué caso el empleador puede poner término al contrato sin derecho a indemnización?",
                "difficulty": Difficulty.HARD,
                "options": [
                    ("Conductas indebidas graves (Art. 160)", True),
                    ("Necesidades de la empresa", False),
                    ("Desahucio", False),
                    ("Mutuo acuerdo", False)
                ]
            },
             {
                "text": "¿Cuál es el tope de gratificación legal en base a 4.75 IMM?",
                "difficulty": Difficulty.HARD,
                "options": [
                    ("Sí, es proporcional a los meses trabajados", True),
                    ("No, es un monto fijo para todos", False),
                    ("Depende de la voluntad del empleador", False),
                    ("Solo aplica para gerentes", False)
                ]
            }
        ]

        created_questions = []
        for q_data in questions_data:
            q = Question(text=q_data["text"], difficulty=q_data["difficulty"])
            db.session.add(q)
            db.session.flush() # get ID
            created_questions.append(q)
            
            for opt_text, is_correct in q_data["options"]:
                opt = Option(question_id=q.id, text=opt_text, is_correct=is_correct)
                db.session.add(opt)
        
        db.session.commit()

        print("Creating Trivias...")
        trivia1 = Trivia(name="Onboarding Talana 2026", description="Demuestra cuánto sabes sobre legislación laboral y cultura Talana.")
        db.session.add(trivia1)
        db.session.flush()

        # Assign all questions to Trivia 1
        for q in created_questions:
            assoc = TriviaQuestion(trivia_id=trivia1.id, question_id=q.id)
            db.session.add(assoc)

        # Assign all players to Trivia 1
        participations = []
        for p in players:
            part = TriviaParticipation(trivia_id=trivia1.id, user_id=p.id)
            db.session.add(part)
            participations.append(part)
        
        db.session.commit()

        print("Simulating Gameplay (Ranking)...")
        # Let's make Player 1 (Jugador 1) get a perfect score
        p1_part = participations[0] # Jugador 1
        p1_score = 0
        
        for q in created_questions:
            # Find correct option
            correct_opt = next(opt for opt in q.options if opt.is_correct)
            
            # Calculate points
            points = 0
            if q.difficulty == Difficulty.EASY: points = 1
            if q.difficulty == Difficulty.MEDIUM: points = 2
            if q.difficulty == Difficulty.HARD: points = 3
            p1_score += points

            # Answer
            ans = UserAnswer(
                participation_id=p1_part.id,
                question_id=q.id,
                selected_option_id=correct_opt.id,
                is_correct=True,
                points_awarded=points
            )
            db.session.add(ans)
        
        p1_part.score = p1_score
        p1_part.completed = True
        p1_part.completed_at = datetime.utcnow()
        
        # Player 2 gets half right
        p2_part = participations[1] # Jugador 2
        p2_score = 0
        for i, q in enumerate(created_questions):
            # Alternate correct/incorrect
            if i % 2 == 0:
                selected_opt = next(opt for opt in q.options if opt.is_correct)
                is_correct = True
                points = 0
                if q.difficulty == Difficulty.EASY: points = 1
                if q.difficulty == Difficulty.MEDIUM: points = 2
                if q.difficulty == Difficulty.HARD: points = 3
            else:
                selected_opt = next(opt for opt in q.options if not opt.is_correct)
                is_correct = False
                points = 0
            
            p2_score += points
            ans = UserAnswer(participation_id=p2_part.id, question_id=q.id, selected_option_id=selected_opt.id, is_correct=is_correct, points_awarded=points)
            db.session.add(ans)

        p2_part.score = p2_score
        p2_part.completed = True
        p2_part.completed_at = datetime.utcnow() - timedelta(minutes=5) # Finished earlier

        # Player 3 has not played yet (Pending)

        db.session.commit()
        print("Database seeded successfully!")
        print(f"Created {len(players)} players and 1 admin.")
        print(f"Created {len(created_questions)} questions.")
        print(f"Created 1 Trivia with participation simulations.")

if __name__ == '__main__':
    seed_database()
