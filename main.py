import hashlib
import sqlite3
import telebot
import uuid
from decouple import config

TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN')
DATABASE_PATH = config('DATABASE_PATH')

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    text = 'Enter your username to enable notifications.'
    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    username = message.text.strip()
    query1 = f"SELECT username_lower FROM main_user WHERE username_lower='{username.lower()}'"
    res = cur.execute(query1)
    fetch1 = res.fetchone()
    if fetch1 is None:
        output = 'Error'
    else:
        query2 = f"SELECT telegram_connected FROM main_user WHERE username_lower='{username.lower()}'"
        res = cur.execute(query2)
        fetch2 = res.fetchone()
        if fetch2[0] == 1:
            output = 'Error'
        elif fetch2[0] == 0:
            while True:
                link = uuid.uuid4()
                h = hashlib.sha256()
                h.update(link.encode())
                link_hash = h.hexdigest()
                query3 = f"SELECT telegram_link_hash FROM main_user WHERE telegram_link_hash='{link_hash}'"
                res = cur.execute(query3)
                fetch3 = res.fetchone()
                if fetch3 is None:
                    break
                else:
                    continue
            chat_id = message.chat.id
            query4 = f"UPDATE main_user SET telegram_chat_id='{chat_id}' WHERE username_lower='{username.lower()}'"
            query5 = f"UPDATE main_user SET telegram_link_hash='{link_hash}' WHERE username_lower='{username.lower()}'"
            cur.execute(query4)
            cur.execute(query5)
            con.commit()
            output = f'Open link https://messedges.com/tg/{link} as user {username} to enable notifications.'
    bot.send_message(message.chat.id, output)


bot.infinity_polling()
