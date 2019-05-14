import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from main import VkBot


longpoll = VkLongPoll(
    vk_api.VkApi(token='d746d9d6bd0237b45bc55bd32d55197ceaaa3bb4103dae63d4df1e19063776687a87123e0b94cf6d42dc8'))
users = {}
for event in longpoll.listen():
    # Если пришло новое сообщение
    if event.type == VkEventType.MESSAGE_NEW:
        # Если оно имеет метку для меня( то есть бота)
        if event.to_me:
            if event.user_id not in users:
                users[event.user_id] = VkBot()
            print(event.user_id, type(event.user_id))
            users[event.user_id].new_message(event)