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
			# хранение картинок, ответов, подсказок на ребусы
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
# главная страница
@app.route('/')
def index():
	return render_template('index.html')


# страница правил
@app.route('/rules')
def rules():
	return render_template('rules.html')


# войти
@app.route('/login', methods=['GET', 'POST'])
def login():
	#  ввод логина, пароля

	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		user = User.query.filter_by(name=username, password=password).first()
		# если введены верные данные
		if user:
			session['username'] = user.name
			session['score'] = user.score
			session['solved_rebuses'] = user.solved_rebuses.split(',') if user.solved_rebuses else []
			return redirect(url_for('game'))
		else:
			flash('Неверное имя пользователя или пароль.', 'danger')
	return render_template('login.html')


# зарегистрироваться
@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		# если уже существует
		if User.query.filter_by(name=username).first():
			flash('Имя пользователя уже занято.', 'danger')
		# создание новой сессии для пользователя
		# сохранение сессии
		else:
			new_user = User(
				name=username,
				password=password,
				score=session.get('score', 0),
				solved_rebuses=','.join(session.get('solved_rebuses', []))
			)
			db.session.add(new_user)
			db.session.commit()
			session['username'] = username
			return redirect(url_for('game'))
	return render_template('register.html')


# выйти
@app.route('/logout')
def logout():
	# если пользователь зарегистрирован, прогресс сохраняется
	# у гостя сессия очищается
	if 'username' in session and session['username'] != 'Guest':
		user = User.query.filter_by(name=session['username']).first()
		if user:
			user.score = session['score']
			user.solved_rebuses = ','.join(session.get('solved_rebuses', []))
			db.session.commit()
	session.clear()
	return redirect(url_for('index'))


# сама игра
@app.route('/game', methods=['GET', 'POST'])
def game():
	# Инициализация данных для гостя или загрузка данных пользователя
	if 'username' not in session:
		session['username'] = 'Guest'
		session['score'] = session.get('score', 0)
		session['solved_rebuses'] = session.get('solved_rebuses', [])
		session['current_rebus_id'] = session.get('current_rebus_id', 1)  # Инициализация текущего ID ребуса
	else:
		user = User.query.filter_by(name=session['username']).first()
		if user:
			session['score'] = user.score
			session['solved_rebuses'] = user.solved_rebuses.split(',') if user.solved_rebuses else []
			session['current_rebus_id'] = session.get('current_rebus_id', 1)

	# Получаем текущий ID ребуса из параметров запроса или сессии
	current_rebus_id = int(request.args.get('rebus_id', session['current_rebus_id']))
	session['current_rebus_id'] = current_rebus_id

	# Проверка на уже решенные ребусы
	while str(current_rebus_id) in session['solved_rebuses']:
		current_rebus_id += 1

	session['current_rebus_id'] = current_rebus_id

	rebuses = Riddle.query.all()
	# отображение текущего ребуса
	current_rebus = next((r for r in rebuses if r.id == current_rebus_id), None)

	# Если все ребусы решены
	if current_rebus is None:
		return redirect(url_for('success'))
	# подсказок осталось

	hints_left_key = f'hints_left_{current_rebus_id}'
	# сколько подсказок осталось
	hints_left = session.get(hints_left_key, 3)

	# при вводе ответа
	if request.method == 'POST':
		action = request.form.get('action')
		# при нажатии проверить ответ
		if action == 'check_answer':
			user_answer = request.form['answer'].strip()
			if user_answer == current_rebus.answer:
				# если ребус не был решен ранее
				if str(current_rebus_id) not in session['solved_rebuses']:
					new_score = min(session['score'] + 20, 100)
					session['score'] = new_score
					session['solved_rebuses'].append(str(current_rebus_id))
					# Обновляем данные в БД только для авторизованных пользователей
					if session['username'] != 'Guest':
						user = User.query.filter_by(name=session['username']).first()
						if user:
							user.score = new_score
							user.solved_rebuses = ','.join(session['solved_rebuses'])
							db.session.commit()
					flash('Правильно!', 'success')
				current_rebus_id += 1
				session['current_rebus_id'] = current_rebus_id
				# Переход к следующему нерешенному ребусу
				while str(current_rebus_id) in session['solved_rebuses']:
					current_rebus_id += 1
				session['current_rebus_id'] = current_rebus_id
				return redirect(url_for('game', rebus_id=current_rebus_id))
			else:
				flash('Неправильно. Попробуйте еще раз.', 'danger')

		# при нажатии на подсказку
		elif action == 'show_hint':
			if hints_left > 0:
				hints_left -= 1
				session[hints_left_key] = hints_left
				# отображение
				flash(f"Подсказка: {current_rebus.hints}", 'info')
			else:
				# если закончились
				flash("У вас закончились подсказки для этого ребуса!", 'warning')

	return render_template(
		'game.html',
		rebus=current_rebus,
		score=session['score'],
		ossetian_alphabet=ossetian_alphabet,
		hints_left=hints_left
	)


# рейтинг
@app.route('/rating')
def rating():
	ratings = User.query.order_by(User.score.desc()).all()
	return render_template('rating.html', ratings=ratings)


# при решении всех ребусов
@app.route('/success')
def success():
	if 'username' in session and session['username'] != 'Guest':
		# Если пользователь авторизован, показываем стандартное сообщение
		return render_template('success.html')
	else:
		# Если пользователь - гость, предлагаем зарегистрироваться
		return render_template('success.html', show_register_prompt=True)


@app.route('/register_prompt/<int:rebus_id>', methods=['GET', 'POST'])
def register_prompt(rebus_id):
	if request.method == 'POST':
		action = request.form.get('action')
		if action == 'continue_as_guest':
			# Продолжаем игру с того же места
			print(f"Redirecting to game with rebus_id={rebus_id}")  # Отладочная информация
			return redirect(url_for('game', rebus_id=rebus_id))
	return render_template('register_prompt.html', rebus_id=rebus_id)


if __name__ == '__main__':
	app.run(debug=True)
