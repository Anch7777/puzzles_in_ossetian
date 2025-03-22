from app import app, db
from models import Riddle

with app.app_context():
    # Очистка таблицы ребусов
    db.session.query(Riddle).delete()
    db.session.commit()

    # Добавление новых ребусов
    rebuses = [
        {"image": "rebus1.png", "answer": "хæрисджын", "hints": "Первая буква 'х', В слове 8 букв, æ дж"},
        {"image": "rebus2.png", "answer": "бирæгъзæнг", "hints": "Первая буква 'б', В слове 9 букв, æ гъ"},
        {"image": "rebus3.png", "answer": "фыййагдон", "hints": "Первая буква 'ф', В слове 9 букв, ы й"},
        {"image": "rebus4.png", "answer": "сындзыхъæу", "hints": "Первая буква 'с', В слове 8 букв, дз хъ"},
        {"image": "rebus5.png", "answer": "дур-дур", "hints": "Первая буква 'д', В слове 7 букв, д"}
    ]

    for r in rebuses:
        new_riddle = Riddle(image=r['image'], answer=r['answer'], hints=r['hints'])
        db.session.add(new_riddle)

    db.session.commit()
