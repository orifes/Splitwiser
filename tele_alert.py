import telebot
from install import get_config, BOT_TOKEN_KEY, CHAT_ID_KEY

config = get_config()
BOT_TOKEN = config[BOT_TOKEN_KEY]
CHAT_ID = config[CHAT_ID_KEY]
bot = telebot.TeleBot(BOT_TOKEN)


def send_message(message):
    bot.send_message(CHAT_ID, message)


def send_messages(msg_list):
    for msg in msg_list:
        send_message(msg)
