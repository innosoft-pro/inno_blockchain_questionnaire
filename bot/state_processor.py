import logging
import random

from bson.objectid import ObjectId
from telegram.keyboardbutton import KeyboardButton
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup

from contractHandler import ContractHandler

import utils
from mongo_repository import MongoRepository

users_repo = MongoRepository('users')
polls_repo = MongoRepository('polls')
answers_repo = MongoRepository('answers')
logger = logging.getLogger(__name__)

QUESTIONS_TO_RATE = 5


def initial_contact_requester(user, bot, update):
    #button_list = [
    #    KeyboardButton("Поделиться данными профиля", request_contact=True)
    #]
    #reply_markup = ReplyKeyboardMarkup(utils.build_menu(button_list, n_cols=1))
    user['state'] = 'not_approved'
    user = users_repo.update(user)
    #bot.send_message(chat_id=update.message.chat_id,
    #                 text="Для начала работы, пожалуйста, предоставьте данные профиля",
    #                 reply_markup=reply_markup)
    contacts_processor(user, bot, update)


def contacts_processor(user, bot, update):
    #phone = update.message.contact.phone_number
    #first_name = update.message.contact.first_name
    #last_name = update.message.contact.last_name
    username = update.message.from_user.username
    phone = update.message.chat_id
    bot.send_message(chat_id=update.message.chat_id, text="Секундочку, дождитесь регистрации в нашей системе",
                     reply_markup={'hide_keyboard': True})
    eth_account = get_ethereum_wallet(phone)
    user['phone'] = phone
    #user['first_name'] = first_name
    #user['last_name'] = last_name
    user['username'] = username
    user['ethereum_wallet'] = eth_account[0]
    user['ethereum_password'] = eth_account[1]
    user['ratings'] = []
    user['state'] = 'on_polls_main_menu'
    user = users_repo.update(user)
    bot.send_message(chat_id=update.message.chat_id, text="Поздравляем, " + username
                                                          + ", Вы зарегистрированы как эксперт")
    main_menu_processor(user, bot, update)


def main_menu_processor(user, bot, update):
    if update.message.text == 'Показать активные опросы':
        user['state'] = 'on_active_polls'
        user = users_repo.update(user)
        active_polls_menu_processor(user, bot, update)

    elif update.message.text == 'Показать архив':
        user['state'] = 'on_archive_polls'
        user = users_repo.update(user)
        archive_poll_menu_processor(user, bot, update)
    else:
        button_list = [
            KeyboardButton("Показать активные опросы"),
            KeyboardButton("Показать архив")
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
        bot.send_message(chat_id=update.message.chat_id,
                         text="Опрос в архиве")
        # user['state'] = 'on_archive_poll'
        # user = users_repo.update(user)
    elif update.message.text == 'Вернуться в главное меню':
        user['state'] = 'on_polls_main_menu'
        user = users_repo.update(user)
        main_menu_processor(user, bot, update)
    else:
        button_list = []
        archive_polls = polls_repo.get_cursor({'archived': True})

        for poll in archive_polls:
            if (not poll['participants']) or (poll['participants'] and user['username'] in poll['participants']):
                button_list.append(KeyboardButton(poll['name']))
        button_list.append(KeyboardButton('Вернуться в главное меню'))

        reply_markup = ReplyKeyboardMarkup(utils.build_menu(button_list, n_cols=1))
        if len(button_list) > 1:
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
    if poll.get('welcome_message'):
        bot.send_message(chat_id=update.message.chat_id,
                         text=poll['welcome_message'],
                         reply_markup={'hide_keyboard': True})
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
            'type': current_question['type'],
            'likes': 0,
            'dislikes': 0,
            'answer': update.message.text
        })
        user = users_repo.update(user)
    elif current_question['type'] == 'select':
        if update.message.text in current_question['options']:
            user['current_questions_answers'].append({
                'question_text': current_question['text'],
                'type': current_question['type'],
                'answer': update.message.text
            })
            user = users_repo.update(user)
        else:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Выберите одну из опций',
                             reply_markup={'hide_keyboard': True})
    elif current_question['type'] == 'multiselect':
        if update.message.text in current_question['options']:
            user['current_questions_answers'].append({
                'question_text': current_question['text'],
                'type': current_question['type'],
                'answer': update.message.text,
                'likes': 0,
                'dislikes': 0
            })
            user = users_repo.update(user)
        elif update.message.text == 'Свой вариант':
            user['on_own_answer'] = True
            user = users_repo.update(user)
            bot.send_message(chat_id=update.message.chat_id,
                             text='Напишите свой вариант ответа',
                             reply_markup={'hide_keyboard': True})
            return
        elif user.get('on_own_answer'):
            user['current_questions_answers'].append({
                'question_text': current_question['text'],
                'type': current_question['type'],
                'likes': 0,
                'dislikes': 0,
                'answer': update.message.text,
            })
            user['on_own_answer'] = False
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
        elif question['type'] == 'select':
            button_list = []
            for option in question['options']:
                button_list.append(KeyboardButton(option))
            reply_markup = ReplyKeyboardMarkup(utils.build_menu(button_list, n_cols=1))
            bot.send_message(chat_id=update.message.chat_id,
                             text=question['text'],
                             reply_markup=reply_markup)
        elif question['type'] == 'multiselect':
            button_list = []
            for option in question['options']:
                button_list.append(KeyboardButton(option))
            button_list.append('Свой вариант')
            reply_markup = ReplyKeyboardMarkup(utils.build_menu(button_list, n_cols=1))
            bot.send_message(chat_id=update.message.chat_id,
                             text=question['text'],
                             reply_markup=reply_markup)
    else:
        bot.send_message(chat_id=update.message.chat_id,
                         text='Секундочку, сохраняем результаты в блокчейн Ethereum',
                         reply_markup={'hide_keyboard': True})

        q_a = [{'q': answer['question_text'], 'a': answer['answer']} for answer in user['current_questions_answers']]
        transaction_hash = save_answers(user['ethereum_wallet'], user['ethereum_password'], q_a)

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
                         text='Ссылка на хэш транзакции в сети: ' + transaction_hash,
                         reply_markup={'hide_keyboard': True})
        end_poll_processor(user, bot, update, come_from='poll_processor')


