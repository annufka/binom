from telebot import types
import telebot
import config
import requests
import json

bot = telebot.TeleBot(config.token)
bot_info = bot.get_me()

@bot.message_handler(commands=['start'])
def handle_start_help(message):
    start = types.ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard = True)
    start.add("/start")
    id_user = message.from_user.id
    bot.send_message(message.chat.id, check(message))
    

def check(message):
    r = requests.get("&".join(config.adr))
    result = r.json()
    dict_id = []
    *c, list_of_dict = result
    
"""
            dict_id.append(result[item][elem]("id"))
    return dict_id
"""
if __name__ == '__main__':
     bot.polling(none_stop=True)
