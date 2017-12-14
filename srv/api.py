import json
import logging
from functools import wraps

from flask import Blueprint, jsonify
from flask import request, Response

from mongo_repository import MongoRepository

api_blueprint = Blueprint('api', __name__)

polls_repo = MongoRepository('polls')

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


@api_blueprint.route('/version', methods=['GET'])
@requires_auth
def version():
    return jsonify({
        'api_version': 1.0,
        'error': None
    })


@api_blueprint.route('/poll', methods=['POST'])
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


@api_blueprint.route('/polls', methods=['GET'])
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
