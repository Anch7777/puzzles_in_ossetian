from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, User, Riddle

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Ключ для работы с сессиями
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///puzzles.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Создание таблиц при первом запуске
with app.app_context():
    db.create_all()

# Буквы осетинского алфавита
ossetian_alphabet = [
    'а', 'æ', 'б', 'г', 'гъ', 'д', 'дж', 'дз', 'ж', 'з', 'и', 'й', 'н', 'о',
    'р', 'с', 'у', 'ф', 'х', 'хъ', 'ы', '-'
]

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

    # Загрузка всех ребусов из базы данных
    rebuses = Riddle.query.all()
    user = User.query.filter_by(name=session['username']).first()
    solved_rebuses = set(user.solved_rebuses.split(',') if user.solved_rebuses else [])
    current_rebus_id = int(request.args.get('rebus_id', 1))
    current_rebus = next((r for r in rebuses if r.id == current_rebus_id), None)

    hints_left = 3  # Оставшиеся подсказки
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