import gspread
import telebot
import datetime
from function import *
from google.oauth2.service_account import Credentials
from config import SPREADSHEET_ID, Token

creds = Credentials.from_service_account_file("single-arcadia-435019-h6-4e59ee50c184.json", scopes=["https://www.googleapis.com/auth/spreadsheets"])
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).worksheet("Tasks")


bot = telebot.TeleBot(Token)


@bot.message_handler(commands=['start'])
def start(message):
       get_start(bot,message)

@bot.message_handler(commands=['задачи'])
def add_task(message):
      bot.send_message(message.chat.id,'Введите задачу:')

      if message.text == 'stop':
             bot.send_message(message.chat.id,'Закончили')
             return

      bot.register_next_step_handler(message, add_task_hadler)

def add_task_hadler(message):
      task = message.text
      sheet.append_row([task, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
      bot.send_message(message.chat.id, "Задача добавлена!")
      bot.register_next_step_handler(message, add_task)

def main():
      bot.polling()

if __name__ == '__main__':
            main()