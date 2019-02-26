from telebot import types
import telebot
import config
import requests
import json
import time
import datetime
import for_db

#экземпляр класса, чтобы создать бота
bot = telebot.TeleBot(config.token)
bot_info = bot.get_me()
class_db = for_db.DB("binom.db")


#комманда старт
@bot.message_handler(commands=['start'])
def handle_start_help(message):
    class_db.create_table()
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("OK")
    msg = bot.send_message(message.chat.id, "Давай приступим", reply_markup=markup)
    bot.register_next_step_handler(msg, first)

def first(message):
    user_key = bot.send_message(message.chat.id, "Введи свой ключ")
    bot.register_next_step_handler(message, second)

def second(message):
    class_db.add_user(message.chat.id, message.text)
    user_sort = bot.send_message(message.chat.id, "Введи число для сортировки по человеку")
    bot.register_next_step_handler(message, send_msg)

def send_msg(message):
    class_db.add_id_group(message.chat.id, message.text)
    while True:
        dateSTR = datetime.datetime.now().strftime("%H:%M:%S")
        if dateSTR >= "22:57:00" and dateSTR <= "23:02:00":
            class_db.del_last_msg()
        else:
            check(collect(message), message)
            time.sleep(600)

#собираем компании
def collect(message):
    get_collect = requests.get(config.url + config.user_group + "&group=" + class_db.get_num_group(message.chat.id) + config.traffic_source + config.date + config.status + class_db.get_api(message.chat.id))
    result = get_collect.json()
    dict_id = []
    for item in range(len(result)):
        dict_id.append((result[item]["id"], result[item]["name"]))
    return dict_id

#проверяем площадки
def check(dict_id, message):
    for i in range(len(dict_id)):
        get_check = requests.get(config.url_campaign + "&camp_id=" + dict_id[i][0] + "&order_name=&order_type=ASC&group1=27&group2=1&group3=1&" + class_db.get_api(message.chat.id))
        all_list = get_check.json()
        for item in range(len(all_list)):
            try:
                if int(all_list[item]["leads"]) > 25 or (int(all_list[item]["clicks"]) > 1000 and int(all_list[item]["leads"] == 0)):
                    all_msg = class_db.get_last(message.chat.id)
                    for_me = str(dict_id[i][0]) + ', ' + str(all_list[item]["name"])
                    if for_me in all_msg:
                        pass
                    else:
                        send(dict_id[i][0], dict_id[i][1], all_list[item]["name"], all_list[item]["clicks"], all_list[item]["leads"], message)
                        
            except:
                pass

def send(id_campaign, name_campaign, name, clicks, leads, message):
    bot.send_message(message.chat.id, "В компании ({}) {} найдена подозрительная площадка '{}' c clicks - {} и leads - {}".format(id_campaign, name_campaign, name, clicks, leads))
    class_db.add_msg(id_campaign, name, message.chat.id)
    

if __name__ == '__main__':
    bot.polling(none_stop=True)
