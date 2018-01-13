import json
import logging
from collections import OrderedDict
from functools import wraps

from flask import Blueprint, jsonify
from flask import request, Response, render_template

from mongo_repository import MongoRepository

api_blueprint = Blueprint('api', __name__)

polls_repo = MongoRepository('polls')
answers_repo = MongoRepository('answers')

logger = logging.getLogger(__name__)


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'admin' and password == 'secret'


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


@api_blueprint.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@api_blueprint.route('/<path:path>', methods=['GET'])
def any_root_path(path):
    return render_template('index.html')


@api_blueprint.route('/api/version', methods=['GET'])
@requires_auth
def version():
    return jsonify({
        'api_version': 1.0,
        'error': None
    })


@api_blueprint.route('/api/poll', methods=['POST'])
@requires_auth
def save_poll():
    logger.info(request.get_data())
    request_body = json.loads(request.get_data().decode('utf-8'))
    logger.info(request_body)
    poll_id = request_body.get('_id')
    logger.info(poll_id)

    if poll_id:
        result = polls_repo.update(request_body)
        logger.info(result)
        return jsonify(result)
    else:
        result = polls_repo.insert(request_body)
        logger.info(result)
        return jsonify(result)


@api_blueprint.route('/api/polls', methods=['GET'])
@requires_auth
def get_polls():
    polls = polls_repo.get_cursor({})
    result = []
    for item in polls:
        item['_id'] = str(item['_id'])
        result.append(item)
    return jsonify({
        'polls': result,
        'error': None
    })


@api_blueprint.route('/api/answers', methods=['GET'])
@requires_auth
def get_answers():
    poll_id = request.args.get('poll_id')
    if not poll_id:
        return jsonify({
            'answers': [],
            'error': 'No poll id provided'
        })

    answer_records = answers_repo.get_cursor({'poll_id': poll_id})
    poll = polls_repo.find_one({'_id': poll_id})

    result = OrderedDict()
    result['participants'] = len(answer_records)
    result['poll_name'] = poll['name']

    for record in answer_records:
        for answer in record['answers']:
            if answer['type'] in ['select', 'multiselect']:
                if not result.get(answer['question_text']):

                    result[answer['question_text']] = {
                        'type': answer['type'],
                        'answers': {
                            {answer['answer']: 1}
                        }
                    }
                elif not result[answer['question_text']].get(answer['answer']):
                    result[answer['question_text']]['answers'][answer['answer']] = 1
                else:
                    result[answer['question_text']]['answers'][answer['answer']] += 1
            elif answer['type'] == 'open':
                if not result.get(answer['question_text']):
                    result[answer['question_text']] = {
                        'type': answer['type'],
                        'answers': {
                            {
                                answer['answer']: {
                                    'likes': answer['likes'],
                                    'dislikes': answer['dislikes']
                                }
                            }
                        }
                    }
                else:
                    result[answer['question_text']]['answers'][answer['answer']] = {
                        'likes': answer['likes'],
                        'dislikes': answer['dislikes']
                    }

    return jsonify({
        'polls': result,
        'error': None
    })


def generate_answer_str_from_dict_result(result):
    str = ''
    str += 'Опрос ' + result['poll_name'] + '\n'
    str += 'Участников: ' + result['participants'] + '\n'
    str += '\n'
    for q, q_data in result['answers'].items():
        if q_data['type'] in ['select', 'multiselect']:
            str += 'Вопрос: ' + q + '(с выбором вариантов)\n'
            total_answers = 0
            for k, v in q_data['answers'].items():
                total_answers += v
            for answ, num in q_data['answers'].items():
                str += '\t' + answ + ' - ' + round(num, 1) + '% (' + num + ' голос)\n'
            str += '\n'
        elif q_data['type'] == 'open':
            str += 'Вопрос: ' + q + '(открытый)\n'
            for answ, likes_data in q_data['answers'].items():
                str += '\t' + answ + ' - ' + '(лайков - ' + likes_data['likes'] + ', дизлайков - ' + likes_data[
                    'dislikes'] + ')\n'
            str += '\n'
    str += 'Итого: ' + (result['participants']) + ' участников\n'
    return str
