import logging

from telegram.ext import Updater
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram.keyboardbutton import KeyboardButton
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup

import utils
from mongo_repository import MongoRepository

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

updater = Updater(token='475545145:AAHtSa3WTcR0je3rQK76kS_wlrYsOiWBKas')
dispatcher = updater.dispatcher

users_repo = MongoRepository('users')
polls_repo = MongoRepository('polls')


def start(bot, update):
    user = users_repo.find_one({'telegram_id': update.message.chat_id})
    if not user:
        user = users_repo.insert({
            'telegram_id': update.message.chat_id,
            'state': 'new'
        })
    all_states_handler(user, bot, update)


STATES = ['new', 'not_approved', 'on_polls_main_menu', 'on_active_polls', 'on_archive_polls']


def all_states_handler(user, bot, update):
    if not user or not user.get('state') or user['state'] not in STATES:
        raise RuntimeError('Bad user received')

    if user['state'] == 'new':
        button_list = [
            KeyboardButton("Поделиться номером телефона", request_contact=True)
        ]
        reply_markup = ReplyKeyboardMarkup(utils.build_menu(button_list, n_cols=1))
        user['state'] = 'not_approved'
        users_repo.update(user)
        bot.send_message(chat_id=update.message.chat_id,
                         text="Для начала работы пожалуйста поделитесь номером телефона",
                         reply_markup=reply_markup)

    elif user['state'] == 'not_approved':
        phone = update.message.contact.phone_number
        first_name = update.message.contact.first_name
        last_name = update.message.contact.last_name
        telegram_id = update.message.contact.user_id
        bot.send_message(chat_id=update.message.chat_id, text="Секундочку, создаем вам etherium кошелек",
                         reply_markup={'hide_keyboard': True})
        eth_wallet = get_etherium_wallet()
        users_repo.insert({
            'phone': phone,
            'first_name': first_name,
            'last_name': last_name,
            'telegram_id': telegram_id,
            'etherium_wallet': eth_wallet
        })
        user['state'] = 'on_polls_main_menu'
        users_repo.update(user)
        bot.send_message(chat_id=update.message.chat_id, text="Вам создан etherium кошелек " + eth_wallet)

    if user['state'] == 'on_polls_main_menu':
        if update.message.text == 'Показать активные опросы':
            user['state'] = 'on_active_polls'
            users_repo.update(user)

        elif update.message.text == 'Показать архивные опросы':
            user['state'] = 'on_archive_polls'
            users_repo.update(user)
        else:
            button_list = [
                KeyboardButton("Показать активные опросы"),
                KeyboardButton("Показать архивные опросы")
            ]
            reply_markup = ReplyKeyboardMarkup(utils.build_menu(button_list, n_cols=1))
            bot.send_message(chat_id=update.message.chat_id,
                             text="Какие опросы вы хотите посмотреть?",
                             reply_markup=reply_markup)

    if user['state'] == 'on_active_polls':
        button_list = []
        active_polls = polls_repo.get_cursor({'archived': False})
        for poll in active_polls:
            button_list.append(KeyboardButton(poll['name']))
        reply_markup = ReplyKeyboardMarkup(utils.build_menu(button_list, n_cols=1))
        bot.send_message(chat_id=update.message.chat_id,
                         text="Выберите опрос для прохождения",
                         reply_markup=reply_markup)
    if user['state'] == 'on_archive_polls':
        pass


def receive_contact(bot, update):
    user = users_repo.find_one({'telegram_id': update.message.chat_id})
    if not user:
        raise RuntimeError('user should be created')
    if user.get('state') == 'not_approved':
        all_states_handler(user, bot, update)


def handle_message(bot, update):
    user = users_repo.find_one({'telegram_id': update.message.chat_id})
    if not user:
        raise RuntimeError('user should be created')
    all_states_handler(user, bot, update)


def get_etherium_wallet():
    # Заглушка. Нужно запилить создание кошеля
    return 'ololo'


contact_handler = MessageHandler(Filters.contact, receive_contact)

text_msg_handler = MessageHandler(Filters.text, handle_message)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(contact_handler)
dispatcher.add_handler(text_msg_handler)

if __name__ == '__main__':
    updater.start_polling()
