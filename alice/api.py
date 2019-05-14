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
        res['response']['buttons'] = get_suggests(user_id)
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
    if 'пока' in user_answer and 'задач' in user_answer:
        res['response']['text'] = "Вот ваши задачи:"


# Функция возвращает две подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    # Если осталась только одна подсказка, предлагаем подсказку
    # со ссылкой на Яндекс.Маркет.
    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=слон",
            "hide": True
        })

    return suggests