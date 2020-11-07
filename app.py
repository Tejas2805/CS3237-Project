from telegram.ext.dispatcher import run_async

from flask import Flask, request
from credentials import bot_token, bot_user_name,URL

import telegram
import logging

import nltk
nltk.download('punkt') #NEED TO RUN THIS THE FIRST TIME YOU USE IT

TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)

logger = logging.getLogger(__name__)

@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    # Telegram understands UTF-8, so encode text for unicode compatibility
    text = update.message.text.encode('utf-8').decode()
    print("got text message :", text)

    response = get_response(text, update)
    if response != "no_response":
            bot.sendMessage(chat_id=chat_id, text=response, parse_mode=telegram.ParseMode.MARKDOWN)
    return 'ok'

@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"

@app.route('/')
def index():
    return '.'


if __name__ == '__main__':
    app.run(threaded=True)

def start_info(update):
    user_first_name = update.message.from_user.first_name
    message = "Hi {}, let's begin!\n\n".format(user_first_name)
    return message

def get_response(msg, update):

    msg_list = msg.split(' ')

    if msg == "/start":
        return start_info(update)
    else:
        return "Wrong input"
