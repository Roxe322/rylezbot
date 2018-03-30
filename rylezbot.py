# -*- coding=UTF-8 -*-

import operator
import requests
import time
import os


class BotHandler:
    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_me(self):
        method = 'getMe'
        resp = requests.get(self.api_url + method)
        result_json = resp.json()['result']
        return result_json

    def get_updates(self, offset=None, timeout=1):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        if not 'result' in resp.json():
            print(u"!!! ATTENTION !!!\n")
            print(resp.json())
            exit()
        result_json = resp.json()['result']
        return result_json

    def get_last_update(self, offset=None, timeout=1):
        get_result = self.get_updates(offset, timeout)

        if len(get_result) > 0:
            return get_result[0]
        return None

    def send_message(self, chat_id, text, parse_mode='markdown', reply_to_message_id=None):
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode}
        if not reply_to_message_id is None:
            params['reply_to_message_id'] = reply_to_message_id
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def delete_message(self, chat_id, message_id):
        params = {'chat_id': chat_id, 'message_id': message_id}
        method = 'deleteMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_chat_member(self, chat_id, user_id):
        method = 'getChatMember'
        params = {'chat_id': chat_id, 'user_id': user_id}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def restrict_chat_member(self, chat_id, user_id, until_date,
                      can_send_messages,
                      can_send_media_messages,
                      can_send_other_messages,
                      can_add_web_page_previews):
        params = {'chat_id': chat_id,
                  'user_id': user_id,
                  'until_date': until_date,
                  'can_send_messages': can_send_messages,
                  'can_send_media_messages': can_send_media_messages,
                  'can_send_other_messages': can_send_other_messages,
                  'can_add_web_page_previews': can_add_web_page_previews}
        method = 'restrictChatMember'
        resp = requests.post(self.api_url + method, params)
        return resp


class Chat:
    def __init__(self):
        self.stats = dict()
        self.users = dict()
        self.is_restricting = False
        self.limit = 5
        self.is_chatbot = False

    def get_user_mention(self, user):
        self.users[user['id']] = user
        if 'username' in user:
            return "@" + user['username']
        elif 'first_name' in user:
            return user['first_name']


bot = BotHandler(os.environ['TOKEN'])
bot_info = None
chats = dict()
admins = [145967250, 126751055, 172210439]
one_day = 86400


def restricting_mode(chat_id, message):
    author = message['from']
    sticker = message['sticker']
    author_name = chats[chat_id].get_user_mention(author)

    if not author['id'] in chats[chat_id].stats:
        chats[chat_id].stats[author['id']] = 1
    else:
        chats[chat_id].stats[author['id']] += 1

    if chats[chat_id].limit - chats[chat_id].stats[author['id']] > 0:
        # bot.send_message(chat_id, u"У {} осталось {} сообщений".format(author_name, chats[chat_id].limit - chats[chat_id].stats[author['id']]))
        if chats[chat_id].limit - chats[chat_id].stats[author['id']] == 1:
            bot.send_message(chat_id, u"Будь осторожен, {}, ведь у тебя остался всего 1 стикер!".format(author_name))
    else:
        result = bot.restrict_chat_member(chat_id, author['id'], 604800, True, True, False, True)
        if result:
            bot.send_message(chat_id, u"{} теперь не может присылать стикеры неделю!".format(author_name))



