import telebot
import sqlite3

bot = telebot.TeleBot("7865221056:AAGd6SguYdbK-telJKWeoGxPTVkUD4mXJ6I")
name = None
password = None


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "Добавить магазины - /add",
    )


@bot.message_handler(commands=["add"])
def add(message):
    conn = sqlite3.connect("database.sql")
    cur = conn.cursor()

    cur.execute(
        "CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, name varchar(50), pass varchar(50), link varchar(100))"
    )
    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(
        message.chat.id, "Чтобы добавить павильон, сначала введите линию (а-я):"
    )
    bot.register_next_step_handler(message, user_name)


def user_name(message):
    global name
    name = message.text.strip()
    bot.send_message(message.chat.id, "Отлично, теперь введите номер павильона:")
    bot.register_next_step_handler(message, user_pass)


def user_pass(message):
    global password
    password = message.text.strip()
    bot.send_message(message.chat.id, "Осталось только добавить ссылку:")
    bot.register_next_step_handler(message, user_link)


def user_link(message):
    link = message.text.strip()
    conn = sqlite3.connect("database.sql")
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO users (name, pass, link) VALUES ('%s', '%s', '%s')"
        % (name, password, link)
    )
    conn.commit()
    cur.close()
    conn.close()

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton(
            "Список добавленных павильонов", callback_data="users"
        )
    )
    bot.send_message(message.chat.id, "Павильон зарегистрирован.", reply_markup=markup)


@bot.message_handler(commands=["look"])
def look(message):
    conn = sqlite3.connect("database.sql")
    cur = conn.cursor()

    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    info = ""
    for el in users:
        info += f"Линия: {el[1]}, павильон: {el[2]}, ссылка: {el[3]}\n"

    cur.close()
    conn.close()

    bot.send_message(message.chat.id, info)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    conn = sqlite3.connect("database.sql")
    cur = conn.cursor()

    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    info = ""
    for el in users:
        info += f"Линия: {el[1]}, павильон: {el[2]}, ссылка: {el[3]}\n"

    cur.close()
    conn.close()

    bot.send_message(call.message.chat.id, info)


@bot.message_handler(commands=["delete"])
def delete(message):
    bot.send_message(message.chat.id, "Введите значение линии и номера через пробел")
    bot.register_next_step_handler(message, delete_data)


def delete_data(message):
    conn = sqlite3.connect("database.sql")
    cur = conn.cursor()
    data = message.text.split()
    line = data[0]
    number = data[1]
    cur.execute(
        "DELETE FROM users WHERE name = ? AND pass = ?",
        (line, number),
    )
    conn.commit()
    bot.send_message(message.chat.id, "Данные удалены!")
    cur.close()
    conn.close()


bot.polling(none_stop=True)
