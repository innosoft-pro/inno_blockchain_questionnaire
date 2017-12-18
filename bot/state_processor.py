import logging

from bson.objectid import ObjectId
from telegram.keyboardbutton import KeyboardButton
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup

import utils
from mongo_repository import MongoRepository

users_repo = MongoRepository('users')
polls_repo = MongoRepository('polls')
answers_repo = MongoRepository('answers')
logger = logging.getLogger(__name__)


def initial_contact_requester(user, bot, update):
    button_list = [
        KeyboardButton("Поделиться номером телефона", request_contact=True)
    ]
    reply_markup = ReplyKeyboardMarkup(utils.build_menu(button_list, n_cols=1))
    user['state'] = 'not_approved'
    user = users_repo.update(user)
    bot.send_message(chat_id=update.message.chat_id,
                     text="Для начала работы пожалуйста поделитесь номером телефона",
                     reply_markup=reply_markup)


def contacts_processor(user, bot, update):
    phone = update.message.contact.phone_number
    first_name = update.message.contact.first_name
    last_name = update.message.contact.last_name
    username = update.message.from_user.username
    bot.send_message(chat_id=update.message.chat_id, text="Секундочку, создаем вам etherium кошелек",
                     reply_markup={'hide_keyboard': True})
    eth_wallet = get_etherium_wallet()
    user['phone'] = phone
    user['first_name'] = first_name
    user['last_name'] = last_name
    user['username'] = username
    user['etherium_wallet'] = eth_wallet
    user['state'] = 'on_polls_main_menu'
    user = users_repo.update(user)
    bot.send_message(chat_id=update.message.chat_id, text="Вам создан etherium кошелек " + eth_wallet)
    main_menu_processor(user, bot, update)


def main_menu_processor(user, bot, update):
    if update.message.text == 'Показать активные опросы':
        user['state'] = 'on_active_polls'
        user = users_repo.update(user)
        active_polls_menu_processor(user, bot, update)

    elif update.message.text == 'Показать архивные опросы':
        user['state'] = 'on_archive_polls'
        user = users_repo.update(user)
        archive_poll_menu_processor(user, bot, update)
    else:
        button_list = [
            KeyboardButton("Показать активные опросы"),
            KeyboardButton("Показать архивные опросы")
        ]
        reply_markup = ReplyKeyboardMarkup(utils.build_menu(button_list, n_cols=1))
        bot.send_message(chat_id=update.message.chat_id,
                         text="Какие опросы вы хотите посмотреть?",
                         reply_markup=reply_markup)


def active_polls_menu_processor(user, bot, update):
    poll = polls_repo.find_one({'name': update.message.text, 'archived': False})

    if poll:
        answer = answers_repo.find_one({'poll_id': str(poll['_id']), 'user_id': str(user['_id'])})
        if answer:
            user['state'] = 'on_poll_end'
            user['current_poll'] = str(poll['_id'])
            user['current_questions_answers'] = []
            user = users_repo.update(user)
            end_poll_processor(user, bot, update)
        else:
            user['state'] = 'on_poll_start'
            user['current_poll'] = str(poll['_id'])
            user['current_questions_answers'] = []
            user = users_repo.update(user)
            poll_start_processor(user, bot, update)

    elif update.message.text == 'Вернуться в главное меню':
        user['state'] = 'on_polls_main_menu'
        user = users_repo.update(user)
        main_menu_processor(user, bot, update)

    else:
        button_list = []
        active_polls = polls_repo.get_cursor({'archived': False})
        for poll in active_polls:
            if (not poll['participants']) or (poll['participants'] and user['username'] in poll['participants']):
                button_list.append(KeyboardButton(poll['name']))
        button_list.append(KeyboardButton('Вернуться в главное меню'))

        reply_markup = ReplyKeyboardMarkup(utils.build_menu(button_list, n_cols=1))
        if len(button_list) > 1:
            bot.send_message(chat_id=update.message.chat_id,
                             text="Выберите опрос для прохождения",
                             reply_markup=reply_markup)
        else:
            bot.send_message(chat_id=update.message.chat_id,
                             text="Активных опросов нет",
                             reply_markup=reply_markup)


