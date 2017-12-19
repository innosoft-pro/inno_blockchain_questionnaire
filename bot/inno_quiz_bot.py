import logging

from telegram.ext import Updater
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler

import state_processor
from mongo_repository import MongoRepository

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

updater = Updater(token='472437427:AAEIl5znA-bTNMVlTkNIm1mKs8jmN7z80Kg')
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


STATES = [
    'new',
    'not_approved',
    'on_polls_main_menu',
    'on_active_polls',
    'on_archive_polls',
    'on_poll_start',
    'on_poll',
    'on_archive_poll',
    'on_poll_end',
    'on_rating_start',
    'on_rating'
]


def all_states_handler(user, bot, update):
    if not user or not user.get('state') or user['state'] not in STATES:
        logger.error(str(user))
        logger.error(str(user['state']))
        logger.error(str(user['state'] in STATES))
        raise RuntimeError('Bad user received')

    if user['state'] == 'new':
        state_processor.initial_contact_requester(user, bot, update)

    elif user['state'] == 'not_approved':
        state_processor.contacts_processor(user, bot, update)

    elif user['state'] == 'on_polls_main_menu':
        state_processor.main_menu_processor(user, bot, update)

    elif user['state'] == 'on_active_polls':
        state_processor.active_polls_menu_processor(user, bot, update)

    elif user['state'] == 'on_archive_polls':
        state_processor.archive_poll_menu_processor(user, bot, update)

    elif user['state'] == 'on_poll_start':
        state_processor.poll_start_processor(user, bot, update)

    elif user['state'] == 'on_poll':
        state_processor.poll_processor(user, bot, update)

    elif user['state'] == 'on_poll_end':
        state_processor.end_poll_processor(user, bot, update)

    elif user['state'] == 'on_rating_start':
        state_processor.rating_start_processor(user, bot, update)

    elif user['state'] == 'on_rating':
        state_processor.rating_processor(user, bot, update)


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


contact_handler = MessageHandler(Filters.contact, receive_contact)

text_msg_handler = MessageHandler(Filters.text, handle_message)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(contact_handler)
dispatcher.add_handler(text_msg_handler)

if __name__ == '__main__':
    updater.start_polling()
