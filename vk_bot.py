import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randint


class VkBot:
    def __init__(self):
        self.listen_for_add = False
        self.root = False
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
        # Команда логина
        if self.COMMANDS[0] in event.text:
            info = event.text.split()
            if len(info) != 3:
                self.write_msg(event.user_id, 'Неправильно ввели команду. Пример: /auth my_login my_password')
                return 'error'
            self.sending_info({'type': 'logs', 'login': info[1], 'password': info[2], 'user_id': event.user_id})
            # Получение ответа result = ответ
            result = 'Good_log'
            type_errors = {'Good_log': 'Вы успешно вышли.',
                           'No_user': 'К сожалению такого пользователя в системе нет.',
                           'Bad_log': 'Неверных логин или пароль. Попробуйте проверить введённыые данные.'}
            self.write_msg(event.user_id, type_errors[result])
            if result == 'Good_log':
                self.root = True
            return type_errors[result]
        elif not self.root:
            self.write_msg(event.user_id, 'Авторизуйтесь (/auth)')

        elif self.COMMANDS[1] == event.text and self.root:
            # ЗАПРОСИТЬ ОТ СЕРВА ДАННЫЕ О ЗАДАЧАх в переменную info

            # Создание текстового ответа
            info = [{'name': 'Учится', 'id': 2, 'date': 11}, {'name': 'Sleep', 'id': 46, 'date': 56}]
            self.write_msg(event.user_id, 'Список ваших задач'+'\n\n'.join(["""
            Название задачи: {}
            Id задачи: {}
            Дедлайн задачи: {}""".format(i['name'], str(i['id']), i['date']) for i in info]))

        elif self.COMMANDS[2] == event.text and self.root:
            # ЗАПРОСИТЬ ОТ СЕРВА ДАННЫЕ О ЗАДАЧАх просроченных в переменную info
            # Создание текстового ответа
            info = [{'name': 'Учится', 'id': 2, 'date': 11}, {'name': 'Sleep', 'id': 46, 'date': 56}]
            self.write_msg(event.user_id, 'Список просроченных задач'+'\n\n'.join(["""
            Название задачи: {}
            Id задачи: {}
            Дедлайн задачи: {}""".format(i['name'], str(i['id']), i['date']) for i in info]))

        elif self.COMMANDS[3] == event.text and self.root:
            self.listen_for_add = True
            self.write_msg(event.user_id, 'Введите название задачи')

        elif self.listen_for_add:
            self.new_task.append(event.text)
            otv = {1: 'Введите описание зачади', 2: 'Введите категорию задачи',
                   3: 'Введите дедлайн задачи(Час:минуты число/месяц/год)', 4: 'Задача создана'}
            self.write_msg(event.user_id, otv[len(self.new_task)])
            if len(self.new_task) == 4:
                self.listen_for_add = False
                self.new_task = []
                # Отправить всё на серв


        else:
            self.write_msg(event.user_id, 'Простите, я не понял.')

    # Функция для получения ключа аутенфикации (на вход ID юзера вк, куда отправить ключ)
    def authentication(self, user_id):
        code = str(randint(10000, 99999))
        self.write_msg(user_id, 'Ваш код: '+code)
        return self.sending_info({'type': 'authentication', 'code': code, 'user_id': user_id})

    # Функция для отправки данных на сервер
    def sending_info(self, info):
        return info
        # !!!Добавить отправку кода на серв


longpoll = VkLongPoll(vk_api.VkApi(token='d746d9d6bd0237b45bc55bd32d55197ceaaa3bb4103dae63d4df1e19063776687a87123e0b94cf6d42dc8'))
users = {}
for event in longpoll.listen():
    # Если пришло новое сообщение
    if event.type == VkEventType.MESSAGE_NEW:
        # Если оно имеет метку для меня( то есть бота)
        if event.to_me:
            if event.user_id not in users:
                users[event.user_id] = VkBot()
            users[event.user_id].new_message(event)
