import json
import requests
import telegram
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)

import logging

#Variables for bot
OPTIONS, CHOOSE_PATIENT, REGISTER, PATIENT_ADDED, IDLE = range(5)


class catalog_connection:
    def __init__(self, IP_addres_man, Port_addres_man, botID):
        response = requests.get("http://" + IP_addres_man + ":" + Port_addres_man + "/address_manager/get")
        r = response.content.decode('utf-8')
        jr = json.loads(r)
        self.catalogIP = jr['ip']
        self.catalogPort = str(jr['port'])

        register_data = json.dumps({'ID': botID, 'end_point': [None, None], 'resources': ['bot']})
        response = requests.post("http://" + self.catalogIP + ":" + self.catalogPort + "/catalog/add_service?json_msg=" + register_data)

        response = requests.get("http://" + self.catalogIP + ":" + self.catalogPort + "/catalog/broker")
        r = response.content.decode('utf-8')
        jr = json.loads(r)
        self.brokerIP = jr['ip']
        self.brokerPort = jr['port']

        print('Service bot registered succesfully')

    def get_user(self, user_ID):
        user_data = json.dumps({'ID':user_ID})
        response = requests.get("http://" + self.catalogIP + ":" + self.catalogPort + "/catalog/search_user?json_msg="+user_data)
        print(response.text)
        if response.text == '204' : #Empty user list
            print(False)
            return(False)
        elif response.text == '404': #User not found
            return(False)
        else:
            user = json.loads(response.text)
            return(user)

    def add_user(self, name, surname , telegram_ID):
        user_data = json.dumps({'name':name, 'surname':surname, 'telegram_ID': telegram_ID})
        response = requests.post("http://" + self.catalogIP + ":" + self.catalogPort + "/catalog/add_user?json_msg=" + user_data)
        print(response)
        print(response.text)
        if response == '200':
            return(True)
        else:
            return(False)



class telegram_bot:
    def __init__(self,TOKEN):
        self.token = TOKEN
        bot = telegram.Bot(token= TOKEN)
        self.bot_id = bot.get_me()['id']
        #Register on catalog
        self.catalog = catalog_connection("192.168.1.122", "8585", self.bot_id)
        #Start updates
        self.updater = Updater(token= self.token, use_context=True)
        self.dispatcher = self.updater.dispatcher


    def start(self, update, context):
        #TODO: Make the conversation with the user using ConversationHandler
        user = update.message.from_user
        is_user = self.catalog.get_user(user['id'])
        if is_user:
            reply_keyboard = [['Add patient', 'Alerts']]

            update.message.reply_text(
                text="Hello {} {}, welcome back to the health care system. "
                                          "What do you want to do?".format(user['first_name'], user['last_name']),
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            return(OPTIONS)

        else:
            reply_keyboard = [['Yes', 'No']]
            update.message.reply_text(
                text="Hello {}, I am the bot of the health care system, I will help you"
                     "to take care of your patients. Would you like to be a caretaker?"
                     "(Your personal information will be stored in our system)".format(user['username']),
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

            return(REGISTER)

    def options(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='The chosen option was {}'.format(update.message.text))

        return (ConversationHandler.END)


    def register(self, update, context):
        user = update.message.from_user
        registry_success = self.catalog.add_user(user['first_name'],user['last_name'],user['id'])
        if registry_success:
            reply_keyboard = [['Add patient', 'Alerts']]

            update.message.reply_text(
                text="Excellent {} {}! You are now a caretaker,"
                     "What do you want to do?".format(user['first_name'], user['last_name']),
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

            return(OPTIONS)

        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='There was an error while registering please type /start '
                                          'to try again')

        return (ConversationHandler.END)

    def cancel(self, update, context):
        user = update.message.from_user
        update.message.reply_text('Bye! I hope we can talk again some day.',
                                  reply_markup=ReplyKeyboardRemove())

        return (ConversationHandler.END)


    def run(self):
        print("Bot started")

        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],

            states={
                OPTIONS: [MessageHandler(Filters.regex('^(New patient|Alerts)$'), self.options)],
                REGISTER: [MessageHandler(Filters.regex('^(Yes|No)$'), self.register)],
            },

            fallbacks=[CommandHandler('cancel', self.cancel)]
        )



        self.dispatcher.add_handler(conv_handler)


        self.updater.start_polling()
        #unknown_handler = MessageHandler(Filters.command, unknown)
        #dispatcher.add_handler(unknown_handler)

if __name__ == '__main__':
    TOKEN = "850291973:AAGzKfdmDjiQ2On-yfX4u20LrpHiuGyMqLA"
    health_bot = telegram_bot(TOKEN=TOKEN)
    health_bot.run()
    health_bot.updater.idle()





