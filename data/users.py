from .db_session import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, default=0)
    solved_rebuses = db.Column(db.String(255), default="")  # Список решенных ребусов через запятую

    def __repr__(self):
        return f'<User {self.name}>'