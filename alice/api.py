# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals

# Импортируем модули для работы с JSON и логами.
import json
import logging

# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request
app = Flask(__name__)


logging.basicConfig(level=logging.DEBUG)

# Хранилище данных о сессиях.
sessionStorage = {}

# Задаем параметры приложения Flask.
@app.route("/", methods=['POST'])

def main():
# Функция получает тело запроса и возвращает ответ.
    logging.info('Request: %r', request.json)

    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }

    handle_dialog(request.json, response)

    logging.info('Response: %r', response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )


class Tasks:
    def __init__(self):
        pass

    def get_all(self):
        pass

    def get_by_id(self, id):
        pass

    def get_prosroch(self):
        pass


class Auth:
    def __init__(self):
        self.login = ''
        self.password = ''
        self.user_id = ''

    def auth(self, user_id):
        exit_code = 'success'
        if exit_code == 'success':
            self.user_id = user_id
        return exit_code


logging_in = 0
auth = Auth()
tasks = Tasks()


# Функция для непосредственной обработки диалога.
def handle_dialog(req, res):
    global logging_in
    user_id = req['session']['user_id']

    if req['session']['new'] or logging_in == 0:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.

        logging_in = 0

        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }

        res['response']['text'] = 'Добро пожаловать в Индекс.Трекер! Войдите, чтобы начать работу. ' \
                                  'Назоваите свой логин.'
        logging_in = 1
        return

    if logging_in == 1:
        auth.login = req['request']['original_utterance'].lower()
        res['response']['text'] = 'Отлично! Теперь введите пароль.'
        logging_in = 2
        return
    elif logging_in == 2:
        auth.password = req['request']['original_utterance'].lower()
        login_res = auth.auth(req['session']['user_id'])
        if login_res == 'success':
            res['response']['text'] = 'Вы успешно вошли в систему!'
            logging_in = 3
        elif login_res == 'unknown user':
            res['response']['text'] = 'Ошибка! Такого пользователя нет в системе. Начнем заново?'
            logging_in = 0
        elif login_res == 'incorrect password':
            res['response']['text'] = 'Ошибка! Неверный пароль. Начнем заново?'
            logging_in = 0
        return
    # Обрабатываем ответ пользователя.
    user_answer = req['request']['original_utterance']
    if 'пока' in user_answer and 'задачи' in user_answer:
        tasks.get_all()
        res['response']['text'] = "Вот ваши задачи:"
    elif 'задачу' in user_answer:
        try:
            id = int(user_answer.split()[-1])
        except Exception:
            res['response']['text'] = 'Назовите корректный номер задачи'
            return
        tasks.get_by_id(id)
        res['response']['text'] = "Вот информация по задаче № " + str(id)
    elif 'пока' in user_answer and ('срок' in user_answer or 'сроч' in user_answer) and 'задачи' in user_answer:
        tasks.get_prosroch()
        res['response']['text'] = "Вот ваши просроченные задачи:"
    else:
        res['response']['text'] = 'К сожалению, я вас не понял. Повторите запрос'
