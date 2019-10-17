import json
import requests
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

class telegram_bot:
    def __init__(self,TOKEN):
        self.token = TOKEN
        self.updater = Updater(token= self.token, use_context=True)
        self.dispatcher = self.updater.dispatcher

    def start(self, update, context, user_data):
        context.bot.send_message(chat_id= update.effective_chat.id,
                                 text="I'm a bot, please talk to me!")
        print(user_data)

    def unknown(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")



    def run(self):
        self.updater.start_polling()
        start_handler = CommandHandler('start', self.start, pass_user_data=True)
        self.dispatcher.add_handler(start_handler)

        #unknown_handler = MessageHandler(Filters.command, unknown)
        #dispatcher.add_handler(unknown_handler)

if __name__ == '__main__':
    TOKEN = "850291973:AAGzKfdmDjiQ2On-yfX4u20LrpHiuGyMqLA"
    health_bot = telegram_bot(TOKEN=TOKEN)
    health_bot.run()
    health_bot.updater.idle()





