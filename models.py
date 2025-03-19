from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, default=0)
    solved_rebuses = db.Column(db.String(255), default="")  # Список решенных ребусов через запятую

class Riddle(db.Model):
    __tablename__ = 'riddles'
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(255), nullable=False)  # Путь к изображению ребуса
    answer = db.Column(db.String(100), nullable=False)  # Ответ на ребус
    hints = db.Column(db.String(255))  # Подсказки через запятую  # Подсказки через запятую

    def __repr__(self):
        return f'<Riddle {self.id}>'