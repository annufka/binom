from telebot import types
import telebot
import config
import requests
import json
import time

bot = telebot.TeleBot(config.token)
bot_info = bot.get_me()

@bot.message_handler(commands=['start'])
def handle_start_help(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Привет")
    msg = bot.send_message(message.chat.id, 'Давай приступим', reply_markup=keyboard)
    bot.register_next_step_handler(msg, send_msg)

def send_msg(message):
    while True:
        check(collect(), message)
        time.sleep(600)

def collect():
    get_collect = requests.get("&".join(config.adr))
    result = get_collect.json()
    dict_id = []
    for item in range(len(result)):
        dict_id.append((result[item]["id"], result[item]["name"]))
    return dict_id

last_msg=[]
def check(dict_id, message):
    for i in range(len(dict_id)):
        get_check = requests.get(config.url_campeign + "&camp_id=" + dict_id[i][0] + "&order_name=&order_type=ASC&group1=27&group2=1&group3=1&" + config.api_key)
        all_list = get_check.json()
        for item in range(len(all_list)):
            try:
                if int(all_list[item]["leads"]) > 25 or (int(all_list[item]["clicks"]) > 1000 and int(all_list[item]["leads"] == 0)):
                    if (dict_id[i][0], all_list[item]["name"]) not in last_msg:         
                        send(dict_id[i][0], all_list[item]["name"], all_list[item]["clicks"], all_list[item]["leads"], message)
                        last_msg.append((dict_id[i][0], all_list[item]["name"]))
            except:
                pass

def send(id_campain, name, clicks, leads, message):
    bot.send_message(message.chat.id, "В компании с id - '{}' найдена подозрительная площадка '{}' c clicks - {} и leads - {}".format(id_campain, name, clicks, leads))
    

if __name__ == '__main__':
     bot.polling(none_stop=True)
