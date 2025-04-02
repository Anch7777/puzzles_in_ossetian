import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from data._all_models import db, User, Riddle

# Создание экземпляра приложения
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Ключ для работы с сессиями

# Настройка пути к базе данных
DATABASE_PATH = os.path.abspath('db/puzzles.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DATABASE_PATH}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация базы данных
db.init_app(app)

# Буквы осетинского алфавита
ossetian_alphabet = [
    'а', 'æ', 'б', 'г', 'гъ', 'д', 'дж', 'дз', 'ж', 'з', 'и', 'й', 'н', 'о',
    'р', 'с', 'у', 'ф', 'х', 'хъ', 'ы', '-'
]

# Создание таблиц и заполнение ребусов при первом запуске
with app.app_context():
    try:
        # Проверяем, существует ли папка db/
        db_dir = os.path.dirname(DATABASE_PATH)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)  # Создаем папку db/, если её нет

        # Создаем таблицы
        db.create_all()

        # Проверяем, есть ли уже ребусы в базе данных
        if not Riddle.query.first():
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
    except Exception as e:
        print(f"Ошибка при создании базы данных: {e}")

# Маршруты
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
        return redirect(url_for('index'))

    rebuses = Riddle.query.all()
    user = User.query.filter_by(name=session['username']).first()
    solved_rebuses = set(user.solved_rebuses.split(',') if user.solved_rebuses else [])
    current_rebus_id = int(request.args.get('rebus_id', 1))
    current_rebus = next((r for r in rebuses if r.id == current_rebus_id), None)

    hints_left = 3
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'check_answer':
            user_answer = request.form['answer'].strip()
            if user_answer == current_rebus.answer:
                if str(current_rebus.id) not in solved_rebuses:
                    user.score += 20
                    solved_rebuses.add(str(current_rebus.id))
                    user.solved_rebuses = ','.join(solved_rebuses)
                    db.session.commit()
                    session['score'] = user.score
                    flash('Правильно!', 'success')
                return redirect(url_for('game', rebus_id=current_rebus_id + 1))
            else:
                flash('Неправильно. Попробуйте еще раз.', 'danger')
        elif action == 'show_hint':
            hints_left -= 1
            flash(f"Подсказка: {current_rebus.hints}", 'info')

    if current_rebus is None:
        return redirect(url_for('success'))

    return render_template(
        'game.html',
        rebus=current_rebus,
        score=session['score'],
        ossetian_alphabet=ossetian_alphabet,
        hints_left=hints_left
    )

@app.route('/rating')
def rating():
    ratings = User.query.order_by(User.score.desc()).all()
    return render_template('rating.html', ratings=ratings)

@app.route('/success')
def success():
    return render_template('success.html')

if __name__ == '__main__':
    app.run(debug=True)