import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randint
from flask_wtf import FlaskForm
from db import UsersModel, TasksModel, DB
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, FileField, BooleanField
from wtforms.validators import DataRequired
from flask import Flask, url_for, request, render_template, redirect, session


root = False


class VkBot:
    def __init__(self):
        global root
        self.listen_for_add = False
        self.root = root
        self.tasks = [{'name': 'Поесть', 'id': 34, 'date': '11 мая'},
                      {'name': 'Купить подарок', 'id': 46, 'date': ''}]
        self.new_task = []
        # Токен группы
        TOKEN = 'd746d9d6bd0237b45bc55bd32d55197ceaaa3bb4103dae63d4df1e19063776687a87123e0b94cf6d42dc8'
        self.VK = vk_api.VkApi(token=TOKEN)

        self.COMMANDS = ["/auth", "/task", "/expired_task", "/add_task", "/delegate_task", ""]

    # Функция для отправки сообщения (Id юзера вк, куда отправить сообщение и текст сообщения)
    def write_msg(self, user_id, message):
        self.VK.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randint(0, 999999)})

    # Функция обработки сообщения (на вход евент)
    def new_message(self, event):
        global root
        # Команда логина
        print(event.user_id)
        if event.text.startswith(self.COMMANDS[0]):
            info = event.text.split()
            if len(info) != 3:
                self.write_msg(event.user_id, 'Неправильно ввели команду. Пример: /auth my_login my_password')
                return 'error'

            # Получение ответа result = ответ
            result = auth({'type': 'logs', 'login': info[1], 'password': info[2], 'user_id': event.user_id})
            type_errors = {'Good_log': 'Вы успешно вoшли.',
                           'No_user': 'К сожалению такого пользователя в системе нет.',
                           'Bad_log': 'Неверный логин или пароль. Попробуйте проверить введённые данные.'}
            self.write_msg(event.user_id, type_errors[result])
            if result == 'Good_log':
                self.root = True
                root = True
                ses('username', info[1])
                # session['vk_id'] = event.user_id
                um.update_vk(info[1], event.user_id)
                #vreturn redirect('/confirm_code')
            return type_errors[result]
        elif event.text == 'root':
            self.write_msg(event.user_id, str(root))
        elif not self.root:
            self.write_msg(event.user_id, 'Авторизуйтесь (/auth)')

        elif self.COMMANDS[1] == event.text and self.root:
            # ЗАПРОСИТЬ ОТ СЕРВА ДАННЫЕ О ЗАДАЧАх в переменную info

            # Создание текстового ответа
            self.write_msg(event.user_id, 'Список ваших задач'+'\n\n'.join(["""
            Название задачи: {}
            Id задачи: {}
            Дедлайн задачи: {}""".format(i['name'], str(i['id']), i['date']) for i in self.tasks]))

        elif self.COMMANDS[2] == event.text and self.root:
            # ЗАПРОСИТЬ ОТ СЕРВА ДАННЫЕ О ЗАДАЧАх просроченных в переменную info
            # Создание текстового ответа
            info = [{'name': 'Выучить алгебру', 'id': 2, 'date': '11 апреля'},
                    {'name': 'Выспаться', 'id': 1, 'date': '1 мая'}]
            self.write_msg(event.user_id, 'Список просроченных задач'+'\n\n'.join(["""
            Название задачи: {}
            Id задачи: {}
            Дедлайн задачи: {}""".format(i['name'], str(i['id']), i['date']) for i in info]))

        elif self.COMMANDS[3] == event.text and self.root:
            self.listen_for_add = True
            self.write_msg(event.user_id, 'Введите название задачи')

        elif event.text.startswith(self.COMMANDS[4]):
            info = event.text.split()
            if len(info) != 3:
                self.write_msg(event.user_id, 'Неправильно ввели команду. Пример: /delegate_task id_task user_name')
                return 'error'

            # Получение ответа result = ответ
            result = auth({'type': 'retasks', 'id_task': info[1], 'user_name': info[2], 'user_id': event.user_id})
            type_errors = {'Good': 'Всё хорошо.',
                           'Bad': 'Упс. Что-то не так'}
            self.write_msg(event.user_id, type_errors[result])

        elif self.listen_for_add:
            self.new_task.append(event.text)
            otv = {1: 'Введите описание задачи', 2: 'Введите категорию задачи',
                   3: 'Введите дедлайн задачи', 4: 'Задача создана'}
            self.write_msg(event.user_id, otv[len(self.new_task)])
            if len(self.new_task) == 4:
                self.listen_for_add = False
                self.tasks.append({'name': self.new_task[0], 'id': str(randint(1, 9)), 'date': self.new_task[3]})
                self.new_task = []
                # Отправить всё на серв
        else:
            self.write_msg(event.user_id, 'Простите, я не понял.')

    # Функция для получения ключа аутенфикации (на вход ID юзера вк, куда отправить ключ)
    def authentication(self, user_id):
        code = str(randint(10000, 99999))
        self.write_msg(user_id, 'Ваш код: '+code)
        return auth({'type': 'authentication', 'code': code, 'user_id': user_id})