def end_poll_processor(user, bot, update, come_from=None):
    poll = polls_repo.find_one({'name': update.message.text, 'archived': False})
    if come_from and come_from == 'start_rating_processor':
        button_list = [
            KeyboardButton("Показать мои ответы"),
            KeyboardButton("Оценить ответы других участников"),
            KeyboardButton("Вернуться в главное меню")
        ]
        reply_markup = ReplyKeyboardMarkup(utils.build_menu(button_list, n_cols=1))
        bot.send_message(chat_id=update.message.chat_id,
                         text="Вы вернулись в меню пройденного опроса",
                         reply_markup=reply_markup)
    elif come_from and come_from == 'poll_processor':
        button_list = [
            KeyboardButton("Показать мои ответы"),
            KeyboardButton("Оценить ответы других участников"),
            KeyboardButton("Вернуться в главное меню")
        ]
        reply_markup = ReplyKeyboardMarkup(utils.build_menu(button_list, n_cols=1))
        bot.send_message(chat_id=update.message.chat_id,
                         text="Опрос пройден успешно! Сейчас вам будут предложены в случайном порядке"
                              " ответы других участников опроса. Просим вас оценить их ('+1' - согласен;"
                              " '-1' - не согласен).",
                         reply_markup=reply_markup)
        user['state'] = 'on_rating_start'
        user = users_repo.update(user)
        rating_start_processor(user, bot, update)
    elif update.message.text == 'Показать мои ответы':
        answers_record = answers_repo.find_one({'poll_id': str(user['current_poll']), 'user_id': str(user['_id'])})
        message = 'Хэш транзакции: ' + answers_record['hash'] + '\n'
        for answer in answers_record['answers']:
            message += 'Вопрос: ' + answer['question_text'] + '\n'
            message += 'Ответ: ' + answer['answer'] + '\n'

        bot.send_message(chat_id=update.message.chat_id,
                         text=message)

    elif update.message.text == 'Оценить ответы других участников':
        user['state'] = 'on_rating_start'
        user = users_repo.update(user)
        rating_start_processor(user, bot, update)
        return
    elif update.message.text == 'Вернуться в главное меню':
        user['state'] = 'on_polls_main_menu'
        user = users_repo.update(user)
        main_menu_processor(user, bot, update)
    elif poll:
        button_list = [
            KeyboardButton("Показать мои ответы"),
            KeyboardButton("Оценить ответы других участников"),
            KeyboardButton("Вернуться в главное меню")
        ]
        reply_markup = ReplyKeyboardMarkup(utils.build_menu(button_list, n_cols=1))
        bot.send_message(chat_id=update.message.chat_id,
                         text="Вы уже проходили данный опрос!",
                         reply_markup=reply_markup)
    else:
        button_list = [
            KeyboardButton("Показать мои ответы"),
            KeyboardButton("Оценить ответы других участников"),
            KeyboardButton("Вернуться в главное меню")
        ]
        reply_markup = ReplyKeyboardMarkup(utils.build_menu(button_list, n_cols=1))
        bot.send_message(chat_id=update.message.chat_id,
                         text="Вы вернулись в меню пройденного опроса",
                         reply_markup=reply_markup)


