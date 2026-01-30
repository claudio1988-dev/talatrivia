import os

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/talatrivia')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default-secret-key')
