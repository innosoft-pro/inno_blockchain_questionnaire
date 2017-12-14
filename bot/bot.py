# -*- coding: utf-8 -*-
import telebot
import time
import threading
import config
import json
from sqlalchemy import desc
from datetime import datetime
from dbms.db_model import session, SessionModel, ProcessModel, UsersSurveysModel
from collections import OrderedDict
from contractHandler import ContractHandler

bot = telebot.TeleBot(config.token)

POLL_NAME = 'CryptoRF'


class BCSaveThread(threading.Thread):
    def __init__(self, telegram_id, list_of_answers):
        super().__init__()
        self.telegram_id = telegram_id
        self.answers = list_of_answers
        self.ch = ContractHandler()

    def run(self):
        tr_hash = self.ch.recordAnswers(POLL_NAME, str(self.telegram_id), str(self.answers))
        bot.send_message(self.telegram_id, 'Результаты сохранены в блокчейне. Хэш транзакции:' + tr_hash)


@bot.message_handler(content_types=['text'])
def process_all_messages(message):
    user_id = message.from_user.id
    if message.text.startswith('ответы'):
        if 'Криптовалюта в РФ' in message.text:
            bot.reply_to(message, 'Выгружаем данные из блокчейна')
            contractHandler = ContractHandler()
            answers = contractHandler.getAnswersById("CryptoRF", str(user_id))
            bot.reply_to(message, answers)
        else:
            bot.reply_to(message, 'Вы не проходили такой опрос')
    else:
        db_model, is_new = get_current_process_and_step(user_id)
        process = None
        answers = None
        if db_model.current_process is None:
            process = get_new_process(message)
            if process is not None:
                setattr(db_model, 'current_process', process['id'])
                setattr(db_model, 'current_param', process['parameters'][0]['id'])
        else:
            process = get_current_process(db_model.current_process)

        if not is_new:
            result_message = 'Привет, я бот-интервьюер\n'
        elif not process:
            result_message = 'Такой опрос не найден\n'
        elif user_already_passed(db_model.user_id, process['id']):
            result_message = 'Вы уже проходили этот опрос\n'
            bot.reply_to(message, result_message)
            setattr(db_model, 'current_process', None)
            return
        else:
            result_message = ''

        if db_model.process_params is None:
            answers = {}
        else:
            answers = json.loads(db_model.process_params)

        result_message = get_result_message_by_process(answers, message, process, db_model, result_message)
        bot.reply_to(message, result_message)


def get_result_message_by_process(answers, message, process, session_model, result_message):
    if process is None:
        result_message += 'Назовите имя опроса, который хотите пройти!\n Доступные опросы:\n Криптовалюта в РФ'
        return result_message

    current_param = None
    current_param_index = -1
    for i in range(len(process['parameters'])):
        param = process['parameters'][i]
        if param['id'] == session_model.current_param:
            current_param = param
            current_param_index = i

    options = current_param['options']
    opt_intersection = find_intersection_string(options, message.text)

    if opt_intersection or not options:
        # идем к следующему параметру
        if options:
            answers[str(current_param['id'])] = opt_intersection
        else:
            answers[str(current_param['id'])] = message.text

        setattr(session_model, 'process_params', json.dumps(answers))
        session.commit()
        if current_param_index < len(process['parameters']) - 1:
            next_param = process['parameters'][current_param_index + 1]
            setattr(session_model, 'current_param', next_param['id'])
            session.commit()
            return 'Ответ записан. \n' + next_param['botMessagesSequence'][0]['text']
        else:
            mand_keys = list(answers.keys())
            if len(mand_keys) == len(process['parameters']):
                action_msg = process['actions'][0]['text']
                answers = OrderedDict(sorted(answers.items()))
                for q, a in answers.items():
                    action_msg += '\nВопрос:\n'
                    action_msg += get_question(q, process['parameters'])
                    action_msg += '\nВаш ответ:\n'
                    action_msg += a
                setattr(session_model, 'expired', 1)
                user_survey = UsersSurveysModel(user_id=session_model.user_id, survey_id=process['id'])
                session.add(user_survey)
                session.commit()

                bc_thread = BCSaveThread(session_model.user_id, list(answers.values()))
                bc_thread.start()

                return action_msg
    elif str(current_param['id']) in answers.keys():
        pass
    else:
        result_message += current_param['botMessagesSequence'][0]['text']
        if options:
            result_message += '\nВозможные варианты ответов: ' + options
        return result_message

    return '!!!Exceptional case!!!'


def get_question(id, params):
    for item in params:
        if str(item['id']) == id:
            return item['botMessagesSequence'][0]['text']
    return ''


def _get_keys(list_of_dict):
    keys = list()
    for item in list_of_dict:
        keys.extend(item.keys())
    return keys


def get_new_process(message):
    processes = session.query(ProcessModel).all()
    for p in processes:
        has_intersection = is_new_process_has_intersection(message, p)
        if has_intersection:
            return p.process_flow
    return None


def get_current_process(process_id):
    record = session.query(ProcessModel).get(process_id)
    if record:
        return record.process_flow
    return None


def is_new_process_has_intersection(message, p):
    json_data = p.process_flow
    keywords = json_data['keywords']
    has_intersection = find_intersection(keywords, message.text)
    return has_intersection


def find_intersection(keywords, words):
    for k_array in keywords:
        k_set = set(k_array.split(','))
        if not (is_keyword_contains_value(k_set, words)):
            return False
    return True


def is_keyword_contains_value(k_set, words):
    for w in k_set:
        if w in words:
            return True
    return False


def find_intersection_string(keywords, text):
    k_set = keywords.split(',')
    if text in k_set:
        return text
    return None


def user_already_passed(user_id, survey_id):
    query_result = session.query(UsersSurveysModel).filter(UsersSurveysModel.user_id == user_id,
                                                           UsersSurveysModel.survey_id == survey_id).first()
    if query_result:
        return True
    return False


def get_current_process_and_step(user_id):
    # find session, return new if not one found
    query_result = session.query(SessionModel).filter(SessionModel.user_id == user_id,
                                                      SessionModel.expired == 0)
    record = query_result.order_by(desc(SessionModel.session_id)).first()
    if record is None:
        model = SessionModel(user_id=user_id, last_access_time=datetime.now())
        session.add(model)
        session.commit()
        return model, False
    else:
        return record, True


if __name__ == '__main__':
    bot.polling(none_stop=True)
