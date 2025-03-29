from flask import Flask, render_template, request, redirect, url_for, session, flash
from data.db_session import db
from data.users import User
from data.riddles import Riddle
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Определение BASE_DIR
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Настройка пути к базе данных
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "data", "puzzles.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Буквы осетинского алфавита
ossetian_alphabet = [
    'а', 'æ', 'б', 'г', 'гъ', 'д', 'дж', 'дз', 'ж', 'з', 'и', 'й', 'н', 'о',
    'р', 'с', 'у', 'ф', 'х', 'хъ', 'ы', '-'
]

def initialize_database():
    """Инициализация базы данных: создание таблиц и добавление начальных данных."""
    with app.app_context():
        db.create_all()  # Создание таблиц

        # Проверка наличия ребусов в базе данных
        if Riddle.query.count() == 0:
            # Очистка таблицы ребусов (если она не пуста)
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rules')
def rules():
    return render_template('rules.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(name=username, password=password).first()
        if user:
            session['username'] = user.name
            session['score'] = user.score
            return redirect(url_for('game'))
        else:
            flash('Неверное имя пользователя или пароль.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(name=username).first():
            flash('Имя пользователя уже занято.', 'danger')
        else:
            new_user = User(name=username, password=password, score=0)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            session['score'] = 0
            return redirect(url_for('game'))
    return render_template('register.html')

@app.route('/game', methods=['GET', 'POST'])
def game():
    if 'username' not in session:
        session['username'] = 'guest'
        session['score'] = 0
        session['solved_rebuses'] = ''
    rebuses = Riddle.query.all()
    user = User.query.filter_by(name=session['username']).first() if session['username'] != 'guest' else None
    solved_rebuses = set(session['solved_rebuses'].split(',') if session['solved_rebuses'] else [])
    current_rebus_id = int(request.args.get('rebus_id', 1))
    current_rebus = next((r for r in rebuses if r.id == current_rebus_id), None)
    hints_left = 3 - len([hint for hint in session.get('used_hints', {}).get(str(current_rebus_id), [])])
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'check_answer':
            user_answer = request.form['answer'].strip()
            if user_answer == current_rebus.answer:
                if str(current_rebus.id) not in solved_rebuses:
                    session['score'] = session.get('score', 0) + 20
                    solved_rebuses.add(str(current_rebus.id))
                    session['solved_rebuses'] = ','.join(solved_rebuses)
                    flash('Правильно!', 'success')
                return redirect(url_for('game', rebus_id=current_rebus_id + 1))
            else:
                flash('Неправильно. Попробуйте еще раз.', 'danger')
        elif action == 'show_hint':
            used_hints = session.setdefault('used_hints', {})
            if len(used_hints.get(str(current_rebus_id), [])) < 3:
                hints = current_rebus.hints.split(',')
                used_hints.setdefault(str(current_rebus_id), []).append(hints[len(used_hints[str(current_rebus_id)])])
                session.modified = True
                flash(f"Подсказка: {hints[len(used_hints[str(current_rebus_id)]) - 1]}", 'info')
            else:
                flash("Вы использовали все подсказки для этого ребуса!", 'warning')
    if current_rebus is None:
        return redirect(url_for('success'))
    show_register_modal = session['username'] == 'guest' and len(solved_rebuses) >= 3
    return render_template(
        'game.html',
        rebus=current_rebus,
        score=session['score'],
        ossetian_alphabet=ossetian_alphabet,
        hints_left=hints_left,
        show_register_modal=show_register_modal
    )

@app.route('/rating')
def rating():
    ratings = User.query.order_by(User.score.desc()).all()
    return render_template('rating.html', ratings=ratings)

@app.route('/success')
def success():
    return render_template('success.html')

if __name__ == '__main__':
    # Инициализация базы данных при первом запуске
    initialize_database()
    app.run(debug=True)