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


def start(bot, update):
    button_list = [
        KeyboardButton("Поделиться номером телефона", request_contact=True)
    ]
    reply_markup = ReplyKeyboardMarkup(utils.build_menu(button_list, n_cols=1))
    bot.send_message(chat_id=update.message.chat_id, text="Для начала работы пожалуйста поделитесь номером телефона",
                     reply_markup=reply_markup)


def receive_contact(bot, update):
    phone = update.message.contact.phone_number
    first_name = update.message.contact.first_name
    last_name = update.message.contact.last_name
    telegram_id = update.message.contact.user_id

    user = users_repo.find_one({'phone': phone})

    if not users_repo.find_one({'phone': phone}):
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
        bot.send_message(chat_id=update.message.chat_id, text="Вам создан etherium кошелек " + eth_wallet)
    else:
        logger.info(user)
        bot.send_message(chat_id=update.message.chat_id,
                         text="Вы уже есть в нашей системе. Etherium кошелек " + user['etherium_wallet'],
                         reply_markup={'hide_keyboard': True})


def get_etherium_wallet():
    # Заглушка. Нужно запилить создание кошеля
    return 'ololo'


contact_handler = MessageHandler(Filters.contact, receive_contact)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(contact_handler)

if __name__ == '__main__':
    updater.start_polling()
