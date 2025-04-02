from flask_sqlalchemy import SQLAlchemy

# Создаем экземпляр базы данных
db = SQLAlchemy()

# Импортируем модели
from .users import User
from .riddles import Riddle