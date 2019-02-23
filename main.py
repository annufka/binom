from telebot import types
import telebot
import config
import requests
import json
import time
import sqlite3
import datetime

class DB:
    """
    класс для работы с базой данных
    """
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name, check_same_thread = False)
        self.cursor = self.conn.cursor()

    #создание таблицы
    def create_table(self):
        self.cursor.execute("CREATE TABLE Users (id_user TEXT PRIMARY KEY, api_key TEXT, group TEXT, last_msg TEXT)")
        self.conn.commit()

    #добавление начальных данных (ид пользователя и api)
    def add_user(self, user, api):
        self.cursor.execute("INSERT INTO Users (id_user, api_key) VALUES (?, ?)", (user, api))
        self.conn.commit()

    #добавление начальных данных (исло для сортировки)
    def add_id_group(self, user, id_group):
        self.cursor.execute("UPDATE Users SET group=? WHERE id_user=?", (id_group, user))
        self.conn.commit()
        
    #добавим tuple из последней компании и плохой площадки, чтобы не повторять сообщения
    def add_msg(self, list_of_companies, user):
        last_db = cursor.execute("SELECT last_msg FROM Users WHERE id_user=?", (user))
        list_of_companies = last_db + list_of_companies
        self.cursor.execute("UPDATE Users SET last_msg=? WHERE id_user=?", (list_of_companies, user))
        self.conn.commit()

    #возвращаем колонку ключей
    def get_api(self, user):
        return self.cursor.execute("SELECT api_key FROM Users WHERE id_user=?", (user))

    #возвращаем колонку номера группы
    def get_num_group(self, user):
        return self.cursor.execute("SELECT group FROM Users WHERE id_user=?", (user))

    #возвращаем колонку сообщений
    def get_last(self, user):
        return self.cursor.execute("SELECT last_msg FROM Users WHERE id_user=?", (user))

    #очищаем колонку с сообщениями раз в сутки
    def del_last_msg(self):
        self.cursor.execute("UPDATE Users SET last_msg = ''")
        self.conn.commit()

#экземпляр класса, чтобы создать бота
bot = telebot.TeleBot(config.token)
bot_info = bot.get_me()


#комманда старт
@bot.message_handler(commands=['start'])
def handle_start_help(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("OK")
    msg = bot.send_message(message.chat.id, "Давай приступим", reply_markup=markup)
    bot.register_next_step_handler(msg, first)

def first(message):
    user_key = bot.send_message(message.chat.id, "Введи свой ключ")
    bot.send_message(user_key.chat.id, message.text)
    #bot.register_next_step_handler(class_db.add_user(message.chat.id, user_key), second)


def second(message):
    user_sort = bot.send_message(message.chat.id, "Введи число для сортировки по человеку")
    class_db.add_id_group(message.chat.id, user_sort)
    bot.register_next_step_handler("Принято, мой повелитель", send_msg)


def send_msg(message):
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
        get_check = requests.get(config.url_campeign + "&camp_id=" + dict_id[i][0] + "&order_name=&order_type=ASC&group1=27&group2=1&group3=1&" + class_db.get_api(message.chat.id))
        all_list = get_check.json()
        for item in range(len(all_list)):
            try:
                if int(all_list[item]["leads"]) > 25 or (int(all_list[item]["clicks"]) > 1000 and int(all_list[item]["leads"] == 0)):
                    if (dict_id[i][0], all_list[item]["name"]) not in class_db.get_last(message.chat.id):
                        send(dict_id[i][0], all_list[item]["name"], all_list[item]["clicks"], all_list[item]["leads"], message)
                        class_db.add_msg((dict_id[i][0], all_list[item]["name"]), message.chat.id)
            except:
                pass

def send(id_campain, name, clicks, leads, message):
    bot.send_message(message.chat.id, "В компании с id - '{}' найдена подозрительная площадка '{}' c clicks - {} и leads - {}".format(id_campain, name, clicks, leads))
    

if __name__ == '__main__':
    class_db = DB("binom.db")
    try:
        class_db.create_table()
    except:
        pass
    bot.polling(none_stop=True)
