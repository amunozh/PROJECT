import json
import requests
import telegram
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
import paho.mqtt.client as PahoMQTT
from threading import Thread

import logging

#Variables for bot
OPTIONS, CHOOSE_PATIENT, REGISTER, ADD_PATIENT, IDLE = range(5)


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
        if response.text == '204' : #Empty user list
            return(False)
        elif response.text == '404': #User not found
            return(False)
        else:
            user = json.loads(response.text)
            return(user)

    def add_user(self, name, surname , telegram_ID):
        user_data = json.dumps({'name':name, 'surname':surname, 'telegram_ID': telegram_ID})
        response = requests.post("http://" + self.catalogIP + ":" + self.catalogPort + "/catalog/add_user?json_msg=" + user_data)
        if response.status_code == 200:
            return(True)
        else:
            return(False)

    def get_patients(self):
        response = requests.get("http://" + self.catalogIP + ":" + self.catalogPort + "/catalog/show_patients")
        if response.status_code == 200:
            list_patients = json.loads(response.text)
            available_patients = []
            if list_patients:
                for patient in list_patients:
                    if patient['caretaker'] is None:
                        available_patients.append(str(patient['ID']) + ':' + patient['name']+' '+patient['surname'])
            return (available_patients)
        else:
            return(False)

    def put_caretaker(self, patient_ID, caretaker_ID):
        data = {'patient_ID':patient_ID,'caretaker': caretaker_ID}
        data_json = json.dumps(data)
        response = requests.put("http://" + self.catalogIP + ":" + self.catalogPort + "/catalog/caretaker?json_msg=" + data_json)
        print(response.text)
        if response.text == '404':
            return(False)
        elif response.text == '204':
            return (False)
        else:
            return (True)

    def my_patients(self, caretaker_ID):
        response = requests.get("http://" + self.catalogIP + ":" + self.catalogPort + "/catalog/show_patients")
        if response.status_code == 200:
            list_patients = json.loads(response.text)
            my_patients = []
            if list_patients:
                for patient in list_patients:
                    if patient['caretaker'] == caretaker_ID:
                        my_patients.append(patient['name']+' '+patient['surname'])
                return(my_patients)
            else:
                return(False)

    def search_patient(self, device_ID):
        response = requests.get("http://" + self.catalogIP + ":" + self.catalogPort + "/catalog/show_patients")
        if response.status_code == 200:
            list_patients = json.loads(response.text)
            for patient in list_patients:
                if patient['health_device'] == device_ID:
                    if patient['caretaker'] != None:
                        return({'patient':patient['name']+' '+patient['surname'], 'caretaker':patient['caretaker']})
                    else:
                        return(False)
            return(False)
        else:
            return(False)

class telegram_sub(Thread):
    def __init__(self, telegram_bot, catalog):
        Thread.__init__(self)
        self.thebot = telegram_bot
        self.thecatalog = catalog
        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client('telegram_sub', False)
        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived

        self.topic = '/Alerts/#'

    def run (self):
        #manage connection to broker
        #client.username_pw_set('rdehsovk', 'yWMIkwY8dkw1')
        print("The broker ip is: " +  self.thecatalog.brokerIP)
        self._paho_mqtt.connect(self.thecatalog.brokerIP, self.thecatalog.brokerPort)
        self._paho_mqtt.loop_start()
        # subscribe for a topic
        self._paho_mqtt.subscribe(self.topic, 2)

    def stop (self):
        self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def myOnConnect (self, paho_mqtt, userdata, flags, rc):
        print ("Connected to message broker with result code: "+str(rc))

    def myOnMessageReceived (self, paho_mqtt , userdata, msg):
        # A new message is received

        print ("Topic:'" + msg.topic+"', QoS: '"+str(msg.qos)+"' Message: '"+str(msg.payload) + "'")

        alert_device = (msg.topic).split('/')[-1]
        info = self.thecatalog.search_patient(alert_device)
        self.thebot.send_message(chat_id=int(info['caretaker']), text='There is a problem with the patient {}'.format(info['patient']))



class telegram_bot:
    def __init__(self,TOKEN, IP_man, Port_man ):
        self.token = TOKEN
        bot = telegram.Bot(token= TOKEN)
        self.bot_id = bot.get_me()['id']
        #Register on catalog
        self.catalog = catalog_connection(IP_man, Port_man, self.bot_id)
        #Start updates
        self.updater = Updater(token= self.token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.subscriber = telegram_sub(bot, self.catalog)



    def helper_text_list(self, listing):
        prefix = "* "
        end_line =" \n"
        text = ""
        for element in listing:
            new_line = prefix + element + end_line
            text = text + new_line
        return(text)

    def start(self, update, context):
        user = update.message.from_user
        is_user = self.catalog.get_user(user['id'])
        if is_user:
            reply_keyboard = [['Add patient', 'Show my patients']]

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
        option = update.message.text


        if option.lower() == 'add patient':
            available_patients = self.catalog.get_patients()

            if available_patients:
                reply_keyboard = [available_patients]

                update.message.reply_text(
                    text="Please select the patients that you are taking care of",
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

                return (ADD_PATIENT)
            else:
                reply_keyboard = [['Add patient', 'Show my patients']]

                update.message.reply_text(
                    text="Not available patients "
                         "What do you want to do?",
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

                return (OPTIONS)

        elif option.lower() == 'show my patients':
            user = update.message.from_user
            patients = self.catalog.my_patients(user['id'])

            if patients:
                reply_keyboard = [['Add patient', 'Show my patients']]
                text = self.helper_text_list(patients)
                update.message.reply_text(
                    text=text + "Now what do you want to do?",
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
                    reply_markdown = True)

            else:
                reply_keyboard = [['Add patient', 'Show my patients']]
                update.message.reply_text(
                    text="You are not taking care of any patient yet. What do you want to do?",
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

        return (OPTIONS)


    def register(self, update, context):
        user = update.message.from_user

        option = update.message.text

        if option.lower() == 'yes':
            registry_success = self.catalog.add_user(user['first_name'], user['last_name'], user['id'])
            if registry_success:

                reply_keyboard = [['Add patient', 'Show my patients']]

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

        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="No problem! Whenever you want to become caretaker type /start")
            return (ConversationHandler.END)

    def add_patient(self,update,context):
        option = update.message.text
        user = update.message.from_user
        patient_ID = int(option.split(':')[0])
        response = self.catalog.put_caretaker(patient_ID, user['id'])

        if response:
            reply_keyboard = [['Add patient', 'Show my patients']]

            update.message.reply_text(
                text="Excelent! The alerts regarding to the patient {} will be sent to you."
                     "Now, what do you want to do?".format(user['first_name']),
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            return (OPTIONS)

        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Please try again typing /start")


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
                OPTIONS: [MessageHandler(Filters.regex('^(Add patient|Show my patients)$'), self.options)],
                REGISTER: [MessageHandler(Filters.regex('^(Yes|No)$'), self.register)],
                ADD_PATIENT: [MessageHandler(Filters.text, self.add_patient)],
            },

            fallbacks=[CommandHandler('cancel', self.cancel)]
        )



        self.dispatcher.add_handler(conv_handler)

        self.subscriber.start()
        self.updater.start_polling()
        #unknown_handler = MessageHandler(Filters.command, unknown)
        #dispatcher.add_handler(unknown_handler)

if __name__ == '__main__':
    TOKEN = "850291973:AAGzKfdmDjiQ2On-yfX4u20LrpHiuGyMqLA"
    health_bot = telegram_bot(TOKEN, "192.168.1.123", "8585")
    health_bot.run()
    health_bot.updater.idle()