def main():
    new_offset = None
    was_previous_sticker = False

    global limit, is_restricting, is_chatbot

    bot_info = bot.get_me()

    while True:
        t = time.gmtime()
        if t.tm_hour == 13 and t.tm_min < 1:
            stats.clear()
            continue

        last_update = bot.get_last_update(new_offset)

        if isinstance(last_update, list):
            last_update_id = last_update[0]['update_id']
        elif last_update is None:
            continue
        else:
            last_update_id = last_update['update_id']

        if 'message' in last_update and 'from' in last_update['message']:
            message = last_update['message']
            author = message['from']
            chat_id = message['chat']['id']

            if not chat_id in chats.keys():
                chats[chat_id] = Chat()

            if 'new_chat_members' in message:
                if chats[chat_id].is_chatbot:
                    bot.send_message(chat_id, u"Новые коммунисты подоспели! _Поздоровайся с дядюшкой Сталиным..._", reply_to_message_id=message['message_id'])
                # else:
                #     welcome_text = u"Привет! Я бот, который *ограничивает ракование стикерами*. Также я могу играть роль чатбота. "
                #     if chats[chat_id].is_restricting:
                #         welcome_text += u"Сейчас я в злом режиме, поэтому тебе доступно всего {} стикеров. *Будь осторожен!* ".format(limit)
                #     else:
                #         welcome_text += u"Сейчас я добрый, поэтому все стикеры, идущие подряд после одного *будут удаляться.* "
                #     bot.send_message(chat_id, welcome_text, reply_to_message_id=message['message_id'])

            if 'left_chat_member' in message:
                if chats[chat_id].is_chatbot:
                    bot.send_message(chat_id, u"_Путен вышел из чата..._", reply_to_message_id=message['message_id'])

            if 'text' in message:
                message_text = message['text'].lower()

                if (u"далер" in message_text or
                    u"дaлеp" in message_text or
                    u"дaлер" in message_text or
                    u"далеp" in message_text or
                    u"дaлep" in message_text or
                    u"далер" in message_text or
                    u"дилдер" in message_text or
                    u"даунлер" in message_text or
                    u"d a l e r" in message_text or
                    u"daler" in message_text or
                    u"dalertalk" in message_text or
                    u"днолер" in message_text):
                    bot.delete_message(chat_id, message['message_id'])
                    # bot.restrict_chat_member(chat_id, author['id'], 3 * one_day, False, False, False, False)
                    # bot.send_message(chat_id, u"Не надо так шутить, {}. Теперь ты не можешь писать сообщения 3 дня.".format(chats[chat_id].get_user_mention(author)), reply_to_message_id=message['message_id'])

                if chats[chat_id].is_chatbot:
                    if ('reply_to_message' in message and
                        'from' in message['reply_to_message'] and
                        message['reply_to_message']['from']['id'] == bot_info['id']):
                            if u"пошел нахуй" in message_text:
                                bot.send_message(chat_id, u"сам иди, путен", reply_to_message_id=message['message_id'])
                            else:
                                bot.send_message(chat_id, u"пошел нахуй, пидор", reply_to_message_id=message['message_id'])

                    elif u"сталин" in message_text:
                        if (u"тупой"  in message_text or
                            u"пидор"  in message_text or
                            u"плохой" in message_text or
                            u"ебанутый" in message_text):
                            bot.send_message(chat_id, u"сам такой", reply_to_message_id=message['message_id'])
                        else:
                            bot.send_message(chat_id, u"Вызывали? Надеюсь, на расстрел Bohemian Coding", reply_to_message_id=message['message_id'])

                    elif (u"коммунизм" in message_text or
                          u"коммунист" in message_text or
                          u"фигма"     in message_text):
                        bot.send_message(chat_id, u"Молодца!", reply_to_message_id=message['message_id'])

                if message_text.startswith('/start'):
                    bot.send_message(
                        chat_id,
                        u'Бот, который поможет сохранить покой в чате (нет).\n@handlerugbots\nПо вопросам обращайтесь к @handlerug'
                    )

                elif message_text.startswith('/stats'):
                    if chats[chat_id].is_restricting:
                        stats_text = u'*Статистика по отправителям стикеров:*\n\n'
                        i = 1
                        # for key, value in sorted(stats, key=stats.get, reverse=True):
                        for key, value in sorted(chats[chat_id].stats.iteritems(), key=operator.itemgetter(1), reverse=True):
                        # for key, value in stats.items():
                            stats_text += u"{}. {} — {}/{} стикеров".format(i, chats[chat_id].users[key], value, chats[chat_id].limit)
                            if chats[chat_id].limit - value <= 0:
                                stats_text += u' (ограничен)'
                            stats_text += '\n'
                            i += 1
                        bot.send_message(chat_id, stats_text)
                    else:
                        bot.send_message(chat_id, u'В данный момент *нет статистики*. Чтобы включить статистику, переключите бота в *ограничивающий режим*.')

                elif message_text.startswith('/limit'):
                    command_params = message_text.split()[1:]
                    if len(command_params) > 0:
                        if bot.get_chat_member(chat_id, author['id'])['status'] in (u"creator", u"administrator"):
                            chats[chat_id].limit = int(command_params[0])
                            bot.send_message(chat_id, u'Лимит стикеров установлен в *{}* стикеров.'.format(chats[chat_id].limit))
                        else:
                            if chats[chat_id].is_chatbot:
                                bot.send_message(chat_id, u'пошел нахуй')
                            else:
                                bot.send_message(chat_id, u'Вы *не администратор* данного чата.')
                    else:
                        bot.send_message(chat_id, u'В данный момент лимит стикеров установлен в *{}* стикеров.'.format(chats[chat_id].limit))

                elif message_text.startswith('/restricting_mode'):
                    command_params = message_text.split()[1:]
                    if len(command_params) > 0:
                        if bot.get_chat_member(chat_id, author['id'])['status'] in (u"creator", u"administrator"):
                            if command_params[0] == u'1':
                                chats[chat_id].is_restricting = True
                                bot.send_message(chat_id, u'Ограничивающий режим *включен*.')
                            elif command_params[0] == u'0':
                                chats[chat_id].is_restricting = False
                                bot.send_message(chat_id, u'Ограничивающий режим *выключен*.')
                        else:
                            if chats[chat_id].is_chatbot:
                                bot.send_message(chat_id, u'пошел нахуй')
                            else:
                                bot.send_message(chat_id, u'Вы *не администратор* данного чата.')
                    else:
                        if chats[chat_id].is_restricting:
                            bot.send_message(chat_id, u'В данный момент ограничивающий режим *включен*.')
                        else:
                            bot.send_message(chat_id, u'В данный момент ограничивающий режим *выключен*.')

                elif message_text.startswith('/enable_chatbot'):
                    command_params = message_text.split()[1:]
                    if len(command_params) > 0:
                        if bot.get_chat_member(chat_id, author['id'])['status'] in (u"creator", u"administrator"):
                            if command_params[0] == u'1':
                                chats[chat_id].is_chatbot = True
                                bot.send_message(chat_id, u'Режим чатбота *включен*.')
                            elif command_params[0] == u'0':
                                chats[chat_id].is_chatbot = False
                                bot.send_message(chat_id, u'Режим чатбота *выключен*.')
                        else:
                            if chats[chat_id].is_chatbot:
                                bot.send_message(chat_id, u'пошел нахуй')
                            else:
                                bot.send_message(chat_id, u'Вы *не администратор* данного чата.')
                    else:
                        if chats[chat_id].is_chatbot:
                            bot.send_message(chat_id, u'В данный момент режим чатбота *включен*.')
                        else:
                            bot.send_message(chat_id, u'В данный момент режим чатбота *выключен*.')

                was_previous_sticker = False

            elif 'sticker' in message:

                if bot.get_chat_member(chat_id, author['id'])['status'] in (u"creator", u"administrator"):
                    was_previous_sticker = True
                    new_offset = last_update_id + 1
                    continue

                sticker = message['sticker']
                if 'set_name' in sticker:
                    if sticker['set_name'] != u"uxuitools":
                        if chats[chat_id].is_restricting:
                            restricting_mode(chat_id, message)
                        else:
                            if was_previous_sticker:
                                bot.delete_message(chat_id, message['message_id'])
                        was_previous_sticker = True
                    else:
                        sid = sticker['file_id']
                        if chats[chat_id].is_chatbot:
                            if sid == u"CAADAgADIwEAAk8RjgfLh5b5maYsTwI":       # Фигма красавица
                                bot.send_message(chat_id, u"Не спорю", reply_to_message_id=message['message_id'])
                            elif sid == u"CAADAgADJAEAAk8RjgevCkhhmYjk0wI":     # Сделай через компоненты
                                bot.send_message(chat_id, u"Символы круче", reply_to_message_id=message['message_id'])
                            elif sid == u"CAADAgADJQEAAk8RjgfATMinRl7uFgI":     # Xd ХУЕТА
                                bot.send_message(chat_id, u"Photoshop ПАРАША", reply_to_message_id=message['message_id'])
                            elif sid == u"CAADAgADJgEAAk8RjgehM2IOMJjr5AI":     # Xd Выбор даунов 2018
                                bot.send_message(chat_id, u"Ваши кечи и вигмы рядом не стоят", reply_to_message_id=message['message_id'])
                            elif sid == u"CAADAgADJwEAAk8RjgdeVJ-xqx7HawI":     # Как поставить шрифт на Фигму?
                                bot.send_message(chat_id, u"Надо было фотошоп юзать", reply_to_message_id=message['message_id'])
                            elif sid == u"CAADAgADKAEAAk8Rjgen7wZfuvRNdAI":     # Скетч Зато у нас плагины
                                bot.send_message(chat_id, u"Забыл про новое API Фигмы?", reply_to_message_id=message['message_id'])
                            elif sid == u"CAADAgADKQEAAk8Rjgfx03AK60ZlhQI":     # Ps Как не нужен?
                                bot.send_message(chat_id, u"Я делаю сайты в фотошопе", reply_to_message_id=message['message_id'])
                            elif sid == u"CAADAgADKgEAAk8RjgdprZRwY6o37QI":     # Ps ПАРАША
                                bot.send_message(chat_id, u"Xd ХУЕТА", reply_to_message_id=message['message_id'])
                            elif sid == u"CAADAgADKwEAAk8RjgcXRy75n55RtgI":     # Фигма Плагины не нужны
                                bot.send_message(chat_id, u"А теперь вспомни про API Фигмы и скажи это еще раз", reply_to_message_id=message['message_id'])
                            elif sid == u"CAADAgADLAEAAk8Rjgfmz0Yq9fgQ_wI":     # Скетч Craft опять повис...
                                bot.send_message(chat_id, u"Инвижон топ", reply_to_message_id=message['message_id'])
                            elif sid == u"CAADAgADLQEAAk8Rjgf3z3_xs08aogI":     # Скетч Макет 600 мегабайт
                                bot.send_message(chat_id, u"В фигме все в облаке", reply_to_message_id=message['message_id'])
                            elif sid == u"CAADAgADLgEAAk8RjgcpBbljvHJzGQI":     # Ps Я UX/UI дизайнер
                                bot.send_message(chat_id, u"Это не UI, это UX", reply_to_message_id=message['message_id'])
                            elif sid == u"CAADAgADLwEAAk8RjgcIlPRc2NZwYQI":     # Фигма Пропал интернет
                                bot.send_message(chat_id, u"А теперь вспомни про автономность фотошопа", reply_to_message_id=message['message_id'])
                            elif sid == u"CAADAgADMAEAAk8RjgeWfxkOB5cAAWkC":    # Скетч На винде не работает!
                                bot.send_message(chat_id, u"Фигма в браузере B)", reply_to_message_id=message['message_id'])
                            elif sid == u"CAADAgADMQEAAk8RjgeX9OVVKLRsiwI":     # Как конвертировать Ps в Скетч?
                                bot.send_message(chat_id, u"Кароч ножимаешь на пунт файл и экспорт", reply_to_message_id=message['message_id'])
                            elif sid == u"CAADAgADMgEAAk8RjgfqvyWQOFWRTwI":     # Фигма круче всех
                                bot.send_message(chat_id, u"Так держать!", reply_to_message_id=message['message_id'])
                            elif sid == u"CAADAgADMwEAAk8Rjgdi4xgAARIe2y8C":    # Скетч Делаю кнопки одного размера
                                bot.send_message(chat_id, u"Вспомни про макеты 600Мб", reply_to_message_id=message['message_id'])
                            elif sid == u"CAADAgADNAEAAk8RjgeeUKe3SpVkKgI":     # В семье не без урода
                                bot.send_message(chat_id, u"Инвижон топ", reply_to_message_id=message['message_id'])
                            elif sid == u"CAADAgADNQEAAk8Rjgd8FOP2Fr17YwI":     # Автор @nerdfox
                                pass

                else:
                    if chats[chat_id].is_chatbot:
                        bot.send_message(chat_id, u"РАССТРЕЛЯТЬ")

        new_offset = last_update_id + 1


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
