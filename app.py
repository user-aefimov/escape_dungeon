import os
from dotenv import load_dotenv

# Что произойдет без load_dotenv()?
# Без загрузки .env
# os.environ.get('SECRET_KEY')  # → None
# # Тогда в Config будет использовано значение по умолчанию:
# SECRET_KEY = None or 'default_key'  # → 'default_key'

load_dotenv('.env', override=True)  # Принудительная перезагрузка # Загружает .env
# Теперь SECRET_KEY будет браться из .env

from flask import Flask, render_template, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, NumberRange
from config import Config

app = Flask(__name__, static_folder='static')

#  Загружаем конфигурацию из класса `Config,
#  При этом все переменные класса `Config` (которые написаны
#  в верхнем регистре) будут скопированы в `app.config`.
app.config.from_object(Config)
rooms = {
        "Подземелье": {
            "description": "Вы в сыром, темном подземелье. Воздух спертый и влажный.",
            "image": "dungeon.jpg",
            "exits": {"восток": "Коридор"}
        },
        "Коридор": {
            "description": "Длинный каменный коридор с факелами на стенах.",
            "image": "corridor.jpg",
            "exits": {"запад": "Подземелье", "север": "Холл", "восток": "Оружейная"}
        },
        "Холл": {
            "description": "Просторный зал с высокими потолками. Видны двери в разные стороны.",
            "image": "hall.jpg",
            "exits": {"юг": "Коридор", "запад": "Спальня", "восток": "Кухня", "север": "Балкон"}
        },
        "Оружейная": {
            "description": "Комната, заполненная старинным оружием и доспехами.",
            "image": "armory.jpg",
            "exits": {"запад": "Коридор"}
        },
        "Кухня": {
            "description": "Запах старой еды и грязной посуды. Здесь явно давно никто не готовил.",
            "image": "kitchen.jpg",
            "exits": {"запад": "Холл"}
        },
        "Спальня": {
            "description": "Аккуратно застеленная кровать. Здесь явно давно никто не спал.",
            "image": "bedroom.jpg",
            "exits": {"восток": "Холл"}
        },
        "Балкон": {
            "description": "Вы на балконе! Свежий воздух и вид на окрестности. Вы свободны!",
            "image": "balcony.jpg",
            "exits": {}
        }
    }

def get_next_room(current_room, direction, steps):
    """Определяет следующую комнату на основе текущего положения и направления"""
    # Получаем данные текущей комнаты
    room_data = rooms.get(current_room, {})
    
    # Проверяем доступность направления
    exits = room_data.get('exits', {})
    
    if direction in exits:
        # В этой реализации шаги не влияют на перемещение
        # (можно добавить логику для многошаговых перемещений)
        return exits[direction]
    
    return None

# Форма для перемещения
class MoveForm(FlaskForm):
    direction = SelectField('Направление', choices=[
        ('север', 'Север'),
        ('юг', 'Юг'),
        ('запад', 'Запад'),
        ('восток', 'Восток')
    ], validators=[DataRequired()])
    steps = IntegerField('Шаги', validators=[
        DataRequired(message="Укажите количество шагов"),
        NumberRange(min=1, max=1, message="От 1 до 10 шагов")
    ], default=1)
    submit = SubmitField('В путь!')

# Форма для начала игры
class StartForm(FlaskForm):
    player_name = StringField('Ваше имя', validators=[
        DataRequired(message="Введите ваше имя"),
    ])
    submit = SubmitField('Начать игру')

@app.route('/check_key')
def show_secret():
    # Получаем ключ разными способами для проверки
    from_env = os.environ.get('SECRET_KEY')
    from_app = app.config['SECRET_KEY']
    
    return f"""
    From environment: {from_env}<br>
    From app config: {from_app}<br>
    Length: {len(from_app)} characters
    """

@app.route("/", methods=['GET', 'POST'])
def index():
    session.pop('player_name', None)  # Удаляем имя игрока
    form = StartForm()
    if form.validate_on_submit():
        session['current_room'] = "Подземелье"
        session['player_name'] = form.player_name.data
        return redirect(url_for('room'))
    return render_template('index.html', form=form)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/room', methods=['GET', 'POST'])
def room():
    # Проверяем наличие текущей комнаты
    if 'current_room' not in session:
        return redirect(url_for('index'))
    
    current_room = session['current_room']
     # Используем локальный словарь комнат вместо конфига
    room_data = rooms.get(current_room, {})

    form = MoveForm()

    if form.validate_on_submit():
        direction = form.direction.data
        steps = form.steps.data

        # Определяем новую комнату с учетом шагов
        new_room = get_next_room(current_room, direction, steps)

        # Проверка доступности направления
        if new_room:
            session['current_room'] = new_room
            flash(f'Вы прошли {steps} шагов на {direction} и попали в {new_room}!', 'success')
            return redirect(url_for('room'))
        else:
            flash(f"На {direction} нет выхода!", 'danger')

    return render_template('room.html',
                           room=current_room,
                           room_data=room_data,
                           form=form,
                           player_name=session.get('player_name', 'Игрок'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

        