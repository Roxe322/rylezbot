# -*- coding=UTF-8 -*-

import operator
import requests
import time
import os


class BotHandler:
    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates(self, offset=None, timeout=1):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def get_last_update(self, offset=None, timeout=1):
        get_result = self.get_updates(offset, timeout)

        if len(get_result) > 0:
            return get_result[0]
        return None

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'markdown'}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def delete_message(self, chat_id, message_id):
        params = {'chat_id': chat_id, 'message_id': message_id}
        method = 'deleteMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

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


bot = BotHandler(os.environ['TOKEN'])
stats = dict()
users = dict()
limit = 5
is_restricting = False
admins = [145967250, 126751055, 172210439]


def restricting_mode(chat_id, message):
    author = message['from']
    sticker = message['sticker']
    if 'set_name' in sticker and sticker['set_name'] != u'uxuitools':
        users[author['id']] = author['first_name']
        if 'username' in author:
            author_name = "@" + author['username']
        elif 'first_name' in author:
            author_name = author['first_name']

        if not author['id'] in stats:
            stats[author['id']] = 1
        else:
            stats[author['id']] += 1

        if limit - stats[author['id']] > 0:
            # bot.send_message(chat_id, u"У {} осталось {} сообщений".format(author_name, limit - stats[author['id']]))
            if limit - stats[author['id']] == 1:
                bot.send_message(chat_id, u"Будь осторожен, {}, ведь у тебя остался всего 1 стикер!".format(author_name))
        else:
            bot.restrict_chat_member(chat_id, author['id'], 604800, True, True, False, True)
            bot.send_message(chat_id, u"{} теперь не может присылать стикеры неделю!".format(author_name))
    else:
        bot.send_message(chat_id, u"РАССТРЕЛЯТЬ")


def main():
    new_offset = None
    was_previous_sticker = False

    global limit, is_restricting

    while True:
        t = time.gmtime()
        if t.tm_hour == 13 and t.tm_min < 1:
            stats.clear()
            continue

        # bot.get_updates(new_offset)

        last_update = bot.get_last_update(new_offset)

        if isinstance(last_update, list):
            last_update_id = last_update[1]['update_id']
        elif last_update is None:
            continue
        else:
            last_update_id = last_update['update_id']

        if 'message' in last_update and 'from' in last_update['message']:
            message = last_update['message']
            author = message['from']
            chat_id = message['chat']['id']

            if 'text' in message:
                message_text = message['text']

                if message_text.startswith('/start'):
                    bot.send_message(
                        chat_id,
                        u'Бот, который поможет сохранить покой в чате.\n@handlerugbots\nПо вопросам обращайтесь к @handlerug'
                    )

                if message_text.startswith('/stats'):
                    if is_restricting:
                        stats_text = u'*Статистика по отправителям стикеров:*\n\n'
                        i = 1
                        # for key, value in sorted(stats, key=stats.get, reverse=True):
                        for key, value in sorted(stats.iteritems(), key=operator.itemgetter(1), reverse=True):
                        # for key, value in stats.items():
                            stats_text += u"{}. {} — {}/{} стикеров".format(i, users[key], value, limit)
                            if limit - value <= 0:
                                stats_text += u' (ограничен)'
                            stats_text += '\n'
                            i += 1
                        bot.send_message(chat_id, stats_text)
                    else:
                        bot.send_message(chat_id, u'В данный момент *нет статистики*. Чтобы включить статистику, переключите бота в *ограничивающий режим*.')

                if message_text.startswith('/limit'):
                    command_params = message_text.split()[1:]
                    if len(command_params) > 0:
                        if author['id'] in admins:
                            limit = int(command_params[0])
                            bot.send_message(chat_id, u'Лимит стикеров установлен в *{}* стикеров.'.format(limit))
                        else:
                            bot.send_message(chat_id, u'пошел нахуй')
                    else:
                        bot.send_message(chat_id, u'В данный момент лимит стикеров установлен в *{}* стикеров.'.format(limit))

                if message_text.startswith('/restricting_mode'):
                    command_params = message_text.split()[1:]
                    if len(command_params) > 0:
                        if author['id'] in admins:
                            if command_params[0] == u'1':
                                is_restricting = True
                                bot.send_message(chat_id, u'Ограничивающий режим *включен*.')
                            elif command_params[0] == u'0':
                                is_restricting = False
                                bot.send_message(chat_id, u'Ограничивающий режим *выключен*.')
                        else:
                            bot.send_message(chat_id, u'пошел нахуй')
                    else:
                        if is_restricting:
                            bot.send_message(chat_id, u'В данный момент ограничивающий режим *включен*.')
                        else:
                            bot.send_message(chat_id, u'В данный момент ограничивающий режим *выключен*.')

                was_previous_sticker = False

            elif 'sticker' in message:
                if is_restricting:
                    restricting_mode(chat_id, message)
                else:
                    if was_previous_sticker:
                        bot.delete_message(chat_id, message['message_id'])
                was_previous_sticker = True

        new_offset = last_update_id + 1


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
