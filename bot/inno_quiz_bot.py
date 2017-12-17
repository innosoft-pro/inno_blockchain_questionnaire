import logging

from telegram.ext import CommandHandler
from telegram.ext import Updater

updater = Updater(token='475545145:AAHtSa3WTcR0je3rQK76kS_wlrYsOiWBKas')
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

if __name__ == '__main__':
    updater.start_polling()