def rating_start_processor(user, bot, update):
    poll = polls_repo.find_one({'_id': ObjectId(user['current_poll'])})
    try:
        next(q for q in poll['questions'] if q['type'] == 'open')
    except StopIteration:
        user['state'] = 'on_poll_end'
        user = users_repo.update(user)
        bot.send_message(chat_id=update.message.chat_id,
                         text="В опросе нет вопросов со свободной формой ответа, функция недоступна",
                         reply_markup={'hide_keyboard': True})
        end_poll_processor(user, bot, update, come_from='start_rating_processor')
        return

    other_answers_cursor = answers_repo.get_cursor(
        {'poll_id': str(user['current_poll']), 'user_id': {'$ne': str(user['_id'])}})
    if not other_answers_cursor.count():
        user['state'] = 'on_poll_end'
        user = users_repo.update(user)
        bot.send_message(chat_id=update.message.chat_id,
                         text="Никто кроме вас еще не прошел опрос, функция недоступна",
                         reply_markup={'hide_keyboard': True})
        end_poll_processor(user, bot, update, come_from='start_rating_processor')
        return

    try:
        next(r for r in user['ratings'] if
             r['poll_id'] == str(user['current_poll']) and r.get('questions_rated') and r['questions_rated'] == len(
                 r['questions']))
        user['state'] = 'on_poll_end'
        user = users_repo.update(user)
        bot.send_message(chat_id=update.message.chat_id,
                         text="Вы уже оценивали ответы в этом опросе",
                         reply_markup={'hide_keyboard': True})
        end_poll_processor(user, bot, update, come_from='start_rating_processor')
        return
    except StopIteration:
        pass

    all_questions = []
    for answer in other_answers_cursor:
        for q_a in answer['answers']:
            if q_a['type'] in ['open', 'multiselect'] and 'ФИО' not in q_a['question_text']:
                all_questions.append({
                    'answer_id': answer['_id'],
                    'question': q_a['question_text'],
                    'answer': q_a['answer']
                })

    random.shuffle(all_questions)

    if len(all_questions) <= QUESTIONS_TO_RATE:
        user['ratings'].append({
            'poll_id': str(user['current_poll']),
            'questions_rated': 0,
            'questions': all_questions
        })
    else:
        question_list = []
        already_picked_questions = set()
        while len(question_list) < QUESTIONS_TO_RATE:
            num = random.randint(0, len(all_questions) - 1)
            if num not in already_picked_questions:
                question_list.append(all_questions[num])
                already_picked_questions.add(num)
        user['ratings'].append({
            'poll_id': str(user['current_poll']),
            'questions_rated': 0,
            'questions': question_list
        })

    user['state'] = 'on_rating'
    user = users_repo.update(user)
    bot.send_message(chat_id=update.message.chat_id,
                     text="Сейчас вы увидите вопросы и ответы других участников. "
                          "Если ответ вам понравился, нажмите '+1'. Иначе - '-1'",
                     reply_markup={'hide_keyboard': True})
    rating_processor(user, bot, update)


def rating_processor(user, bot, update):
    current_ratings_record = next(
        record for record in user['ratings'] if record['poll_id'] == str(user['current_poll']))
    if update.message.text == '+1':
        question_to_rate = next(
            question for question in current_ratings_record['questions'] if not question.get('rate'))
        question_to_rate['rate'] = 1
        current_ratings_record['questions_rated'] += 1
        users_repo.update(user)
    elif update.message.text == '-1':
        question_to_rate = next(
            question for question in current_ratings_record['questions'] if not question.get('rate'))
        question_to_rate['rate'] = -1
        current_ratings_record['questions_rated'] += 1
        users_repo.update(user)

    try:
        question_to_rate = next(
            question for question in current_ratings_record['questions'] if not question.get('rate'))
        button_list = [
            KeyboardButton('+1'),
            KeyboardButton('-1')
        ]
        reply_markup = ReplyKeyboardMarkup(utils.build_menu(button_list, n_cols=1))
        bot.send_message(chat_id=update.message.chat_id,
                         text='Вопрос: ' + question_to_rate['question'] + '\n' + 'Ответ: ' + question_to_rate['answer'],
                         reply_markup=reply_markup)

    except StopIteration:
        for question in current_ratings_record['questions']:
            true_answer_record = answers_repo.find_one({'_id': ObjectId(question['answer_id'])})
            answer = next(
                answer for answer in true_answer_record['answers'] if answer['question_text'] == question['question'])
            if question['rate'] == -1:
                answer['dislikes'] += 1
            elif question['rate'] == 1:
                answer['likes'] += 1
            answers_repo.update(true_answer_record)

        user['state'] = 'on_poll_end'
        user = users_repo.update(user)
        bot.send_message(chat_id=update.message.chat_id,
                         text="Спасибо за участие в оценке ответов!\n\nПриглашаем стать участником"
                              " сообщества по обсуждению вопросов регулирования"
                              " технологий блокчейн, криптовалют и ICO:\n\n"
                              "https://t.me/InnoExpert",
                         reply_markup={'hide_keyboard': True})
        end_poll_processor(user, bot, update)


def get_ethereum_wallet(phone):
    # Заглушка. Нужно запилить создание кошеля
    # возвращает ethereum wallet
    return (phone, 'eth_wallet_password')


def save_answers(ethereum_wallet, eth_password, questions_answers):
    # questions_answers - массив, каждый элемент которого { q: string, a: string }
    contractHandler = ContractHandler()
    hash = contractHandler.recordAnswers("CryptoRF", ethereum_wallet, str(questions_answers))
    return hash


def get_answers(phone):
    # вытаскивает ответы по хэшу транзакции в первозданном виде
    contractHandler = ContractHandler()
    answers = contractHandler.getAnswersById("CryptoRF", phone)
    return answers
