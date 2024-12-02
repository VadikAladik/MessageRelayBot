import telebot
from telebot import types
import json

from config import *

bot = telebot.TeleBot(bot_token)


@bot.message_handler(commands=['start', 'send', 'load'])
def start(message):
    print(f'@{message.from_user.username}({message.from_user.id}) ввел команду: {message.text}')
    if message.from_user.id == admin_id:
        print(f'@{message.from_user.username}({message.from_user.id}) является админом')
        bot.reply_to(message, text='Вы админ\n'
                                   'Пока что /start админа ничего не делает 😉')
    else:
        print(f'@{message.from_user.username}({message.from_user.id}) является простым юзером')
        # bot.reply_to(message, text=f'Вы обычный пользователь\n'
        #                           f'Ваш айди: {message.from_user.id}')
        input_mess_text = bot.send_message(message.chat.id, text='📝 Введите ваше сообщение:')
        bot.register_next_step_handler(input_mess_text, input_message)


def input_message(message):
    original_chat_id = message.chat.id
    user_callback_data = json.dumps({'action': 'reply_by_user', 'chat_id': original_chat_id})
    callback_data = json.dumps({'action': 'reply', 'chat_id': original_chat_id})

    kb_for_admin = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text='💬 Ответить', callback_data=callback_data)
    kb_for_admin.add(button1)

    kb_for_user = types.InlineKeyboardMarkup()
    button2 = types.InlineKeyboardButton(text='💬 Добавить сообщение', callback_data=user_callback_data)
    kb_for_user.add(button2)

    print(f'@{message.from_user.username}({message.from_user.id}) отправил тип сообщения: {message.content_type}')
    if message.content_type == 'text':  # обработка текста
        print(f'@{message.from_user.username}({message.from_user.id}) написал: {message.text}')

        bot.send_message(admin_id, text=f'id этого сообщения: <code>{message.message_id}</code>\n'
                                        f'id чата: <code>{message.chat.id}</code>\n'
                                        f'@{message.from_user.username}(<code>{message.from_user.id}</code>) написал:\n'
                                        f'<b>{message.text}</b>', reply_markup=kb_for_admin, parse_mode='HTML')
        bot.send_message(message.chat.id, text='✅ Сообщение доставлено администратору', reply_markup=kb_for_user)


    elif message.content_type == 'photo':  # обработка фото
        file_id = message.photo[-1].file_id

        if message.caption:
            mess_capt = message.caption
        else:
            mess_capt = ' '

        print(
            f'@{message.from_user.username}({message.from_user.id}) отправил фото, комментарий: {message.caption if message.caption else 'без комментария'}')
        bot.send_photo(admin_id, file_id, caption=f'Отправлено @{message.from_user.username}({message.from_user.id})\n'
                                                  f'Комментарий: <b>{mess_capt}</b>', parse_mode='HTML')
        bot.send_message(message.chat.id, text='✅ Сообщение доставлено администратору', reply_markup=kb_for_user)

    elif message.content_type == 'video':  # обработка видео
        file_id = message.video.file_id

        if message.caption:
            mess_capt = message.caption
        else:
            mess_capt = ' '

        print(
            f'@{message.from_user.username}({message.from_user.id}) отправил видео, комментарий: {message.caption if message.caption else 'без комментария'}')
        bot.send_video(admin_id, file_id, caption=f'Отправлено @{message.from_user.username}({message.from_user.id})\n'
                                                  f'Комментарий: <b>{mess_capt}</b>', parse_mode='HTML')
        bot.send_message(message.chat.id, text='✅ Сообщение доставлено администратору', reply_markup=kb_for_user)

    elif message.content_type == 'video_note':  # обработка кружочков
        file_id = message.video_note.file_id

        print(f'@{message.from_user.username}({message.from_user.id}) отправил кружок')
        bot.send_message(admin_id, text=f'Отправлено @{message.from_user.username}({message.from_user.id})\n'
                                        'Сам кружок:')
        bot.send_video_note(admin_id, file_id)
        bot.send_message(message.chat.id, text='✅ Сообщение доставлено администратору', reply_markup=kb_for_user)

    else:
        print(
            f'@{message.from_user.username}({message.from_user.id}) отправил {message.content_type}, данный тип не поддерживается')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    data = json.loads(call.data)

    original_chat_id = data['chat_id']
    if data['action'] == 'reply_by_user':
        input_mess = bot.send_message(original_chat_id, text='📝 Введите ваше сообщение:')
        bot.register_next_step_handler(input_mess, input_message)


    elif data['action'] == 'reply':
        text = bot.send_message(admin_id, text='📝 Введите сообщение для ответа')
        bot.register_next_step_handler(text, send_reply, original_chat_id)


def send_reply(message, original_chat_id):
    reply_text = message.text
    print(f'Админ ввел ответ: {reply_text}')

    try:
        bot.send_message(original_chat_id, f'Админ ответил: {reply_text}')
        print(f'Сообщение "{reply_text}" отправлено пользователю')
        bot.send_message(message.chat.id, text='✅ Сообщение отправлено пользователю')

    except Exception as e:
        print(f'Сообщение "{reply_text}" не отправлено пользователю. Произошла ошибка : {e}')

        if '403' in str(e):
            bot.send_message(message.chat.id, text='❌ Сообщение не отправлено пользователю\n'
                                                   '❓ Пользователь заблокировал бота')
        else:
            bot.send_message(message.chat.id, text='❌ Сообщение не отправлено пользователю\n'
                                                   f'❓ {e}')


if __name__ == "__main__":
    bot.polling()
