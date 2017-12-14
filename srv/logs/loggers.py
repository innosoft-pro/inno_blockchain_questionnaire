import json
import logging
import logging.config
import os
import time


def setup_logging(
        default_path='app/logs/logging.json',
        default_level=logging.DEBUG,
        env_key='LOG_CFG'
):
    logging.Formatter.converter = time.gmtime

    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

    logger = logging.getLogger('')

    current_env = os.getenv('CURR_ENV', 'test')
    if current_env.lower() in ['test', 'dev']:
        logger.setLevel(logging.DEBUG)
    elif current_env.lower() == 'production':
        logger.setLevel(logging.INFO)
