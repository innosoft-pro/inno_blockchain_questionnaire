"""
Joined initialization for app component
"""
import logging

from flask import Flask, jsonify
from api import api_blueprint

from logs.loggers import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

# Initialization of the app
app = Flask(__name__)
app.register_blueprint(api_blueprint)


@app.errorhandler(404)
def page_not_found(e):
    response = jsonify({
        'error': 'Method not found.'
    })
    response.status_code = 404
    return response


@app.errorhandler(Exception)
def all_exceptions_handler(error):
    response = jsonify({
        'error': str(error)
    })
    response.status_code = 500
    return response
