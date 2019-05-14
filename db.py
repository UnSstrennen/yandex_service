import sqlite3
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, FileField, BooleanField
from wtforms.validators import DataRequired
from flask import Flask, url_for, request, render_template, redirect, session


app = Flask(__name__)
app.config['SECRET_KEY'] = '1323232313swdsds'


auth_code = ''


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


class DB:
    def __init__(self):
        conn = sqlite3.connect('app.db', check_same_thread=False)
        self.conn = conn

    def get_connection(self):
        return self.conn

    def __del__(self):
        self.conn.close()


class UsersModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             user_name VARCHAR(50),
                             password_hash VARCHAR(128))''')
        cursor.close()
        self.connection.commit()

    def exists(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ? AND password_hash = ?",
                       (user_name, password_hash))
        row = cursor.fetchone()
        return (True, row[0]) if row else (False,)

    def get(self, user_name):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ?", (user_name,))
        row = cursor.fetchone()
        return row

    def get_from_id(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (str(user_id),))
        row = cursor.fetchone()
        return row

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return rows

    def get_logins(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        a = []
        for i in rows:
            a.append(i[1])
        return a

    def insert(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users 
                          (user_name, password_hash) 
                          VALUES (?,?)''', (user_name, password_hash))
        cursor.close()
        self.connection.commit()



class TasksModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS tasks 
                            (task_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             title VARCHAR(100),
                             content VARCHAR (1000),
                             comments VARCHAR (1000),
                             user_ids VARCHAR(200), 
                             categories VARCHAR(200),
                             stages VARCHAR(500),
                             author INTEGER, 
                             dat DATE
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, title, content, com, ids, cats, stages, aut, d):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO tasks
                          (title, content, comments, user_ids, categories, stages, author, dat) 
                          VALUES (?,?,?,?,?,?,?,?)''', (title, content, com, ids, cats, stages, aut, d,))
        cursor.close()
        self.connection.commit()

    def get(self, task_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (str(task_id),))
        row = cursor.fetchone()
        return row

    def add_ids(self, user_id, task_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (str(task_id),))
        row = cursor.fetchone()
        ids = row[4] + '; ' + str(user_id)
        cursor.execute("UPDATE tasks SET users_id = ? WHERE id = ?", (ids, str(task_id),))

    def get_all(self, user_ids=None):
        cursor = self.connection.cursor()
        if user_ids:
            cursor.execute("SELECT * FROM tasks WHERE user_ids = ?",
                           (str(user_ids),))
        else:
            cursor.execute("SELECT * FROM tasks")
        rows = cursor.fetchall()
        return rows

    def delete(self, task_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM tasks WHERE task_id = ?''', (str(task_id)))
        cursor.close()
        self.connection.commit()


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
            # confirm_code = VkBot.authentication()
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
    if code == confirm_code:
        redirect('/index')
    else:
        redirect('/login')


def auth(dit):
    global confirm_code
    if dit['type'] == 'logs':
        user_model = UsersModel(db.get_connection())
        exists = user_model.exists(dit['login'], dit['password'])
        if dit['login'] not in user_model.get_logins():
            return 'No_user'
        elif not exists[0]:
            return 'Bad_logs'
        else:
            session['username'] = dit['login']
            session['user_id'] = exists[1]
            return 'Good_log'
    elif dit['type'] == 'authentication':
        pass


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
