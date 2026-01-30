from app import create_app, db
from flask_migrate import upgrade

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Auto-create tables for dev convenience if they don't exist
        # In production, use 'flask db upgrade'
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
