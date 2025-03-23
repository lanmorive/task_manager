import gspread
import datetime
from telebot import TeleBot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from google.oauth2.service_account import Credentials
import pandas as pd
import threading
import schedule
from sheet_manager import SheetManager
from config import SPREADSHEET_ID, Token
import time
from task import Task

# Настройка Google Sheets
db = SheetManager(SPREADSHEET_ID)
bot = TeleBot(Token)

# Временное хранилище задач
user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard = True)
    markup.add(KeyboardButton('/add'), KeyboardButton('/list'), KeyboardButton('/close'))
    bot.send_message(message.chat.id, "/add - добавить задачи, /list - посмотреть задачи, /close - закрыть задачи", reply_markup=markup)


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
    task = Task(id_=call.message.chat.id, task=user_data.get(call.message.chat.id, {}).get('task'), priority=call.data, date=user_data.get(call.message.chat.id, {}).get('date'), status='Активно')
    db.add_task(task.task,task.date,task.priority)    
    bot.edit_message_reply_markup(chat_id=task.id_, message_id=call.message.message_id, reply_markup=None)
    bot.answer_callback_query(call.id, text="Задача добавлена ✅")


#Для вывода list
@bot.message_handler(commands=['list'])
def get_list(message):
    for row in db.get_active_tasks().values.tolist():
        bot.send_message(message.chat.id, f"""Задача под номером {row[0]}: {row[1]}\nДата добавления: {row[3]}\nПриоритет: {row[2]}""")

#Закрываем тасочки
@bot.message_handler(commands=['close'])
def close(message):
    bot.send_message(message.chat.id, 'Введите номер задачи, которую хотите закрыть: ')
    bot.register_next_step_handler(message,close_task)

def close_task(message):
    bot.send_message(message.chat.id, db.close_task(message.text))

#На репит бота ставим
def send_daily_reminder():
    bot.send_message(1493002170, f'Сегодня нужно сделать некоторые задачи!!!!')


reminder_times = ["11:00", "15:00", "19:35"]
for t in reminder_times:
    schedule.every().day.at(t).do(send_daily_reminder)

def schedule_tasks():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    threading.Thread(target=schedule_tasks,daemon=True).start()
    bot.polling(none_stop=True)
