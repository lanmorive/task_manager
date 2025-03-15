import gspread
import datetime
from telebot import TeleBot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from google.oauth2.service_account import Credentials
import pandas as pd
from config import SPREADSHEET_ID, Token

# Настройка Google Sheets
creds = Credentials.from_service_account_file(
    "single-arcadia-435019-h6-4e59ee50c184.json",
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).worksheet("Tasks")

bot = TeleBot(Token)

# Временное хранилище задач
user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard = True)
    markup.add(KeyboardButton('/add'), KeyboardButton('/list'), KeyboardButton('/close'))
    bot.send_message(message.chat.id, "/add - добавить задачи, /list - посмотреть задачи, /close - закрыть бот", reply_markup=markup)


@bot.message_handler(commands=['add'])
def add(message):
    user_data[message.chat.id] = {}
    bot.send_message(message.chat.id, 'Введите задачу: ')


#Код для приоритета
@bot.message_handler(func=lambda message: message.chat.id in user_data and 'task' not in user_data[message.chat.id])
def add_task(message):
    user_data[message.chat.id]['task'] = message.text
    user_data[message.chat.id]['date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Важно, но несрочно", callback_data="Важно, но несрочно"),
        InlineKeyboardButton("Важно и срочно", callback_data="Важно и срочно"),
        InlineKeyboardButton("Неважно, но срочно", callback_data="Неважно, но срочно"),
        InlineKeyboardButton("Неважно и несрочно", callback_data="Неважно и несрочно")
    )

    bot.send_message(message.chat.id, "Выберите приоритет задачи:", reply_markup=keyboard)


#Для обработки кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: CallbackQuery):
    chat_id = call.message.chat.id
    priority = call.data

    task = user_data.get(chat_id, {}).get('task')
    date = user_data.get(chat_id, {}).get('date')
    sheet.append_row([task, priority, date, 'Активно'])
    bot.send_message(chat_id, "Задача успешно добавлена!")
    user_data.pop(chat_id, None)
    bot.answer_callback_query(call.id)


#Для вывода list
@bot.message_handler(commands=['list'])
def get_list(message):
    rows = sheet.get_all_records()
    df = pd.DataFrame(rows).query('(priority == "Важно и срочно") & (status == "Активно")').sort_values(by='date', ascending=False).head(5)
    for row in  df.itertuples(index=False):
        bot.send_message(message.chat.id, f"""Задача: {row.Tasks}\nДата добавления: {row.date}""")

@bot.message_handler(commands=['close'])
def close(message):
    bot.
if __name__ == '__main__':
    bot.polling(none_stop=True)
