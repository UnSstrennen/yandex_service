import sqlite3


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
                             password_hash VARCHAR(128),
                             vk_id VARCHAR(100),
                             alice_id VARCHAR(100)
                             )''')
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

    def update_vk(self, username, vk_id):
        cursor = self.connection.cursor()
        print('UPDATE users SET vk_id={} WHERE user_name={}'.format(vk_id, username))
        cursor.execute('UPDATE users SET vk_id = ? WHERE user_name = ?', (str(vk_id), username))
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