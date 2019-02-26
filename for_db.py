import sqlite3

class DB:
    """
    класс для работы с базой данных
    """

    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.conn.text_factory = sqlite3.OptimizedUnicode

    # создание таблицы
    def create_table(self):
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS Users (id_user TEXT PRIMARY KEY, api_key TEXT, id_group TEXT, last_msg TEXT)")
        self.conn.commit()

    # добавление начальных данных (ид пользователя и api)
    def add_user(self, user, api):
        self.cursor.execute("INSERT OR IGNORE INTO Users (id_user, api_key) VALUES (?, ?)", (str(user), api))
        self.conn.commit()

    # добавление начальных данных (число для сортировки)
    def add_id_group(self, user, group_input):
        self.cursor.execute("UPDATE Users SET id_group=? WHERE id_user=?", (group_input, user))
        self.conn.commit()

    # добавим последнюю компанию и плохую площадку, чтобы не повторять сообщения
    def add_msg(self, id_for_add, name_for_add, user):
        self.cursor.execute("SELECT last_msg FROM Users WHERE id_user=?", [user])
        last_db = str(self.cursor.fetchall()[0])
        list_of_companies = last_db + ', ' + str(id_for_add) + ', ' + name_for_add
        self.cursor.execute("UPDATE Users SET last_msg=? WHERE id_user=?", (list_of_companies, user))
        self.conn.commit()

    # возвращаем колонку ключей
    def get_api(self, user):
        self.cursor.execute("SELECT api_key FROM Users WHERE id_user=?", [user])
        return_key = str(self.cursor.fetchall()[0])
        return_key = return_key.replace("('", "").replace("',)", "")
        return return_key

    # возвращаем колонку номера группы
    def get_num_group(self, user):
        self.cursor.execute("SELECT id_group FROM Users WHERE id_user=?", [user])
        return_group = str(self.cursor.fetchall()[0])
        return_group = return_group.replace("('", "").replace("',)", "")
        return return_group

    # возвращаем колонку сообщений
    def get_last(self, user):
        self.cursor.execute("SELECT last_msg FROM Users WHERE id_user=?", [user])
        return_msg = str(self.cursor.fetchall()[0])
        return_msg = return_msg.replace("('", "").replace("',)", "")
        return return_msg

    # очищаем колонку с сообщениями раз в сутки
    def del_last_msg(self):
        self.cursor.execute("UPDATE Users SET last_msg = NULL")
        self.conn.commit()