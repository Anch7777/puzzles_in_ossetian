from .db_session import db

class Riddle(db.Model):
    __tablename__ = 'riddles'
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(255), nullable=False)  # Путь к изображению ребуса
    answer = db.Column(db.String(100), nullable=False)  # Ответ на ребус
    hints = db.Column(db.String(255))  # Подсказки через запятую

    def __repr__(self):
        return f'<Riddle {self.id}>'