class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class ReginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_confirm = PasswordField('Подтвредите пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class CodeConfirmForm(FlaskForm):
    code = StringField('Введите код', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')


def auth(dit):
    global confirm_code
    print('in auth')
    if dit['type'] == 'logs':
        user_model = UsersModel(db.get_connection())
        exists = user_model.exists(dit['login'], dit['password'])
        if dit['login'] not in user_model.get_logins():
            return 'No_user'
        elif not exists[0]:
            return 'Bad_log'
        else:
            # session['username'] = dit['login']
            # session['user_id'] = exists[1]
            return 'Good_log'
    elif dit['type'] == 'authentication':
        confirm_code = dit['code']
        return redirect('/confirm_code')


class AliceHandler:
    def __init__(self):
        pass


app = Flask(__name__)
app.config['SECRET_KEY'] = '1323232313swdsds'

auth_code = ''


db = DB()
um = UsersModel(db.get_connection())
um.init_table()
um.insert('NIKITA', '123')
tasks_model = TasksModel(db.get_connection())
tasks_model.init_table()
tasks_model.insert('zadacha1', 'content', 'сложная задача', '1; 2; 3', 'срочно; обязательно',
                   'только начал', '1', '2003-09-23')

@app.route('/')
@app.route('/index')
def index():
    if 'username' not in session:
        return redirect('/login')
    #n = TasksModel(db.get_connection())
    #tasks = n.get_all(session['user_id'])
    return render_template('index.html', username=session['username'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    user_name = form.username.data
    password = form.password.data
    user_model = UsersModel(db.get_connection())
    exists = user_model.exists(user_name, password)
    if user_name not in user_model.get_logins() and user_name is not None:
        return render_template('login.html', title='Авторизация', form=form, is_correct_password=True,
                               is_known=False)
    if exists[0] or password is None:
        if form.validate_on_submit():
            session['username'] = user_name
            session['user_id'] = exists[1]
            user_id = exists[1]

            return redirect("/index")
    else:
        return render_template('login.html', title='Авторизация', form=form, is_correct_password=False,
                               is_known=True)
    return render_template('login.html', title='Авторизация', form=form, is_correct_password=True,
                           is_known=True)


@app.route('/register', methods=['GET', 'POST'])
def register():
    session.pop('username', 0)
    session.pop('user_id', 0)
    form = ReginForm()
    user_name = form.username.data
    password = form.password.data
    password_confirm = form.password_confirm.data
    user_model = UsersModel(db.get_connection())
    if user_name in user_model.get_logins():
        return render_template('register.html', form=form, correct=False, correct_p=True)
    if password_confirm != password:
        return render_template('register.html', form=form, correct_p=False, correct=True)
    if form.validate_on_submit():
        user_model.insert(user_name, password)
        return redirect("/login")
    return render_template('register.html', title='Регистрация', form=form, correct=True, correct_p=True)

@app.route('/confirm_code', methods=['GET', 'POST'])
def confirm_code():
    global confirm_code
    form = CodeConfirmForm()
    code = form.code.data
    confirm_code = VkBot.authentication(  )
    if code == confirm_code:
        redirect('/index')
    else:
        redirect('/login')


if __name__ == '__main__':
    app.run(port=80, host='127.0.0.1')