def archive_poll_menu_processor(user, bot, update):
    poll = polls_repo.find_one({'name': update.message.text, 'archived': True})
    if poll:
        user['state'] = 'on_archive_poll'
        user = users_repo.update(user)
    elif update.message.text == 'Вернуться в главное меню':
        user['state'] = 'on_polls_main_menu'
        user = users_repo.update(user)
        main_menu_processor(user, bot, update)
    else:
        button_list = []
        archive_polls = polls_repo.get_cursor({'archived': True})

        for poll in archive_polls:
            button_list.append(KeyboardButton(poll['name']))
        button_list.append(KeyboardButton('Вернуться в главное меню'))

        reply_markup = ReplyKeyboardMarkup(utils.build_menu(button_list, n_cols=1))
        if archive_polls.count():
            bot.send_message(chat_id=update.message.chat_id,
                             text="Эти опросы нельзя пройти",
                             reply_markup=reply_markup)
        else:
            bot.send_message(chat_id=update.message.chat_id,
                             text="Архивных опросов нет",
                             reply_markup=reply_markup)


def poll_start_processor(user, bot, update):
    poll = polls_repo.find_one({'_id': ObjectId(user['current_poll'])})
    question = poll['questions'][0]
    bot.send_message(chat_id=update.message.chat_id,
                     text='Сейчас вам будут задаваться вопросы.',
                     reply_markup={'hide_keyboard': True})
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


def poll_processor(user, bot, update):
    poll = polls_repo.find_one({'_id': ObjectId(user['current_poll'])})
    current_question = poll['questions'][len(user['current_questions_answers'])]
    if current_question['type'] == 'open':
        user['current_questions_answers'].append({
            'question_text': current_question['text'],
            'type': current_question['text'],
            'likes': 0,
            'dislikes': 0,
            'answer': update.message.text
        })
        user = users_repo.update(user)
    elif current_question['type'] in ['select', 'multiselect']:
        if update.message.text in current_question['options']:
            user['current_questions_answers'].append({
                'question_text': current_question['text'],
                'type': current_question['text'],
                'likes': 0,
                'dislikes': 0,
                'answer': update.message.text
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

        q_a = [{'q': answer['question_text'], 'a': answer['answer']} for answer in user['current_questions_answers']]
        transaction_hash = save_answers(user['etherium_wallet'], q_a)

        answers_repo.insert({
            'poll_id': str(poll['_id']),
            'user_id': str(user['_id']),
            'answers': user['current_questions_answers'],
            'hash': transaction_hash
        })

        user['state'] = 'on_poll_end'
        user['current_questions_answers'] = []
        user = users_repo.update(user)
        bot.send_message(chat_id=update.message.chat_id,
                         text='Хэш транзакции: ' + transaction_hash,
                         reply_markup={'hide_keyboard': True})
        end_poll_processor(user, bot, update)


def end_poll_processor(user, bot, update):
    poll = polls_repo.find_one({'name': update.message.text, 'archived': False})

    if update.message.text == 'Показать мои ответы':
        answers_record = answers_repo.find_one({'poll_id': str(user['current_poll']), 'user_id': str(user['_id'])})
        message = 'Хэш транзакции: ' + answers_record['hash'] + '\n'
        for answer in answers_record['answers']:
            message += 'Вопрос: ' + answer['question_text'] + '\n'
            message += 'Ответ: ' + answer['answer'] + '\n'

        bot.send_message(chat_id=update.message.chat_id,
                         text=message)

    elif update.message.text == 'Прорейтинговать ответы других участников':
        user['state'] = 'on_rating'
        user = users_repo.update(user)
        rating_processor(user, bot, update)
    elif update.message.text == 'Вернуться в главное меню':
        user['state'] = 'on_polls_main_menu'
        user = users_repo.update(user)
        main_menu_processor(user, bot, update)
    elif poll:
        button_list = [
            KeyboardButton("Показать мои ответы"),
            KeyboardButton("Прорейтинговать ответы других участников"),
            KeyboardButton("Вернуться в главное меню")
        ]
        reply_markup = ReplyKeyboardMarkup(utils.build_menu(button_list, n_cols=1))
        bot.send_message(chat_id=update.message.chat_id,
                         text="Вы уже проходили данный опрос!",
                         reply_markup=reply_markup)
    else:
        button_list = [
            KeyboardButton("Показать мои ответы"),
            KeyboardButton("Прорейтинговать ответы других участников"),
            KeyboardButton("Вернуться в главное меню")
        ]
        reply_markup = ReplyKeyboardMarkup(utils.build_menu(button_list, n_cols=1))
        bot.send_message(chat_id=update.message.chat_id,
                         text="Опрос пройден успешно!",
                         reply_markup=reply_markup)


def rating_processor(user, bot, update):
    poll = polls_repo.find_one({'name': update.message.text, 'archived': False})


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
