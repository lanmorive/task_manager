import telebot


#start
def get_start(bot,message):
    bot.send_message(message.chat.id, 'Привет! Я бот для управления списком задач.')

