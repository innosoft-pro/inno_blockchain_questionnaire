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


STATES = [
    'new',
    'not_approved',
    'on_polls_main_menu',
    'on_active_polls',
    'on_archive_polls',
    'on_poll_start',
    'on_poll',
    'on_archive_poll',
    'on_poll_end'
]


def all_states_handler(user, bot, update):
    if not user or not user.get('state') or user['state'] not in STATES:
        raise RuntimeError('Bad user received')

    if user['state'] == 'new':
        button_list = [
            KeyboardButton("Поделиться номером телефона", request_contact=True)
        ]
        reply_markup = ReplyKeyboardMarkup(utils.build_menu(button_list, n_cols=1))
        user['state'] = 'not_approved'
        user = users_repo.update(user)
        bot.send_message(chat_id=update.message.chat_id,
                         text="Для начала работы пожалуйста поделитесь номером телефона",
                         reply_markup=reply_markup)

    elif user['state'] == 'not_approved':
        phone = update.message.contact.phone_number
        first_name = update.message.contact.first_name
        last_name = update.message.contact.last_name
        bot.send_message(chat_id=update.message.chat_id, text="Секундочку, создаем вам etherium кошелек",
                         reply_markup={'hide_keyboard': True})
        eth_wallet = get_etherium_wallet()
        user['phone'] = phone,
        user['first_name'] = first_name,
        user['last_name'] = last_name,
        user['etherium_wallet'] = eth_wallet
        user['state'] = 'on_polls_main_menu'
        user = users_repo.update(user)
        bot.send_message(chat_id=update.message.chat_id, text="Вам создан etherium кошелек " + eth_wallet)

    if user['state'] == 'on_polls_main_menu':
        if update.message.text == 'Показать активные опросы':
            user['state'] = 'on_active_polls'
            user = users_repo.update(user)

        elif update.message.text == 'Показать архивные опросы':
            user['state'] = 'on_archive_polls'
            user = users_repo.update(user)
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
        poll = polls_repo.find_one({'name': update.message.text, 'archived': False})

        if poll:
            user['state'] = 'on_poll_start'
            logger.info(poll)
            user['current_poll'] = poll['_id']
            user['current_questions_answers'] = []
            user = users_repo.update(user)

        else:
            button_list = []
            active_polls = polls_repo.get_cursor({'archived': False})
            for poll in active_polls:
                button_list.append(KeyboardButton(poll['name']))
            reply_markup = ReplyKeyboardMarkup(utils.build_menu(button_list, n_cols=1))
            bot.send_message(chat_id=update.message.chat_id,
                             text="Выберите опрос для прохождения",
                             reply_markup=reply_markup)

    if user['state'] == 'on_archive_polls':
        poll = polls_repo.get_cursor({'name': update.message.text, 'archived': True})
        if poll:
            user['state'] = 'on_archive_poll'
            user = users_repo.update(user)
        button_list = []
        active_polls = polls_repo.get_cursor({'archived': True})
        for poll in active_polls:
            button_list.append(KeyboardButton(poll['name']))
        reply_markup = ReplyKeyboardMarkup(utils.build_menu(button_list, n_cols=1))
        bot.send_message(chat_id=update.message.chat_id,
                         text="Выберите опрос для просмотра",
                         reply_markup=reply_markup)

    if user['state'] == 'on_poll_start':
        poll = polls_repo.find_one({'_id': user['current_poll']})
        question = poll['questions'][0]
        user['state'] = 'on_poll'
        user = users_repo.update(user)
        if question['type'] == 'open':
            bot.send_message(chat_id=update.message.chat_id,
                             text=question['text'],
                             reply_markup={'hide_keyboard': True})
        elif question['type'] in ['select', 'multiselect']:
            button_list = []
            for option in question['options']:
                button_list.append(KeyboardButton(option))
            reply_markup = ReplyKeyboardMarkup(utils.build_menu(button_list, n_cols=1))
            bot.send_message(chat_id=update.message.chat_id,
                             text=question['text'],
                             reply_markup=reply_markup)
    elif user['state'] == 'on_poll':
        poll = polls_repo.find_one({'_id': user['current_poll']})
        current_question = poll['questions'][len(user['current_questions_answers'])]
        if current_question['type'] == 'open':
            user['current_questions_answers'].append({
                'q': current_question['text'],
                'a': update.message.text
            })
            user = users_repo.update(user)
        elif current_question['type'] in ['select', 'multiselect']:
            if update.message.text in current_question['options']:
                user['current_questions_answers'].append({
                    'q': current_question['text'],
                    'a': update.message.text
                })
                user = users_repo.update(user)
            else:
                bot.send_message(chat_id=update.message.chat_id,
                                 text='Выберите одну из опций',
                                 reply_markup={'hide_keyboard': True})

        if len(user['current_questions_answers']) < len(poll['questions']):
            question = poll['questions'][len(user['current_questions_answers'])]
            if question['type'] == 'open':
                bot.send_message(chat_id=update.message.chat_id,
                                 text=question['text'],
                                 reply_markup={'hide_keyboard': True})
            elif question['type'] in ['select', 'multiselect']:
                button_list = []
                for option in question['options']:
                    button_list.append(KeyboardButton(option))
                reply_markup = ReplyKeyboardMarkup(utils.build_menu(button_list, n_cols=1))
                bot.send_message(chat_id=update.message.chat_id,
                                 text=question['text'],
                                 reply_markup=reply_markup)
        else:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Секундочку, сохраняем результаты в блокчейн',
                             reply_markup={'hide_keyboard': True})
            transaction_hash = save_answers(user['etherium_wallet'], user['current_questions_answers'])

            poll['answers'].append({
                'user': user['_id'],
                'answers': user['current_questions_answers'],
                'hash': transaction_hash
            })
            polls_repo.update(poll)

            user['state'] = 'on_poll_end'
            user['current_questions_answers'] = []
            user = users_repo.update(user)
            bot.send_message(chat_id=update.message.chat_id,
                             text='Хэш транзакции: ' + transaction_hash,
                             reply_markup={'hide_keyboard': True})

    if user['state'] == 'on_poll_end':
        if update.message.text == 'Показать мои ответы':
            poll = polls_repo.find_one({'_id': user['current_poll']})
            answers_record = next(item for item in poll['answers'] if item['user'] == str(user['_id']))
            message = 'Хэш транзакции: ' + answers_record['hash'] + '\n'
            for answer in answers_record['answers']:
                message += 'Вопрос: ' + answer['q'] + '\n'
                message += 'Ответ: ' + answer['a'] + '\n'

            bot.send_message(chat_id=update.message.chat_id,
                             text=message)

        elif update.message.text == 'Прорейтинговать ответы других участников':
            user['state'] = 'on_poll_end'
            user = users_repo.update(user)
        else:
            button_list = [
                KeyboardButton("Показать мои ответы"),
                KeyboardButton("Прорейтинговать ответы других участников")
            ]
            reply_markup = ReplyKeyboardMarkup(utils.build_menu(button_list, n_cols=1))
            bot.send_message(chat_id=update.message.chat_id,
                             text="Опрос пройден успешно!",
                             reply_markup=reply_markup)


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
    # возвращает etherium wallet
    return 'eth_wallet_string'


def save_answers(etherium_wallet, questions_answers):
    # questions_answers - массив, каждый элемент которого { q: string, a: string }
    return 'transaction_hash_string'


def get_answers(transaction_hash):
    # вытаскивает ответы по хэшу транзакции в первозданном виде
    return 'answers from blockchain'


contact_handler = MessageHandler(Filters.contact, receive_contact)

text_msg_handler = MessageHandler(Filters.text, handle_message)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(contact_handler)
dispatcher.add_handler(text_msg_handler)

if __name__ == '__main__':
    updater.start_polling()
